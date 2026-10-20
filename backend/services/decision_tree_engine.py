
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import yaml
from .tree_schema import entry_point, icd10_codes, node_format, node_list, tree_id as _tree_id, tree_name
from .clinical_review import review_fields, review_notice
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
            tree_id = _tree_id(doc)
            if tree_id:
                # Internal aliases used by evaluate()/list() below
                doc["id"] = tree_id
                doc["title"] = tree_name(doc)
                doc["entry"] = entry_point(doc)
                doc["node_format"] = node_format(doc)
                # Convert nodes from dict to list if needed
                if isinstance(doc.get("nodes"), dict):
                    doc["nodes"] = node_list(doc)
                trees[tree_id] = doc
        return trees
    def list(self):
        return [{"id": t["id"], "title": t.get("title"), **review_fields(t.get("status"))}
                for t in self.trees.values()]
    def _tree_summary(self, t):
        return {"id": t["id"], "title": t.get("title"), "icd10": icd10_codes(t), **review_fields(t.get("status"))}
    def evaluate(self, tree_id: str, patient: Dict[str, Any]):
        result = self._evaluate(tree_id, patient)
        if "error" not in result:
            # Every evaluation carries the tree's review status and the global notice
            result["clinical_review_notice"] = review_notice()
        return result
    def _evaluate(self, tree_id: str, patient: Dict[str, Any]):
        t=self.trees.get(tree_id)
        if not t: return {"error": f"tree '{tree_id}' not found"}

        if not t.get("nodes"):
            return {
                "tree": self._tree_summary(t),
                "path": [],
                "tests": [],
                "provisional_dx": [],
                "referrals": [],
                "trace": [],
                "evaluated": False,
                "warning": (
                    f"Tree '{tree_id}' has no interactive decision-node structure; "
                    "use /search/by-symptoms for presentation-based matching."
                ),
            }

        node_ids = {n.get("id") for n in t.get("nodes", [])}
        if not t.get("entry"):
            return {"error": f"tree '{tree_id}' has decision nodes but no entry_point; it cannot be evaluated"}
        if t["entry"] not in node_ids:
            return {"error": f"tree '{tree_id}' entry_point '{t['entry']}' does not match any node id; it cannot be evaluated"}

        # Trees the engine cannot walk: report them as not evaluated rather than
        # returning empty lists that could be read as "no findings".
        not_evaluated = {
            "questionnaire": (
                "This tree is an interactive questionnaire that requires answers from the user "
                "and was not evaluated automatically."
            ),
            "content": (
                "This tree has no decision branches to evaluate (its nodes hold reference "
                "content only) and was not evaluated automatically."
            ),
        }
        fmt = t.get("node_format")
        if fmt in ("questionnaire", "mixed", "content"):
            return {
                "tree": self._tree_summary(t),
                "path": [],
                "tests": [],
                "provisional_dx": [],
                "referrals": [],
                "trace": [],
                "evaluated": False,
                "node_format": fmt,
                "warning": not_evaluated["content" if fmt == "content" else "questionnaire"],
            }

        cur=t.get("entry"); path=[]; tests=[]; dx=[]; referrals=[]; trace_all=[]; seen=set()
        for _ in range(64):
            if cur is None or cur in seen: break
            seen.add(cur)
            node=next((n for n in t.get("nodes", []) if n.get("id")==cur), None)
            if not node: break
            ok,tr=_match(node.get("when") or {}, patient)
            trace_all.extend([f"[{cur}] "+s for s in tr])
            path.append(cur); tests.extend(node.get("tests") or []); dx.extend(node.get("suggest_dx") or [])
            referrals.extend(node.get("referrals") or [])
            nxt=None
            # Handle "next" field which can be a list of conditional branches
            next_branches = node.get("next") or []
            for branch in next_branches:
                # New format: {node: "name", if: {conditions}, default: true}
                if branch.get("default"):
                    nxt=branch.get("node")
                if "if" in branch:
                    b_ok,_=_match(branch["if"], patient)
                    if b_ok: 
                        nxt=branch.get("node")
                        break
                # Old format: {default: "name", when: {conditions}, go: "name"}
                elif "when" in branch:
                    b_ok,_=_match(branch["when"], patient)
                    if b_ok: nxt=branch.get("go", nxt); break
                elif "default" in branch and isinstance(branch["default"], str):
                    nxt=branch["default"]
            cur=nxt
        
        return {
            "tree": self._tree_summary(t), 
            "path": path, 
            "tests": sorted(set(tests)), 
            "provisional_dx": sorted(set(dx)), 
            "referrals": sorted(set(referrals)), 
            "trace": trace_all,
            "evaluated": True,
        }
