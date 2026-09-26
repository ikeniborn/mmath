import pytest


@pytest.mark.asyncio
async def test_profile_change_cannot_alter_issued_problem_or_session_settings(family, lesson):
    assert (await family.post("/auth/confirm-password", {"password": "correct horse battery staple"})).status_code == 204
    changed = await family.patch(f"/players/{family.player_id}", {"mode": "fixed", "difficulty_band": 4, "session_minutes": 5})
    assert changed.status_code == 200
    snapshot = (await family.get(f"/sessions/{lesson.session_id}")).json()
    assert snapshot["current_problem"] == lesson.problem
    assert snapshot["settings"] == {"mode": "automatic", "difficulty_band": 0, "topics": ["addition"], "session_minutes": 10}
    assert snapshot["time_limit_ms"] == 10 * 60_000
    body = (await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)).json()
    advanced = (await family.post(f"/sessions/{lesson.session_id}/advance", json={"attempt_id": body["attempt_id"], "expected_version": body["session"]["version"]})).json()
    assert advanced["current_problem"]["band"] == 0
    finished = await family.post(f"/sessions/{lesson.session_id}/finish")
    assert finished.json()["state"] == "finished"
    fresh = (await family.post("/sessions", {"player_id": family.player_id})).json()
    assert fresh["settings"]["mode"] == "fixed" and fresh["settings"]["difficulty_band"] == 4 and fresh["time_limit_ms"] == 5 * 60_000
    assert fresh["current_problem"]["band"] == 4
