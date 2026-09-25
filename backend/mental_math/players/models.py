from uuid import UUID

from uuid6 import uuid7

from sqlalchemy import CheckConstraint, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from mental_math.db import Base


class Player(Base):
    __tablename__ = "players"
    __table_args__ = (
        CheckConstraint("age BETWEEN 4 AND 10", name="player_age_range"),
        CheckConstraint("difficulty_band BETWEEN 0 AND 4", name="player_band_range"),
        CheckConstraint("mode IN ('automatic', 'fixed')", name="player_mode_allowed"),
        CheckConstraint("session_minutes IN (5, 10, 15)", name="player_minutes_allowed"),
        CheckConstraint("theme IN ('flowers', 'dolls', 'cars', 'construction')", name="player_theme_allowed"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid7)
    account_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    age: Mapped[int]
    avatar: Mapped[str] = mapped_column(String(20), default="star")
    topics: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    mode: Mapped[str] = mapped_column(String(10), default="automatic")
    difficulty_band: Mapped[int]
    session_minutes: Mapped[int] = mapped_column(default=10)
    theme: Mapped[str] = mapped_column(String(20), default="flowers")
