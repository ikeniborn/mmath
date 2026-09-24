import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
os.environ.setdefault("MMATH_DATABASE_URL", "postgresql+psycopg://dummy:dummy@127.0.0.1/dummy")
os.environ.setdefault("MMATH_ORIGIN", "http://127.0.0.1")
os.environ.setdefault("MMATH_MODE", "lan-http")

from mental_math.main import create_app


target = Path("frontend/src/api-schema.json")
target.write_text(json.dumps(create_app().openapi(), ensure_ascii=False, indent=2, sort_keys=True) + "\n")
