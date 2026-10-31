"""
Completing an invite on a database (production stores users in Postgres):
the setup link sets the password once, then sign-in works; an expired setup
link is refused. Runs the app in a subprocess against a throwaway SQLite
database, because the database is chosen at import time.
"""
import os
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT = textwrap.dedent('''
    import os
    from datetime import datetime, timedelta
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.services import database
    from backend.services.security import limiter
    limiter.enabled = False
    assert database.DATABASE_AVAILABLE
    admin = {"Authorization": "Bearer " + os.environ["ADMIN_TOKEN"]}
    with TestClient(app, raise_server_exceptions=False) as c:
        os.environ["ALLOW_SELF_REGISTRATION"] = "1"
        assert c.post("/users/register", json={"email": "op@realdiag.com", "password": "ClassPass123!", "full_name": "O"}).status_code == 201
        c.cookies.clear()
        op = c.post("/users/login", json={"email": "op@realdiag.com", "password": "ClassPass123!"}).cookies.get("access_token")
        c.cookies.clear()
        os.environ["ALLOW_SELF_REGISTRATION"] = "0"
        kw = {"headers": admin, "cookies": {"access_token": op}}

        r = c.post("/admin/users/invite", json={"email": "new@realdiag.com", "full_name": "New"}, **kw)
        assert r.status_code == 201, r.text
        token = r.json()["setup_url"].split("token=")[1].split("&")[0]
        with database.get_db_session() as db:
            row = db.query(database.User).filter_by(email="new@realdiag.com").first()
            assert row.account_setup_pending and row.invited_by and row.invited_at
            # Older than a reset link's 24 hours, still within the invite's 72.
            row.password_reset_sent_at = datetime.utcnow() - timedelta(hours=30)
        r = c.post("/users/reset-password", json={"token": token, "new_password": "Chosen-Pass-1"})
        assert r.status_code == 200, r.text
        c.cookies.clear()
        assert c.post("/users/login", json={"email": "new@realdiag.com", "password": "Chosen-Pass-1"}).status_code == 200
        c.cookies.clear()
        # One-time: the link no longer works.
        assert c.post("/users/reset-password", json={"token": token, "new_password": "Other-Pass-2"}).status_code == 400
        with database.get_db_session() as db:
            assert not db.query(database.User).filter_by(email="new@realdiag.com").first().account_setup_pending

        r = c.post("/admin/users/invite", json={"email": "late@realdiag.com"}, **kw)
        token = r.json()["setup_url"].split("token=")[1].split("&")[0]
        with database.get_db_session() as db:
            db.query(database.User).filter_by(email="late@realdiag.com").first().password_reset_sent_at = (
                datetime.utcnow() - timedelta(hours=73))
        assert c.post("/users/reset-password", json={"token": token, "new_password": "Chosen-Pass-1"}).status_code == 400
    print("INVITE-DB-OK")
''')


def test_invite_setup_link_on_a_database(tmp_path):
    env = dict(os.environ)
    env.update({
        "DATABASE_URL": f"sqlite:///{tmp_path / 'invite.db'}",
        "JWT_SECRET_KEY": "test-only-ci-secret-key-not-for-production-use",
        "ADMIN_TOKEN": "test-admin-token-" + "e" * 24,
        "TESTING": "1",
    })
    result = subprocess.run([sys.executable, "-c", SCRIPT], cwd=ROOT, env=env, capture_output=True, text=True,
                            timeout=300)
    assert result.returncode == 0, (result.stdout[-2000:], result.stderr[-4000:])
    assert "INVITE-DB-OK" in result.stdout
