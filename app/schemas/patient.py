from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import Sex, VaccinationStatus


class PatientCreate(BaseModel):
    full_name: str
    sex: Sex = Sex.unknown
    date_of_birth: Optional[date] = None
    age_months: Optional[int] = None
    guardian_name: Optional[str] = None
    address: Optional[str] = None
    vaccination_status: VaccinationStatus = VaccinationStatus.unknown
    doses: Optional[int] = None
    location_id: Optional[int] = None


class PatientResponse(BaseModel):
    id: int
    full_name: str
    sex: Sex
    date_of_birth: Optional[date] = None
    age_months: Optional[int] = None
    guardian_name: Optional[str] = None
    address: Optional[str] = None
    vaccination_status: VaccinationStatus
    doses: Optional[int] = None
    location_id: Optional[int] = None
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
