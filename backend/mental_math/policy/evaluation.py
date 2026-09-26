"""Deterministic offline evaluation of exported policy evidence.

The report compares model proposals with the rule decisions that were actually applied. In shadow mode
every outcome followed the rule action, so no metric here can establish a causal benefit of the model.
"""

import json
import sys
from pathlib import Path

DISCLAIMER = "Shadow outcomes follow the applied rule action; these metrics describe agreement and evidence completeness and cannot establish causal benefit of the unchosen model action. Active rollout needs a separately authorised evaluation."
BINS = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.01)]


def candidate_reward(outcome: dict) -> float | None:
    """LLD candidate reward: 0.40 accuracy gain + 0.25 speed gain + 0.20 completion + 0.15 retention. None when any component is missing."""
    prior, following = outcome.get("prior_5") or {}, outcome.get("next_5") or {}
    if not outcome.get("complete") or outcome.get("session_completed") is None or outcome.get("returned") is None:
        return None
    if prior.get("accuracy") is None or following.get("accuracy") is None or not prior.get("avg_time_ms") or following.get("avg_time_ms") is None:
        return None
    improvement_accuracy = following["accuracy"] - prior["accuracy"]
    improvement_speed = max(-1.0, min(1.0, (prior["avg_time_ms"] - following["avg_time_ms"]) / prior["avg_time_ms"]))
    return 0.40 * improvement_accuracy + 0.25 * improvement_speed + 0.20 * float(outcome["session_completed"]) + 0.15 * float(outcome["returned"])


def _quantile(values: list[int], q: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * q))]


def evaluate(records: list[dict]) -> dict:
    proposals = [record for record in records if record["decision"].get("proposed_action") is not None]
    failures = [record for record in records if record["decision"].get("failure_code")]
    agreements = sum(1 for record in proposals if record["decision"]["proposed_action"] == record["decision"].get("rule_action"))
    illegal = sum(1 for record in proposals if record["decision"]["proposed_action"] not in record["allowed_actions"])
    # Timeouts hit the deadline by construction; they are counted separately so the quantiles describe answered calls.
    timeouts = sum(1 for record in records if record["decision"].get("failure_code") == "timeout")
    latencies = [record["decision"]["latency_ms"] for record in records if isinstance(record["decision"].get("latency_ms"), int) and record["decision"].get("failure_code") != "timeout"]
    rewards = [reward for reward in (candidate_reward(record["outcome"]) for record in records) if reward is not None]
    bins = []
    for low, high in BINS:
        inside = [record for record in proposals if isinstance(record["decision"].get("confidence"), (int, float)) and low <= record["decision"]["confidence"] < high]
        agree = sum(1 for record in inside if record["decision"]["proposed_action"] == record["decision"].get("rule_action"))
        bins.append({"confidence_from": low, "confidence_to": min(high, 1.0), "proposals": len(inside), "agreement_with_rules": (agree / len(inside)) if inside else None})
    return {
        "records": len(records),
        "proposals": len(proposals),
        "failures": len(failures),
        "agreement_with_rules": (agreements / len(proposals)) if proposals else None,
        "illegal_proposal_rate": (illegal / len(proposals)) if proposals else None,
        "fallback_rate": (len(failures) / len(records)) if records else None,
        "latency_ms": {"p50": _quantile(latencies, 0.5), "p95": _quantile(latencies, 0.95), "max": max(latencies) if latencies else None, "samples": len(latencies), "timeouts": timeouts},
        "calibration": {"note": "agreement with the applied rule action per confidence bin; not a probability of learning benefit", "bins": bins},
        "reward": {"complete_windows": len(rewards), "incomplete_windows": len(records) - len(rewards), "mean": (sum(rewards) / len(rewards)) if rewards else None},
        "disclaimer": DISCLAIMER,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m mental_math.policy.evaluation <export.jsonl>", file=sys.stderr)
        return 2
    records = [json.loads(line) for line in Path(argv[0]).read_text(encoding="utf-8").splitlines() if line.strip()]
    print(json.dumps(evaluate(records), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
