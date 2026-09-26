import pytest
from httpx import ASGITransport, AsyncClient

from mental_math.main import create_app


@pytest.mark.asyncio
async def test_start_returns_existing_active_session(family, lesson):
    again = await family.post("/sessions", {"player_id": family.player_id})
    assert again.status_code == 200
    assert again.json()["id"] == lesson.session_id


@pytest.mark.asyncio
async def test_feedback_and_advance_survive_process_restart(family, lesson):
    answered = await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)
    assert answered.status_code == 200
    body = answered.json()
    assert body["session"]["phase"] == "feedback"
    assert body["feedback"]["correct"] is True
    assert body["session"]["current_problem"]["id"] == lesson.problem["id"]
    assert body["next_problem"] is None
    # A second process with its own pool sees the committed position.
    restarted = create_app()
    async with AsyncClient(transport=ASGITransport(app=restarted), base_url="http://test", headers={"Origin": "http://test"}, cookies=family.client.cookies) as client:
        snapshot = (await client.get(f"/api/v1/sessions/{lesson.session_id}")).json()
        assert snapshot["phase"] == "feedback" and snapshot["version"] == body["session"]["version"]
        assert snapshot["feedback"]["correct"] is True
        assert snapshot["last_attempt_id"] == body["attempt_id"]
        advance = {"attempt_id": snapshot["last_attempt_id"], "expected_version": snapshot["version"]}
        first = await client.post(f"/api/v1/sessions/{lesson.session_id}/advance", json=advance, headers={"X-CSRF-Token": family.csrf})
        second = await client.post(f"/api/v1/sessions/{lesson.session_id}/advance", json=advance, headers={"X-CSRF-Token": family.csrf})
        assert first.status_code == second.status_code == 200
        assert first.json()["version"] == second.json()["version"]
        assert first.json()["phase"] == "answer"
        assert first.json()["current_problem"]["ordinal"] == lesson.problem["ordinal"] + 1
        assert first.json()["feedback"] is None


@pytest.mark.asyncio
async def test_finish_is_idempotent_and_keeps_attempts(family, lesson, counts):
    assert (await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)).status_code == 200
    first = await family.post(f"/sessions/{lesson.session_id}/finish")
    second = await family.post(f"/sessions/{lesson.session_id}/finish")
    assert first.status_code == second.status_code == 200
    assert first.json()["state"] == "finished" and first.json()["version"] == second.json()["version"]
    assert first.json()["answered_count"] == 1
    assert (await counts(family.player_id))["attempts"] == 1
    fresh = await family.post("/sessions", {"player_id": family.player_id})
    assert fresh.status_code == 201 and fresh.json()["id"] != lesson.session_id


@pytest.mark.asyncio
async def test_profile_change_does_not_rewrite_session_snapshot(family, lesson):
    assert (await family.post("/auth/confirm-password", {"password": "correct horse battery staple"})).status_code == 204
    assert (await family.patch(f"/players/{family.player_id}", {"mode": "fixed", "difficulty_band": 3})).status_code == 200
    snapshot = (await family.get(f"/sessions/{lesson.session_id}")).json()
    assert snapshot["settings"] == {"mode": "automatic", "difficulty_band": 0, "topics": ["addition"], "session_minutes": 10}


@pytest.mark.asyncio
async def test_last_problem_advance_finishes_session(family, lesson):
    session_id, version, problem = lesson.session_id, lesson.version, lesson.problem
    for index in range(10):
        command = {"submission_id": f"5f4b4b3e-9c3f-4c58-9e5e-1f7d5c1a01{index:02d}", "problem_id": problem["id"], "answer": problem["operand_a"] + problem["operand_b"], "response_ms": 1200, "expected_version": version}
        answered = await family.post(f"/sessions/{session_id}/attempts", json=command)
        assert answered.status_code == 200, answered.text
        body = answered.json()
        advanced = await family.post(f"/sessions/{session_id}/advance", json={"attempt_id": body["attempt_id"], "expected_version": body["session"]["version"]})
        assert advanced.status_code == 200, advanced.text
        snapshot = advanced.json()
        version, problem = snapshot["version"], snapshot["current_problem"]
        if index < 9:
            assert snapshot["state"] == "active" and problem is not None
    assert snapshot["state"] == "finished" and snapshot["current_problem"] is None
    assert snapshot["answered_count"] == 10 and snapshot["correct_count"] == 10
