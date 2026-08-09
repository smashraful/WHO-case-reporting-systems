from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.lab_result import LabResultCreate, LabResultResponse
from app.services.case_service import get_case
from app.services.lab_result_service import (
    create_lab_result,
    get_lab_results_for_case,
)

router = APIRouter(prefix="/cases/{case_id}/lab-results", tags=["Lab Results"])


@router.post(
    "", response_model=LabResultResponse, status_code=status.HTTP_201_CREATED
)
def create(
    case_id: int,
    data: LabResultCreate,
    current_user: User = Depends(require_roles(UserRole.lab_staff, UserRole.admin)),
    db: Session = Depends(get_db),
):
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="Case not found")
    return create_lab_result(db, case_id, data, entered_by=current_user.id)


@router.get("", response_model=list[LabResultResponse])
def list_for_case(
    case_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not get_case(db, case_id):
        raise HTTPException(status_code=404, detail="Case not found")
    return get_lab_results_for_case(db, case_id)
