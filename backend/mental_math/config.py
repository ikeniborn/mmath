import os
from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Settings:
    database_url: str
    origin: str
    mode: str
    policy_mode: str = "rules"
    framework_url: str | None = None
    framework_model: str = "laya-auto"
    framework_token_file: str | None = None
    confidence_threshold: float | None = None
    rollout_authorization: str | None = None

    @property
    def allowed_hosts(self) -> tuple[str, ...]:
        """Public host from the origin plus the internal names used by Caddy and container health checks."""
        return (urlsplit(self.origin).hostname or "", "api", "localhost", "127.0.0.1")

    @classmethod
    def from_env(cls) -> "Settings":
        database_url = os.environ.get("MMATH_DATABASE_URL")
        origin = os.environ.get("MMATH_ORIGIN")
        mode = os.environ.get("MMATH_MODE")
        if not database_url or not origin or mode not in {"public", "lan-http"}:
            raise RuntimeError("MMATH_DATABASE_URL, MMATH_ORIGIN and MMATH_MODE (public | lan-http) are required")
        if mode == "public" and not origin.startswith("https://"):
            raise RuntimeError("Public mode requires an HTTPS origin")
        if mode == "lan-http" and not origin.startswith("http://"):
            raise RuntimeError("LAN mode requires an explicit HTTP origin")
        policy_mode = os.environ.get("MMATH_POLICY_MODE", "rules")
        if policy_mode not in {"rules", "shadow", "active"}:
            raise RuntimeError("MMATH_POLICY_MODE must be rules, shadow or active")
        framework_url = os.environ.get("MMATH_FRAMEWORK_URL") or None
        if policy_mode in {"shadow", "active"} and not framework_url:
            raise RuntimeError("MMATH_FRAMEWORK_URL is required for shadow and active policy modes")
        threshold: float | None = None
        authorization: str | None = None
        if policy_mode == "active":
            raw = os.environ.get("MMATH_ACTIVE_CONFIDENCE_THRESHOLD")
            if not raw:
                raise RuntimeError("MMATH_ACTIVE_CONFIDENCE_THRESHOLD is required for active policy mode; the spec's 0.8 is a proposal, not a default")
            threshold = float(raw)
            if not 0.5 <= threshold <= 1.0:
                raise RuntimeError("MMATH_ACTIVE_CONFIDENCE_THRESHOLD must be between 0.5 and 1.0")
            authorization = os.environ.get("MMATH_ACTIVE_ROLLOUT_AUTHORIZATION") or None
            if not authorization:
                raise RuntimeError("MMATH_ACTIVE_ROLLOUT_AUTHORIZATION must name the recorded rollout decision for active policy mode")
        return cls(database_url, origin.rstrip("/"), mode, policy_mode, framework_url, os.environ.get("MMATH_FRAMEWORK_MODEL", "laya-auto"), os.environ.get("MMATH_FRAMEWORK_TOKEN_FILE") or None, threshold, authorization)
