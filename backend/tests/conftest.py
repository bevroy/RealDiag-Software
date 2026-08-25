import os

# smart_router.py's SMART_STATE_SECRET falls back to JWT_SECRET_KEY at
# import time, so this needs to be set before any test in this directory
# imports backend.services.smart_router. Mirrors the same defaults
# tests/conftest.py sets for the app-level test client.
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-" + "a" * 32)
