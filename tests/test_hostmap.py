import subprocess
import sys


def test_hostmap_node():
    """Run the frontend Node hostmap test script and assert it exits successfully.

    This keeps the heuristic covered in CI without introducing a JS test runner.
    """
    proc = subprocess.run(["node", "frontend/scripts/test-hostmap.js"], capture_output=True, text=True)
    # Print outputs to help debugging in CI logs
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)

    assert proc.returncode == 0, "frontend/scripts/test-hostmap.js failed"
