import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    origin: str
    mode: str

    @classmethod
    def from_env(cls) -> "Settings":
        database_url = os.environ.get("MMATH_DATABASE_URL")
        origin = os.environ.get("MMATH_ORIGIN")
        mode = os.environ.get("MMATH_MODE")
        if not database_url or not origin or mode not in {"public", "lan-http"}:
            raise RuntimeError("MMATH_DATABASE_URL, MMATH_ORIGIN and MMATH_MODE are required")
        if mode == "public" and not origin.startswith("https://"):
            raise RuntimeError("Public mode requires an HTTPS origin")
        if mode == "lan-http" and not origin.startswith("http://"):
            raise RuntimeError("LAN mode requires an HTTP origin")
        return cls(database_url, origin.rstrip("/"), mode)
