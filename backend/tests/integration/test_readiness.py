import pytest
from httpx import ASGITransport, AsyncClient

from mental_math import health
from mental_math.main import create_app


@pytest.mark.asyncio
async def test_live_and_ready_report_database_and_schema(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        live = await client.get("/health/live")
        assert live.status_code == 200 and live.json() == {"status": "live"}
        ready = await client.get("/health/ready")
        assert ready.status_code == 200
        body = ready.json()
        assert body["status"] == "ready" and body["database"] == "ok" and body["schema"] == "ok"
        assert "framework" not in body


@pytest.mark.asyncio
async def test_schema_drift_and_database_outage_make_readiness_fail(monkeypatch, app):
    monkeypatch.setattr(health, "expected_revision", lambda: "9999_future")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        drift = await client.get("/health/ready")
        assert drift.status_code == 503 and drift.json()["schema"] == "mismatch"
    monkeypatch.undo()
    broken = create_app()

    class Broken:
        async def __aenter__(self):
            raise RuntimeError("database unreachable")

        async def __aexit__(self, *args):
            return False

    broken.state.session_factory = lambda: Broken()
    async with AsyncClient(transport=ASGITransport(app=broken), base_url="http://test") as client:
        down = await client.get("/health/ready")
        assert down.status_code == 503 and down.json()["database"] == "unavailable"
        assert "unreachable" not in down.text
