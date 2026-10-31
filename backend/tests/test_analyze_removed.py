"""POST /analyze was removed: nothing called it and none of its domain analyzers
returned the declared AnalyzeResponse (checked by running each domain)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_analyze_route_is_not_registered():
    main = (ROOT / "backend" / "main.py").read_text()
    assert '@app.post("/analyze"' not in main
    assert "from backend.services.diagnostic_engine import analyze_case" not in main


def test_no_frontend_client_for_analyze():
    for path in (ROOT / "frontend").rglob("*"):
        if "node_modules" in path.parts or ".next" in path.parts or "out" in path.parts or not path.is_file():
            continue
        if path.suffix in (".js", ".jsx", ".ts", ".tsx"):
            assert '"/analyze"' not in path.read_text(errors="ignore"), path
