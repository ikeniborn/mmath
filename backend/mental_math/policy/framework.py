"""Framework System One transport for typed decisions.

Contract (framework runbook laya-systemone-model-usage, 2026-09-25): POST {base}/v1/systemone with
{"model": alias, "state": {...}, "questions": {name: {"type": "choice", "criteria": [...]}}}; response
{"answers": {name: answer}, "usage": {...}, "routing": {"model": alias}}; 2 MiB body limits; concurrent
inference answers 429 systemone_busy (never retried here); controlled failures 400/413/422/502/503/504.
The bearer token is read from a mounted file by the caller; the request carries no cookies or identity.
"""

from dataclasses import asdict

import httpx

from mental_math.policy.types import PolicyProposal, PolicyState

MAX_BODY_BYTES = 2 * 1024 * 1024
QUESTION = "next_action"


class TransportFailure(Exception):
    """A failure from the reviewed taxonomy; anything else is a programming error and propagates."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


FAILURE_TAXONOMY: tuple[type[BaseException], ...] = (TransportFailure, httpx.TimeoutException, httpx.NetworkError, httpx.ProtocolError, httpx.DecodingError, httpx.TooManyRedirects)


class FrameworkTransport:
    def __init__(self, base_url: str, model: str, token: str | None, client: httpx.AsyncClient) -> None:
        self._base = base_url.rstrip("/")
        self._model = model
        self._token = token
        self._client = client

    def __repr__(self) -> str:  # never reveal the token
        return f"FrameworkTransport(base_url={self._base!r}, model={self._model!r}, token={'set' if self._token else 'none'})"

    __str__ = __repr__

    async def predict(self, state: PolicyState, allowed_actions: tuple[str, ...]) -> PolicyProposal:
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        body = {"model": self._model, "state": asdict(state), "questions": {QUESTION: {"type": "choice", "criteria": list(allowed_actions)}}}
        try:
            response = await self._client.post(f"{self._base}/v1/systemone", json=body, headers=headers)
        except httpx.TimeoutException:
            return PolicyProposal.failure("timeout")
        except (httpx.NetworkError, httpx.ProtocolError, httpx.TooManyRedirects):
            return PolicyProposal.failure("network")
        if response.status_code == 429:
            return PolicyProposal.failure("busy")
        if 400 <= response.status_code < 500:
            return PolicyProposal.failure("http_4xx")
        if response.status_code >= 500:
            return PolicyProposal.failure("http_5xx")
        if len(response.content) > MAX_BODY_BYTES:
            return PolicyProposal.failure("oversized")
        try:
            payload = response.json()
            answer = payload["answers"][QUESTION]
            routing_model = payload.get("routing", {}).get("model")
        except (ValueError, KeyError, TypeError, AttributeError):
            return PolicyProposal.failure("malformed")
        model_version = routing_model if isinstance(routing_model, str) else None
        if isinstance(answer, str):
            return PolicyProposal(action=answer, confidence=None, provider="framework", model_version=model_version)
        if isinstance(answer, dict):
            choice = answer.get("choice", answer.get("value"))
            if not isinstance(choice, str):
                return PolicyProposal.failure("malformed")
            probabilities = answer.get("probabilities")
            confidence = probabilities.get(choice) if isinstance(probabilities, dict) and isinstance(probabilities.get(choice), (int, float)) else None
            return PolicyProposal(action=choice, confidence=float(confidence) if confidence is not None else None, provider="framework", model_version=model_version)
        return PolicyProposal.failure("malformed")


def build_transport(base_url: str, model: str, token_file: str | None) -> FrameworkTransport:
    token = None
    if token_file:
        with open(token_file, encoding="utf-8") as handle:
            token = handle.read().strip() or None
    client = httpx.AsyncClient(timeout=httpx.Timeout(connect=0.2, read=0.3, write=0.2, pool=0.2))
    return FrameworkTransport(base_url=base_url, model=model, token=token, client=client)
