import asyncio
from uuid import UUID

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from mental_math.accounts.models import Account
from mental_math.game import engine
from mental_math.game.schemas import SubmitAttempt
from tests.conftest import make_family


async def _submit(app, account_id, session_id, command):
    async with app.state.session_factory() as db:
        try:
            result = await engine.submit_attempt(db, account_id, session_id, command)
            await db.commit()
            return result
        except HTTPException as error:
            await db.rollback()
            return error


@pytest.mark.asyncio
async def test_simultaneous_answers_from_two_browsers_grade_once(app, family, lesson, counts):
    async with app.state.session_factory() as db:
        account_id = await db.scalar(select(Account.id).where(Account.email == family.parent_email))
    first = SubmitAttempt(**lesson.command)
    second = SubmitAttempt(**{**lesson.command, "submission_id": "5f4b4b3e-9c3f-4c58-9e5e-1f7d5c1a0099", "answer": lesson.command["answer"] + 1})
    outcomes = await asyncio.gather(_submit(app, account_id, UUID(lesson.session_id), first), _submit(app, account_id, UUID(lesson.session_id), second))
    winners = [outcome for outcome in outcomes if not isinstance(outcome, HTTPException)]
    losers = [outcome for outcome in outcomes if isinstance(outcome, HTTPException)]
    assert len(winners) == 1 and len(losers) == 1
    assert losers[0].status_code == 409
    assert losers[0].detail["snapshot"]["version"] == winners[0].session.version
    assert losers[0].detail["snapshot"]["phase"] == "feedback"
    assert (await counts(family.player_id)) == {"attempts": 1, "decisions": 1, "hinted_problems": 0, "hinted_attempts": 0}


@pytest.mark.asyncio
async def test_two_children_progress_independently(app, family):
    sibling = (await family.post("/players", {"name": "Petya", "age": 6, "topics": ["addition"]})).json()["id"]
    first = (await family.post("/sessions", {"player_id": family.player_id})).json()
    second = (await family.post("/sessions", {"player_id": sibling})).json()
    assert first["id"] != second["id"]

    def command(snapshot, suffix):
        problem = snapshot["current_problem"]
        return {"submission_id": f"5f4b4b3e-9c3f-4c58-9e5e-1f7d5c1a1{suffix}", "problem_id": problem["id"], "answer": problem["operand_a"] + problem["operand_b"], "response_ms": 900, "expected_version": snapshot["version"]}

    responses = await asyncio.gather(family.post(f"/sessions/{first['id']}/attempts", json=command(first, "001")), family.post(f"/sessions/{second['id']}/attempts", json=command(second, "002")))
    assert [response.status_code for response in responses] == [200, 200]
    assert responses[0].json()["session"]["answered_count"] == 1 and responses[1].json()["session"]["answered_count"] == 1
    other = await make_family(app, "stranger@example.com", "Zoe")
    try:
        assert (await other.get(f"/sessions?player_id={family.player_id}")).status_code == 404
    finally:
        await other.client.aclose()
