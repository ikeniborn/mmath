import pytest
from httpx import ASGITransport, AsyncClient

from mental_math.main import create_app


@pytest.mark.asyncio
async def test_other_parent_cannot_read_child():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Origin": "http://test"}) as first, AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers={"Origin": "http://test"}) as second:
        async def register(client, email):
            csrf = (await client.get("/api/v1/auth/session")).json()["csrf_token"]
            response = await client.post("/api/v1/auth/register", json={"email": email, "password": "correct horse battery staple"}, headers={"X-CSRF-Token": csrf})
            assert response.status_code == 201
            return response.json()["csrf_token"]

        csrf_first = await register(first, "first@example.com")
        await register(second, "second@example.com")
        child = await first.post("/api/v1/players", json={"name": "Masha", "age": 7, "topics": ["addition"]}, headers={"X-CSRF-Token": csrf_first})
        assert child.status_code == 201
        child_id = child.json()["id"]
        assert child.json()["mode"] == "automatic"
        assert (await second.get(f"/api/v1/players/{child_id}")).status_code == 404
        assert (await first.get(f"/api/v1/players/{child_id}")).status_code == 200
