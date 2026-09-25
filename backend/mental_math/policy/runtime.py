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
MODES = ("rules", "shadow")


@dataclass(frozen=True)
class PolicyRuntime:
    mode: str = "rules"
    transport: PolicyTransport | None = None


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
    reason = proposal.failure_code or "shadow"
    return PolicyDecisionRecord(allowed_actions=allowed, mode=state.mode, proposal=proposal, applied_action=rule.action, latency_ms=int((time.perf_counter() - started) * 1000), fallback_reason=reason, policy_mode="shadow", rule_action=rule.action)
