import time
from dataclasses import asdict

from mental_math.policy.fallback import allowed_actions, rules_proposal
from mental_math.policy.types import PolicyDecisionRecord, PolicyProposal, PolicyState


def decide(state: PolicyState, proposal: PolicyProposal | None = None) -> PolicyDecisionRecord:
    """Constrained decision: restrictions apply before (allowed set) and after (legal-action gate) selection."""
    started = time.perf_counter()
    allowed = allowed_actions(state)
    chosen = proposal or rules_proposal(state)
    if chosen.action in allowed:
        applied, reason = chosen.action, None
    else:
        applied, reason = rules_proposal(state).action, "illegal_action"
    return PolicyDecisionRecord(allowed_actions=allowed, mode=state.mode, proposal=chosen, applied_action=applied, latency_ms=int((time.perf_counter() - started) * 1000), fallback_reason=reason, policy_mode="rules", rule_action=rules_proposal(state).action)


def state_payload(state: PolicyState) -> dict:
    return asdict(state)
