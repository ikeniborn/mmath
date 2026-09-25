import json

import pytest

from mental_math.policy.evaluation import candidate_reward, evaluate
from mental_math.policy.export import PolicyExportRow, public_record


def record(*, proposed="repeat", rule="repeat", applied="repeat", allowed=("repeat", "hint", "switch"), failure=None, confidence=None, latency=12, outcome=None, policy_mode="shadow"):
    return {
        "state": {"skill": "addition", "band": 1, "mode": "automatic", "attempts": 10, "correct": 7, "mastery": 0.6, "correct_streak": 1, "error_streak": 0},
        "allowed_actions": list(allowed),
        "decision": {"proposed_action": proposed, "rule_action": rule, "confidence": confidence, "provider": "framework" if proposed or failure else "rules", "failure_code": failure, "fallback_reason": failure or ("shadow" if policy_mode == "shadow" else None), "latency_ms": latency},
        "applied_action": applied,
        "versions": {"policy_mode": policy_mode, "model_version": "laya-english" if proposed else None, "rules_version": "rules-v1", "formula_version": "mastery-v1-10s"},
        "outcome": outcome or {"complete": True, "prior_5": {"count": 5, "accuracy": 0.4, "avg_time_ms": 5000}, "next_5": {"count": 5, "accuracy": 0.8, "avg_time_ms": 3500}, "session_completed": True, "returned": True},
    }


def test_metrics_are_deterministic_and_exclude_incomplete_evidence():
    records = [
        record(proposed="repeat", confidence=0.9),
        record(proposed="hint", confidence=0.6),
        record(proposed="teleport", confidence=0.95),
        record(proposed=None, failure="timeout", latency=360),
        record(proposed="repeat", outcome={"complete": False, "prior_5": {"count": 2, "accuracy": 0.5, "avg_time_ms": 4000}, "next_5": {"count": 1, "accuracy": 1.0, "avg_time_ms": 3000}, "session_completed": None, "returned": None}),
    ]
    first, second = evaluate(records), evaluate(records)
    assert first == second
    assert first["records"] == 5 and first["proposals"] == 4 and first["failures"] == 1
    assert first["agreement_with_rules"] == pytest.approx(2 / 4)
    assert first["illegal_proposal_rate"] == pytest.approx(1 / 4)
    assert first["fallback_rate"] == pytest.approx(1 / 5)
    assert first["latency_ms"]["p50"] == 12 and first["latency_ms"]["max"] == 360
    assert first["reward"]["complete_windows"] == 4 and first["reward"]["incomplete_windows"] == 1
    assert first["reward"]["mean"] == pytest.approx(candidate_reward(records[0]["outcome"]))
    assert "cannot establish causal benefit" in first["disclaimer"]
    assert first["calibration"]["bins"][-1]["confidence_from"] == pytest.approx(0.8)


def test_candidate_reward_follows_the_lld_formula_and_refuses_incomplete_windows():
    outcome = {"complete": True, "prior_5": {"count": 5, "accuracy": 0.4, "avg_time_ms": 5000}, "next_5": {"count": 5, "accuracy": 0.8, "avg_time_ms": 3500}, "session_completed": True, "returned": False}
    expected = 0.40 * (0.8 - 0.4) + 0.25 * ((5000 - 3500) / 5000) + 0.20 * 1 + 0.15 * 0
    assert candidate_reward(outcome) == pytest.approx(expected)
    assert candidate_reward({**outcome, "returned": None}) is None
    assert candidate_reward({**outcome, "complete": False}) is None
    assert candidate_reward({**outcome, "prior_5": {"count": 5, "accuracy": 0.4, "avg_time_ms": None}}) is None


def test_public_record_drops_unknown_nested_fields_recursively():
    raw = record()
    raw["state"]["email"] = "SYNTHETIC_MARKER_EMAIL"
    raw["decision"]["provider_debug"] = {"cookie": "SYNTHETIC_MARKER_COOKIE"}
    raw["versions"]["headers"] = {"authorization": "SYNTHETIC_MARKER_TOKEN"}
    raw["outcome"]["next_5"]["player_name"] = "SYNTHETIC_MARKER_NAME"
    raw["extra_top_level"] = "SYNTHETIC_MARKER_TOP"
    public = public_record(raw)
    text = json.dumps(public)
    assert set(public) == {"state", "allowed_actions", "decision", "applied_action", "versions", "outcome"}
    assert "SYNTHETIC_MARKER" not in text
    assert public["outcome"]["next_5"] == {"count": 5, "accuracy": 0.8, "avg_time_ms": 3500}
    assert PolicyExportRow.SCHEMA["decision"]["proposed_action"] is None
