import pytest

from tests.conftest import solve


async def answer(family, session):
    problem = session["current_problem"]
    from uuid6 import uuid7

    return await family.post(f"/sessions/{session['id']}/attempts", json={"submission_id": str(uuid7()), "problem_id": problem["id"], "answer": solve(problem), "response_ms": 900, "expected_version": session["version"]})


@pytest.mark.asyncio
async def test_shadow_cannot_override_rules(family, lesson, policy_fake):
    policy_fake.action = "harder"
    result = await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)
    assert result.status_code == 200
    decision = await policy_fake.persisted_decision()
    assert decision.policy_mode == "shadow"
    assert decision.proposed_action == "harder" and decision.provider == "fake" and decision.model_version == "fake-1"
    assert decision.applied_action == decision.rule_action == "repeat"
    assert decision.fallback_reason == "shadow"
    assert policy_fake.calls == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("behaviour, code", [("busy", "busy"), ("http_5xx", "http_5xx"), ("malformed", "malformed"), ("oversized", "oversized"), ("network", "network")])
async def test_transport_failures_yield_legal_rule_action_and_one_audit_row(family, lesson, policy_fake, counts, behaviour, code):
    policy_fake.behaviour = behaviour
    result = await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)
    assert result.status_code == 200 and result.json()["correct"] is True
    decision = await policy_fake.persisted_decision()
    assert decision.applied_action == decision.rule_action and decision.proposed_action is None
    assert decision.fallback_reason == code and decision.provider == "framework"
    assert (await counts(family.player_id))["decisions"] == 1


@pytest.mark.asyncio
async def test_illegal_or_unknown_proposal_is_recorded_and_rules_apply(family, lesson, policy_fake):
    policy_fake.action = "teleport"
    assert (await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)).status_code == 200
    decision = await policy_fake.persisted_decision()
    assert decision.proposed_action == "teleport" and decision.applied_action == "repeat" and decision.fallback_reason == "shadow"
    assert "teleport" not in decision.allowed_actions


@pytest.mark.asyncio
async def test_fixed_mode_shadow_never_offers_band_changes_in_either_path(family, policy_fake):
    from tests.integration.test_difficulty_modes import configure

    await configure(family, mode="fixed", difficulty_band=2)
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    policy_fake.action = "easier"
    for _ in range(3):
        response = await answer(family, session)
        assert response.status_code == 200
        body = response.json()
        decision = await policy_fake.persisted_decision()
        assert "easier" not in decision.allowed_actions and "harder" not in decision.allowed_actions
        assert decision.applied_action in {"repeat", "switch", "hint"}
        advanced = await family.post(f"/sessions/{session['id']}/advance", json={"attempt_id": body["attempt_id"], "expected_version": body["session"]["version"]})
        session = advanced.json()
        assert session["current_problem"]["band"] == 2
    assert policy_fake.requests and all(request["state"]["mode"] == "fixed" for request in policy_fake.requests)


@pytest.mark.asyncio
async def test_rules_mode_default_never_calls_the_transport(app, family, lesson, policy_fake):
    from mental_math.policy.runtime import PolicyRuntime

    app.state.policy = PolicyRuntime(mode="rules", transport=policy_fake)
    assert (await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)).status_code == 200
    decision = await policy_fake.persisted_decision()
    assert decision.policy_mode == "rules" and decision.provider == "rules" and policy_fake.calls == 0


@pytest.mark.asyncio
async def test_state_sent_to_inference_carries_no_identifiers(family, lesson, policy_fake):
    assert (await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)).status_code == 200
    import json

    payload = json.dumps(policy_fake.requests[0]).lower()
    for marker in (family.parent_email.lower(), family.player_id.lower(), lesson.session_id.lower(), "cookie", "token", "email"):
        assert marker not in payload, marker
