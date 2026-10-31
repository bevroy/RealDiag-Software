"""FHIR access/refresh tokens are encrypted at rest in smart_sessions."""
import os
import sqlite3
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
from cryptography.fernet import Fernet, InvalidToken

from backend.services import smart_session_store as store

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def fresh_cipher(monkeypatch):
    store._token_cipher.cache_clear()
    yield
    store._token_cipher.cache_clear()


def test_round_trip_with_key_derived_from_jwt_secret(monkeypatch):
    monkeypatch.delenv(store.TOKEN_KEY_ENV, raising=False)
    stored = store.encrypt_token("access-123")
    assert stored.startswith("enc:v1:") and "access-123" not in stored
    assert store.decrypt_token(stored) == "access-123"
    assert store.encrypt_token(None) is None and store.decrypt_token(None) is None


def test_dedicated_key_is_used_when_set(monkeypatch):
    key = Fernet.generate_key().decode()
    monkeypatch.setenv(store.TOKEN_KEY_ENV, key)
    stored = store.encrypt_token("refresh-456")
    assert Fernet(key.encode()).decrypt(stored[len("enc:v1:"):].encode()) == b"refresh-456"


def test_value_saved_before_encryption_is_read_as_is():
    assert store.decrypt_token("legacy-plaintext-token") == "legacy-plaintext-token"


def test_wrong_key_cannot_decrypt(monkeypatch):
    stored = store.encrypt_token("access-123")
    monkeypatch.setenv(store.TOKEN_KEY_ENV, Fernet.generate_key().decode())
    store._token_cipher.cache_clear()
    with pytest.raises(InvalidToken):
        store.decrypt_token(stored)


SCRIPT = textwrap.dedent('''
    from datetime import datetime, timedelta
    from backend.services import database, smart_session_store as store
    assert database.DATABASE_AVAILABLE
    database.init_database()
    sid = store.create_smart_session("epic", "https://fhir.example", "pat-1", "ACCESS-SECRET", "REFRESH-SECRET",
                                     datetime.utcnow() + timedelta(minutes=30))
    row = store.get_smart_session(sid)
    assert (row.fhir_access_token, row.fhir_refresh_token) == ("ACCESS-SECRET", "REFRESH-SECRET")
    print("SID=" + sid)
''')


def test_tokens_are_ciphertext_in_the_database(tmp_path):
    db_file = tmp_path / "smart.db"
    env = dict(os.environ, DATABASE_URL=f"sqlite:///{db_file}", TESTING="1",
               JWT_SECRET_KEY="test-only-ci-secret-key-not-for-production-use")
    env.pop(store.TOKEN_KEY_ENV, None)
    result = subprocess.run([sys.executable, "-c", SCRIPT], cwd=ROOT, env=env, capture_output=True, text=True,
                            timeout=300)
    assert result.returncode == 0, (result.stdout[-2000:], result.stderr[-4000:])
    sid = next(l for l in result.stdout.splitlines() if l.startswith("SID="))[4:]
    with sqlite3.connect(db_file) as conn:
        access, refresh = conn.execute("SELECT fhir_access_token, fhir_refresh_token FROM smart_sessions "
                                       "WHERE session_id = ?", (sid,)).fetchone()
    assert access.startswith("enc:v1:") and "ACCESS-SECRET" not in access
    assert refresh.startswith("enc:v1:") and "REFRESH-SECRET" not in refresh
