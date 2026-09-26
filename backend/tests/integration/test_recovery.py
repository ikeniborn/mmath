import pytest
from httpx import ASGITransport, AsyncClient

from mental_math.accounts.cli import reset_password
from mental_math.main import create_app


@pytest.mark.asyncio
async def test_operator_recovery_revokes_old_session():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Origin": "http://test"}) as client:
        csrf = (await client.get("/api/v1/auth/session")).json()["csrf_token"]
        await client.post("/api/v1/auth/register", json={"email": "recovery@example.com", "password": "correct horse battery staple"}, headers={"X-CSRF-Token": csrf})
        assert (await client.get("/api/v1/auth/session")).json()["email"] == "recovery@example.com"
        await reset_password(app.state.settings.database_url, "recovery@example.com", "new secure passphrase 123")
        assert (await client.get("/api/v1/players")).status_code == 401
        signed_in = await client.post("/api/v1/auth/login", json={"email": "recovery@example.com", "password": "new secure passphrase 123"}, headers={"X-CSRF-Token": csrf})
        assert signed_in.status_code == 200
