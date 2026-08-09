from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.location import LocationCreate, LocationResponse
from app.services.location_service import (
    create_location,
    get_locations,
    get_location,
)

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.post(
    "",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.admin))],
)
def create(data: LocationCreate, db: Session = Depends(get_db)):
    return create_location(db, data)


@router.get("", response_model=list[LocationResponse])
def list_all(
    parent_id: Optional[int] = None,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_locations(db, parent_id=parent_id)


@router.get("/{location_id}", response_model=LocationResponse)
def get_one(
    location_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    location = get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location
