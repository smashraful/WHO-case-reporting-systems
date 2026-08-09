from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientResponse
from app.services.patient_service import (
    create_patient,
    get_patients,
    get_patient,
)

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: PatientCreate,
    current_user: User = Depends(
        require_roles(UserRole.field_worker, UserRole.admin)
    ),
    db: Session = Depends(get_db),
):
    return create_patient(db, data, created_by=current_user.id)


@router.get("", response_model=list[PatientResponse])
def list_all(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_patients(db)


@router.get("/{patient_id}", response_model=PatientResponse)
def get_one(
    patient_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
