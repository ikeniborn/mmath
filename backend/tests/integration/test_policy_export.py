import json
from pathlib import Path

import pytest
from uuid6 import uuid7

from mental_math.policy.export import PolicyExportRow, export_rows, write_export
from tests.conftest import Family, solve

MARKER_EMAIL = "marker-secret-owner@example.com"
MARKER_NAME = "MarkerChildName"


async def play(family: Family, session: dict, count: int, *, correct: bool = True) -> dict:
    for _ in range(count):
        problem = session["current_problem"]
        answer = solve(problem)
        body = {"submission_id": str(uuid7()), "problem_id": problem["id"], "answer": answer if correct else answer + 100, "response_ms": 2000, "expected_version": session["version"]}
        result = (await family.post(f"/sessions/{session['id']}/attempts", json=body)).json()
        session = (await family.post(f"/sessions/{session['id']}/advance", json={"attempt_id": result["attempt_id"], "expected_version": result["session"]["version"]})).json()
    return session


@pytest.fixture
async def export_row(app, family, policy_fake):
    """Real persisted synthetic evidence: seven attempts in shadow mode, the first decision has a complete next-five window."""
    from tests.integration.test_difficulty_modes import configure

    await configure(family, name=MARKER_NAME, topics=["comparison"], mode="fixed", difficulty_band=3)
    policy_fake.action = "hint"
    policy_fake.confidence = 0.7
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    await play(family, session, 7)
    async with app.state.session_factory() as db:
        rows = await export_rows(db)
    assert len(rows) == 7
    return rows[0]


@pytest.mark.asyncio
async def test_export_uses_allowlist(export_row):
    record = export_row.to_public_record()
    assert set(record) == {"state", "allowed_actions", "decision", "applied_action", "versions", "outcome"}
    assert "email" not in record["state"] and "token" not in record["state"]
    assert record["decision"]["proposed_action"] == "hint" and record["decision"]["rule_action"] == "repeat" and record["applied_action"] == "repeat"
    assert record["versions"]["policy_mode"] == "shadow" and record["versions"]["model_version"] == "fake-1"
    assert record["outcome"]["complete"] is True and record["outcome"]["next_5"]["count"] == 5
    assert record["decision"]["confidence"] == 0.7
    assert record["outcome"]["session_completed"] is None and record["outcome"]["returned"] is None


@pytest.mark.asyncio
async def test_serialized_export_contains_no_identifiers_and_marks_incomplete_windows(app, family, policy_fake, tmp_path):
    from tests.integration.test_difficulty_modes import configure

    await configure(family, name=MARKER_NAME)
    async with app.state.session_factory() as db:
        from sqlalchemy import update

        from mental_math.accounts.models import Account

        await db.execute(update(Account).values(email=MARKER_EMAIL))
        await db.commit()
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    await play(family, session, 3)
    async with app.state.session_factory() as db:
        rows = await export_rows(db)
    target = tmp_path / "export.jsonl"
    written = write_export(target, rows)
    assert written == 3
    text = target.read_text()
    for marker in (MARKER_EMAIL, MARKER_NAME, "marker-secret", family.player_id, session["id"], "password", "cookie", "csrf", "authorization"):
        assert marker not in text, marker
    records = [json.loads(line) for line in text.splitlines()]
    assert all(record["outcome"]["complete"] is False for record in records)
    assert records[0]["outcome"]["next_5"]["count"] == 2 and records[2]["outcome"]["next_5"]["count"] == 0
    with pytest.raises(FileExistsError):
        write_export(target, rows)
    assert write_export(target, rows, overwrite=True) == 3


@pytest.mark.asyncio
async def test_retries_and_replays_do_not_duplicate_evidence(app, family, lesson, policy_fake):
    first = await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)
    second = await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)
    assert first.status_code == second.status_code == 200
    async with app.state.session_factory() as db:
        rows = await export_rows(db)
    assert len(rows) == 1 and rows[0].to_public_record()["outcome"]["next_5"]["count"] == 0


@pytest.mark.asyncio
async def test_completion_and_return_signals_come_from_later_sessions_not_fabricated(app, family, policy_fake):
    session = (await family.post("/sessions", {"player_id": family.player_id})).json()
    await play(family, session, 2)
    assert (await family.post(f"/sessions/{session['id']}/finish")).status_code == 200
    async with app.state.session_factory() as db:
        rows = await export_rows(db)
    outcome = rows[0].to_public_record()["outcome"]
    assert outcome["session_completed"] is True and outcome["returned"] is None
    later = (await family.post("/sessions", {"player_id": family.player_id})).json()
    await play(family, later, 1)
    async with app.state.session_factory() as db:
        rows = await export_rows(db)
    assert rows[0].to_public_record()["outcome"]["returned"] is True
    assert isinstance(rows[0], PolicyExportRow)
