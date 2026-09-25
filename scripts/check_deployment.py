"""Deployment checks without touching any real deployment.

Default: validate the public and LAN compose renderings with the committed synthetic env files.
--isolated: additionally bring up a uniquely named compose project (LAN mode plus deploy/compose.check.yaml,
which adds a project-scoped PostgreSQL that publishes no port), prove readiness through the edge, register an
account, restart only the API and confirm the session survives, then remove exactly the resources this run
created. It never attaches to an existing database or volume.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def compose_cli() -> list[str]:
    for candidate in (["docker", "compose"], ["docker-compose"]):
        try:
            subprocess.run([*candidate, "version"], check=True, capture_output=True)
            return candidate
        except (OSError, subprocess.CalledProcessError):
            continue
    raise SystemExit("neither `docker compose` nor `docker-compose` is available")


def render(cli: list[str], env_file: str, overlay: str, project: str | None = None) -> dict:
    args = [*cli, "--env-file", f"deploy/{env_file}", "-f", "compose.yaml", "-f", f"deploy/{overlay}"]
    if project:
        args += ["-p", project]
    subprocess.run([*args, "config", "--quiet"], check=True, cwd=REPO)
    rendered = subprocess.run([*args, "config", "--format", "json"], check=True, cwd=REPO, capture_output=True, text=True).stdout
    return json.loads(rendered)


def check_rendering(cli: list[str]) -> None:
    public = render(cli, "test.public.env", "compose.public.yaml")
    lan = render(cli, "test.lan.env", "compose.lan-http.yaml")
    for name, service in public["services"].items():
        if service.get("ports"):
            raise SystemExit(f"public mode must not publish ports: {name}")
    if public["services"]["api"]["environment"]["MMATH_MODE"] != "public" or not public["services"]["api"]["environment"]["MMATH_ORIGIN"].startswith("https://"):
        raise SystemExit("public mode must use an HTTPS origin")
    edge = next(net for net in public["networks"].values() if net.get("external"))
    if edge["name"] != "mmath-check-edge":
        raise SystemExit("public overlay must attach to the configured external network")
    if lan["services"]["api"]["environment"]["MMATH_MODE"] != "lan-http" or lan["services"]["web"]["ports"][0]["published"] != "18080":
        raise SystemExit("LAN mode must publish the edge only on the configured loopback port")
    if "postgres" in public["services"] or "postgres" in lan["services"]:
        raise SystemExit("the database is external and must not be part of the project")
    print("compose renderings: ok (public: no ports, external edge network; lan: loopback edge only)")


def fetch(url: str, opener, data: bytes | None = None, headers: dict | None = None):
    request = urllib.request.Request(url, data=data, headers=headers or {}, method="POST" if data else "GET")
    with opener.open(request, timeout=10) as response:
        return response.status, json.loads(response.read() or b"null")


def isolated(cli: list[str]) -> None:
    project = f"mmath-check-{int(time.time())}"
    existing = subprocess.run(["docker", "ps", "-a", "--filter", f"name={project}", "--format", "{{.Names}}"], capture_output=True, text=True, check=True).stdout.strip()
    if existing:
        raise SystemExit(f"refusing to reuse existing resources for {project}")
    base = [*cli, "--env-file", "deploy/test.lan.env", "-f", "compose.yaml", "-f", "deploy/compose.lan-http.yaml", "-f", "deploy/compose.check.yaml", "-p", project]
    origin = "http://127.0.0.1:18080"
    try:
        try:
            subprocess.run([*base, "up", "-d", "--build", "--wait"], check=True, cwd=REPO)
        except subprocess.CalledProcessError:
            subprocess.run([*base, "logs", "--tail", "40", "migrate", "api", "web"], cwd=REPO)
            raise
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
        status, session = fetch(f"{origin}/api/v1/auth/session", opener)
        assert status == 200 and session["email"] is None
        email = f"drill-{int(time.time())}@example.com"
        headers = {"Origin": origin, "X-CSRF-Token": session["csrf_token"], "Content-Type": "application/json"}
        status, registered = fetch(f"{origin}/api/v1/auth/register", opener, json.dumps({"email": email, "password": "correct horse battery staple"}).encode(), headers)
        assert status == 201 and registered["email"] == email
        subprocess.run([*base, "restart", "api"], check=True, cwd=REPO)
        deadline = time.time() + 60
        while True:
            try:
                status, after = fetch(f"{origin}/api/v1/auth/session", opener)
                if status == 200 and after["email"] == email:
                    break
            except (urllib.error.URLError, AssertionError):
                pass
            if time.time() > deadline:
                raise SystemExit("session did not survive the API restart")
            time.sleep(2)
        with urllib.request.urlopen(f"{origin}/health/ready", timeout=5) as response:
            body = response.read().decode(errors="ignore")
            if "application/json" in response.headers.get("content-type", "") or '"database"' in body:
                raise SystemExit("internal health path must not be reachable through the edge")
        print(f"isolated deployment {project}: ok (readiness via edge, account survives API restart, internal paths hidden)")
    finally:
        subprocess.run([*base, "down", "--volumes", "--remove-orphans"], cwd=REPO)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--isolated", action="store_true")
    args = parser.parse_args()
    cli = compose_cli()
    os.environ.setdefault("DOCKER_BUILDKIT", "1")
    check_rendering(cli)
    if args.isolated:
        isolated(cli)


if __name__ == "__main__":
    sys.exit(main())
