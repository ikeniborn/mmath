"""Policy runtime: deployment mode plus the optional transport, resolved inside the answer transaction.

rules: the deterministic rules decide. shadow: the model proposal is recorded but the rule action is applied.
Every transport call is bounded by one total deadline; no failure changes the constraint set or the answer.
"""

import asyncio
import time
from dataclasses import dataclass

from mental_math.policy.fallback import allowed_actions, rules_proposal
from mental_math.policy.framework import FAILURE_TAXONOMY, TransportFailure
from mental_math.policy.types import PolicyDecisionRecord, PolicyProposal, PolicyState, PolicyTransport

TOTAL_DEADLINE_SECONDS = 0.350
MODES = ("rules", "shadow", "active")
MIN_THRESHOLD, MAX_THRESHOLD = 0.5, 1.0


@dataclass(frozen=True)
class PolicyRuntime:
    mode: str = "rules"
    transport: PolicyTransport | None = None
    confidence_threshold: float = 0.8


def gate_proposal(proposal: PolicyProposal, allowed: tuple[str, ...], *, threshold: float) -> tuple[str | None, str | None]:
    """Active-mode gate: (applied action, None) or (None, reason). Post-validation runs even if the criteria were prefiltered."""
    if not MIN_THRESHOLD <= threshold <= MAX_THRESHOLD:
        raise ValueError(f"confidence threshold must be between {MIN_THRESHOLD} and {MAX_THRESHOLD}")
    if proposal.failure_code:
        return None, proposal.failure_code
    if proposal.action not in allowed:
        return None, "illegal_action"
    if proposal.confidence is None:
        return None, "confidence_missing"
    if proposal.confidence < threshold:
        return None, "confidence_low"
    return proposal.action, None


async def bounded_predict(transport: PolicyTransport, state: PolicyState, allowed: tuple[str, ...]) -> PolicyProposal:
    try:
        async with asyncio.timeout(TOTAL_DEADLINE_SECONDS):
            return await transport.predict(state, allowed)
    except TimeoutError:
        from mental_math.observability import metrics

        metrics.observe_inference_deadline()
        return PolicyProposal.failure("timeout")
    except TransportFailure as failure:
        return PolicyProposal.failure(failure.code)
    except FAILURE_TAXONOMY:
        return PolicyProposal.failure("network")


async def resolve(state: PolicyState, runtime: PolicyRuntime | None) -> PolicyDecisionRecord:
    """Constrained decision for the current policy mode. Restrictions apply before and after selection."""
    started = time.perf_counter()
    allowed = allowed_actions(state)
    rule = rules_proposal(state)
    if runtime is None or runtime.mode == "rules" or runtime.transport is None:
        return PolicyDecisionRecord(allowed_actions=allowed, mode=state.mode, proposal=rule, applied_action=rule.action, latency_ms=int((time.perf_counter() - started) * 1000), fallback_reason=None, policy_mode="rules", rule_action=rule.action)
    proposal = await bounded_predict(runtime.transport, state, allowed)
    if runtime.mode == "shadow":
        reason = proposal.failure_code or "shadow"
        return PolicyDecisionRecord(allowed_actions=allowed, mode=state.mode, proposal=proposal, applied_action=rule.action, latency_ms=int((time.perf_counter() - started) * 1000), fallback_reason=reason, policy_mode="shadow", rule_action=rule.action)
    applied, reason = gate_proposal(proposal, allowed, threshold=runtime.confidence_threshold)
    return PolicyDecisionRecord(allowed_actions=allowed, mode=state.mode, proposal=proposal, applied_action=applied or rule.action, latency_ms=int((time.perf_counter() - started) * 1000), fallback_reason=reason, policy_mode="active", rule_action=rule.action)
