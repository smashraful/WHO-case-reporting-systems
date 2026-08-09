from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Date, DateTime, Enum, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import CaseStatus


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus, name="case_status"),
        nullable=False,
        default=CaseStatus.suspected,
        index=True,
    )
    onset_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    reporting_facility: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )
    # symptoms
    has_fever: Mapped[bool] = mapped_column(Boolean, default=False)
    has_rash: Mapped[bool] = mapped_column(Boolean, default=False)
    has_cough: Mapped[bool] = mapped_column(Boolean, default=False)
    has_coryza: Mapped[bool] = mapped_column(Boolean, default=False)
    has_conjunctivitis: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    reported_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    verified_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    lab_results: Mapped[list["LabResult"]] = relationship(
        "LabResult", back_populates="case", cascade="all, delete-orphan"
    )
