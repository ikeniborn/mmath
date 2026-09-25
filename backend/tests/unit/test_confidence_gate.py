import pytest

from mental_math.policy.runtime import gate_proposal
from mental_math.policy.types import PolicyProposal

ALLOWED = ("repeat", "hint", "switch", "harder")


def proposal(action, confidence):
    return PolicyProposal(action=action, confidence=confidence, provider="framework", model_version="laya-english")


@pytest.mark.parametrize("candidate, expected", [
    (proposal("harder", 0.95), ("harder", None)),
    (proposal("harder", 0.8), ("harder", None)),
    (proposal("harder", 0.79), (None, "confidence_low")),
    (proposal("harder", None), (None, "confidence_missing")),
    (proposal("easier", 0.99), (None, "illegal_action")),
    (proposal("teleport", 1.0), (None, "illegal_action")),
    (PolicyProposal.failure("busy"), (None, "busy")),
    (PolicyProposal.failure("timeout"), (None, "timeout")),
])
def test_gate_applies_only_confident_legal_proposals(candidate, expected):
    assert gate_proposal(candidate, ALLOWED, threshold=0.8) == expected


def test_gate_post_validates_even_when_prefiltered_actions_were_supplied():
    # The transport was given the allowed set as criteria; the gate still refuses anything outside it.
    assert gate_proposal(proposal("no_hint", 0.9), ("repeat", "hint"), threshold=0.8) == (None, "illegal_action")
    assert gate_proposal(proposal("no_hint", 0.9), ("repeat", "hint", "no_hint"), threshold=0.8) == ("no_hint", None)


def test_threshold_bounds_are_validated():
    with pytest.raises(ValueError):
        gate_proposal(proposal("repeat", 0.9), ALLOWED, threshold=0.4)
    with pytest.raises(ValueError):
        gate_proposal(proposal("repeat", 0.9), ALLOWED, threshold=1.01)
