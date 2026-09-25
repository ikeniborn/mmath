import os
import subprocess
import sys
from pathlib import Path

from tests.conftest import TEST_DATABASE_URL

BACKEND = Path(__file__).resolve().parents[2]


def test_alembic_accepts_a_percent_encoded_password():
    """%6d decodes to 'm', so the DSN is valid; ConfigParser must not see the percent sign."""
    encoded = TEST_DATABASE_URL.replace("mmath_test:mmath_test@", "mmath_test:%6dmath_test@")
    assert "%6d" in encoded
    env = {**os.environ, "MMATH_DATABASE_URL": encoded}
    result = subprocess.run([sys.executable, "-m", "alembic", "-c", str(BACKEND / "alembic.ini"), "current"], cwd=BACKEND, env=env, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr
    assert "(head)" in result.stdout
