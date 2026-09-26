from mental_math.policy.fallback import allowed_actions, rules_proposal
from mental_math.policy.service import decide
from mental_math.policy.types import PolicyProposal, PolicyState


def state(**overrides) -> PolicyState:
    base = dict(skill="addition", band=1, min_band=0, max_band=4, mode="automatic", attempts=10, correct=7, mastery=0.6, correct_streak=0, error_streak=0, session_answered=3, skill_run=1, last_correct=True, last_hinted=False, other_skills=1)
    return PolicyState(**{**base, **overrides})


def test_fixed_mode_never_offers_or_applies_band_changes():
    fixed = state(mode="fixed", correct_streak=9, error_streak=0)
    assert set(allowed_actions(fixed)) == {"repeat", "switch", "hint", "no_hint"}
    assert decide(fixed).applied_action in {"repeat", "switch"}
    forced = decide(fixed, proposal=PolicyProposal(action="harder", confidence=1.0, provider="test", model_version="t"))
    assert forced.applied_action in {"repeat", "switch"} and forced.fallback_reason == "illegal_action"


def test_automatic_promotion_needs_five_unhinted_correct_and_one_band_at_most():
    assert rules_proposal(state(correct_streak=4)).action == "repeat"
    assert rules_proposal(state(correct_streak=5)).action == "harder"
    assert "harder" in allowed_actions(state(correct_streak=5))
    assert "harder" not in allowed_actions(state(correct_streak=4))
    assert rules_proposal(state(correct_streak=5, band=4)).action in {"switch", "repeat"}
    assert "harder" not in allowed_actions(state(correct_streak=5, band=4))


def test_three_errors_forbid_harder_and_select_easier_or_hint_at_the_floor():
    assert rules_proposal(state(error_streak=3, correct_streak=0)).action == "easier"
    assert "harder" not in allowed_actions(state(error_streak=3, correct_streak=5))
    floor = state(error_streak=3, band=0)
    assert rules_proposal(floor).action == "hint"
    assert "easier" not in allowed_actions(floor)


def test_post_validation_applies_only_legal_actions():
    illegal = decide(state(error_streak=3, correct_streak=5), proposal=PolicyProposal(action="harder", confidence=0.9, provider="test", model_version="t"))
    assert illegal.applied_action == "easier" and illegal.fallback_reason == "illegal_action"
    assert "harder" not in illegal.allowed_actions


def test_switch_follows_three_correct_on_the_same_skill_but_never_while_struggling():
    assert rules_proposal(state(skill_run=3, correct_streak=3)).action == "switch"
    assert rules_proposal(state(skill_run=3, correct_streak=0, last_correct=False, error_streak=1)).action == "repeat"
    assert rules_proposal(state(skill_run=3, correct_streak=3, other_skills=0)).action == "repeat"
