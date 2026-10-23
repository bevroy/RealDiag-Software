"""Find /diagnose answers that walk a conditional tree to each of its end nodes.

Used by test_tree_walks.py. The answers are built only from the tree's own
branch predicates (the same choices /diagnostic/trees/{id}/inputs offers), and
every path is confirmed by running the real engine, so a pass means a student
can reach that end node from the /diagnose form.
"""
from __future__ import annotations

import itertools
import re
from typing import Any, Dict, List, Optional

from backend.services.decision_tree_engine import LIST_PREDICATES

LIST_FACTS = sorted({fact for fact, _ in LIST_PREDICATES.values()})
_CMP = re.compile(r"^\s*(<=|>=|<|>|=)?\s*(-?\d+(?:\.\d+)?)\s*$")
MAX_ALTERNATIVES = 64


def _empty() -> Dict[str, Any]:
    return {**{f: [] for f in LIST_FACTS}, "findings": {}, "age": [], "onset": [], "diagnosis": []}


def _merge(a: Dict[str, Any], b: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    out = _empty()
    for f in LIST_FACTS:
        out[f] = list(dict.fromkeys(a[f] + b[f]))
    for k, v in list(a["findings"].items()) + list(b["findings"].items()):
        if k in out["findings"] and str(out["findings"][k]).lower() != str(v).lower():
            return None
        out["findings"][k] = v
    for k in ("age", "onset", "diagnosis"):
        out[k] = a[k] + b[k]
    return out


def _alternatives(pred: Any) -> List[Dict[str, Any]]:
    """Fact fragments, each of which satisfies `pred`."""
    if not pred:
        return [_empty()]
    alts = [_empty()]
    for key, want in pred.items():
        if key == "any_of":
            opts = [a for sub in want or [] for a in _alternatives(sub)]
        elif key == "all_of":
            opts = [_empty()]
            for sub in want or []:
                opts = [m for x, y in itertools.product(opts, _alternatives(sub)) if (m := _merge(x, y))]
        elif key in LIST_PREDICATES:
            fact, mode = LIST_PREDICATES[key]
            toks = [str(t) for t in (want if isinstance(want, (list, tuple)) else [want]) if t is not None]
            frags = [[t] for t in toks] if mode == "any" else [toks]
            opts = []
            for frag in frags:
                o = _empty()
                o[fact] = frag
                opts.append(o)
        elif key in ("min_age", "age"):
            o = _empty()
            o["age"] = [(">=", float(want))] if key == "min_age" else [_comparator(want)]
            opts = [o]
        elif key == "onset_hours_le":
            o = _empty()
            o["onset"] = [float(want)]
            opts = [o]
        elif key == "diagnosis_contains":
            o = _empty()
            o["diagnosis"] = [str(want)]
            opts = [o]
        else:
            o = _empty()
            o["findings"] = {key: want}
            opts = [o]
        alts = [m for x, y in itertools.product(alts, opts) if (m := _merge(x, y))][:MAX_ALTERNATIVES]
    return alts


def _comparator(want):
    m = _CMP.match(str(want))
    return (m.group(1) or "=", float(m.group(2))) if m else ("=", float("nan"))


def _pick_age(constraints) -> Optional[float]:
    if not constraints:
        return None
    for candidate in sorted({n + d for _, n in constraints for d in (-1, 0, 1)}):
        if all({"<": candidate < n, "<=": candidate <= n, ">": candidate > n, ">=": candidate >= n,
                "=": candidate == n}[op] for op, n in constraints):
            return candidate
    return float("nan")


def to_patient(frag: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Turn a fragment into the body /diagnose posts."""
    patient: Dict[str, Any] = {f: list(frag[f]) for f in LIST_FACTS}
    patient["findings"] = dict(frag["findings"])
    age = _pick_age(frag["age"])
    if age is not None:
        if age != age:  # nan: contradictory age constraints
            return None
        patient["age"] = age
    if frag["onset"]:
        patient["onset_hours"] = min(frag["onset"])
    if frag["diagnosis"]:
        patient["diagnosis"] = " ".join(frag["diagnosis"])
    return patient


def _targets(node: Dict[str, Any]) -> List[str]:
    out = []
    for b in node.get("next") or []:
        if not isinstance(b, dict):
            continue
        for key in ("node", "go"):
            if b.get(key):
                out.append(b[key])
        if isinstance(b.get("default"), str):
            out.append(b["default"])
    return out


def end_nodes(tree: Dict[str, Any]) -> List[str]:
    """End nodes reachable in the tree's graph from its entry point."""
    nodes = {n["id"]: n for n in tree["nodes"]}
    seen, stack, ends = set(), [tree["entry"]], []
    while stack:
        cur = stack.pop()
        if cur in seen or cur not in nodes:
            continue
        seen.add(cur)
        nxt = [t for t in _targets(nodes[cur]) if t in nodes]
        if not nxt:
            ends.append(cur)
        stack.extend(nxt)
    return sorted(ends)


def missing_targets(tree: Dict[str, Any]) -> List[str]:
    """'node -> target' for branches whose target is not a node in the tree."""
    ids = {n["id"] for n in tree["nodes"]}
    return sorted(f"{n['id']} -> {t}" for n in tree["nodes"] for t in _targets(n) if t not in ids)


def solve(engine, tree_id: str) -> Dict[str, Dict[str, Any]]:
    """{end node id: patient body that the engine walks to it}."""
    tree = engine.trees[tree_id]
    nodes = {n["id"]: n for n in tree["nodes"]}
    found: Dict[str, Dict[str, Any]] = {}

    def walk(path: List[str], frag: Dict[str, Any]):
        patient = to_patient(frag)
        if patient is None:
            return
        actual = engine.evaluate(tree_id, patient)["path"]
        if actual[: len(path)] != path:
            return
        cur = path[-1]
        if len(actual) == len(path):  # the walk ends here with these answers
            found.setdefault(cur, patient)
        for b in nodes[cur].get("next") or []:
            if not isinstance(b, dict):
                continue
            target = b.get("node") or b.get("go") or (b["default"] if isinstance(b.get("default"), str) else None)
            if not target or target in path or target not in nodes:
                continue
            pred = b.get("if") if "if" in b else b.get("when")
            for alt in _alternatives(pred) if pred is not None else [_empty()]:
                merged = _merge(frag, alt)
                if merged is not None:
                    walk(path + [target], merged)

    walk([tree["entry"]], _empty())
    return found
