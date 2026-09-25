from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class PlayerInput(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    age: int = Field(ge=5, le=10)
    avatar: Literal["star", "rocket", "fox", "owl"] = "star"
    topics: list[Literal["addition", "subtraction", "counting", "multiplication", "division", "comparison"]] = Field(min_length=1)
    mode: Literal["automatic", "fixed"] = "automatic"
    difficulty_band: int | None = Field(default=None, ge=0, le=4)
    session_minutes: Literal[5, 10, 15] = 10
    theme: Literal["flowers", "dolls", "cars", "construction"] = "flowers"

    @field_validator("name")
    @classmethod
    def nonblank_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name is required")
        return value

    @field_validator("topics")
    @classmethod
    def unique_topics(cls, value: list[str]) -> list[str]:
        return list(dict.fromkeys(value))

    @model_validator(mode="after")
    def resolve_band(self):
        if self.difficulty_band is None:
            self.difficulty_band = 0 if self.age <= 6 else 1 if self.age <= 8 else 2
        return self


class PlayerPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=40)
    age: int | None = Field(default=None, ge=5, le=10)
    avatar: Literal["star", "rocket", "fox", "owl"] | None = None
    topics: list[Literal["addition", "subtraction", "counting", "multiplication", "division", "comparison"]] | None = Field(default=None, min_length=1)
    mode: Literal["automatic", "fixed"] | None = None
    difficulty_band: int | None = Field(default=None, ge=0, le=4)
    session_minutes: Literal[5, 10, 15] | None = None
    theme: Literal["flowers", "dolls", "cars", "construction"] | None = None

    @model_validator(mode="after")
    def validate_patch(self):
        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        if self.name is not None:
            self.name = self.name.strip()
            if not self.name:
                raise ValueError("Name is required")
        if self.topics is not None:
            self.topics = list(dict.fromkeys(self.topics))
        return self


class PlayerView(PlayerInput):
    id: UUID


class SkillProgress(BaseModel):
    skill: str
    band: int
    attempts: int
    correct: int
    mastery: float | None
    formula_version: str | None
    updated_at: datetime


class SessionHistory(BaseModel):
    id: UUID
    state: Literal["active", "finished"]
    started_at: datetime
    finished_at: datetime | None
    answered_count: int
    correct_count: int
    active_ms: int
    settings: dict


class ProgressView(BaseModel):
    skills: list[SkillProgress]
    sessions: list[SessionHistory]
    total_sessions: int
