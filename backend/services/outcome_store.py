"""
Medication outcome feedback (POST /diagnostic/medication-outcomes), persisted.

Counts of success / failure / adverse outcomes per medication class feed the
medication-history weighting in tree evaluation. They used to live in a
module-level dict, so they were lost on every restart and each worker had its
own copy. With a database they are stored in the medication_outcomes table
(created by init_database, like the other tables) and every increment is a
single atomic UPDATE, so concurrent workers do not overwrite each other.
Without a database (local runs, some tests) an in-process dict is used.
"""

import logging
from datetime import datetime
from typing import Dict

from .database import Base, DATABASE_AVAILABLE, get_db_session

logger = logging.getLogger(__name__)

OUTCOMES = ("success", "failure", "adverse")

if DATABASE_AVAILABLE and Base is not None:
    from sqlalchemy import Column, DateTime, Integer, String, update
    from sqlalchemy.exc import IntegrityError

    class MedicationOutcome(Base):
        """Outcome counts for one medication class."""
        __tablename__ = "medication_outcomes"

        med_class = Column(String(255), primary_key=True)
        success = Column(Integer, nullable=False, default=0)
        failure = Column(Integer, nullable=False, default=0)
        adverse = Column(Integer, nullable=False, default=0)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
else:
    MedicationOutcome = None

_memory: Dict[str, Dict[str, int]] = {}


def _empty() -> Dict[str, int]:
    return {o: 0 for o in OUTCOMES}


def get_outcomes(med_class: str) -> Dict[str, int]:
    """{success, failure, adverse} counts for a medication class (zeros if none)."""
    if MedicationOutcome is None:
        return dict(_memory.get(med_class) or _empty())
    with get_db_session() as db:
        row = db.query(MedicationOutcome).filter_by(med_class=med_class).first()
        return {o: int(getattr(row, o) or 0) for o in OUTCOMES} if row else _empty()


def record_outcome(med_class: str, outcome: str) -> Dict[str, int]:
    """Add one outcome and return the class's updated counts."""
    if outcome not in OUTCOMES:
        raise ValueError(f"outcome must be one of: {', '.join(OUTCOMES)}")
    if MedicationOutcome is None:
        bucket = _memory.setdefault(med_class, _empty())
        bucket[outcome] += 1
        return dict(bucket)
    column = getattr(MedicationOutcome, outcome)
    for _ in range(2):  # a concurrent first insert for the same class is retried as an update
        try:
            with get_db_session() as db:
                updated = db.execute(update(MedicationOutcome)
                                     .where(MedicationOutcome.med_class == med_class)
                                     .values({outcome: column + 1, "updated_at": datetime.utcnow()}))
                if updated.rowcount == 0:
                    db.add(MedicationOutcome(med_class=med_class, **{o: int(o == outcome) for o in OUTCOMES}))
            break
        except IntegrityError:
            logger.info(f"medication_outcomes: concurrent insert for {med_class!r}; retrying as update")
    return get_outcomes(med_class)


def reset_memory() -> None:
    """Clear the in-process store (tests)."""
    _memory.clear()
