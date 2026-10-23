
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple
import re
import yaml
from .tree_schema import entry_point, icd10_codes, node_format, node_list, tree_id as _tree_id, tree_name
from .clinical_review import review_fields, review_notice
TREES_PATH = Path(__file__).resolve().parents[1] / "trees"
def _lower_list(xs):
    if xs is None: return []
    if not isinstance(xs, (list, tuple, set)): xs = [xs]
    return [str(x).lower() for x in xs]
def _num(x):
    try: return float(x)
    except (TypeError, ValueError): return None

# Predicate vocabulary. Every key a tree uses in `when` / `if` is one of these;
# a key the engine does not know fails the predicate (it used to be ignored,
# which made the branch match for every patient).
#   list predicates: key -> (fact list, "any" | "all")
LIST_PREDICATES = {
    "symptoms_contains_any": ("symptoms", "any"),
    "symptoms_contains_all": ("symptoms", "all"),
    "symptoms": ("symptoms", "all"),
    "exam_flags_any": ("exam", "any"),
    "exam_findings_any": ("exam", "any"),
    "exam_findings": ("exam", "all"),
    "red_flags_any": ("red_flags", "any"),
    "patient_characteristics_any": ("patient_characteristics", "any"),
    "no_red_flags": ("no_red_flags", "all"),
}
_COMPARATOR = re.compile(r"^\s*(<=|>=|<|>|=)?\s*(-?\d+(?:\.\d+)?)\s*$")
# Any other key with a single value (fever: '>38.5', dix_hallpike: positive,
# recent_attempt: true) is a named finding: it matches when
# facts["findings"][key] equals that value exactly.
def _is_finding_value(v): return isinstance(v, (str, bool, int, float))
def _finding_text(v): return str(v).lower()

def _match(preds, facts):
    trace=[]
    if not preds: return True, trace
    if not isinstance(preds, dict): return False, [f"unsupported predicate {preds!r}"]
    diag=(facts.get("diagnosis") or "").lower()
    age=_num(facts.get("age")); onset=_num(facts.get("onset_hours"))
    findings={str(k): v for k, v in (facts.get("findings") or {}).items()}
    for key, want in preds.items():
        if key == "diagnosis_contains":
            if not want: continue
            if str(want).lower() not in diag: return False, trace
            trace.append(f"diagnosis contains '{want}'")
        elif key in LIST_PREDICATES:
            fact, mode = LIST_PREDICATES[key]
            toks=_lower_list(want); have=_lower_list(facts.get(fact))
            if not toks: continue
            hit=lambda tok: any(tok in h for h in have)
            if not (any(map(hit, toks)) if mode == "any" else all(map(hit, toks))): return False, trace
            label={"symptoms": "symptoms", "exam": "exam", "red_flags": "red flags"}.get(fact, fact.replace("_", " "))
            trace.append(f"{label} {mode} of {toks}")
        elif key == "min_age":
            if want is None: continue
            if age is None or age < int(want): return False, trace
            trace.append(f"age >= {want}")
        elif key == "onset_hours_le":
            if want is None: continue
            if onset is None or onset > float(want): return False, trace
            trace.append(f"onset_hours <= {want}")
        elif key == "age":
            m=_COMPARATOR.match(str(want))
            if not m or age is None: return False, trace
            op, n = m.group(1) or "=", float(m.group(2))
            if not {"<": age < n, "<=": age <= n, ">": age > n, ">=": age >= n, "=": age == n}[op]: return False, trace
            trace.append(f"age {op} {m.group(2)}")
        elif key == "any_of":
            for sub in want or []:
                okk, tr=_match(sub, facts)
                if okk: trace.extend(tr+["any_of satisfied"]); break
            else: return False, trace
        elif key == "all_of":
            for sub in want or []:
                okk, tr=_match(sub, facts)
                if not okk: return False, trace
                trace.extend(tr)
            trace.append("all_of satisfied")
        elif _is_finding_value(want):
            if key not in findings or _finding_text(findings[key]) != _finding_text(want): return False, trace
            trace.append(f"{key} = {want}")
        else:
            return False, trace+[f"unsupported predicate '{key}'"]
    return True, trace

def _text_items(xs):
    """Node list items as text. An unquoted "- Label: detail" line loads as a
    one-key mapping; render it back as the line was written (it used to crash
    the walk with "unhashable type: 'dict'")."""
    out=[]
    for x in [] if xs is None else (xs if isinstance(xs, list) else [xs]):
        if isinstance(x, dict): out.extend(f"{k}: {v}" for k, v in x.items())
        elif x is not None: out.append(str(x))
    return out

