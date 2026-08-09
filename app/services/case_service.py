from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.cache import cache_get, cache_set, cache_delete
from app.core.messaging import publish_event
from app.models.case import Case
from app.models.enums import CaseStatus
from app.models.location import Location
from app.models.patient import Patient
from app.schemas.case import CaseCreate, CaseStatusUpdate

STATS_CACHE_KEY = "cases:stats"
STATS_TTL_SECONDS = 60


def _invalidate_stats() -> None:
    cache_delete(STATS_CACHE_KEY)


def create_case(db: Session, data: CaseCreate, reported_by: int) -> Case:
    patient = db.query(Patient).filter(Patient.id == data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    case = Case(**data.model_dump(), reported_by=reported_by)
    db.add(case)
    db.commit()
    db.refresh(case)

    _invalidate_stats()
    publish_event(
        "case.created",
        {"case_id": case.id, "patient_id": case.patient_id, "status": case.status.value},
    )
    return case


def get_cases(db: Session) -> list[Case]:
    return db.query(Case).order_by(Case.id.desc()).all()


def get_case(db: Session, case_id: int) -> Case | None:
    return db.query(Case).filter(Case.id == case_id).first()


def update_case_status(
    db: Session, case: Case, data: CaseStatusUpdate, verified_by: int
) -> Case:
    case.status = data.status
    if data.notes is not None:
        case.notes = data.notes
    if data.status in (CaseStatus.confirmed, CaseStatus.discarded):
        case.verified_by = verified_by
    db.commit()
    db.refresh(case)

    _invalidate_stats()
    if data.status == CaseStatus.confirmed:
        publish_event(
            "case.confirmed",
            {
                "case_id": case.id,
                "patient_id": case.patient_id,
                "location_id": case.location_id,
            },
        )
    return case


def get_case_stats(db: Session) -> dict:
    cached = cache_get(STATS_CACHE_KEY)
    if cached is not None:
        return cached

    total = db.query(func.count(Case.id)).scalar() or 0

    by_status = {s.value: 0 for s in CaseStatus}
    for status_value, count in (
        db.query(Case.status, func.count(Case.id)).group_by(Case.status).all()
    ):
        key = status_value.value if hasattr(status_value, "value") else str(status_value)
        by_status[key] = count

    by_location: dict[str, int] = {}
    rows = (
        db.query(Location.name, func.count(Case.id))
        .outerjoin(Case, Case.location_id == Location.id)
        .group_by(Location.name)
        .all()
    )
    for name, count in rows:
        if count:
            by_location[name] = count

    stats = {"total": total, "by_status": by_status, "by_location": by_location}
    cache_set(STATS_CACHE_KEY, stats, ttl_seconds=STATS_TTL_SECONDS)
    return stats
