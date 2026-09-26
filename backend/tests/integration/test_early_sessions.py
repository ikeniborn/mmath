import pytest

from tests.conftest import solve, wrong


async def child(family, age: int, **extra) -> dict:
    response = await family.post("/players", {"name": f"Age{age}", "age": age, **extra})
    assert response.status_code == 201, response.text
    return response.json()


async def answer(family, snapshot: dict, value: int, index: int) -> tuple[dict, dict]:
    result = await family.post(f"/sessions/{snapshot['id']}/attempts", {"submission_id": f"6f4b4b3e-9c3f-4c58-9e5e-1f7d5c1a{index:04d}", "problem_id": snapshot["current_problem"]["id"], "answer": value, "response_ms": 1200, "expected_version": snapshot["version"]})
    assert result.status_code == 200, result.text
    return result.json(), result.json()["session"]


@pytest.mark.asyncio
async def test_age_four_profile_defaults_to_early_topics_six_tasks_and_picture_mode(family):
    player = await child(family, 4)
    assert player["topics"] == ["early", "addition", "subtraction", "counting"] and player["round_tasks"] == 6
    snapshot = (await family.post("/sessions", {"player_id": player["id"]})).json()
    assert snapshot["total_problems"] == 6 and snapshot["settings"]["round_tasks"] == 6 and snapshot["settings"]["picture_mode"] is True


@pytest.mark.asyncio
async def test_age_seven_profile_keeps_ten_tasks_and_prompts_without_options(family):
    player = await child(family, 7, topics=["addition"])
    assert player["topics"] == ["addition"] and player["round_tasks"] == 10
    snapshot = (await family.post("/sessions", {"player_id": player["id"]})).json()
    assert snapshot["total_problems"] == 10 and snapshot["settings"]["picture_mode"] is False
    assert "options" not in (snapshot["current_problem"]["prompt"] or {})


@pytest.mark.asyncio
async def test_picture_mode_adds_unmarked_options_to_numeric_kinds(family):
    player = await child(family, 4, topics=["addition"])
    snapshot = (await family.post("/sessions", {"player_id": player["id"]})).json()
    problem = snapshot["current_problem"]
    options = problem["prompt"]["options"]
    correct = solve(problem)
    assert len(options) == 3 == len(set(options)) and options.count(correct) == 1
    assert all(isinstance(value, int) and value >= 0 for value in options)


@pytest.mark.asyncio
async def test_early_round_of_six_is_solvable_and_finishes(family, counts):
    player = await child(family, 4, topics=["early"])
    snapshot = (await family.post("/sessions", {"player_id": player["id"]})).json()
    kinds = set()
    for index in range(6):
        problem = snapshot["current_problem"]
        kinds.add(problem["kind"])
        result, snapshot = await answer(family, snapshot, solve(problem), index)
        assert result["correct"] is True
        snapshot = (await family.post(f"/sessions/{snapshot['id']}/advance", {"attempt_id": result["attempt_id"], "expected_version": snapshot["version"]})).json()
    assert snapshot["state"] == "finished" and snapshot["answered_count"] == 6 and snapshot["correct_count"] == 6
    assert len(kinds) >= 5, kinds  # picture mode switches skill after every correct answer: a round is varied
    assert (await counts(player["id"]))["attempts"] == 6


@pytest.mark.asyncio
async def test_wrong_early_answers_are_graded_wrong(family):
    player = await child(family, 5, topics=["early"])
    snapshot = (await family.post("/sessions", {"player_id": player["id"]})).json()
    problem = snapshot["current_problem"]
    result, _ = await answer(family, snapshot, wrong(problem, solve(problem)), 99)
    assert result["correct"] is False


@pytest.mark.asyncio
async def test_round_tasks_is_validated_and_applies_to_new_sessions(family):
    assert (await family.post("/players", {"name": "Bad", "age": 6, "topics": ["addition"], "round_tasks": 7})).status_code == 422
    player = await child(family, 8, topics=["addition"], round_tasks=6)
    snapshot = (await family.post("/sessions", {"player_id": player["id"]})).json()
    assert snapshot["total_problems"] == 6
    patched = await family.patch(f"/players/{player['id']}", {"round_tasks": 10})
    assert patched.status_code in (200, 403)  # 403 when the parent confirmation window is closed; the value itself validates


@pytest.mark.asyncio
async def test_picture_mode_round_with_default_topics_shows_at_least_five_game_forms(family):
    player = await child(family, 4)
    snapshot = (await family.post("/sessions", {"player_id": player["id"]})).json()
    skills = []
    for index in range(6):
        problem = snapshot["current_problem"]
        skills.append(problem["skill"])
        result, snapshot = await answer(family, snapshot, solve(problem), 50 + index)
        snapshot = (await family.post(f"/sessions/{snapshot['id']}/advance", {"attempt_id": result["attempt_id"], "expected_version": snapshot["version"]})).json()
    assert len(set(skills)) >= 5, skills
    assert snapshot["state"] == "finished"


@pytest.mark.asyncio
async def test_older_children_keep_the_three_correct_switch_rule(family):
    player = await child(family, 7, topics=["addition", "subtraction"])
    snapshot = (await family.post("/sessions", {"player_id": player["id"]})).json()
    skills = []
    for index in range(3):
        problem = snapshot["current_problem"]
        skills.append(problem["skill"])
        result, snapshot = await answer(family, snapshot, solve(problem), 70 + index)
        snapshot = (await family.post(f"/sessions/{snapshot['id']}/advance", {"attempt_id": result["attempt_id"], "expected_version": snapshot["version"]})).json()
    assert len(set(skills)) == 1, skills  # three correct on one skill before the switch
