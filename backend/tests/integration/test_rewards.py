import pytest

from mental_math.players.rewards import STICKERS_PER_THEME, sticker_code
from tests.conftest import solve


async def play_round(family, player_id: str, answers: int) -> dict:
    snapshot = (await family.post("/sessions", {"player_id": player_id})).json()
    for index in range(answers):
        problem = snapshot["current_problem"]
        result = (await family.post(f"/sessions/{snapshot['id']}/attempts", {"submission_id": f"8f4b4b3e-9c3f-4c58-9e5e-{index:04d}{answers:04d}0000", "problem_id": problem["id"], "answer": solve(problem), "response_ms": 800, "expected_version": snapshot["version"]})).json()
        snapshot = (await family.post(f"/sessions/{snapshot['id']}/advance", {"attempt_id": result["attempt_id"], "expected_version": result["session"]["version"]})).json()
    if snapshot["state"] != "finished":
        snapshot = (await family.post(f"/sessions/{snapshot['id']}/finish")).json()
    return snapshot


@pytest.mark.asyncio
async def test_rewards_count_finished_rounds_with_at_least_half_answered(family):
    player = (await family.post("/players", {"name": "Four", "age": 4, "topics": ["early"], "theme": "cars"})).json()
    progress = (await family.get(f"/players/{player['id']}/progress")).json()
    assert progress["rewards"] == {"count": 0, "latest": None}
    await play_round(family, player["id"], 6)  # full round
    await play_round(family, player["id"], 2)  # abandoned early: no reward
    await play_round(family, player["id"], 3)  # exactly half: reward
    progress = (await family.get(f"/players/{player['id']}/progress")).json()
    assert progress["rewards"] == {"count": 2, "latest": "cars-2"}


def test_sticker_codes_cycle_per_theme():
    assert sticker_code("flowers", 1) == "flowers-1"
    assert sticker_code("flowers", STICKERS_PER_THEME) == f"flowers-{STICKERS_PER_THEME}"
    assert sticker_code("flowers", STICKERS_PER_THEME + 1) == "flowers-1"
