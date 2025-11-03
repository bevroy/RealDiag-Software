
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import yaml
TREES_PATH = Path(__file__).resolve().parents[1] / "trees"
def _lower_list(xs): return [str(x).lower() for x in xs or []]
def _match(preds, facts):
    trace=[]; 
    if not preds: return True, trace
    diag=(facts.get("diagnosis") or "").lower()
    symptoms=_lower_list(facts.get("symptoms") or [])
    exam=_lower_list(facts.get("exam") or [])
    red=_lower_list(facts.get("red_flags") or [])
    age=facts.get("age"); onset=facts.get("onset_hours")
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
