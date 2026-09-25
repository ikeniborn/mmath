import time
from dataclasses import asdict

from mental_math.policy.fallback import allowed_actions, rules_proposal
from mental_math.policy.types import PolicyDecisionRecord, PolicyState


def decide(state: PolicyState) -> PolicyDecisionRecord:
    """Constrained rules decision. Restrictions apply before and after selection."""
    started = time.perf_counter()
    allowed = allowed_actions(state)
    proposal = rules_proposal(state)
    applied, reason = (proposal.action, None) if proposal.action in allowed else (allowed[0], "illegal_action")
    return PolicyDecisionRecord(allowed_actions=allowed, mode=state.mode, proposal=proposal, applied_action=applied, latency_ms=int((time.perf_counter() - started) * 1000), fallback_reason=reason)


def state_payload(state: PolicyState) -> dict:
    return asdict(state)
