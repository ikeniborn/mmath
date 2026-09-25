from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class StartSession(BaseModel):
    player_id: UUID


class SubmitAttempt(BaseModel):
    submission_id: UUID
    problem_id: UUID
    answer: int = Field(ge=-1000, le=1000)
    response_ms: int | None = Field(default=None, ge=0, le=3_600_000)
    expected_version: int = Field(ge=1)


class AdvanceSession(BaseModel):
    attempt_id: UUID
    expected_version: int = Field(ge=1)


class PublicProblem(BaseModel):
    id: UUID
    ordinal: int
    skill: str
    band: int
    operation: str
    operand_a: int
    operand_b: int


class Feedback(BaseModel):
    correct: bool
    submitted_answer: int
    correct_answer: int


class SessionSettings(BaseModel):
    mode: Literal["automatic", "fixed"]
    difficulty_band: int
    topics: list[str]
    session_minutes: int


class SessionSnapshot(BaseModel):
    id: UUID
    player_id: UUID
    version: int
    state: Literal["active", "finished"]
    phase: Literal["answer", "feedback"]
    current_problem: PublicProblem | None
    feedback: Feedback | None
    last_attempt_id: UUID | None
    settings: SessionSettings
    answered_count: int
    correct_count: int
    total_problems: int


class AttemptResult(BaseModel):
    attempt_id: UUID
    correct: bool
    feedback: Feedback
    next_problem: PublicProblem | None
    session: SessionSnapshot
