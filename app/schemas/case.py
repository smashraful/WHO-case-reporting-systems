from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import CaseStatus


class CaseCreate(BaseModel):
    patient_id: int
    onset_date: Optional[date] = None
    report_date: date
    reporting_facility: Optional[str] = None
    has_fever: bool = False
    has_rash: bool = False
    has_cough: bool = False
    has_coryza: bool = False
    has_conjunctivitis: bool = False
    notes: Optional[str] = None
    location_id: Optional[int] = None


class CaseStatusUpdate(BaseModel):
    status: CaseStatus
    notes: Optional[str] = None


class CaseResponse(BaseModel):
    id: int
    patient_id: int
    status: CaseStatus
    onset_date: Optional[date] = None
    report_date: date
    reporting_facility: Optional[str] = None
    has_fever: bool
    has_rash: bool
    has_cough: bool
    has_coryza: bool
    has_conjunctivitis: bool
    notes: Optional[str] = None
    location_id: Optional[int] = None
    reported_by: int
    verified_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseStats(BaseModel):
    total: int
    by_status: dict[str, int]
    by_location: dict[str, int]
