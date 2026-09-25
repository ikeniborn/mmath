from dataclasses import dataclass

import pytest
from uuid6 import uuid7

from mental_math.policy.runtime import PolicyRuntime
from tests.conftest import Family, solve, wrong
from tests.integration.test_difficulty_modes import configure


@dataclass
class FixedLesson:
    session_id: str
    problem: dict
    version: int
    band: int
    command: dict


@pytest.fixture
async def fixed_lesson(family) -> FixedLesson:
    await configure(family, mode="fixed", difficulty_band=2)
    started = (await family.post("/sessions", {"player_id": family.player_id})).json()
    problem = started["current_problem"]
    return FixedLesson(started["id"], problem, started["version"], 2, {"submission_id": str(uuid7()), "problem_id": problem["id"], "answer": solve(problem), "response_ms": 1200, "expected_version": started["version"]})


@pytest.fixture
def active(app, policy_fake):
    app.state.policy = PolicyRuntime(mode="active", transport=policy_fake, confidence_threshold=0.8)
    return policy_fake


async def answer(family: Family, session: dict, *, correct: bool = True) -> tuple[dict, dict]:
    problem = session["current_problem"]
    value = solve(problem)
    result = (await family.post(f"/sessions/{session['id']}/attempts", json={"submission_id": str(uuid7()), "problem_id": problem["id"], "answer": value if correct else wrong(problem, value), "response_ms": 1200, "expected_version": session["version"]})).json()
    advanced = (await family.post(f"/sessions/{session['id']}/advance", json={"attempt_id": result["attempt_id"], "expected_version": result["session"]["version"]})).json()
    return result, advanced


@pytest.mark.asyncio
async def test_active_cannot_raise_fixed_band(family, fixed_lesson, active):
    active.action = "harder"
    active.confidence = 1.0
    response = await family.post(f"/sessions/{fixed_lesson.session_id}/attempts", json=fixed_lesson.command)
    assert response.status_code == 200
    body = response.json()
    assert body["session"]["settings"]["difficulty_band"] == fixed_lesson.band
    advanced = await family.post(f"/sessions/{fixed_lesson.session_id}/advance", json={"attempt_id": body["attempt_id"], "expected_version": body["session"]["version"]})
    assert advanced.json()["current_problem"]["band"] == fixed_lesson.band
    decision = await active.persisted_decision()
    assert decision.policy_mode == "active" and decision.proposed_action == "harder" and decision.applied_action != "harder"
    assert decision.fallback_reason == "illegal_action" and "harder" not in decision.allowed_actions


@pytest.mark.asyncio
async def test_active_applies_a_confident_legal_proposal_and_stores_no_reason(family, active):
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    active.action = "hint"
    active.confidence = 0.95
    _, advanced = await answer(family, session)
    decision = await active.persisted_decision()
    assert decision.policy_mode == "active" and decision.applied_action == "hint" and decision.rule_action == "repeat" and decision.fallback_reason is None
    assert decision.confidence == 0.95 and decision.provider == "fake"
    assert advanced["hint"] is not None  # the next problem arrived with the visual support the model chose


@pytest.mark.asyncio
async def test_active_may_decline_or_take_a_legal_promotion(family, active):
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    active.action = "repeat"
    active.confidence = 0.9
    for _ in range(5):
        _, session = await answer(family, session)
    declined = await active.persisted_decision()
    assert declined.rule_action == "harder" and declined.applied_action == "repeat" and declined.fallback_reason is None
    assert session["current_problem"]["band"] == 0
    active.action = "harder"
    _, session = await answer(family, session)
    taken = await active.persisted_decision()
    assert taken.applied_action == "harder" and taken.fallback_reason is None
    assert session["current_problem"]["band"] == 1  # the band lives per child and skill; the profile setting is the starting band


