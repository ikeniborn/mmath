from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from mental_math.db import Base


class PlayerSkill(Base):
    """Per-child, per-skill aggregates. T2 keeps lifetime counts; T4 adds mastery."""

    __tablename__ = "player_skills"

    player_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), primary_key=True)
    skill: Mapped[str] = mapped_column(String(20), primary_key=True)
    band: Mapped[int] = mapped_column(Integer, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
