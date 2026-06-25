
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import yaml
TREES_PATH = Path(__file__).resolve().parents[1] / "trees"
DEFAULT_TRIAGE_THRESHOLDS = {
    "severe_htn_sbp": 180,
    "severe_htn_dbp": 120,
    "hypotension_sbp": 90,
    "hypoxemia_o2": 92,
    "tachycardia_hr": 130,
    "tachypnea_resp": 30,
    "high_fever_temp_c": 39.0,
}
def _lower_list(xs): return [str(x).lower() for x in xs or []]
def _num(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None

def _merged_triage_thresholds(facts):
    out = dict(DEFAULT_TRIAGE_THRESHOLDS)
    custom = facts.get("triage_thresholds") or {}
    if isinstance(custom, dict):
        for key, value in custom.items():
            n = _num(value)
            if n is not None:
                out[str(key)] = n
    return out

def _threshold(thresholds, key):
    return _num(thresholds.get(str(key)))

def _match(preds, facts):
    trace=[]; 
    if not preds: return True, trace
    diag=(facts.get("diagnosis") or "").lower()
    symptoms=_lower_list(facts.get("symptoms") or [])
    exam=_lower_list(facts.get("exam") or [])
    red=_lower_list(facts.get("red_flags") or [])
    age=facts.get("age"); onset=facts.get("onset_hours")
    vitals=facts.get("vitals") or {}
    sbp=_num(vitals.get("bp_systolic", facts.get("sbp")))
    dbp=_num(vitals.get("bp_diastolic", facts.get("dbp")))
    hr=_num(vitals.get("hr", facts.get("hr")))
    resp=_num(vitals.get("resp", facts.get("resp")))
    o2=_num(vitals.get("o2", facts.get("o2")))
    temp_c=_num(vitals.get("temp_c", facts.get("temp_c")))
    triage_thresholds=_merged_triage_thresholds(facts)
    def ok(msg): trace.append(msg); return True
    if (dc:=preds.get("diagnosis_contains")) and str(dc).lower() not in diag: return False, trace
    if preds.get("diagnosis_contains"): ok(f"diagnosis contains '{preds['diagnosis_contains']}'")
    if (sca:=preds.get("symptoms_contains_any")):
        sca=_lower_list(sca); 
        if not any(tok in s for tok in sca for s in symptoms): return False, trace
        ok(f"symptoms any of {sca}")
    if (efa:=preds.get("exam_flags_any")):
        efa=_lower_list(efa); 
        if not any(tok in e for tok in efa for e in exam): return False, trace
        ok(f"exam any of {efa}")
    if (rfa:=preds.get("red_flags_any")):
        rfa=_lower_list(rfa); 
        if not any(tok in rr for tok in rfa for rr in red): return False, trace
        ok(f"red flags any of {rfa}")
    if (min_age:=preds.get("min_age")) is not None:
        if age is None or age < int(min_age): return False, trace
        ok(f"age >= {min_age}")
    if (oh:=preds.get("onset_hours_le")) is not None:
        if onset is None or onset > float(oh): return False, trace
        ok(f"onset_hours <= {oh}")
    if (v:=preds.get("sbp_ge")) is not None:
        if sbp is None or sbp < float(v): return False, trace
        ok(f"sbp >= {v}")
    if (v:=preds.get("sbp_le")) is not None:
        if sbp is None or sbp > float(v): return False, trace
        ok(f"sbp <= {v}")
    if (v:=preds.get("dbp_ge")) is not None:
        if dbp is None or dbp < float(v): return False, trace
        ok(f"dbp >= {v}")
    if (v:=preds.get("dbp_le")) is not None:
        if dbp is None or dbp > float(v): return False, trace
        ok(f"dbp <= {v}")
    if (v:=preds.get("hr_ge")) is not None:
        if hr is None or hr < float(v): return False, trace
        ok(f"hr >= {v}")
    if (v:=preds.get("hr_le")) is not None:
        if hr is None or hr > float(v): return False, trace
        ok(f"hr <= {v}")
    if (v:=preds.get("resp_ge")) is not None:
        if resp is None or resp < float(v): return False, trace
        ok(f"resp >= {v}")
    if (v:=preds.get("resp_le")) is not None:
        if resp is None or resp > float(v): return False, trace
        ok(f"resp <= {v}")
    if (v:=preds.get("o2_ge")) is not None:
        if o2 is None or o2 < float(v): return False, trace
        ok(f"o2 >= {v}")
    if (v:=preds.get("o2_le")) is not None:
        if o2 is None or o2 > float(v): return False, trace
        ok(f"o2 <= {v}")
    if (v:=preds.get("temp_c_ge")) is not None:
        if temp_c is None or temp_c < float(v): return False, trace
        ok(f"temp_c >= {v}")
    if (v:=preds.get("temp_c_le")) is not None:
        if temp_c is None or temp_c > float(v): return False, trace
        ok(f"temp_c <= {v}")
    if (name:=preds.get("triage_sbp_ge")) is not None:
        limit=_threshold(triage_thresholds, name)
        if limit is None or sbp is None or sbp < limit: return False, trace
        ok(f"sbp >= threshold '{name}' ({limit})")
    if (name:=preds.get("triage_sbp_le")) is not None:
        limit=_threshold(triage_thresholds, name)
        if limit is None or sbp is None or sbp > limit: return False, trace
        ok(f"sbp <= threshold '{name}' ({limit})")
    if (name:=preds.get("triage_dbp_ge")) is not None:
        limit=_threshold(triage_thresholds, name)
        if limit is None or dbp is None or dbp < limit: return False, trace
        ok(f"dbp >= threshold '{name}' ({limit})")
    if (name:=preds.get("triage_dbp_le")) is not None:
        limit=_threshold(triage_thresholds, name)
        if limit is None or dbp is None or dbp > limit: return False, trace
        ok(f"dbp <= threshold '{name}' ({limit})")
    if (name:=preds.get("triage_hr_ge")) is not None:
        limit=_threshold(triage_thresholds, name)
        if limit is None or hr is None or hr < limit: return False, trace
        ok(f"hr >= threshold '{name}' ({limit})")
    if (name:=preds.get("triage_hr_le")) is not None:
        limit=_threshold(triage_thresholds, name)
        if limit is None or hr is None or hr > limit: return False, trace
        ok(f"hr <= threshold '{name}' ({limit})")
    if (name:=preds.get("triage_resp_ge")) is not None:
        limit=_threshold(triage_thresholds, name)
        if limit is None or resp is None or resp < limit: return False, trace
        ok(f"resp >= threshold '{name}' ({limit})")
    if (name:=preds.get("triage_resp_le")) is not None:
        limit=_threshold(triage_thresholds, name)
        if limit is None or resp is None or resp > limit: return False, trace
        ok(f"resp <= threshold '{name}' ({limit})")
    if (name:=preds.get("triage_o2_ge")) is not None:
        limit=_threshold(triage_thresholds, name)
        if limit is None or o2 is None or o2 < limit: return False, trace
        ok(f"o2 >= threshold '{name}' ({limit})")
    if (name:=preds.get("triage_o2_le")) is not None:
        limit=_threshold(triage_thresholds, name)
        if limit is None or o2 is None or o2 > limit: return False, trace
        ok(f"o2 <= threshold '{name}' ({limit})")
    if (name:=preds.get("triage_temp_c_ge")) is not None:
        limit=_threshold(triage_thresholds, name)
        if limit is None or temp_c is None or temp_c < limit: return False, trace
        ok(f"temp_c >= threshold '{name}' ({limit})")
    if (name:=preds.get("triage_temp_c_le")) is not None:
        limit=_threshold(triage_thresholds, name)
        if limit is None or temp_c is None or temp_c > limit: return False, trace
        ok(f"temp_c <= threshold '{name}' ({limit})")
    if (any_of:=preds.get("any_of")):
        for sub in any_of:
            okk, tr=_match(sub, facts)
            if okk: trace.extend(tr+["any_of satisfied"]); break
        else: return False, trace
    if (all_of:=preds.get("all_of")):
        for sub in all_of:
            okk, tr=_match(sub, facts)
            if not okk: return False, trace
            trace.extend(tr)
        trace.append("all_of satisfied")
    return True, trace
class DecisionTreeEngine:
    def __init__(self, trees_path: Path | None = None):
        self.trees_path = trees_path or TREES_PATH
        self.trees = self._load_trees()
    def _load_trees(self):
        trees={}
        if not self.trees_path.exists(): return trees
        for f in sorted(self.trees_path.glob("*.yml")):
            doc=yaml.safe_load(f.read_text()) or {}
            if "id" in doc: trees[doc["id"]]=doc
        return trees
    def list(self): return [{"id":t["id"],"title":t.get("title")} for t in self.trees.values()]
    def evaluate(self, tree_id: str, patient: Dict[str, Any]):
        t=self.trees.get(tree_id)
        if not t: return {"error": f"tree '{tree_id}' not found"}
        cur=t.get("entry"); path=[]; tests=[]; dx=[]; trace_all=[]; seen=set()
        for _ in range(64):
            if cur is None or cur in seen: break
            seen.add(cur)
            node=next((n for n in t.get("nodes", []) if n.get("id")==cur), None)
            if not node: break
            ok,tr=_match(node.get("when") or {}, patient)
            trace_all.extend([f"[{cur}] "+s for s in tr])
            path.append(cur); tests.extend(node.get("tests") or []); dx.extend(node.get("suggest_dx") or [])
            nxt=None
            for branch in node.get("next") or []:
                if "default" in branch: nxt=branch["default"]
                if "when" in branch:
                    b_ok,_=_match(branch["when"], patient)
                    if b_ok: nxt=branch.get("go", nxt); break
            cur=nxt
        return {"tree":{"id":t["id"],"title":t.get("title")}, "path":path, "tests":sorted(set(tests)), "provisional_dx":sorted(set(dx)), "trace":trace_all}
