import json
import logging

import pytest
from httpx import ASGITransport, AsyncClient

from mental_math.observability import JsonFormatter, metrics


@pytest.mark.asyncio
async def test_metrics_aggregate_requests_and_attempts_without_identifiers(family, lesson):
    before = metrics.snapshot()
    assert (await family.post(f"/sessions/{lesson.session_id}/attempts", json=lesson.command)).status_code == 200
    text = (await family.client.get("/internal/metrics")).text
    assert "mmath_http_requests_total{route=\"/api/v1/sessions/{session_id}/attempts\",status=\"2xx\"}" in text
    assert "mmath_attempts_total{correct=\"true\"}" in text
    assert "mmath_policy_decisions_total{applied=\"repeat\"}" in text
    assert "mmath_policy_fallback_total" in text and "mmath_inference_deadline_total" in text
    assert lesson.session_id not in text and family.player_id not in text and "example.com" not in text
    after = metrics.snapshot()
    assert after["attempts_total"]["true"] == before["attempts_total"].get("true", 0) + 1


def test_json_logs_redact_secret_fields_and_values(caplog):
    marker = "SYNTHETIC_SECRET_9f8e2c"
    formatter = JsonFormatter()
    record = logging.LogRecord("mental_math", logging.INFO, __file__, 1, "login for %s", ("parent@example.com",), None)
    record.password = marker
    record.authorization = f"Bearer {marker}"
    record.cookie = f"mmath_session={marker}"
    record.player = "p-1"
    record.database_url = f"postgresql+psycopg://mmath:{marker}@db/mmath"
    line = formatter.format(record)
    payload = json.loads(line)
    assert marker not in line and "parent@example.com" not in line
    assert payload["password"] == "[redacted]" and payload["authorization"] == "[redacted]" and payload["cookie"] == "[redacted]"
    assert payload["database_url"] == "[redacted]" and payload["player"] == "p-1"
    assert payload["level"] == "INFO" and payload["logger"] == "mental_math"


@pytest.mark.asyncio
async def test_unhandled_exception_is_counted_and_logged_as_500():
    from mental_math.main import create_app

    app = create_app()

    @app.get("/api/v1/_crash")
    async def crash():
        raise RuntimeError("boom")

    records: list[logging.LogRecord] = []
    handler = logging.Handler()
    handler.emit = records.append  # the app logger does not propagate to caplog
    app.state.logger.addHandler(handler)
    before = metrics.snapshot()["requests_total"].get(("/api/v1/_crash", "5xx"), 0)
    try:
        async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
            assert (await client.get("/api/v1/_crash")).status_code == 500
    finally:
        app.state.logger.removeHandler(handler)
    assert metrics.snapshot()["requests_total"].get(("/api/v1/_crash", "5xx"), 0) == before + 1
    assert any(getattr(record, "status", None) == 500 and getattr(record, "route", None) == "/api/v1/_crash" for record in records)
