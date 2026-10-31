"""Medication outcome feedback is persisted (medication_outcomes table), so it survives
restarts and is shared by workers; without a database an in-process store is used."""
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from backend.services import outcome_store

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def clean_memory():
    outcome_store.reset_memory()
    yield
    outcome_store.reset_memory()


@pytest.mark.skipif(outcome_store.MedicationOutcome is not None, reason="in-memory fallback only")
def test_in_memory_fallback_counts_outcomes():
    assert outcome_store.get_outcomes("ACE inhibitor") == {"success": 0, "failure": 0, "adverse": 0}
    outcome_store.record_outcome("ACE inhibitor", "adverse")
    assert outcome_store.record_outcome("ACE inhibitor", "success") == {"success": 1, "failure": 0, "adverse": 1}
    with pytest.raises(ValueError):
        outcome_store.record_outcome("ACE inhibitor", "maybe")


def test_weighting_reads_the_store():
    from backend.services.diagnostic_router import _get_outcome_bias
    for _ in range(3):
        outcome_store.record_outcome("statin", "adverse")
    # (success - failure - 2*adverse) / total * weight = (0 - 0 - 6) / 3 * 0.5
    assert _get_outcome_bias("statin", 0.5) == pytest.approx(-1.0)


RECORD = textwrap.dedent('''
    import sys
    from backend.services import database, outcome_store
    assert database.DATABASE_AVAILABLE and outcome_store.MedicationOutcome is not None
    database.init_database()
    for outcome in sys.argv[1:]:
        print(outcome_store.record_outcome("ACE inhibitor", outcome))
''')


def run(db_file, *outcomes):
    env = dict(os.environ, DATABASE_URL=f"sqlite:///{db_file}", TESTING="1",
               JWT_SECRET_KEY="test-only-ci-secret-key-not-for-production-use")
    result = subprocess.run([sys.executable, "-c", RECORD, *outcomes], cwd=ROOT, env=env,
                            capture_output=True, text=True, timeout=300)
    assert result.returncode == 0, (result.stdout[-2000:], result.stderr[-4000:])
    return result.stdout.strip().splitlines()[-1]


def test_outcomes_survive_a_restart(tmp_path):
    db_file = tmp_path / "outcomes.db"
    assert run(db_file, "success", "adverse") == "{'success': 1, 'failure': 0, 'adverse': 1}"
    # A new process (a restart, or another worker) sees and adds to the same counts.
    assert run(db_file, "adverse", "failure") == "{'success': 1, 'failure': 1, 'adverse': 2}"
