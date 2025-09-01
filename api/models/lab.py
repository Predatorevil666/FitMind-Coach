from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.utils import get_utc_now
from api.models.base import Base

if TYPE_CHECKING:
    from api.models.user import User


class LabResult(Base):
    """Модель результатов лабораторных анализов."""

    __tablename__ = "lab_results"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now
    )
    test_type: Mapped[str] = mapped_column(String(100))
    results: Mapped[Optional[dict]] = mapped_column(JSONB)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Отношения
    user: Mapped["User"] = relationship(back_populates="lab_results")
