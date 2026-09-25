from uuid import UUID

import pytest

from mental_math.game import engine
from mental_math.game.schemas import SubmitAttempt


@pytest.mark.asyncio
async def test_failure_before_commit_leaves_no_attempt(monkeypatch, family, lesson, counts):
    def explode(*args, **kwargs):
        raise RuntimeError("injected failure after the attempt row was written")

    monkeypatch.setattr(engine, "decide", explode)
    with pytest.raises(RuntimeError):
        await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)
    assert (await counts(family.player_id)) == {"attempts": 0, "decisions": 0}
    snapshot = (await family.get(f"/sessions/{lesson.session_id}")).json()
    assert snapshot["version"] == lesson.version and snapshot["phase"] == "answer"
    monkeypatch.undo()
    recovered = await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)
    assert recovered.status_code == 200
    assert (await counts(family.player_id)) == {"attempts": 1, "decisions": 1}


@pytest.mark.asyncio
async def test_lost_response_after_commit_is_replayed_without_second_write(app, family, lesson, counts):
    account_id = await _account_id(app, family.parent_email)
    command = SubmitAttempt(**lesson.command)
    async with app.state.session_factory() as db:
        committed = await engine.submit_attempt(db, account_id, UUID(lesson.session_id), command)
        await db.commit()
    # The HTTP response is "lost" here: the client retries the identical command through the route.
    retried = await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)
    assert retried.status_code == 200
    assert retried.json()["attempt_id"] == str(committed.attempt_id)
    assert (await counts(family.player_id)) == {"attempts": 1, "decisions": 1}


async def _account_id(app, email: str) -> UUID:
    from sqlalchemy import select

    from mental_math.accounts.models import Account

    async with app.state.session_factory() as db:
        return await db.scalar(select(Account.id).where(Account.email == email))
