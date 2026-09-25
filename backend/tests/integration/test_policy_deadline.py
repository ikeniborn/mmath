import time

import pytest
from httpx import ASGITransport, AsyncClient

from mental_math.observability import metrics


@pytest.mark.asyncio
async def test_slow_inference_hits_the_total_deadline_and_the_answer_still_commits(family, lesson, policy_fake, counts):
    policy_fake.behaviour = "slow"
    policy_fake.delay = 3.0
    before = metrics.snapshot()["inference_deadline_total"]
    started = time.perf_counter()
    result = await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)
    elapsed = time.perf_counter() - started
    assert result.status_code == 200 and result.json()["correct"] is True
    assert elapsed < 1.5, elapsed
    decision = await policy_fake.persisted_decision()
    assert decision.fallback_reason == "timeout" and decision.applied_action == decision.rule_action
    assert decision.latency_ms <= 600
    assert metrics.snapshot()["inference_deadline_total"] == before + 1
    assert (await counts(family.player_id)) == {"attempts": 1, "decisions": 1, "hinted_problems": 0, "hinted_attempts": 0}


@pytest.mark.asyncio
async def test_model_unavailability_does_not_affect_readiness_or_rules_play(app, family, lesson, policy_fake):
    policy_fake.behaviour = "network"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        ready = await client.get("/health/ready")
        assert ready.status_code == 200 and "framework" not in ready.text
    assert (await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)).status_code == 200


def test_shadow_configuration_requires_a_framework_url(monkeypatch):
    from mental_math.config import Settings

    monkeypatch.setenv("MMATH_DATABASE_URL", "postgresql+psycopg://u:p@db/x")
    monkeypatch.setenv("MMATH_ORIGIN", "http://test")
    monkeypatch.setenv("MMATH_MODE", "lan-http")
    monkeypatch.setenv("MMATH_POLICY_MODE", "shadow")
    monkeypatch.delenv("MMATH_FRAMEWORK_URL", raising=False)
    with pytest.raises(RuntimeError, match="MMATH_FRAMEWORK_URL"):
        Settings.from_env()
    monkeypatch.setenv("MMATH_POLICY_MODE", "active")
    with pytest.raises(RuntimeError, match="active"):
        Settings.from_env()
    monkeypatch.delenv("MMATH_POLICY_MODE")
    assert Settings.from_env().policy_mode == "rules"
