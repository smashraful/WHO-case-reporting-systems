from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.case import (
    CaseCreate,
    CaseResponse,
    CaseStats,
    CaseStatusUpdate,
)
from app.services.case_service import (
    create_case,
    get_cases,
    get_case,
    get_case_stats,
    update_case_status,
)

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: CaseCreate,
    current_user: User = Depends(
        require_roles(UserRole.field_worker, UserRole.admin)
    ),
    db: Session = Depends(get_db),
):
    return create_case(db, data, reported_by=current_user.id)


@router.get("", response_model=list[CaseResponse])
def list_all(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_cases(db)


@router.get("/stats", response_model=CaseStats)
def stats(
    _: User = Depends(
        require_roles(
            UserRole.program_manager, UserRole.district_officer, UserRole.admin
        )
    ),
    db: Session = Depends(get_db),
):
    return get_case_stats(db)


@router.get("/{case_id}", response_model=CaseResponse)
def get_one(
    case_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.patch("/{case_id}/status", response_model=CaseResponse)
def update_status(
    case_id: int,
    data: CaseStatusUpdate,
    current_user: User = Depends(
        require_roles(UserRole.district_officer, UserRole.admin)
    ),
    db: Session = Depends(get_db),
):
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return update_case_status(db, case, data, verified_by=current_user.id)
