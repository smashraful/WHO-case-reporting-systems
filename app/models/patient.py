from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Date, DateTime, Enum, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import Sex, VaccinationStatus


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    sex: Mapped[Sex] = mapped_column(
        Enum(Sex, name="sex"), nullable=False, default=Sex.unknown
    )
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    age_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    guardian_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    vaccination_status: Mapped[VaccinationStatus] = mapped_column(
        Enum(VaccinationStatus, name="vaccination_status"),
        nullable=False,
        default=VaccinationStatus.unknown,
    )
    doses: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
