import os
from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Settings:
    database_url: str
    origin: str
    mode: str

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
        return cls(database_url, origin.rstrip("/"), mode)
