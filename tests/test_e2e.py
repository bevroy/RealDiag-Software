import subprocess
import time
import requests


def wait_for(url, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=3)
            return r
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"Timed out waiting for {url}")


def test_e2e_stack():
    """Bring up docker-compose, wait for services, and probe /health and /version."""
    # Start compose (detached)
    subprocess.run(["docker", "compose", "up", "--build", "-d"], check=True)
    try:
        h = wait_for("http://localhost:8000/health", timeout=30)
        assert h.status_code == 200
        v = wait_for("http://localhost:8000/version", timeout=10)
        assert v.status_code == 200
        # Check frontend page is served
        f = wait_for("http://localhost:3000/diagnostic", timeout=30)
        assert f.status_code == 200
    finally:
        # Tear down
        subprocess.run(["docker", "compose", "down"], check=False)
