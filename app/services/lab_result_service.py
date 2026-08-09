from sqlalchemy.orm import Session

from app.models.lab_result import LabResult
from app.schemas.lab_result import LabResultCreate


def create_lab_result(
    db: Session, case_id: int, data: LabResultCreate, entered_by: int
) -> LabResult:
    lab_result = LabResult(
        case_id=case_id, entered_by=entered_by, **data.model_dump()
    )
    db.add(lab_result)
    db.commit()
    db.refresh(lab_result)
    return lab_result


def get_lab_results_for_case(db: Session, case_id: int) -> list[LabResult]:
    return (
        db.query(LabResult)
        .filter(LabResult.case_id == case_id)
        .order_by(LabResult.id.desc())
        .all()
    )
