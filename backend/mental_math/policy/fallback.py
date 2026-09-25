"""Constrained rules: the bounded action space and the deterministic fallback proposal."""

from mental_math.policy.types import PolicyProposal, PolicyState

RULES_VERSION = "rules-v1"
PROMOTION_STREAK = 5
ERROR_STREAK = 3
SWITCH_RUN = 3


def allowed_actions(state: PolicyState) -> tuple[str, ...]:
    actions = ["repeat", "hint"]
    if state.other_skills > 0:
        actions.append("switch")
    if state.mode == "automatic":
        if state.band > state.min_band:
            actions.append("easier")
        if state.band < state.max_band and state.error_streak < ERROR_STREAK and state.correct_streak >= PROMOTION_STREAK:
            actions.append("harder")
    return tuple(actions)


def rules_proposal(state: PolicyState) -> PolicyProposal:
    allowed = allowed_actions(state)
    if state.error_streak >= ERROR_STREAK:
        action = "easier" if "easier" in allowed else "hint"
    elif state.correct_streak >= PROMOTION_STREAK:
        action = "harder" if "harder" in allowed else ("switch" if "switch" in allowed else "repeat")
    elif state.last_correct and state.skill_run >= SWITCH_RUN and "switch" in allowed:
        action = "switch"
    else:
        action = "repeat"
    return PolicyProposal(action=action, confidence=None, provider="rules", model_version=RULES_VERSION)
