import pytest
from uuid6 import uuid7

from tests.conftest import Family, solve, wrong
from tests.integration.test_difficulty_modes import configure


async def play_one(family: Family, session: dict, *, correct: bool = True) -> tuple[dict, dict]:
    problem = session["current_problem"]
    answer = solve(problem)
    body = {"submission_id": str(uuid7()), "problem_id": problem["id"], "answer": answer if correct else wrong(problem, answer), "response_ms": 900, "expected_version": session["version"]}
    answered = await family.post(f"/sessions/{session['id']}/attempts", json=body)
    assert answered.status_code == 200, answered.text
    result = answered.json()
    assert result["correct"] is correct, (problem, body, result["feedback"])
    advanced = await family.post(f"/sessions/{session['id']}/advance", json={"attempt_id": result["attempt_id"], "expected_version": result["session"]["version"]})
    assert advanced.status_code == 200, advanced.text
    return result, advanced.json()


@pytest.mark.asyncio
@pytest.mark.parametrize("topics", [["comparison"], ["counting"], ["division"], ["multiplication"], ["subtraction"], ["addition"]])
async def test_every_topic_plays_a_full_session_with_the_independent_solver(family, topics):
    await configure(family, topics=topics, difficulty_band=4, mode="automatic")
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    kinds, skills = set(), set()
    while session["state"] == "active":
        problem = session["current_problem"]
        assert "correct_answer" not in problem
        kinds.add(problem["kind"])
        skills.add(problem["skill"])
        _, session = await play_one(family, session)
    assert session["answered_count"] == 10 and session["correct_count"] == 10
    from mental_math.game.catalogue import skills_for_topics

    assert len(skills) >= min(3, len(skills_for_topics(topics)))


@pytest.mark.asyncio
async def test_compare_and_parity_answers_are_graded_and_wrong_choices_are_other(app, family):
    from uuid import UUID

    from sqlalchemy import select

    from mental_math.game.models import Attempt

    await configure(family, topics=["comparison"], difficulty_band=3, mode="fixed")
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    problem = session["current_problem"]
    assert problem["kind"] == "compare" and set(problem["prompt"]) == {"left", "right"}
    result, session = await play_one(family, session, correct=False)
    assert result["feedback"]["correct_answer"] in {-1, 0, 1}
    async with app.state.session_factory() as db:
        attempt = await db.scalar(select(Attempt).where(Attempt.session_id == UUID(session["id"])))
        assert attempt.error_type == "other"


@pytest.mark.asyncio
async def test_missing_operand_prompt_carries_result_and_hint_never_carries_answer(family):
    await configure(family, topics=["addition"], difficulty_band=4, mode="fixed")
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    seen_missing = False
    while session["state"] == "active" and not seen_missing:
        problem = session["current_problem"]
        if problem["kind"] == "missing":
            seen_missing = True
            hinted = await family.post(f"/sessions/{session['id']}/hint", json={"problem_id": problem["id"], "expected_version": session["version"]})
            assert hinted.status_code == 200
            hint = hinted.json()["hint"]
            assert hint["kind"] in {"counters", "ten_frame", "number_line", "groups", "pairs"} and "correct_answer" not in hint
            session = hinted.json()["session"]
            assert problem["prompt"]["result"] == problem["operand_a"] + problem["operand_b"]
        _, session = await play_one(family, session)
    assert seen_missing


@pytest.mark.asyncio
async def test_new_topics_are_accepted_and_bands_validated(family):
    changed = await configure(family, topics=["counting", "division", "comparison"], difficulty_band=2, mode="automatic")
    assert changed["topics"] == ["counting", "division", "comparison"]
    assert (await family.post("/auth/confirm-password", {"password": "correct horse battery staple"})).status_code == 204
    rejected = await family.patch(f"/players/{family.player_id}", {"mode": "fixed", "topics": ["division"], "difficulty_band": 0})
    assert rejected.status_code == 422 and rejected.json()["detail"]["supported_bands"] == [1, 3, 4]
