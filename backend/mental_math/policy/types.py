from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PolicyState:
    """Aggregated, identity-free view of the child's progress for one skill."""

    skill: str
    band: int
    min_band: int
    max_band: int
    mode: str
    attempts: int
    correct: int
    mastery: float | None
    correct_streak: int
    error_streak: int
    session_answered: int
    skill_run: int
    last_correct: bool
    last_hinted: bool
    other_skills: int


@dataclass(frozen=True)
class PolicyProposal:
    action: str | None
    confidence: float | None
    provider: str
    model_version: str | None
    failure_code: str | None = None

    @classmethod
    def failure(cls, code: str, provider: str = "framework") -> "PolicyProposal":
        """Typed failure with no action, confidence or model; the code is from the reviewed taxonomy only."""
        return cls(action=None, confidence=None, provider=provider, model_version=None, failure_code=code)


@dataclass(frozen=True)
class PolicyDecisionRecord:
    allowed_actions: tuple[str, ...]
    mode: str
    proposal: PolicyProposal
    applied_action: str
    latency_ms: int
    fallback_reason: str | None
    policy_mode: str = "rules"
    rule_action: str | None = None


class PolicyTransport(Protocol):
    async def predict(self, state: PolicyState, allowed_actions: tuple[str, ...]) -> PolicyProposal: ...
