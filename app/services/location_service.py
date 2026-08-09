from typing import Optional

from sqlalchemy.orm import Session

from app.models.location import Location
from app.schemas.location import LocationCreate


def create_location(db: Session, data: LocationCreate) -> Location:
    location = Location(name=data.name, type=data.type, parent_id=data.parent_id)
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


def get_locations(db: Session, parent_id: Optional[int] = None) -> list[Location]:
    query = db.query(Location)
    if parent_id is not None:
        query = query.filter(Location.parent_id == parent_id)
    return query.order_by(Location.name).all()


def get_location(db: Session, location_id: int) -> Location | None:
    return db.query(Location).filter(Location.id == location_id).first()
