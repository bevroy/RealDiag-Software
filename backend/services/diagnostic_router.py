
from fastapi import APIRouter, Body
from typing import Any, Dict
from .decision_tree_engine import DecisionTreeEngine

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])
_trees = DecisionTreeEngine()

@router.get("/trees")
def list_trees():
    return {"trees": _trees.list()}

@router.post("/evaluate/{tree_id}")
def evaluate_tree(tree_id: str, patient: Dict[str, Any] = Body(...)):
    return {"tree_result": _trees.evaluate(tree_id, patient)}
