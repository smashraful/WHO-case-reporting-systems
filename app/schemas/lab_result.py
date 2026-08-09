from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import LabResultValue


class LabResultCreate(BaseModel):
    specimen_type: str
    collection_date: Optional[date] = None
    result: LabResultValue = LabResultValue.pending
    lab_name: Optional[str] = None
    result_date: Optional[date] = None


class LabResultResponse(BaseModel):
    id: int
    case_id: int
    specimen_type: str
    collection_date: Optional[date] = None
    result: LabResultValue
    lab_name: Optional[str] = None
    result_date: Optional[date] = None
    entered_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
