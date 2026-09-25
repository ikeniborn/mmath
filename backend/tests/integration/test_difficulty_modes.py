import pytest
from httpx import ASGITransport, AsyncClient

from tests.conftest import Family

PASSWORD = "correct horse battery staple"


async def play(family: Family, session: dict, *, correct: bool, hint: bool = False, count: int = 1) -> dict:
    """Answer `count` problems in a row; returns the snapshot after the last advance."""
    for _ in range(count):
        problem = session["current_problem"]
        version = session["version"]
        if hint:
            hinted = await family.post(f"/sessions/{session['id']}/hint", json={"problem_id": problem["id"], "expected_version": version})
            assert hinted.status_code == 200, hinted.text
            version = hinted.json()["session"]["version"]
        answer = {"addition": problem["operand_a"] + problem["operand_b"], "subtraction": problem["operand_a"] - problem["operand_b"], "multiplication": problem["operand_a"] * problem["operand_b"]}[problem["operation"]]
        from uuid6 import uuid7

        body = {"submission_id": str(uuid7()), "problem_id": problem["id"], "answer": answer if correct else answer + 100, "response_ms": 1500, "expected_version": version}
        answered = await family.post(f"/sessions/{session['id']}/attempts", json=body)
        assert answered.status_code == 200, answered.text
        result = answered.json()
        advanced = await family.post(f"/sessions/{session['id']}/advance", json={"attempt_id": result["attempt_id"], "expected_version": result["session"]["version"]})
        assert advanced.status_code == 200, advanced.text
        session = advanced.json()
    return session


async def configure(family: Family, **patch) -> dict:
    assert (await family.post("/auth/confirm-password", {"password": PASSWORD})).status_code == 204
    changed = await family.patch(f"/players/{family.player_id}", patch)
    assert changed.status_code == 200, changed.text
    return changed.json()


@pytest.mark.asyncio
async def test_new_child_defaults_to_automatic_and_starts_at_the_profile_band(family):
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    assert session["settings"]["mode"] == "automatic" and session["current_problem"]["band"] == 0


@pytest.mark.asyncio
async def test_fixed_band_never_moves_but_mastery_still_updates(family):
    await configure(family, mode="fixed", difficulty_band=2)
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    assert session["settings"] == {"mode": "fixed", "difficulty_band": 2, "topics": ["addition"], "session_minutes": 10}
    session = await play(family, session, correct=True, count=6)
    assert session["current_problem"]["band"] == 2
    session = await play(family, session, correct=False, count=3)
    assert session["current_problem"]["band"] == 2 and session["state"] == "active"
    progress = (await family.get(f"/players/{family.player_id}/progress")).json()
    skill = next(row for row in progress["skills"] if row["skill"] == "addition")
    assert skill["attempts"] == 9 and skill["correct"] == 6 and skill["mastery"] is not None
    assert skill["formula_version"].startswith("mastery-v1")


INITIAL_BANDS = {"addition": 0, "doubles": 1, "near_doubles": 1, "make_ten": 1}


async def bands(family: Family) -> dict[str, int]:
    progress = (await family.get(f"/players/{family.player_id}/progress")).json()
    return {row["skill"]: row["band"] for row in progress["skills"]}


@pytest.mark.asyncio
async def test_automatic_promotes_after_five_unhinted_correct_by_one_band(family, other_family):
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    assert session["current_problem"] == {**session["current_problem"], "skill": "addition", "band": 0}
    # Three correct on the same skill switch to the next one; the fifth correct in a row promotes that skill.
    session = await play(family, session, correct=True, count=3)
    assert session["current_problem"]["skill"] == "doubles" and session["current_problem"]["band"] == 1
    session = await play(family, session, correct=True, count=1)
    assert session["current_problem"]["band"] == 1
    session = await play(family, session, correct=True, count=1)
    assert session["current_problem"]["skill"] == "doubles" and session["current_problem"]["band"] == 3
    assert (await bands(family)) == {"addition": 0, "doubles": 3}
    # The streak restarts after a promotion: four more correct do not promote again.
    session = await play(family, session, correct=True, count=4)
    practised = await bands(family)
    assert practised["doubles"] == 3 and all(practised[code] == INITIAL_BANDS[code] for code in practised if code != "doubles")
    sibling = (await other_family.post("/sessions", {"player_id": other_family.player_id})).json()
    assert sibling["current_problem"]["band"] == 0 and (await bands(other_family)) == {}


@pytest.mark.asyncio
async def test_hinted_answers_do_not_count_toward_promotion(family):
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    session = await play(family, session, correct=True, count=4)
    session = await play(family, session, correct=True, hint=True, count=1)
    session = await play(family, session, correct=True, count=4)
    practised = await bands(family)
    assert practised and all(practised[code] == INITIAL_BANDS[code] for code in practised)


@pytest.mark.asyncio
async def test_three_errors_select_easier_and_never_promote(family):
    await configure(family, difficulty_band=2)
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    assert session["current_problem"]["skill"] == "addition" and session["current_problem"]["band"] == 2
    session = await play(family, session, correct=False, count=3)
    assert session["current_problem"]["skill"] == "addition" and session["current_problem"]["band"] == 1
    session = await play(family, session, correct=False, count=3)
    assert session["current_problem"]["skill"] == "addition" and session["current_problem"]["band"] == 0
    # At the floor the rule repeats with a visual hint already exposed.
    session = await play(family, session, correct=False, count=3)
    assert session["current_problem"]["band"] == 0 and session["hint"] is not None
    assert (await bands(family)) == {"addition": 0}


@pytest.mark.asyncio
async def test_enabled_topics_alternate_and_multiplication_uses_its_supported_bands(family):
    await configure(family, topics=["addition", "subtraction", "multiplication"], difficulty_band=2)
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    seen = []
    while session["state"] == "active":
        problem = session["current_problem"]
        seen.append((problem["operation"], problem["band"]))
        session = await play(family, session, correct=True, count=1)
    assert {operation for operation, _ in seen} == {"addition", "subtraction", "multiplication"}
    assert all(band >= 2 for operation, band in seen if operation == "multiplication")


@pytest.mark.asyncio
async def test_invalid_fixed_combination_is_rejected_with_alternatives(family):
    assert (await family.post("/auth/confirm-password", {"password": PASSWORD})).status_code == 204
    rejected = await family.patch(f"/players/{family.player_id}", {"mode": "fixed", "topics": ["multiplication"], "difficulty_band": 0})
    assert rejected.status_code == 422
    assert rejected.json()["detail"]["code"] == "unsupported_difficulty"
    assert rejected.json()["detail"]["supported_bands"] == [2, 3, 4]
    created = await family.post("/players", {"name": "Lena", "age": 9, "topics": ["multiplication"], "mode": "fixed", "difficulty_band": 1})
    assert created.status_code == 422


@pytest.mark.asyncio
async def test_progress_lists_sessions_newest_first_with_pagination(family, lesson):
    finished = await family.post(f"/sessions/{lesson.session_id}/finish")
    assert finished.status_code == 200
    second = (await family.post("/sessions", {"player_id": family.player_id})).json()
    progress = (await family.get(f"/players/{family.player_id}/progress?limit=1")).json()
    assert [row["id"] for row in progress["sessions"]] == [second["id"]]
    assert progress["total_sessions"] == 2
    page_two = (await family.get(f"/players/{family.player_id}/progress?limit=1&offset=1")).json()
    assert [row["id"] for row in page_two["sessions"]] == [lesson.session_id]
    assert page_two["sessions"][0]["state"] == "finished"
