from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Date, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import LabResultValue


class LabResult(Base):
    __tablename__ = "lab_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    case_id: Mapped[int] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    specimen_type: Mapped[str] = mapped_column(String(100), nullable=False)
    collection_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    result: Mapped[LabResultValue] = mapped_column(
        Enum(LabResultValue, name="lab_result_value"),
        nullable=False,
        default=LabResultValue.pending,
    )
    lab_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    result_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    entered_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    case: Mapped["Case"] = relationship("Case", back_populates="lab_results")
