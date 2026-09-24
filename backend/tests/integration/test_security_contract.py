import pytest
from httpx import ASGITransport, AsyncClient

from mental_math.config import Settings
from mental_math.main import create_app


@pytest.mark.asyncio
async def test_origin_csrf_and_input_limits():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Origin": "http://test"}) as client:
        csrf = (await client.get("/api/v1/auth/session")).json()["csrf_token"]
        payload = {"email": "limit@example.com", "password": "correct horse battery staple"}
        assert (await client.post("/api/v1/auth/register", json=payload, headers={"X-CSRF-Token": csrf, "Origin": "https://evil.example.com"})).status_code == 403
        assert (await client.post("/api/v1/auth/register", json=payload, headers={"X-CSRF-Token": csrf, "Origin": ""})).status_code == 403
        assert (await client.post("/api/v1/auth/register", json=payload, headers={"X-CSRF-Token": "wrong"})).status_code == 403
        assert (await client.post("/api/v1/auth/register", json={**payload, "password": "short"}, headers={"X-CSRF-Token": csrf})).status_code == 422
        registered = await client.post("/api/v1/auth/register", json=payload, headers={"X-CSRF-Token": csrf})
        assert registered.status_code == 201
        assert "httponly" in registered.headers["set-cookie"].lower()
        assert "secure" not in registered.headers["set-cookie"].lower()
        assert registered.headers["cache-control"] == "no-store"
        csrf = registered.json()["csrf_token"]
        assert (await client.post("/api/v1/players", json={"name": "A", "age": 4, "topics": ["addition"]}, headers={"X-CSRF-Token": csrf})).status_code == 422
        assert (await client.post("/api/v1/players", json={"name": "A", "age": 7, "topics": []}, headers={"X-CSRF-Token": csrf})).status_code == 422


def test_public_mode_requires_https(monkeypatch):
    monkeypatch.setenv("MMATH_DATABASE_URL", "postgresql+psycopg://dummy:dummy@localhost/dummy")
    monkeypatch.setenv("MMATH_MODE", "public")
    monkeypatch.setenv("MMATH_ORIGIN", "http://example.com")
    with pytest.raises(RuntimeError, match="HTTPS"):
        Settings.from_env()


def test_missing_config_fails_explicitly(monkeypatch):
    monkeypatch.delenv("MMATH_DATABASE_URL")
    with pytest.raises(RuntimeError, match="MMATH_DATABASE_URL"):
        Settings.from_env()


@pytest.mark.asyncio
async def test_public_session_cookie_is_secure(monkeypatch):
    monkeypatch.setenv("MMATH_ORIGIN", "https://math.example.com")
    monkeypatch.setenv("MMATH_MODE", "public")
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://math.example.com") as client:
        csrf = (await client.get("/api/v1/auth/session")).json()["csrf_token"]
        response = await client.post("/api/v1/auth/register", json={"email": "secure@example.com", "password": "correct horse battery staple"}, headers={"X-CSRF-Token": csrf, "Origin": "https://math.example.com"})
        assert response.status_code == 201
        assert "secure" in response.headers["set-cookie"].lower()
