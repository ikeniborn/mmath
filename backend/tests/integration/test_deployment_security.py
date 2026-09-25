import pytest
from httpx import ASGITransport, AsyncClient

from mental_math.config import Settings
from mental_math.main import create_app

REPO = __import__("pathlib").Path(__file__).resolve().parents[3]


def test_public_mode_rejects_http_origin_and_lan_requires_explicit_http(monkeypatch):
    monkeypatch.setenv("MMATH_DATABASE_URL", "postgresql+psycopg://u:p@db/x")
    monkeypatch.setenv("MMATH_ORIGIN", "http://mmath.test")
    monkeypatch.setenv("MMATH_MODE", "public")
    with pytest.raises(RuntimeError, match="HTTPS"):
        Settings.from_env()
    monkeypatch.setenv("MMATH_ORIGIN", "https://mmath.test")
    monkeypatch.setenv("MMATH_MODE", "lan-http")
    with pytest.raises(RuntimeError, match="HTTP origin"):
        Settings.from_env()
    monkeypatch.delenv("MMATH_MODE")
    with pytest.raises(RuntimeError):
        Settings.from_env()
    monkeypatch.setenv("MMATH_MODE", "public")
    settings = Settings.from_env()
    assert settings.allowed_hosts == ("mmath.test", "api", "localhost", "127.0.0.1")


@pytest.mark.asyncio
async def test_public_mode_sets_secure_cookie_flags_and_rejects_foreign_host(monkeypatch):
    monkeypatch.setenv("MMATH_ORIGIN", "https://mmath.test")
    monkeypatch.setenv("MMATH_MODE", "public")
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://mmath.test", headers={"Origin": "https://mmath.test"}) as client:
        bootstrap = await client.get("/api/v1/auth/session")
        assert bootstrap.status_code == 200
        registered = await client.post("/api/v1/auth/register", json={"email": "secure@example.com", "password": "correct horse battery staple"}, headers={"X-CSRF-Token": bootstrap.json()["csrf_token"]})
        assert registered.status_code == 201
        cookies = [value.lower() for value in registered.headers.get_list("set-cookie")]
        session_cookie = next(value for value in cookies if value.startswith("mmath_session="))
        assert "secure" in session_cookie and "httponly" in session_cookie and "samesite=lax" in session_cookie
        assert "expose" not in registered.text
        foreign = await client.get("/api/v1/auth/session", headers={"Host": "evil.example"})
        assert foreign.status_code == 400
        cross_origin = await client.post("/api/v1/auth/register", json={"email": "x@example.com", "password": "correct horse battery staple"}, headers={"X-CSRF-Token": bootstrap.json()["csrf_token"], "Origin": "https://evil.example"})
        assert cross_origin.status_code == 403


def test_caddyfile_routes_api_before_spa_fallback_and_hides_internal_paths():
    caddyfile = (REPO / "deploy" / "Caddyfile").read_text()
    assert caddyfile.index("handle /api/*") < caddyfile.index("try_files")
    assert "/health" not in caddyfile and "/internal" not in caddyfile
    # forwarded addresses are trusted only from the configured proxy; the default trusts loopback only
    assert "trusted_proxies static {$MMATH_TRUSTED_PROXIES:127.0.0.1}" in caddyfile and "client_ip_headers X-Forwarded-For" in caddyfile
    public_overlay = (REPO / "deploy" / "compose.public.yaml").read_text()
    assert "MMATH_TRUSTED_PROXIES: ${MMATH_TRUSTED_PROXIES:?" in public_overlay


def test_compose_publishes_no_database_or_api_port_and_uses_external_services():
    import yaml

    base = yaml.safe_load((REPO / "compose.yaml").read_text())
    public = yaml.safe_load((REPO / "deploy" / "compose.public.yaml").read_text())
    lan = yaml.safe_load((REPO / "deploy" / "compose.lan-http.yaml").read_text())
    assert "postgres" not in base["services"] and "volumes" not in base
    assert set(base["services"]) == {"migrate", "api", "web"}
    for document in (base, public):
        for name, service in document["services"].items():
            assert "ports" not in service, name
    assert base["services"]["api"]["depends_on"]["migrate"]["condition"] == "service_completed_successfully"
    assert "${MMATH_DATABASE_URL" in base["services"]["api"]["environment"]["MMATH_DATABASE_URL"]
    assert public["services"]["api"]["environment"]["MMATH_MODE"] == "public"
    assert public["networks"]["edge"]["external"] is True
    assert "aliases" in public["services"]["web"]["networks"]["edge"]
    assert lan["services"]["api"]["environment"]["MMATH_MODE"] == "lan-http"
    assert lan["services"]["web"]["ports"] == ["${MMATH_LAN_BIND:-127.0.0.1}:${MMATH_LAN_PORT:-8080}:80"]


def test_synthetic_env_files_carry_no_real_secrets():
    for name in ("test.public.env", "test.lan.env", ".env.example"):
        text = (REPO / "deploy" / name).read_text()
        assert "replace-with" in text or "example" in text or "test" in text
        assert "ikeniborn" not in text


def test_traefik_route_contract_matches_the_platform_rules():
    import yaml

    route = yaml.safe_load((REPO / "deploy" / "traefik" / "conf.d" / "mmath.yml").read_text())
    router = route["http"]["routers"]["mmath-web"]
    assert router["rule"] == "Host(`mmath.ikeniborn.ru`)"
    assert router["entryPoints"] == ["websecure"] and router["tls"] == {"certResolver": "letsencrypt"}
    assert router["service"] == "mmath-web"
    service = route["http"]["services"]["mmath-web"]["loadBalancer"]
    assert service["passHostHeader"] is True and service["servers"] == [{"url": "http://mmath-web:80"}]
    assert "middlewares" not in router
    compose = yaml.safe_load((REPO / "compose.yaml").read_text())
    assert compose["name"] == "mmath"
