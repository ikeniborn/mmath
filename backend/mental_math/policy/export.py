"""Pseudonymous learning-evidence export: one JSON line per committed policy decision.

Every record passes a recursive allowlist so no provider or database field outside the schema can leak.
"""

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_math.game.models import Attempt, LearningSession, PolicyDecision, Problem
from mental_math.policy.fallback import RULES_VERSION
from mental_math.policy.outcomes import AttemptFact, build_outcome
from mental_math.student.mastery import FORMULA_VERSION

STATE_FIELDS = {"skill": None, "band": None, "min_band": None, "max_band": None, "mode": None, "attempts": None, "correct": None, "mastery": None, "correct_streak": None, "error_streak": None, "session_answered": None, "skill_run": None, "last_correct": None, "last_hinted": None, "other_skills": None}
WINDOW_FIELDS = {"count": None, "accuracy": None, "avg_time_ms": None}


def public_record(raw: dict) -> dict:
    return _filter(raw, PolicyExportRow.SCHEMA)


def _filter(value, schema):
    if schema is None:
        return value if isinstance(value, (str, int, float, bool)) or value is None else None
    if schema == "list[str]":
        return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []
    if isinstance(schema, dict):
        return {key: _filter(value.get(key), sub) for key, sub in schema.items()} if isinstance(value, dict) else {}
    raise TypeError(schema)


@dataclass(frozen=True)
class PolicyExportRow:
    SCHEMA = {
        "state": STATE_FIELDS,
        "allowed_actions": "list[str]",
        "decision": {"proposed_action": None, "rule_action": None, "confidence": None, "provider": None, "failure_code": None, "fallback_reason": None, "latency_ms": None},
        "applied_action": None,
        "versions": {"policy_mode": None, "model_version": None, "rules_version": None, "formula_version": None},
        "outcome": {"complete": None, "prior_5": WINDOW_FIELDS, "next_5": WINDOW_FIELDS, "session_completed": None, "returned": None},
    }

    raw: dict

    def to_public_record(self) -> dict:
        return public_record(self.raw)


async def export_rows(db: AsyncSession, now: datetime | None = None) -> list[PolicyExportRow]:
    now = now or datetime.now(timezone.utc)
    decisions = (await db.execute(select(PolicyDecision, Attempt, Problem, LearningSession).join(Attempt, Attempt.id == PolicyDecision.attempt_id).join(Problem, Problem.id == Attempt.problem_id).join(LearningSession, LearningSession.id == PolicyDecision.session_id).order_by(Attempt.created_at, Attempt.id))).all()
    histories: dict[tuple, list[AttemptFact]] = {}
    session_starts: dict = {}
    for _, attempt, problem, session in decisions:
        histories.setdefault((session.player_id, problem.skill), []).append(AttemptFact(str(attempt.id), attempt.created_at, attempt.correct, attempt.response_ms))
        session_starts.setdefault(session.player_id, []).append(session.started_at)
    rows = []
    for decision, attempt, problem, session in decisions:
        history = histories[(session.player_id, problem.skill)]
        later = any(start > session.started_at for start in session_starts[session.player_id])
        outcome = build_outcome(history, str(attempt.id), session.state, session.started_at, later, now)
        raw = {
            "state": dict(decision.state or {}),
            "allowed_actions": list(decision.allowed_actions or []),
            "decision": {"proposed_action": decision.proposed_action, "rule_action": decision.rule_action, "confidence": decision.confidence, "provider": decision.provider, "failure_code": decision.fallback_reason if decision.proposed_action is None and decision.fallback_reason not in {None, "shadow", "illegal_action"} else None, "fallback_reason": decision.fallback_reason, "latency_ms": decision.latency_ms},
            "applied_action": decision.applied_action,
            "versions": {"policy_mode": decision.policy_mode, "model_version": decision.model_version, "rules_version": RULES_VERSION, "formula_version": FORMULA_VERSION},
            "outcome": outcome,
        }
        rows.append(PolicyExportRow(raw))
    return rows


def write_export(path: Path, rows: list[PolicyExportRow], *, overwrite: bool = False) -> int:
    """Write JSON lines to a new file; an existing file is never overwritten unless asked explicitly."""
    path = Path(path)
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} exists; choose a new file or pass --overwrite")
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.to_public_record(), ensure_ascii=False, sort_keys=True) + "\n")
    return len(rows)


async def _main() -> int:
    parser = argparse.ArgumentParser(description="Export pseudonymous policy evidence as JSON lines.")
    parser.add_argument("--out", required=True, type=Path, help="new output file")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    from mental_math.db import session_factory

    database_url = os.environ.get("MMATH_DATABASE_URL")
    if not database_url:
        print("MMATH_DATABASE_URL is required", file=sys.stderr)
        return 2
    factory = session_factory(database_url)
    async with factory() as db:
        rows = await export_rows(db)
    count = write_export(args.out, rows, overwrite=args.overwrite)
    print(f"exported {count} records to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(_main()))
