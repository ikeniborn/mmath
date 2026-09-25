"""Atomic game flow. Every function runs inside the caller's unit of work and never commits.

Lock order is child row first, then learning session. A conflict returns 409 with the
committed snapshot so a stale browser can reconcile instead of grading twice.
"""

import hashlib
import json
from datetime import timedelta
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mental_math.accounts.security import now
from mental_math.game.generator import generate_addition
from mental_math.game.hints import render_hint
from mental_math.game.models import Attempt, LearningSession, PolicyDecision, Problem
from mental_math.game.schemas import AttemptResult, Feedback, HintResult, PublicProblem, SessionSnapshot, SubmitAttempt
from mental_math.game.validator import grade
from mental_math.players.models import Player
from mental_math.players.service import owned_player
from mental_math.policy.service import decide, state_payload
from mental_math.policy.types import PolicyState
from mental_math.student.state import record_attempt

TOTAL_PROBLEMS = 10
TIMING_TOLERANCE = timedelta(seconds=5)


def public_problem(problem: Problem | None) -> PublicProblem | None:
    if problem is None:
        return None
    return PublicProblem(id=problem.id, ordinal=problem.ordinal, skill=problem.skill, band=problem.band, operation=problem.operation, operand_a=problem.operand_a, operand_b=problem.operand_b)


async def snapshot(db: AsyncSession, session: LearningSession) -> SessionSnapshot:
    current = await db.get(Problem, session.current_problem_id) if session.current_problem_id else None
    hint = render_hint(current) if current is not None and current.hinted_at is not None else None
    return SessionSnapshot(id=session.id, player_id=session.player_id, version=session.version, state=session.state, phase=session.phase, current_problem=public_problem(current), feedback=Feedback(**session.feedback) if session.feedback else None, hint=hint, last_attempt_id=session.last_attempt_id, settings=session.settings, answered_count=session.answered_count, correct_count=session.correct_count, total_problems=TOTAL_PROBLEMS, active_ms=session.active_ms, time_limit_ms=time_limit_ms(session))


def time_limit_ms(session: LearningSession) -> int:
    return int(session.settings["session_minutes"]) * 60_000


def conflict(current: SessionSnapshot) -> HTTPException:
    return HTTPException(409, detail={"code": "version_conflict", "snapshot": current.model_dump(mode="json")})


async def _owned_session(db: AsyncSession, account_id: UUID, session_id: UUID) -> tuple[Player, LearningSession]:
    """Authorize through the child, lock child then session, and return both."""
    player_id = await db.scalar(select(LearningSession.player_id).join(Player, Player.id == LearningSession.player_id).where(LearningSession.id == session_id, Player.account_id == account_id))
    if player_id is None:
        raise HTTPException(404, detail={"code": "not_found"})
    player = await owned_player(db, account_id, player_id, lock=True)
    session = await db.get(LearningSession, session_id, with_for_update=True)
    return player, session


def _issue(session: LearningSession, ordinal: int) -> Problem:
    generated = generate_addition(session.id, ordinal, session.settings["difficulty_band"])
    return Problem(session_id=session.id, ordinal=ordinal, skill=generated.skill, band=generated.band, operation=generated.operation, operand_a=generated.operand_a, operand_b=generated.operand_b, correct_answer=generated.correct_answer)


async def start_session(db: AsyncSession, account_id: UUID, player_id: UUID) -> tuple[SessionSnapshot, bool]:
    """Return the child's active session, or atomically create one. Second value: created."""
    player = await owned_player(db, account_id, player_id, lock=True)
    existing = await db.scalar(select(LearningSession).where(LearningSession.player_id == player.id, LearningSession.state == "active"))
    if existing is not None:
        return await snapshot(db, existing), False
    if "addition" not in player.topics:
        raise HTTPException(422, detail={"code": "skill_unavailable", "supported": ["addition"]})
    settings = {"mode": player.mode, "difficulty_band": player.difficulty_band, "topics": list(player.topics), "session_minutes": player.session_minutes}
    session = LearningSession(player_id=player.id, settings=settings, state="active", phase="answer", version=1, answered_count=0, correct_count=0, active_ms=0)
    db.add(session)
    await db.flush()
    first = _issue(session, 1)
    db.add(first)
    await db.flush()
    session.current_problem_id = first.id
    session.active_from = now()
    await db.flush()
    return await snapshot(db, session), True


async def active_session(db: AsyncSession, account_id: UUID, player_id: UUID) -> SessionSnapshot | None:
    """Read-only lookup for the child home screen; never creates a session."""
    player = await owned_player(db, account_id, player_id)
    session = await db.scalar(select(LearningSession).where(LearningSession.player_id == player.id, LearningSession.state == "active"))
    return await snapshot(db, session) if session is not None else None


async def read_session(db: AsyncSession, account_id: UUID, session_id: UUID) -> SessionSnapshot:
    session = await db.scalar(select(LearningSession).join(Player, Player.id == LearningSession.player_id).where(LearningSession.id == session_id, Player.account_id == account_id))
    if session is None:
        raise HTTPException(404, detail={"code": "not_found"})
    return await snapshot(db, session)


