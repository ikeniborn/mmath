import pytest
from httpx import ASGITransport, AsyncClient

from mental_math.main import create_app


@pytest.mark.asyncio
async def test_parent_can_register_and_sign_in():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Origin": "http://test"}) as client:
        csrf = (await client.get("/api/v1/auth/session")).json()["csrf_token"]
        registered = await client.post(
            "/api/v1/auth/register",
            json={"email": "parent@example.com", "password": "correct horse battery staple"},
            headers={"X-CSRF-Token": csrf},
        )
        assert registered.status_code == 201
        assert registered.json()["email"] == "parent@example.com"
        assert "password" not in registered.json()
        assert client.cookies.get("mmath_session")

        assert (await client.get("/api/v1/auth/session")).json()["email"] == "parent@example.com"
        assert (await client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": registered.json()["csrf_token"]})).status_code == 204
        signed_in = await client.post(
            "/api/v1/auth/login",
            json={"email": "parent@example.com", "password": "correct horse battery staple"},
            headers={"X-CSRF-Token": csrf},
        )
        assert signed_in.status_code == 200
        assert signed_in.json()["email"] == "parent@example.com"
