"""Fail when the built frontend bundle contains anything that looks like a secret or server-only value."""

import gzip
import re
import sys
from pathlib import Path

DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"
BUDGET_GZIP_BYTES = 160 * 1024  # JS+CSS of one build, gzip; the early numeracy SVG set must fit in it
MARKERS = [re.compile(pattern) for pattern in (r"postgresql(\+\w+)?://", r"MMATH_DATABASE_URL", r"BEGIN (RSA |EC )?PRIVATE KEY", r"Bearer [A-Za-z0-9._-]{16,}", r"mmath_test:mmath_test")]


def main(extra: list[str]) -> int:
    if not DIST.exists():
        print("frontend/dist is missing: run the build first", file=sys.stderr)
        return 2
    patterns = MARKERS + [re.compile(re.escape(marker)) for marker in extra]
    findings = []
    for path in DIST.rglob("*"):
        if path.is_file() and path.suffix in {".js", ".css", ".html", ".json", ".map"}:
            text = path.read_text(errors="ignore")
            findings += [(path.relative_to(DIST), pattern.pattern) for pattern in patterns if pattern.search(text)]
    compressed = sum(len(gzip.compress(path.read_bytes())) for path in (DIST / "assets").glob("*") if path.suffix in {".js", ".css"})
    print(f"bundle gzip: {compressed} bytes (budget {BUDGET_GZIP_BYTES})")
    if compressed > BUDGET_GZIP_BYTES:
        findings.append((Path("assets"), f"bundle gzip {compressed} exceeds {BUDGET_GZIP_BYTES}"))
    for path, pattern in findings:
        print(f"{path}: matches {pattern}", file=sys.stderr)
    print("bundled assets: ok" if not findings else f"bundled assets: {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
