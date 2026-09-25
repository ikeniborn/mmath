import json

import httpx
import pytest

from mental_math.policy.framework import FrameworkTransport, MAX_BODY_BYTES
from mental_math.policy.types import PolicyState

STATE = PolicyState(skill="addition", band=1, min_band=0, max_band=4, mode="automatic", attempts=10, correct=7, mastery=0.6, correct_streak=2, error_streak=0, session_answered=3, skill_run=1, last_correct=True, last_hinted=False, other_skills=2)
ALLOWED = ("repeat", "hint", "switch", "easier")


def transport_with(handler, token: str | None = "SYNTHETIC_EDGE_TOKEN_7a1c") -> FrameworkTransport:
    return FrameworkTransport(base_url="https://framework.test", model="laya-english", token=token, client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))


@pytest.mark.asyncio
async def test_success_maps_choice_and_probability_and_sends_identity_free_state():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers.get("authorization")
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json={"answers": {"next_action": {"choice": "hint", "probabilities": {"hint": 0.7, "repeat": 0.3}}}, "usage": {"prompt_tokens": 12}, "routing": {"model": "laya-english"}})

    proposal = await transport_with(handler).predict(STATE, ALLOWED)
    assert proposal.action == "hint" and proposal.confidence == pytest.approx(0.7)
    assert proposal.provider == "framework" and proposal.model_version == "laya-english" and proposal.failure_code is None
    assert seen["url"] == "https://framework.test/v1/systemone"
    assert seen["auth"] == "Bearer SYNTHETIC_EDGE_TOKEN_7a1c"
    body = seen["body"]
    assert body["model"] == "laya-english"
    assert body["questions"] == {"next_action": {"type": "choice", "criteria": list(ALLOWED)}}
    assert set(body["state"]) == set(STATE.__dict__) and "email" not in json.dumps(body).lower() and "cookie" not in json.dumps(body).lower()


@pytest.mark.asyncio
async def test_plain_string_answer_without_probabilities_has_null_confidence():
    proposal = await transport_with(lambda request: httpx.Response(200, json={"answers": {"next_action": "repeat"}, "usage": {}, "routing": {"model": "laya-auto"}})).predict(STATE, ALLOWED)
    assert proposal.action == "repeat" and proposal.confidence is None and proposal.model_version == "laya-auto"


@pytest.mark.asyncio
@pytest.mark.parametrize("status, code", [(429, "busy"), (400, "http_4xx"), (413, "http_4xx"), (422, "http_4xx"), (502, "http_5xx"), (503, "http_5xx"), (504, "http_5xx")])
async def test_controlled_http_failures_become_typed_failures_without_retry(status, code):
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(status, json={"error": "systemone_busy"}, headers={"Retry-After": "1"})

    proposal = await transport_with(handler).predict(STATE, ALLOWED)
    assert proposal.failure_code == code and proposal.action is None and proposal.confidence is None and proposal.model_version is None
    assert calls["n"] == 1


@pytest.mark.asyncio
async def test_malformed_oversized_and_network_errors_are_typed():
    malformed = await transport_with(lambda request: httpx.Response(200, content=b"not json")).predict(STATE, ALLOWED)
    assert malformed.failure_code == "malformed"
    missing = await transport_with(lambda request: httpx.Response(200, json={"usage": {}})).predict(STATE, ALLOWED)
    assert missing.failure_code == "malformed"
    oversized = await transport_with(lambda request: httpx.Response(200, content=b"x" * (MAX_BODY_BYTES + 1))).predict(STATE, ALLOWED)
    assert oversized.failure_code == "oversized"

    def boom(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    assert (await transport_with(boom).predict(STATE, ALLOWED)).failure_code == "network"


@pytest.mark.asyncio
async def test_token_is_optional_for_reviewed_lan_access_and_never_in_repr():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        return httpx.Response(200, json={"answers": {"next_action": "repeat"}, "usage": {}, "routing": {"model": "laya-auto"}})

    transport = transport_with(handler, token=None)
    await transport.predict(STATE, ALLOWED)
    assert seen["auth"] is None
    secret = transport_with(handler, token="SYNTHETIC_EDGE_TOKEN_7a1c")
    assert "SYNTHETIC_EDGE_TOKEN_7a1c" not in repr(secret) and "SYNTHETIC_EDGE_TOKEN_7a1c" not in str(secret)


def test_programming_errors_are_not_swallowed():
    from mental_math.policy.framework import FAILURE_TAXONOMY

    assert KeyError not in FAILURE_TAXONOMY and TypeError not in FAILURE_TAXONOMY


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [httpx.ProxyError("proxy refused CONNECT"), httpx.UnsupportedProtocol("no scheme"), httpx.RemoteProtocolError("truncated"), httpx.TooManyRedirects("loop")])
async def test_every_httpx_transport_error_is_a_typed_network_failure(error):
    def handler(request: httpx.Request) -> httpx.Response:
        raise error

    proposal = await transport_with(handler).predict(STATE, ALLOWED)
    assert proposal.failure_code == "network" and proposal.action is None


@pytest.mark.asyncio
async def test_over_long_answer_is_malformed_and_model_alias_is_bounded():
    long_action = "repeat_current_difficulty"
    proposal = await transport_with(lambda request: httpx.Response(200, json={"answers": {"next_action": long_action}, "usage": {}, "routing": {"model": "laya-auto"}})).predict(STATE, ALLOWED)
    assert proposal.failure_code == "malformed"
    proposal = await transport_with(lambda request: httpx.Response(200, json={"answers": {"next_action": {"choice": long_action, "probabilities": {long_action: 0.9}}}, "usage": {}, "routing": {"model": "laya-auto"}})).predict(STATE, ALLOWED)
    assert proposal.failure_code == "malformed"
    alias = "laya-" + "x" * 60
    proposal = await transport_with(lambda request: httpx.Response(200, json={"answers": {"next_action": "repeat"}, "usage": {}, "routing": {"model": alias}})).predict(STATE, ALLOWED)
    assert proposal.action == "repeat" and proposal.model_version == alias[:40]


def test_framework_url_requires_a_scheme(monkeypatch):
    from mental_math.config import Settings

    monkeypatch.setenv("MMATH_DATABASE_URL", "postgresql+psycopg://u:p@db/x")
    monkeypatch.setenv("MMATH_ORIGIN", "http://test")
    monkeypatch.setenv("MMATH_MODE", "lan-http")
    monkeypatch.setenv("MMATH_POLICY_MODE", "shadow")
    monkeypatch.setenv("MMATH_FRAMEWORK_URL", "framework.internal")
    with pytest.raises(RuntimeError, match="http"):
        Settings.from_env()
    monkeypatch.setenv("MMATH_FRAMEWORK_URL", "https://framework.internal")
    assert Settings.from_env().framework_url == "https://framework.internal"