@pytest.mark.asyncio
@pytest.mark.parametrize("action, confidence, behaviour, reason", [
    ("hint", 0.79, "ok", "confidence_low"),
    ("hint", None, "ok", "confidence_missing"),
    ("teleport", 1.0, "ok", "illegal_action"),
    ("easier", 1.0, "ok", "illegal_action"),
    (None, None, "busy", "busy"),
    (None, None, "network", "network"),
])
async def test_every_gate_failure_applies_the_rule_action(family, active, counts, action, confidence, behaviour, reason):
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    active.action = action
    active.confidence = confidence
    active.behaviour = behaviour
    result, advanced = await answer(family, session)
    decision = await active.persisted_decision()
    assert decision.applied_action == decision.rule_action == "repeat"
    assert decision.fallback_reason == reason
    assert advanced["current_problem"]["band"] == 0
    assert (await counts(family.player_id))["decisions"] == 1


@pytest.mark.asyncio
async def test_error_streak_and_band_ceiling_block_promotion_even_with_full_confidence(family, active):
    await configure(family, difficulty_band=4)
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    active.action = "harder"
    active.confidence = 1.0
    for _ in range(3):
        _, session = await answer(family, session, correct=False)
    decision = await active.persisted_decision()
    assert "harder" not in decision.allowed_actions and decision.applied_action == decision.rule_action
    await configure(family, difficulty_band=0)
    fresh = await family.post(f"/sessions/{session['id']}/finish")
    assert fresh.status_code == 200
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    for _ in range(5):
        _, session = await answer(family, session)
    top = await active.persisted_decision()
    assert top.applied_action in {"harder", "repeat", "switch"}
    assert all(problem_band <= 4 for problem_band in [session["current_problem"]["band"]])


@pytest.mark.asyncio
async def test_issued_problems_are_immutable_across_mode_changes(app, family, lesson, active):
    from mental_math.policy.runtime import PolicyRuntime as Runtime

    before = (await family.get(f"/sessions/{lesson.session_id}")).json()
    app.state.policy = Runtime(mode="rules", transport=None)
    after_rules = (await family.get(f"/sessions/{lesson.session_id}")).json()
    app.state.policy = Runtime(mode="active", transport=active, confidence_threshold=0.9)
    after_active = (await family.get(f"/sessions/{lesson.session_id}")).json()
    assert before["current_problem"] == after_rules["current_problem"] == after_active["current_problem"]
    assert before["version"] == after_active["version"]
    assert (await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)).status_code == 200


def test_active_configuration_requires_explicit_authorization(monkeypatch):
    from mental_math.config import Settings

    monkeypatch.setenv("MMATH_DATABASE_URL", "postgresql+psycopg://u:p@db/x")
    monkeypatch.setenv("MMATH_ORIGIN", "http://test")
    monkeypatch.setenv("MMATH_MODE", "lan-http")
    monkeypatch.setenv("MMATH_POLICY_MODE", "active")
    monkeypatch.setenv("MMATH_FRAMEWORK_URL", "https://framework.test")
    with pytest.raises(RuntimeError, match="MMATH_ACTIVE_CONFIDENCE_THRESHOLD"):
        Settings.from_env()
    monkeypatch.setenv("MMATH_ACTIVE_CONFIDENCE_THRESHOLD", "0.8")
    with pytest.raises(RuntimeError, match="MMATH_ACTIVE_ROLLOUT_AUTHORIZATION"):
        Settings.from_env()
    monkeypatch.setenv("MMATH_ACTIVE_ROLLOUT_AUTHORIZATION", "ledger-decision-2026-09-25")
    settings = Settings.from_env()
    assert settings.policy_mode == "active" and settings.confidence_threshold == 0.8 and settings.rollout_authorization == "ledger-decision-2026-09-25"
    monkeypatch.setenv("MMATH_ACTIVE_CONFIDENCE_THRESHOLD", "0.3")
    with pytest.raises(RuntimeError, match="between"):
        Settings.from_env()
