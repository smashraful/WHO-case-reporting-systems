from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.patient import PatientCreate


def create_patient(db: Session, data: PatientCreate, created_by: int) -> Patient:
    patient = Patient(**data.model_dump(), created_by=created_by)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patients(db: Session) -> list[Patient]:
    return db.query(Patient).order_by(Patient.id.desc()).all()


def get_patient(db: Session, patient_id: int) -> Patient | None:
    return db.query(Patient).filter(Patient.id == patient_id).first()
