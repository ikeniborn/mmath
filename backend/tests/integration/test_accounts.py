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


@pytest.mark.asyncio
async def test_confirm_password_is_throttled_like_login_and_the_counter_clears_on_success():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Origin": "http://test"}) as client:
        csrf = (await client.get("/api/v1/auth/session")).json()["csrf_token"]
        registered = await client.post("/api/v1/auth/register", json={"email": "guard@example.com", "password": "correct horse battery staple"}, headers={"X-CSRF-Token": csrf})
        headers = {"X-CSRF-Token": registered.json()["csrf_token"]}
        for _ in range(5):
            assert (await client.post("/api/v1/auth/confirm-password", json={"password": "wrong guess"}, headers=headers)).status_code == 403
        throttled = await client.post("/api/v1/auth/confirm-password", json={"password": "correct horse battery staple"}, headers=headers)
        assert throttled.status_code == 429 and throttled.json()["detail"]["code"] == "login_throttled"
        # the same counter protects sign-in from this address
        login = await client.post("/api/v1/auth/login", json={"email": "guard@example.com", "password": "correct horse battery staple"}, headers={"X-CSRF-Token": csrf})
        assert login.status_code == 429
    async with AsyncClient(transport=ASGITransport(app=app, client=("203.0.113.7", 1234)), base_url="http://test", headers={"Origin": "http://test"}) as other_address:
        csrf = (await other_address.get("/api/v1/auth/session")).json()["csrf_token"]
        signed_in = await other_address.post("/api/v1/auth/login", json={"email": "guard@example.com", "password": "correct horse battery staple"}, headers={"X-CSRF-Token": csrf})
        assert signed_in.status_code == 200
        headers = {"X-CSRF-Token": signed_in.json()["csrf_token"]}
        assert (await other_address.post("/api/v1/auth/confirm-password", json={"password": "wrong guess"}, headers=headers)).status_code == 403
        assert (await other_address.post("/api/v1/auth/confirm-password", json={"password": "correct horse battery staple"}, headers=headers)).status_code == 204
        for _ in range(4):
            assert (await other_address.post("/api/v1/auth/confirm-password", json={"password": "wrong guess"}, headers=headers)).status_code == 403
        assert (await other_address.post("/api/v1/auth/confirm-password", json={"password": "correct horse battery staple"}, headers=headers)).status_code == 204


@pytest.mark.asyncio
async def test_csrf_cookie_lives_as_long_as_the_session_cookie():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Origin": "http://test"}) as client:
        csrf = (await client.get("/api/v1/auth/session")).json()["csrf_token"]
        registered = await client.post("/api/v1/auth/register", json={"email": "cookie@example.com", "password": "correct horse battery staple"}, headers={"X-CSRF-Token": csrf})
        cookies = {value.split("=", 1)[0]: value for value in registered.headers.get_list("set-cookie")}
        assert "Max-Age=2592000" in cookies["mmath_session"] and "Max-Age=2592000" in cookies["mmath_auth_csrf"]
        assert (await client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": registered.json()["csrf_token"]})).status_code == 204
        login = await client.post("/api/v1/auth/login", json={"email": "cookie@example.com", "password": "correct horse battery staple"}, headers={"X-CSRF-Token": csrf})
        cookies = {value.split("=", 1)[0]: value for value in login.headers.get_list("set-cookie")}
        assert "Max-Age=2592000" in cookies["mmath_auth_csrf"]
