from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from mental_math.db import Base


class PlayerSkill(Base):
    """Per-child, per-skill aggregates: lifetime counts, the recent window, streaks, band and mastery."""

    __tablename__ = "player_skills"

    player_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), primary_key=True)
    skill: Mapped[str] = mapped_column(String(20), primary_key=True)
    band: Mapped[int] = mapped_column(Integer, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    recent: Mapped[list[dict]] = mapped_column(JSON, default=list)
    mastery: Mapped[float | None] = mapped_column(Float)
    correct_streak: Mapped[int] = mapped_column(Integer, default=0, server_default="0")  # unhinted correct answers in a row on this skill, across sessions
    error_streak: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    formula_version: Mapped[str | None] = mapped_column(String(40))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
