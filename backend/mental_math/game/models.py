from datetime import datetime
from uuid import UUID

from uuid6 import uuid7

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, JSON, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from mental_math.db import Base


class LearningSession(Base):
    __tablename__ = "learning_sessions"
    __table_args__ = (
        CheckConstraint("state IN ('active', 'finished')", name="session_state_allowed"),
        CheckConstraint("phase IN ('answer', 'feedback')", name="session_phase_allowed"),
        Index("ux_learning_sessions_one_active", "player_id", unique=True, postgresql_where=text("state = 'active'")),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid7)
    player_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("players.id", ondelete="CASCADE"), index=True)
    state: Mapped[str] = mapped_column(String(10), default="active")
    phase: Mapped[str] = mapped_column(String(10), default="answer")
    version: Mapped[int] = mapped_column(Integer, default=1)
    settings: Mapped[dict] = mapped_column(JSON, nullable=False)
    current_problem_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    pending_problem_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    last_attempt_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    feedback: Mapped[dict | None] = mapped_column(JSON)
    answered_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    active_ms: Mapped[int] = mapped_column(Integer, default=0)
    correct_streak: Mapped[int] = mapped_column(Integer, default=0)
    error_streak: Mapped[int] = mapped_column(Integer, default=0)
    skill_run: Mapped[int] = mapped_column(Integer, default=0)
    active_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Problem(Base):
    __tablename__ = "problems"
    __table_args__ = (UniqueConstraint("session_id", "ordinal", name="ux_problems_session_ordinal"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid7)
    session_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("learning_sessions.id", ondelete="CASCADE"), index=True)
    ordinal: Mapped[int] = mapped_column(Integer, nullable=False)
    skill: Mapped[str] = mapped_column(String(20), nullable=False)
    band: Mapped[int] = mapped_column(Integer, nullable=False)
    operation: Mapped[str] = mapped_column(String(20), nullable=False)
    operand_a: Mapped[int] = mapped_column(Integer, nullable=False)
    operand_b: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_answer: Mapped[int] = mapped_column(Integer, nullable=False)
    kind: Mapped[str] = mapped_column(String(20), default="result")
    prompt: Mapped[dict | None] = mapped_column(JSON)
    hinted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Attempt(Base):
    __tablename__ = "attempts"
    __table_args__ = (UniqueConstraint("session_id", "problem_id", name="ux_attempts_session_problem"),)

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid7)
    session_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("learning_sessions.id", ondelete="CASCADE"), index=True)
    problem_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("problems.id", ondelete="CASCADE"))
    submission_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), unique=True, nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    answer: Mapped[int] = mapped_column(Integer, nullable=False)
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    response_ms: Mapped[int | None] = mapped_column(Integer)
    hint_used: Mapped[bool] = mapped_column(Boolean, default=False)
    error_type: Mapped[str | None] = mapped_column(String(24))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PolicyDecision(Base):
    __tablename__ = "policy_decisions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid7)
    attempt_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("attempts.id", ondelete="CASCADE"), unique=True)
    session_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("learning_sessions.id", ondelete="CASCADE"), index=True)
    mode: Mapped[str] = mapped_column(String(10), nullable=False)
    allowed_actions: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    state: Mapped[dict] = mapped_column(JSON, nullable=False)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(40))
    proposed_action: Mapped[str | None] = mapped_column(String(20))
    rule_action: Mapped[str | None] = mapped_column(String(20))
    confidence: Mapped[float | None] = mapped_column(Float)
    policy_mode: Mapped[str] = mapped_column(String(10), default="rules")
    applied_action: Mapped[str] = mapped_column(String(20), nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    fallback_reason: Mapped[str | None] = mapped_column(String(40))
    next_problem_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
