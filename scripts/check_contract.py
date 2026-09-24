import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
os.environ.setdefault("MMATH_DATABASE_URL", "postgresql+psycopg://dummy:dummy@127.0.0.1/dummy")
os.environ.setdefault("MMATH_ORIGIN", "http://127.0.0.1")
os.environ.setdefault("MMATH_MODE", "lan-http")

from mental_math.main import create_app


actual = json.dumps(create_app().openapi(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
schema_path = Path("frontend/src/api-schema.json")
if schema_path.read_text() != actual:
    raise SystemExit("OpenAPI schema drift: regenerate with scripts/export_openapi.py")

with tempfile.TemporaryDirectory() as directory:
    generated = Path(directory) / "api-types.ts"
    subprocess.run(["frontend/node_modules/.bin/openapi-typescript", str(schema_path), "-o", str(generated)], check=True)
    if generated.read_text() != Path("frontend/src/api-types.ts").read_text():
        raise SystemExit("TypeScript contract drift: regenerate api-types.ts")
