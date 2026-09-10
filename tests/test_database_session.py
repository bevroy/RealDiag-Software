"""
Regression coverage for the DetachedInstanceError bug in database.py.

get_user_by_id/get_user_by_email (and the other db_get_user_* helpers)
return an ORM row *after* their `with get_db_session()` block has already
committed and closed the session. Before the fix, SQLAlchemy's default
expire_on_commit=True marked every attribute on that row as expired at
commit time, and the following session.close() detached the object -- so
any attribute access afterwards (e.g. auth_service.py's user.to_dict() in
get_current_user/get_optional_user) raised DetachedInstanceError. This only
ever reproduces when a real DATABASE_URL is configured (DATABASE_AVAILABLE
is True); it's invisible under the in-memory fallback used by the rest of
this test suite, so these tests deliberately point DATABASE_URL at a real
(temp file) SQLite database, matching the pattern already used by
tests/test_integration_api_keys.py's restart-survival test.

Must run in isolation from the rest of the module state: reloads
backend.services.database mid-test, which rebinds process-wide globals
(engine/SessionLocal/Base/DATABASE_AVAILABLE). Restores the original
DATABASE_URL and reloads back to the prior state in `finally`.
"""

import importlib
import os
import tempfile

import pytest


@pytest.fixture()
def real_sqlite_database():
    """Point DATABASE_URL at a fresh temp SQLite file and reload
    backend.services.database against it, restoring everything afterward."""
    from backend.services import database as database_module

    original_database_url = os.environ.get("DATABASE_URL")
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "detached_instance_test.db")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    importlib.reload(database_module)
    assert database_module.DATABASE_AVAILABLE is True
    database_module.init_database()

    try:
        yield database_module
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        importlib.reload(database_module)


def _make_user(database_module, user_id: str, email: str):
    with database_module.get_db_session() as db:
        user = database_module.User(
            user_id=user_id,
            email=email,
            hashed_password="hashed",
            full_name="Regression Test User",
            is_active=True,
            search_count=0,
            favorite_count=0,
        )
        db.add(user)


def test_get_user_by_id_to_dict_survives_session_close(real_sqlite_database):
    """This is the exact call sequence auth_service.get_current_user/
    get_optional_user use: get_user_by_id() (with block already committed
    and closed) followed by .to_dict() on the returned row."""
    _make_user(real_sqlite_database, "user_detached_1", "detached1@realdiag.com")

    user = real_sqlite_database.get_user_by_id("user_detached_1")
    assert user is not None

    # Before the fix this raised sqlalchemy.orm.exc.DetachedInstanceError.
    result = user.to_dict()
    assert result["user_id"] == "user_detached_1"
    assert result["email"] == "detached1@realdiag.com"


def test_get_user_by_email_to_dict_survives_session_close(real_sqlite_database):
    _make_user(real_sqlite_database, "user_detached_2", "detached2@realdiag.com")

    user = real_sqlite_database.get_user_by_email("detached2@realdiag.com")
    assert user is not None

    result = user.to_dict()
    assert result["user_id"] == "user_detached_2"
    assert result["email"] == "detached2@realdiag.com"


def test_get_user_search_history_to_dict_survives_session_close(real_sqlite_database):
    """Same detached-object bug also affected get_user_search_history/
    get_user_favorites/get_user_custom_lists/get_user_settings -- spot
    check one of them here."""
    _make_user(real_sqlite_database, "user_detached_3", "detached3@realdiag.com")
    with real_sqlite_database.get_db_session() as db:
        search = real_sqlite_database.SearchHistory(
            search_id="search_detached_1",
            user_id="user_detached_3",
            symptoms=["fever"],
            result_count=1,
        )
        db.add(search)

    history = real_sqlite_database.get_user_search_history("user_detached_3")
    assert len(history) == 1

    result = history[0].to_dict()
    assert result["search_id"] == "search_detached_1"
