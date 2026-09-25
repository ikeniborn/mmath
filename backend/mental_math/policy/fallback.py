from mental_math.policy.types import PolicyProposal, PolicyState

RULES_VERSION = "rules-t2-repeat"


def allowed_actions(state: PolicyState) -> tuple[str, ...]:
    """T2 baseline: every mode may only repeat the current band. T4 widens this."""
    return ("repeat",)


def rules_proposal(state: PolicyState) -> PolicyProposal:
    return PolicyProposal(action="repeat", confidence=None, provider="rules", model_version=RULES_VERSION)
