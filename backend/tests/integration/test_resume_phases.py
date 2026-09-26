import pytest


@pytest.mark.asyncio
async def test_answer_phase_reload_restores_same_problem_without_answer(family, lesson):
    listed = await family.get(f"/sessions?player_id={family.player_id}")
    assert listed.status_code == 200
    assert listed.json()["id"] == lesson.session_id
    snapshot = (await family.get(f"/sessions/{lesson.session_id}")).json()
    assert snapshot["phase"] == "answer" and snapshot["current_problem"]["id"] == lesson.problem["id"]
    assert snapshot["version"] == lesson.version and snapshot["hint"] is None
    assert "correct_answer" not in snapshot["current_problem"]


@pytest.mark.asyncio
async def test_feedback_phase_reload_restores_feedback_and_hides_next_problem(family, lesson):
    body = (await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)).json()
    snapshot = (await family.get(f"/sessions/{lesson.session_id}")).json()
    assert snapshot["phase"] == "feedback" and snapshot["feedback"] == body["feedback"]
    assert snapshot["current_problem"]["id"] == lesson.problem["id"]
    assert "pending_problem" not in snapshot and body["next_problem"] is None


@pytest.mark.asyncio
async def test_no_active_session_lists_nothing(family):
    listed = await family.get(f"/sessions?player_id={family.player_id}")
    assert listed.status_code == 204


@pytest.mark.asyncio
async def test_active_time_limit_finishes_after_current_feedback(app, family, lesson):
    from datetime import timedelta
    from uuid import UUID

    from sqlalchemy import update

    from mental_math.accounts.security import now
    from mental_math.game.models import LearningSession

    async with app.state.session_factory() as db:
        # 10-minute profile: leave 4 seconds of budget and make the pending problem old enough to accept a 5 s sample.
        await db.execute(update(LearningSession).where(LearningSession.id == UUID(lesson.session_id)).values(active_ms=10 * 60_000 - 4_000, active_from=now() - timedelta(seconds=20)))
        await db.commit()
    answered = await family.post(f"/sessions/{lesson.session_id}/attempts", json={**lesson.command, "response_ms": 5_000})
    assert answered.status_code == 200
    body = answered.json()
    assert body["session"]["active_ms"] == 10 * 60_000 + 1_000
    assert body["session"]["phase"] == "feedback"
    advanced = await family.post(f"/sessions/{lesson.session_id}/advance", json={"attempt_id": body["attempt_id"], "expected_version": body["session"]["version"]})
    assert advanced.json()["state"] == "finished" and advanced.json()["answered_count"] == 1


@pytest.mark.asyncio
async def test_implausible_timing_is_excluded_but_answer_still_counts(family, lesson, app):
    from uuid import UUID

    from sqlalchemy import select

    from mental_math.game.models import Attempt

    answered = await family.post(f"/sessions/{lesson.session_id}/attempts", json={**lesson.command, "response_ms": 3_000_000})
    assert answered.status_code == 200 and answered.json()["correct"] is True
    assert answered.json()["session"]["active_ms"] == 0
    async with app.state.session_factory() as db:
        attempt = await db.scalar(select(Attempt).where(Attempt.session_id == UUID(lesson.session_id)))
        assert attempt.response_ms is None
