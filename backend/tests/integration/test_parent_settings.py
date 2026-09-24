from datetime import timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import update

from mental_math.accounts.models import AuthSession, LoginFailure
from mental_math.accounts.security import now
from mental_math.main import create_app


@pytest.mark.asyncio
async def test_settings_require_csrf_and_recent_password_confirmation():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Origin": "http://test"}) as client:
        bootstrap = (await client.get("/api/v1/auth/session")).json()["csrf_token"]
        account = await client.post("/api/v1/auth/register", json={"email": "settings@example.com", "password": "correct horse battery staple"}, headers={"X-CSRF-Token": bootstrap})
        csrf = account.json()["csrf_token"]
        assert (await client.post("/api/v1/players", json={"name": "A", "age": 5, "topics": ["addition"]})).status_code == 403
        created = await client.post("/api/v1/players", json={"name": "A", "age": 5, "topics": ["addition"]}, headers={"X-CSRF-Token": csrf})
        assert created.status_code == 201
        player_id = created.json()["id"]
        assert created.json()["difficulty_band"] == 0
        assert (await client.patch(f"/api/v1/players/{player_id}", json={"mode": "fixed"}, headers={"X-CSRF-Token": csrf})).status_code == 403
        assert (await client.post("/api/v1/auth/confirm-password", json={"password": "incorrect"}, headers={"X-CSRF-Token": csrf})).status_code == 403
        assert (await client.post("/api/v1/auth/confirm-password", json={"password": "correct horse battery staple"}, headers={"X-CSRF-Token": csrf})).status_code == 204
        changed = await client.patch(f"/api/v1/players/{player_id}", json={"mode": "fixed", "difficulty_band": 2}, headers={"X-CSRF-Token": csrf})
        assert changed.status_code == 200
        assert changed.json()["mode"] == "fixed"
        async with app.state.session_factory() as db:
            await db.execute(update(AuthSession).values(confirmed_at=now() - timedelta(minutes=11)))
            await db.commit()
        assert (await client.patch(f"/api/v1/players/{player_id}", json={"mode": "automatic"}, headers={"X-CSRF-Token": csrf})).status_code == 403


@pytest.mark.asyncio
async def test_expired_session_and_cross_family_mutation_rejected():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Origin": "http://test"}) as first, AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Origin": "http://test"}) as second:
        async def register(client, email):
            csrf = (await client.get("/api/v1/auth/session")).json()["csrf_token"]
            return (await client.post("/api/v1/auth/register", json={"email": email, "password": "correct horse battery staple"}, headers={"X-CSRF-Token": csrf})).json()["csrf_token"]

        first_csrf = await register(first, "first@example.com")
        second_csrf = await register(second, "second@example.com")
        player_id = (await first.post("/api/v1/players", json={"name": "B", "age": 8, "topics": ["subtraction"]}, headers={"X-CSRF-Token": first_csrf})).json()["id"]
        await second.post("/api/v1/auth/confirm-password", json={"password": "correct horse battery staple"}, headers={"X-CSRF-Token": second_csrf})
        assert (await second.patch(f"/api/v1/players/{player_id}", json={"name": "X"}, headers={"X-CSRF-Token": second_csrf})).status_code == 404
        async with app.state.session_factory() as db:
            await db.execute(update(AuthSession).values(expires_at=now() - timedelta(seconds=1)))
            await db.commit()
        assert (await first.get(f"/api/v1/players/{player_id}")).status_code == 401


@pytest.mark.asyncio
async def test_login_throttle_expires_without_permanent_lock():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Origin": "http://test"}) as client:
        csrf = (await client.get("/api/v1/auth/session")).json()["csrf_token"]
        for _ in range(5):
            response = await client.post("/api/v1/auth/login", json={"email": "unknown@example.com", "password": "wrong password"}, headers={"X-CSRF-Token": csrf})
            assert response.status_code == 401
        assert (await client.post("/api/v1/auth/login", json={"email": "unknown@example.com", "password": "wrong password"}, headers={"X-CSRF-Token": csrf})).status_code == 429
        async with app.state.session_factory() as db:
            await db.execute(update(LoginFailure).values(occurred_at=now() - timedelta(minutes=16)))
            await db.commit()
        assert (await client.post("/api/v1/auth/login", json={"email": "unknown@example.com", "password": "wrong password"}, headers={"X-CSRF-Token": csrf})).status_code == 401
