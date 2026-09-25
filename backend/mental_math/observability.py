"""Aggregate metrics and safe structured logging. No identifiers, no secrets, low-cardinality labels only."""

import json
import logging
import re
import threading
import time
from collections import Counter, defaultdict

from fastapi import Request, Response

SECRET_KEYS = re.compile(r"(password|passwd|secret|token|cookie|authorization|csrf|database_url|dsn|email)", re.IGNORECASE)
SECRET_VALUES = [re.compile(r"postgresql(\+\w+)?://\S+", re.IGNORECASE), re.compile(r"Bearer\s+\S+", re.IGNORECASE), re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")]
REDACTED = "[redacted]"


def redact(value: object) -> object:
    if isinstance(value, str):
        text = value
        for pattern in SECRET_VALUES:
            text = pattern.sub(REDACTED, text)
        return text
    return value


class JsonFormatter(logging.Formatter):
    """One JSON object per line; secret-looking keys and values are redacted at this boundary."""

    RESERVED = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {"message", "asctime"}

    def format(self, record: logging.LogRecord) -> str:
        payload = {"time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"), "level": record.levelname, "logger": record.name, "message": redact(record.getMessage())}
        for key, value in record.__dict__.items():
            if key in self.RESERVED or key.startswith("_"):
                continue
            payload[key] = REDACTED if SECRET_KEYS.search(key) else redact(value)
        if record.exc_info:
            payload["exception"] = record.exc_info[0].__name__ if record.exc_info[0] else "error"
        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("mental_math")
    logger.handlers = [handler]
    logger.setLevel(level)
    logger.propagate = False
    return logger


class Metrics:
    """Process-local counters in Prometheus text format. Labels are route templates and enumerations only."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.requests: Counter = Counter()
        self.attempts: Counter = Counter()
        self.decisions: Counter = Counter()
        self.fallbacks: Counter = Counter()
        self.inference_deadlines = 0
        self.decision_latency_ms: defaultdict[str, list[int]] = defaultdict(list)

    def observe_request(self, route: str, status: int) -> None:
        with self._lock:
            self.requests[(route, f"{status // 100}xx")] += 1

    def observe_attempt(self, *, correct: bool, applied_action: str, fallback_reason: str | None, latency_ms: int, mode: str) -> None:
        with self._lock:
            self.attempts[str(correct).lower()] += 1
            self.decisions[applied_action] += 1
            if fallback_reason:
                self.fallbacks[fallback_reason] += 1
            samples = self.decision_latency_ms[mode]
            samples.append(latency_ms)
            del samples[:-500]

    def observe_inference_deadline(self) -> None:
        with self._lock:
            self.inference_deadlines += 1

    def snapshot(self) -> dict:
        with self._lock:
            return {"requests_total": dict(self.requests), "attempts_total": dict(self.attempts), "decisions_total": dict(self.decisions), "fallback_total": dict(self.fallbacks), "inference_deadline_total": self.inference_deadlines}

    def render(self) -> str:
        with self._lock:
            lines = []
            for (route, status), count in sorted(self.requests.items()):
                lines.append(f'mmath_http_requests_total{{route="{route}",status="{status}"}} {count}')
            for correct, count in sorted(self.attempts.items()):
                lines.append(f'mmath_attempts_total{{correct="{correct}"}} {count}')
            for action, count in sorted(self.decisions.items()):
                lines.append(f'mmath_policy_decisions_total{{applied="{action}"}} {count}')
            lines.append(f"mmath_policy_fallback_total {sum(self.fallbacks.values())}")
            for reason, count in sorted(self.fallbacks.items()):
                lines.append(f'mmath_policy_fallback_reason_total{{reason="{reason}"}} {count}')
            lines.append(f"mmath_inference_deadline_total {self.inference_deadlines}")
            for mode, samples in sorted(self.decision_latency_ms.items()):
                if samples:
                    ordered = sorted(samples)
                    lines.append(f'mmath_policy_decision_latency_ms{{mode="{mode}",quantile="0.5"}} {ordered[len(ordered) // 2]}')
                    lines.append(f'mmath_policy_decision_latency_ms{{mode="{mode}",quantile="0.95"}} {ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]}')
                    lines.append(f'mmath_policy_decision_latency_ms_count{{mode="{mode}"}} {len(samples)}')
            return "\n".join(lines) + "\n"


metrics = Metrics()


async def request_metrics(request: Request, call_next) -> Response:
    started = time.perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    template = getattr(route, "path", None) or "unmatched"
    metrics.observe_request(template, response.status_code)
    if template.startswith("/api/"):
        request.app.state.logger.info("request", extra={"route": template, "method": request.method, "status": response.status_code, "duration_ms": int((time.perf_counter() - started) * 1000)})
    return response
