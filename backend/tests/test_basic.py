"""
Basic sanity tests for the RealDiag backend.
"""
import pytest


def test_python_version():
    """Verify Python 3.11+ is being used."""
    import sys
    assert sys.version_info >= (3, 11), "Python 3.11+ is required"


def test_import_fastapi():
    """Verify FastAPI is available."""
    try:
        import fastapi
        assert fastapi is not None
    except ImportError:
        pytest.fail("FastAPI is not installed")


def test_yaml_loading():
    """Verify PyYAML is available for loading decision trees."""
    try:
        import yaml
        test_data = {"test": "value"}
        serialized = yaml.dump(test_data)
        deserialized = yaml.safe_load(serialized)
        assert deserialized == test_data
    except ImportError:
        pytest.fail("PyYAML is not installed")


def test_pydantic_available():
    """Verify Pydantic is available for data validation."""
    try:
        import pydantic
        assert pydantic is not None
    except ImportError:
        pytest.fail("Pydantic is not installed")


def test_uvicorn_available():
    """Verify Uvicorn is available for running the server."""
    try:
        import uvicorn
        assert uvicorn is not None
    except ImportError:
        pytest.fail("Uvicorn is not installed")
