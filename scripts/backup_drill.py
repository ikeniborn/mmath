"""Synthetic backup/restore drill against a separate restore database.

Dumps the source database with pg_dump inside the given PostgreSQL container, restores it into a
freshly created database on the same server, and compares account ids, attempt count and the current
problem of every active session. Refuses to run when the restore database already exists.
"""

import argparse
import json
import subprocess
import sys

QUERY = """
SELECT json_build_object(
  'account_ids', (SELECT coalesce(json_agg(id ORDER BY id), '[]'::json) FROM accounts),
  'attempt_count', (SELECT count(*) FROM attempts),
  'current_problem_ids', (SELECT coalesce(json_agg(current_problem_id ORDER BY id), '[]'::json) FROM learning_sessions WHERE state = 'active')
)::text
"""


def psql(container: str, user: str, database: str, sql: str, *flags: str) -> str:
    return subprocess.run(["docker", "exec", container, "psql", "-U", user, "-d", database, "-At", *flags, "-c", sql], check=True, capture_output=True, text=True).stdout.strip()


def state(container: str, user: str, database: str) -> dict:
    return json.loads(psql(container, user, database, QUERY))


def assert_restored_state(before: dict, after: dict) -> None:
    assert after["account_ids"] == before["account_ids"], "account ids differ"
    assert after["attempt_count"] == before["attempt_count"], "attempt count differs"
    assert after["current_problem_ids"] == before["current_problem_ids"], "resumed problem ids differ"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--container", required=True, help="PostgreSQL container that holds pg_dump/psql matching the server")
    parser.add_argument("--user", required=True)
    parser.add_argument("--source", required=True, help="source database name")
    parser.add_argument("--restore", required=True, help="new database name to restore into; must not exist")
    parser.add_argument("--keep", action="store_true", help="keep the restore database after the comparison")
    args = parser.parse_args()
    if args.restore == args.source:
        raise SystemExit("restore database must differ from the source")
    if psql(args.container, args.user, "postgres", f"SELECT 1 FROM pg_database WHERE datname = '{args.restore}'"):
        raise SystemExit(f"restore database {args.restore} already exists; choose a fresh name")
    before = state(args.container, args.user, args.source)
    dump = subprocess.run(["docker", "exec", args.container, "pg_dump", "-U", args.user, "-d", args.source, "--no-owner", "--no-acl"], check=True, capture_output=True).stdout
    psql(args.container, args.user, "postgres", f'CREATE DATABASE "{args.restore}"')
    try:
        subprocess.run(["docker", "exec", "-i", args.container, "psql", "-U", args.user, "-d", args.restore, "-q", "-v", "ON_ERROR_STOP=1"], input=dump, check=True, capture_output=True)
        after = state(args.container, args.user, args.restore)
        assert_restored_state(before, after)
        print(f"backup drill: ok ({len(before['account_ids'])} accounts, {before['attempt_count']} attempts, {len(before['current_problem_ids'])} active sessions match; dump {len(dump)} bytes)")
        return 0
    finally:
        if not args.keep:
            psql(args.container, args.user, "postgres", f'DROP DATABASE "{args.restore}"')


if __name__ == "__main__":
    sys.exit(main())
