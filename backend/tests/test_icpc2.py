"""ICPC-2 mechanism: loading, status, validation, display. No codes are generated:
every tree reports "pending licensed mapping and review"."""
from pathlib import Path

import yaml

from backend.services import icpc2
from backend.services.decision_tree_engine import DecisionTreeEngine
from backend.services.rules_engine import RulesEngine
from backend.services.search_router import _extract_clinical_info

TREES = Path(__file__).resolve().parents[1] / "trees"
TREE_IDS = [p.stem for p in TREES.glob("*.yml")]


def test_mapping_file_is_pending_and_empty():
    mapping = icpc2.load_mapping()
    assert mapping["status"] == icpc2.PENDING_STATUS == "pending licensed mapping and review"
    assert mapping["mappings"] == {} and mapping["source"] is None
    assert icpc2.mapping_problems(mapping, TREE_IDS, {}) == []


def test_every_tree_reports_pending_with_no_codes():
    for path in TREES.glob("*.yml"):
        tree = yaml.safe_load(path.read_text())
        assert icpc2.icpc2_for(tree) == {"icpc2": [], "icpc2_status": icpc2.PENDING_STATUS}, path.name


def test_responses_carry_the_icpc2_status():
    tree = yaml.safe_load((TREES / "PULM-COUGH.yml").read_text())
    assert _extract_clinical_info(tree)["icpc2_status"] == icpc2.PENDING_STATUS
    assert RulesEngine().get_rule("PULM-COUGH")["icpc2_status"] == icpc2.PENDING_STATUS
    summary = DecisionTreeEngine().inputs("ENT-SORE-THROAT")["tree"]
    assert summary["icpc2"] == [] and summary["icpc2_status"] == icpc2.PENDING_STATUS


def test_validator_rules():
    ok_entry = {"code": "R05", "label": "Cough", "mapped_by": "A", "reviewed_by": "B", "reviewed_on": "2027-01-01"}
    # Codes cannot be added while the mapping is pending.
    pending = {"status": icpc2.PENDING_STATUS, "mappings": {"PULM-COUGH": [ok_entry]}}
    assert "codes cannot be added while status is 'pending licensed mapping and review'" in \
        icpc2.mapping_problems(pending, TREE_IDS, {})
    # A reviewed mapping needs its licensed source and full provenance per code.
    reviewed = {"status": "reviewed", "source": "WONCA ICPC-2", "version": "2015",
                "mappings": {"PULM-COUGH": [ok_entry], "NOPE": [{"code": "Cough"}]}}
    problems = icpc2.mapping_problems(reviewed, TREE_IDS, {})
    assert "NOPE: unknown tree" in problems
    assert "NOPE[0]: 'Cough' is not an ICPC-2 code (letter + two digits)" in problems
    assert any(p.startswith("NOPE[0]: missing label") for p in problems)
    assert not [p for p in problems if p.startswith("PULM-COUGH")]
    assert "a reviewed mapping must name its licensed source and version" in icpc2.mapping_problems(
        {"status": "reviewed", "mappings": {}}, TREE_IDS, {})
    # Codes written into a tree are checked too.
    assert "PULM-COUGH: codes.icpc2 has codes while the ICPC-2 mapping is 'pending licensed mapping and review'" \
        in icpc2.mapping_problems({"status": icpc2.PENDING_STATUS, "mappings": {}}, TREE_IDS, {"PULM-COUGH": ["R05"]})
