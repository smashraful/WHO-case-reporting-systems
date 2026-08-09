from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import LocationType


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    type: Mapped[LocationType] = mapped_column(
        Enum(LocationType, name="location_type"), nullable=False
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"), nullable=True
    )

    parent: Mapped[Optional["Location"]] = relationship(
        "Location", remote_side="Location.id", backref="children"
    )
