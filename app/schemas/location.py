from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import LocationType


class LocationCreate(BaseModel):
    name: str
    type: LocationType
    parent_id: Optional[int] = None


class LocationResponse(BaseModel):
    id: int
    name: str
    type: LocationType
    parent_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