def _branch_predicates(tree):
    """(node, branch predicate) for every branch that decides the walk."""
    for n in tree.get("nodes") or []:
        for b in n.get("next") or []:
            if not isinstance(b, dict): continue
            if "if" in b: yield n, b.get("if")
            elif "when" in b: yield n, b.get("when")

def _add(seq, v):
    if v not in seq: seq.append(v)

def tree_inputs(tree):
    """The answers that can change a conditional tree's walk, taken from its own branches.

    Returns symptoms / exam / red_flags / patient_characteristics / no_red_flags as
    lists of the trees' own tokens, findings as {name: [values]}, and which of age,
    onset_hours and free-text diagnosis the branches use.
    """
    out={"symptoms": [], "exam": [], "red_flags": [], "patient_characteristics": [], "no_red_flags": [],
         "findings": {}, "uses_age": False, "uses_onset_hours": False, "uses_diagnosis": False}
    def visit(p):
        if not isinstance(p, dict): return
        for key, want in p.items():
            if key in ("any_of", "all_of"):
                for sub in want or []: visit(sub)
            elif key in LIST_PREDICATES:
                for tok in (want if isinstance(want, (list, tuple)) else [want]):
                    if tok is not None: _add(out[LIST_PREDICATES[key][0]], str(tok))
            elif key in ("min_age", "age"): out["uses_age"]=True
            elif key == "onset_hours_le": out["uses_onset_hours"]=True
            elif key == "diagnosis_contains": out["uses_diagnosis"]=True
            elif _is_finding_value(want): _add(out["findings"].setdefault(key, []), want)
    for _, pred in _branch_predicates(tree): visit(pred)
    return out
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
        return [{"id": t["id"], "title": t.get("title"), "node_format": self._format(t), **review_fields(t.get("status"))}
                for t in self.trees.values()]
    def _format(self, t):
        return t.get("node_format") if t.get("nodes") else "none"
    def _tree_summary(self, t):
        return {"id": t["id"], "title": t.get("title"), "icd10": icd10_codes(t), **review_fields(t.get("status"))}
    def inputs(self, tree_id: str):
        """Answer choices for /diagnose, built from a conditional tree's own branches."""
        t=self.trees.get(tree_id)
        if not t: return {"error": f"tree '{tree_id}' not found"}
        fmt=self._format(t)
        if fmt != "conditional":
            return {"error": f"tree '{tree_id}' is not a conditional decision tree (node format: {fmt})", "node_format": fmt}
        return {"tree": self._tree_summary(t), "node_format": fmt, "inputs": tree_inputs(t),
                "clinical_review_notice": review_notice()}
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
        # Why the walk stopped: "end_node" (the node has no further branches),
        # "no_matching_branch" (none of its branches matched and it has no default),
        # "missing_node" (a branch points to a node id the tree does not contain),
        # or "loop".
        end_reason="end_node"; missing_node=None
        for _ in range(64):
            if cur is None: break
            if cur in seen: end_reason="loop"; break
            seen.add(cur)
            node=next((n for n in t.get("nodes", []) if n.get("id")==cur), None)
            if not node: end_reason="missing_node"; missing_node=cur; break
            ok,tr=_match(node.get("when") or {}, patient)
            trace_all.extend([f"[{cur}] "+s for s in tr])
            path.append(cur); tests.extend(_text_items(node.get("tests"))); dx.extend(_text_items(node.get("suggest_dx")))
            referrals.extend(_text_items(node.get("referrals")))
            nxt=None; why=[]
            # Handle "next" field which can be a list of conditional branches
            next_branches = node.get("next") or []
            for branch in next_branches:
                # New format: {node: "name", if: {conditions}, default: true}
                if branch.get("default"):
                    nxt=branch.get("node")
                if "if" in branch:
                    b_ok,b_tr=_match(branch["if"], patient)
                    if b_ok: 
                        nxt=branch.get("node"); why=b_tr
                        break
                # Old format: {default: "name", when: {conditions}, go: "name"}
                elif "when" in branch:
                    b_ok,b_tr=_match(branch["when"], patient)
                    if b_ok: nxt=branch.get("go", nxt); why=b_tr; break
                elif "default" in branch and isinstance(branch["default"], str):
                    nxt=branch["default"]
            if nxt is not None:
                trace_all.append(f"[{cur}] -> {nxt}" + (f": {'; '.join(why)}" if why else " (default)"))
            elif any(b.get("node") or b.get("go") or isinstance(b.get("default"), str) for b in next_branches):
                end_reason="no_matching_branch"
            cur=nxt
        
        return {
            "tree": self._tree_summary(t), 
            "path": path, 
            "tests": sorted(set(tests)), 
            "provisional_dx": sorted(set(dx)), 
            "referrals": sorted(set(referrals)), 
            "trace": trace_all,
            "end_reason": end_reason,
            "missing_node": missing_node,
            "evaluated": True,
        }
