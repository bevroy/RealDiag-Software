"""
Database path for sign-in lockout, deactivation and admin password reset
(production stores users in Postgres). Runs the app in a subprocess against a
throwaway SQLite database, because the database is chosen at import time.

The database starts with a users table that predates failed_login_count /
locked_until, so this also checks the startup column auto-migration.
"""
import os
import sqlite3
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT = textwrap.dedent('''
    import os
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.services import database, auth_service
    from backend.services.security import limiter
    limiter.enabled = False
    assert database.DATABASE_AVAILABLE

    PW = "ClassPass123!"
    admin = {"Authorization": "Bearer " + os.environ["ADMIN_TOKEN"]}

    with TestClient(app, raise_server_exceptions=False) as c:
        from sqlalchemy import inspect
        cols = {col["name"] for col in inspect(database.engine).get_columns("users")}
        assert {"failed_login_count", "locked_until"} <= cols, cols

        def register(email):
            r = c.post("/users/register", json={"email": email, "password": PW, "full_name": "S"})
            assert r.status_code == 201, r.text
            c.cookies.clear()

        def login(email, pw=PW):
            r = c.post("/users/login", json={"email": email, "password": pw})
            c.cookies.clear()
            return r

        register("victim@realdiag.com"); register("classmate@realdiag.com"); register("operator@realdiag.com")
        op = c.post("/users/login", json={"email": "operator@realdiag.com", "password": PW}).cookies.get("access_token")
        c.cookies.clear()
        kw = {"headers": admin, "cookies": {"access_token": op}}

        # Lockout is stored on the row, so it holds across workers/sessions.
        for _ in range(auth_service.LOGIN_MAX_FAILED_ATTEMPTS - 1):
            assert login("victim@realdiag.com", "nope").status_code == 401
        assert login("victim@realdiag.com", "nope").status_code == 429
        with database.get_db_session() as db:
            row = db.query(database.User).filter_by(email="victim@realdiag.com").first()
            assert row.locked_until is not None
        assert login("victim@realdiag.com").status_code == 429
        assert login("classmate@realdiag.com").status_code == 200

        # Admin reset clears the lock and sets a temporary password.
        r = c.post("/admin/users/reset-password", json={"email": "victim@realdiag.com"}, **kw)
        assert r.status_code == 200, r.text
        temp = r.json()["temporary_password"]
        assert login("victim@realdiag.com").status_code == 401
        assert login("victim@realdiag.com", temp).status_code == 200

        # Deactivation blocks sign-in and an existing session.
        session = c.post("/users/login", json={"email": "classmate@realdiag.com", "password": PW}).cookies.get("access_token")
        c.cookies.clear()
        assert c.post("/admin/users/deactivate", json={"email": "classmate@realdiag.com"}, **kw).status_code == 200
        assert login("classmate@realdiag.com").status_code == 403
        assert c.get("/users/me", cookies={"access_token": session}).status_code == 403
        assert c.post("/admin/users/reactivate", json={"email": "classmate@realdiag.com"}, **kw).status_code == 200
        assert login("classmate@realdiag.com").status_code == 200
    print("DB-PATH-OK")
''')


def test_lockout_deactivation_and_admin_reset_on_a_database(tmp_path):
    db_file = tmp_path / "accounts.db"
    # A users table from before this change (no lockout columns).
    with sqlite3.connect(db_file) as conn:
        conn.execute("""CREATE TABLE users (
            id INTEGER PRIMARY KEY, user_id VARCHAR(255) UNIQUE, email VARCHAR(255) UNIQUE,
            username VARCHAR(255), hashed_password TEXT, full_name VARCHAR(255), specialty VARCHAR(255),
            institution VARCHAR(255), is_active BOOLEAN, is_verified BOOLEAN, is_employee BOOLEAN,
            email_verified BOOLEAN, email_verification_token VARCHAR(255), email_verification_sent_at TIMESTAMP,
            created_at TIMESTAMP, last_login TIMESTAMP, search_count INTEGER, favorite_count INTEGER)""")

    env = dict(os.environ)
    env.update({
        "DATABASE_URL": f"sqlite:///{db_file}",
        "JWT_SECRET_KEY": "test-only-ci-secret-key-not-for-production-use",
        "ADMIN_TOKEN": "test-admin-token-" + "c" * 24,
        "TESTING": "1",
    })
    result = subprocess.run([sys.executable, "-c", SCRIPT], cwd=ROOT, env=env,
                            capture_output=True, text=True, timeout=300)
    assert result.returncode == 0, (result.stdout[-2000:], result.stderr[-4000:])
    assert "DB-PATH-OK" in result.stdout
