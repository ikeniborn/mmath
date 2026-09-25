import pytest


@pytest.mark.asyncio
async def test_hint_is_recorded_once(family, lesson, counts):
    path = f"/sessions/{lesson.session_id}/hint"
    command = {"problem_id": lesson.problem["id"], "expected_version": lesson.version}
    first = await family.post(path, json=command)
    second = await family.post(path, json=command)
    assert first.status_code == second.status_code == 200, (first.text, second.text)
    assert first.json()["hint"] == second.json()["hint"]
    assert first.json()["session"]["version"] == second.json()["session"]["version"] == lesson.version + 1
    assert (await counts(family.player_id))["hinted_problems"] == 1
    snapshot = (await family.get(f"/sessions/{lesson.session_id}")).json()
    assert snapshot["hint"] == first.json()["hint"]
    assert "correct_answer" not in str(snapshot["hint"])


@pytest.mark.asyncio
async def test_hint_content_is_deterministic_from_operands(family, lesson):
    hint = (await family.post(f"/sessions/{lesson.session_id}/hint", json={"problem_id": lesson.problem["id"], "expected_version": lesson.version})).json()["hint"]
    assert hint["operand_a"] == lesson.problem["operand_a"] and hint["operand_b"] == lesson.problem["operand_b"]
    assert hint["kind"] in {"counters", "ten_frame", "number_line"}
    assert hint["kind"] == "counters"  # band 0 in the test profile


@pytest.mark.asyncio
async def test_hint_marks_attempt_and_stale_or_foreign_problem_is_rejected(family, lesson, counts):
    path = f"/sessions/{lesson.session_id}/hint"
    stale = await family.post(path, json={"problem_id": lesson.problem["id"], "expected_version": lesson.version + 1})
    assert stale.status_code == 409 and stale.json()["detail"]["code"] == "version_conflict"
    hinted = await family.post(path, json={"problem_id": lesson.problem["id"], "expected_version": lesson.version})
    assert hinted.status_code == 200
    version = hinted.json()["session"]["version"]
    answered = await family.post(f"/sessions/{lesson.session_id}/attempts", json={**lesson.command, "expected_version": version})
    assert answered.status_code == 200
    body = answered.json()
    # Replay of the already-exposed hint for the answered problem is safe and mutation-free.
    replay = await family.post(path, json={"problem_id": lesson.problem["id"], "expected_version": lesson.version})
    assert replay.status_code == 200 and replay.json()["session"]["version"] == body["session"]["version"]
    advanced = await family.post(f"/sessions/{lesson.session_id}/advance", json={"attempt_id": body["attempt_id"], "expected_version": body["session"]["version"]})
    next_problem = advanced.json()["current_problem"]
    # A hint request naming a problem that is not the current one and was never exposed is rejected.
    foreign = await family.post(path, json={"problem_id": next_problem["id"], "expected_version": lesson.version})
    assert foreign.status_code == 409
    assert (await counts(family.player_id))["hinted_problems"] == 1
    assert (await counts(family.player_id))["hinted_attempts"] == 1


@pytest.mark.asyncio
async def test_dropped_hint_response_retry_returns_same_content(app, family, lesson, counts):
    from uuid import UUID

    from sqlalchemy import select

    from mental_math.accounts.models import Account
    from mental_math.game import engine

    async with app.state.session_factory() as db:
        account_id = await db.scalar(select(Account.id).where(Account.email == family.parent_email))
        first = await engine.hint_session(db, account_id, UUID(lesson.session_id), UUID(lesson.problem["id"]), lesson.version)
        await db.commit()
    retried = await family.post(f"/sessions/{lesson.session_id}/hint", json={"problem_id": lesson.problem["id"], "expected_version": lesson.version})
    assert retried.status_code == 200
    assert retried.json()["hint"] == first.hint.model_dump()
    assert (await counts(family.player_id))["hinted_problems"] == 1
