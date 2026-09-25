import pytest


@pytest.mark.asyncio
async def test_retry_does_not_duplicate(family, lesson, counts):
    path = f"/sessions/{lesson.session_id}/attempts"
    first = await family.post(path, json=lesson.command)
    second = await family.post(path, json=lesson.command)
    assert first.status_code == second.status_code == 200, (first.text, second.text)
    assert first.json()["attempt_id"] == second.json()["attempt_id"]
    assert first.json()["correct"] is True
    assert second.json()["session"]["version"] == first.json()["session"]["version"]
    assert (await counts(family.player_id)) == {"attempts": 1, "decisions": 1}


@pytest.mark.asyncio
async def test_same_submission_id_with_different_payload_is_rejected(family, lesson, counts):
    path = f"/sessions/{lesson.session_id}/attempts"
    assert (await family.post(path, json=lesson.command)).status_code == 200
    changed = await family.post(path, json={**lesson.command, "answer": lesson.command["answer"] + 1})
    assert changed.status_code == 409
    assert changed.json()["detail"]["code"] == "submission_conflict"
    assert (await counts(family.player_id))["attempts"] == 1


@pytest.mark.asyncio
async def test_second_submission_id_for_answered_problem_returns_conflict_with_snapshot(family, lesson, counts):
    path = f"/sessions/{lesson.session_id}/attempts"
    accepted = await family.post(path, json=lesson.command)
    assert accepted.status_code == 200
    again = await family.post(path, json={**lesson.command, "submission_id": "5f4b4b3e-9c3f-4c58-9e5e-1f7d5c1a0002"})
    assert again.status_code == 409
    detail = again.json()["detail"]
    assert detail["code"] == "version_conflict"
    assert detail["snapshot"]["version"] == accepted.json()["session"]["version"]
    assert detail["snapshot"]["phase"] == "feedback"
    assert (await counts(family.player_id))["attempts"] == 1


@pytest.mark.asyncio
async def test_stale_version_is_rejected_and_answer_is_never_disclosed(family, lesson):
    snapshot = (await family.get(f"/sessions/{lesson.session_id}")).json()
    assert "correct_answer" not in snapshot["current_problem"]
    stale = await family.post(f"/sessions/{lesson.session_id}/attempts", json={**lesson.command, "expected_version": lesson.version + 5})
    assert stale.status_code == 409
    assert stale.json()["detail"]["code"] == "version_conflict"


@pytest.mark.asyncio
async def test_other_family_cannot_touch_session(family, other_family, lesson):
    assert (await other_family.get(f"/sessions/{lesson.session_id}")).status_code == 404
    assert (await other_family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)).status_code == 404
    assert (await other_family.post("/sessions", {"player_id": family.player_id})).status_code == 404
