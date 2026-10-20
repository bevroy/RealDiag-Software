import os
import subprocess
import sys
from pathlib import Path

import pytest

from backend.services.database import normalize_database_url

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("url,expected", [
    ("postgresql://u:p@db.example:5432/realdiag", "postgresql+psycopg2://u:p@db.example:5432/realdiag"),
    ("postgres://u:p@db.example:5432/realdiag", "postgresql+psycopg2://u:p@db.example:5432/realdiag"),
    ("postgresql+psycopg2://u:p@h/db", "postgresql+psycopg2://u:p@h/db"),
    ("postgresql+asyncpg://u:p@h/db", "postgresql+asyncpg://u:p@h/db"),
    ("sqlite:///local.db", "sqlite:///local.db"),
    (None, None),
    ("", ""),
])
def test_normalize_database_url(url, expected):
    assert normalize_database_url(url) == expected


def test_app_imports_with_plain_postgresql_url():
    """Regression: SQLAlchemy 2.1 maps postgresql:// to psycopg (v3), which is
    not installed, so the app crashed on startup on Render (realdiag-test-backend)."""
    env = dict(os.environ)
    env["DATABASE_URL"] = "postgresql://user:pass@127.0.0.1:5999/realdiag"
    env.setdefault("JWT_SECRET_KEY", "test-only-ci-secret-key-not-for-production-use")
    code = (
        "import backend.main\n"
        "from backend.services import database\n"
        "print(database.engine.dialect.driver)\n"
    )
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env,
                            capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr[-2000:]
    assert result.stdout.strip().splitlines()[-1] == "psycopg2"