def fingerprint(command: SubmitAttempt) -> str:
    canonical = json.dumps({"problem_id": str(command.problem_id), "answer": command.answer, "response_ms": command.response_ms, "expected_version": command.expected_version}, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _validated_timing(session: LearningSession, response_ms: int | None) -> int | None:
    if response_ms is None or session.active_from is None:
        return None
    elapsed = now() - session.active_from + TIMING_TOLERANCE
    return response_ms if timedelta(milliseconds=response_ms) <= elapsed else None


async def submit_attempt(db: AsyncSession, account_id: UUID, session_id: UUID, command: SubmitAttempt) -> AttemptResult:
    player, session = await _owned_session(db, account_id, session_id)
    replay = await db.scalar(select(Attempt).where(Attempt.submission_id == command.submission_id, Attempt.session_id == session.id))
    if replay is not None:
        if replay.fingerprint != fingerprint(command):
            raise HTTPException(409, detail={"code": "submission_conflict"})
        return AttemptResult(attempt_id=replay.id, correct=replay.correct, feedback=Feedback(**session.feedback) if session.last_attempt_id == replay.id else await _feedback_for(db, replay), next_problem=None, session=await snapshot(db, session))
    current = await snapshot(db, session)
    if session.state != "active" or session.phase != "answer" or command.expected_version != session.version or command.problem_id != session.current_problem_id:
        raise conflict(current)
    problem = await db.get(Problem, session.current_problem_id)
    correct = grade(problem, command.answer)
    response_ms = _validated_timing(session, command.response_ms)
    attempt = Attempt(session_id=session.id, problem_id=problem.id, submission_id=command.submission_id, fingerprint=fingerprint(command), answer=command.answer, correct=correct, response_ms=response_ms, hint_used=problem.hinted_at is not None)
    db.add(attempt)
    await db.flush()
    skill = await record_attempt(db, player.id, problem.skill, problem.band, correct)
    session.answered_count += 1
    session.correct_count += int(correct)
    session.active_ms += response_ms or 0
    state = PolicyState(skill=problem.skill, band=problem.band, mode=session.settings["mode"], attempts=skill.attempts, correct=skill.correct, session_answered=session.answered_count, last_correct=correct)
    decision = decide(state)
    db.add(PolicyDecision(attempt_id=attempt.id, session_id=session.id, mode=decision.mode, allowed_actions=list(decision.allowed_actions), state=state_payload(state), provider=decision.proposal.provider, model_version=decision.proposal.model_version, proposed_action=decision.proposal.action, applied_action=decision.applied_action, latency_ms=decision.latency_ms, fallback_reason=decision.fallback_reason))
    session.feedback = Feedback(correct=correct, submitted_answer=command.answer, correct_answer=problem.correct_answer).model_dump()
    session.last_attempt_id = attempt.id
    session.phase = "feedback"
    session.pending_problem_id = None
    if session.answered_count < TOTAL_PROBLEMS and session.active_ms < time_limit_ms(session):
        pending = _issue(session, problem.ordinal + 1)
        db.add(pending)
        await db.flush()
        session.pending_problem_id = pending.id
    session.version += 1
    await db.flush()
    return AttemptResult(attempt_id=attempt.id, correct=correct, feedback=Feedback(**session.feedback), next_problem=None, session=await snapshot(db, session))


async def _feedback_for(db: AsyncSession, attempt: Attempt) -> Feedback:
    problem = await db.get(Problem, attempt.problem_id)
    return Feedback(correct=attempt.correct, submitted_answer=attempt.answer, correct_answer=problem.correct_answer)


async def hint_session(db: AsyncSession, account_id: UUID, session_id: UUID, problem_id: UUID, expected_version: int) -> HintResult:
    """Record hint exposure once under the child lock; an already-exposed hint replays without mutation."""
    _, session = await _owned_session(db, account_id, session_id)
    problem = await db.scalar(select(Problem).where(Problem.id == problem_id, Problem.session_id == session.id))
    if problem is None:
        raise HTTPException(404, detail={"code": "not_found"})
    if problem.hinted_at is not None:
        return HintResult(hint=render_hint(problem), session=await snapshot(db, session))
    current = await snapshot(db, session)
    if session.state != "active" or session.phase != "answer" or problem.id != session.current_problem_id or expected_version != session.version:
        raise conflict(current)
    problem.hinted_at = now()
    session.version += 1
    await db.flush()
    return HintResult(hint=render_hint(problem), session=await snapshot(db, session))


async def advance_session(db: AsyncSession, account_id: UUID, session_id: UUID, attempt_id: UUID, expected_version: int) -> SessionSnapshot:
    _, session = await _owned_session(db, account_id, session_id)
    already_advanced = session.last_attempt_id == attempt_id and (session.phase == "answer" or session.state == "finished")
    if already_advanced:
        return await snapshot(db, session)
    current = await snapshot(db, session)
    if session.state != "active" or session.phase != "feedback" or session.last_attempt_id != attempt_id or expected_version != session.version:
        raise conflict(current)
    session.feedback = None
    if session.pending_problem_id is None:
        session.current_problem_id = None
        session.state = "finished"
        session.finished_at = now()
    else:
        session.current_problem_id, session.pending_problem_id = session.pending_problem_id, None
        session.active_from = now()
    session.phase = "answer"
    session.version += 1
    await db.flush()
    return await snapshot(db, session)


async def finish_session(db: AsyncSession, account_id: UUID, session_id: UUID) -> SessionSnapshot:
    _, session = await _owned_session(db, account_id, session_id)
    if session.state == "finished":
        return await snapshot(db, session)
    session.state = "finished"
    session.finished_at = now()
    session.current_problem_id = None
    session.pending_problem_id = None
    session.feedback = None
    session.phase = "answer"
    session.version += 1
    await db.flush()
    return await snapshot(db, session)
