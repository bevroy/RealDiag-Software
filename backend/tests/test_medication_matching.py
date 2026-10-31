"""Chart medications matched to the trees' related_medications through RxNorm
(backend/data/medication_rxnorm.json): ingredients, brand names, product codes,
and ATC classes for the "*x" patterns."""
import json
from pathlib import Path

import pytest

from backend.services import medication_matching as mm

DATA = json.loads(mm.DATA_PATH.read_text())
RXNORM = "http://www.nlm.nih.gov/research/umls/rxnorm"


def med(text=None, code=None):
    concept = {}
    if text:
        concept["text"] = text
    if code:
        concept["coding"] = [{"system": RXNORM, "code": code}]
    return {"medicationCodeableConcept": concept}


def ingredient(entry, name):
    return next(i for i in DATA["entries"][entry]["ingredients"] if i["name"] == name)


@pytest.mark.parametrize("text", ["Carvedilol 12.5 mg tablet", "Labetalol 200 mg", "Metoprolol succinate ER",
                                  "Coreg 25 mg", "Toprol XL 50 mg"])
def test_beta_blockers_match_the_olol_entry_including_carvedilol_and_labetalol(text):
    assert mm.matches_entry(med(text), "*olol")


def test_nystatin_is_not_a_statin_but_brands_are():
    assert not mm.matches_entry(med("Nystatin 100,000 units/mL suspension"), "*statin")
    assert mm.matches_entry(med("Lipitor 40 mg"), "*statin")
    assert mm.matches_entry(med("Atorvastatin calcium 20 mg"), "*statin")


def test_brand_names_match_their_ingredient():
    assert mm.matches_entry(med("Glucophage 500 mg"), "metformin")
    assert mm.matches_entry(med("Synthroid 75 mcg"), "levothyroxine")
    assert mm.matches_entry(med("Lantus SoloStar"), "insulin")


def test_rxnorm_product_code_matches_without_a_name():
    product = ingredient("*statin", "atorvastatin")["product_rxcuis"][0]
    assert mm.matches_entry(med(code=product), "*statin")
    assert not mm.matches_entry(med(code=product), "metformin")
    found = mm.medication_ingredients(med(code=product))
    # A combination product (here atorvastatin/ezetimibe) maps to each of its ingredients.
    assert ("atorvastatin", f"RxNorm code {product}") in [(i["name"], i["via"]) for i in found]


def test_combination_brand_matches_each_ingredient():
    zestoretic = med("Zestoretic 20-12.5 mg")
    assert mm.matches_entry(zestoretic, "*pril") and mm.matches_entry(zestoretic, "hydrochlorothiazide")


def test_whole_words_only():
    assert not mm.matches_entry(med("Prilosec 20 mg"), "*pril")
    assert not mm.matches_entry(med("Aspirin 81 mg"), "*olol")


def test_unresolved_entry_falls_back_to_the_name_pattern(monkeypatch):
    index = dict(mm._index())
    index["resolved"] = index["resolved"] - {"metformin"}
    monkeypatch.setattr(mm, "_index", lambda path=None: index)
    assert mm.matches_entry(med("metformin 500 mg"), "metformin")
    assert not mm.matches_entry(med("Glucophage 500 mg"), "metformin")


def test_data_file_covers_every_tree_entry():
    import yaml
    entries = set()
    for path in (Path(__file__).resolve().parents[1] / "trees").glob("*.yml"):
        criteria = (yaml.safe_load(path.read_text()) or {}).get("criteria")
        if isinstance(criteria, dict):
            entries |= {e.strip().lower() for e in criteria.get("related_medications") or []}
    assert entries <= set(DATA["entries"])
    assert DATA["unresolved"] == []
    assert DATA["entries"]["*olol"]["atc_class"] == "C07A"
    assert "RxNorm version" in DATA["source"]
