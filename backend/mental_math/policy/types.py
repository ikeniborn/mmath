from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PolicyState:
    """Aggregated, identity-free view of the child's progress for one skill."""

    skill: str
    band: int
    mode: str
    attempts: int
    correct: int
    session_answered: int
    last_correct: bool


@dataclass(frozen=True)
class PolicyProposal:
    action: str
    confidence: float | None
    provider: str
    model_version: str
    failure_code: str | None = None


@dataclass(frozen=True)
class PolicyDecisionRecord:
    allowed_actions: tuple[str, ...]
    mode: str
    proposal: PolicyProposal
    applied_action: str
    latency_ms: int
    fallback_reason: str | None


class PolicyTransport(Protocol):
    async def predict(self, state: PolicyState, allowed_actions: tuple[str, ...]) -> PolicyProposal: ...
