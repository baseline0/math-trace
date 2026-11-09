#!/usr/bin/env python3
"""Dockerfile standard: the minimum every fleet Dockerfile meets, checked before commit.

Standard-only, stdlib-only, so every repo can vendor this one file and run it with python3.

Every Dockerfile must:
  - pin its base image: a tag other than latest, or a digest;
  - declare its tier with LABEL fleet.role="service" | "job" | "dev";
  - run as a numeric non-root USER (named users cannot be checked by Kubernetes runAsNonRoot);
  - use an exec-form CMD or ENTRYPOINT (JSON array), so signals reach the process;
  - sit beside a .dockerignore that excludes .env files and .git.

A Dockerfile with fleet.role="service" must also:
  - run as uid 10001;
  - EXPOSE 8080;
  - declare a HEALTHCHECK that calls /healthz;
  - set FLEET_DATA_DIR=/data.

Usage: python3 scripts/dockerfile_check.py [PATH ...]
With no paths it checks every Dockerfile tracked by git, or found on disk if git is unavailable.
Exit 0 when every file complies; 1 with one line per problem otherwise.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SERVICE_UID = "10001"
SERVICE_PORT = "8080"
ROLES = frozenset({"service", "job", "dev"})


def logical_lines(text: str) -> list[str]:
    """Instructions with comments removed and backslash continuations joined."""
    lines: list[str] = []
    pending = ""
    for raw in text.splitlines():
        stripped = raw.strip()
        if not pending and (not stripped or stripped.startswith("#")):
            continue
        if stripped.endswith("\\"):
            pending += stripped[:-1] + " "
            continue
        lines.append((pending + stripped).strip())
        pending = ""
    if pending.strip():
        lines.append(pending.strip())
    return lines


def _instructions(lines: list[str], keyword: str) -> list[str]:
    prefix = keyword.upper() + " "
    return [line[len(prefix) :].strip() for line in lines if line.upper().startswith(prefix)]


def _last_user(lines: list[str]) -> str | None:
    users = _instructions(lines, "USER")
    return users[-1] if users else None


def _exec_form(value: str) -> bool:
    try:
        parsed = json.loads(value)
    except (ValueError, TypeError):
        return False
    return isinstance(parsed, list) and bool(parsed) and all(isinstance(item, str) for item in parsed)


def _labels(lines: list[str]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for body in _instructions(lines, "LABEL"):
        for key, value in re.findall(r'([\w.\-]+)=("(?:[^"\\]|\\.)*"|\S+)', body):
            labels[key] = value.strip('"')
    return labels


def _env(lines: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for body in _instructions(lines, "ENV"):
        for key, value in re.findall(r'([\w.\-]+)=("(?:[^"\\]|\\.)*"|\S+)', body):
            values[key] = value.strip('"')
    return values


def check(path: Path) -> list[str]:
    """The problems in one Dockerfile, or an empty list when it complies."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return [f"cannot read: {error}"]
    lines = logical_lines(text)
    problems: list[str] = []

    froms = _instructions(lines, "FROM")
    if not froms:
        problems.append("no FROM instruction")
    for base in froms:
        image = base.split()[0]
        if "@" in image:
            continue  # a digest pins the image exactly
        name = image.rsplit("/", 1)[-1]
        tag = name.split(":", 1)[1] if ":" in name else ""
        if not tag or tag == "latest":
            problems.append(f"base image {image!r} is not pinned: use a tag other than latest, or a digest")

    labels = _labels(lines)
    role = labels.get("fleet.role")
    if role not in ROLES:
        problems.append('LABEL fleet.role must be "service", "job" or "dev"')

    user = _last_user(lines)
    uid = user.split(":")[0] if user else None
    if user is None:
        problems.append("no USER instruction: the container would run as root")
    elif uid is None or not uid.isdigit():
        problems.append(f"USER {user!r} is not a numeric uid (Kubernetes runAsNonRoot needs one)")
    elif uid == "0":
        problems.append("USER 0 runs as root")

    entry = _instructions(lines, "CMD") + _instructions(lines, "ENTRYPOINT")
    if not entry:
        problems.append("no CMD or ENTRYPOINT")
    elif not all(_exec_form(value) for value in entry):
        problems.append("CMD or ENTRYPOINT is not in exec (JSON array) form")

    if role == "service":
        if uid != SERVICE_UID:
            problems.append(f"service image must run as uid {SERVICE_UID}, not {uid}")
        if not any(p == SERVICE_PORT or p.startswith(SERVICE_PORT + "/") for p in _instructions(lines, "EXPOSE")):
            problems.append(f"service image must EXPOSE {SERVICE_PORT}")
        healthchecks = [h for h in _instructions(lines, "HEALTHCHECK") if "/healthz" in h]
        if not healthchecks:
            problems.append("service image must declare a HEALTHCHECK that calls /healthz")
        if _env(lines).get("FLEET_DATA_DIR") != "/data":
            problems.append("service image must set FLEET_DATA_DIR=/data")

    ignore = path.parent / ".dockerignore"
    if not ignore.exists():
        problems.append(".dockerignore is missing beside the Dockerfile")
    else:
        rules = [line.strip() for line in ignore.read_text(encoding="utf-8").splitlines()]
        if not any(rule.lstrip("/").startswith(("**/.env", ".env")) for rule in rules):
            problems.append(".dockerignore does not exclude .env files")
        if not any(rule.lstrip("/").startswith((".git", "**/.git")) for rule in rules):
            problems.append(".dockerignore does not exclude .git")
    return problems


def discover(root: Path) -> list[Path]:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True, timeout=30
        ).stdout
        names = [line for line in out.splitlines() if line]
    except (OSError, subprocess.SubprocessError):
        names = [str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]
    return sorted(
        root / name for name in names if Path(name).name == "Dockerfile" or Path(name).name.startswith("Dockerfile.")
    )


def main(argv: list[str]) -> int:
    root = Path.cwd()
    paths = [Path(arg) for arg in argv] if argv else discover(root)
    if not paths:
        print("dockerfile-check: no Dockerfile in this repo")
        return 0
    failures = 0
    for path in paths:
        for problem in check(path):
            failures += 1
            print(f"{path}: {problem}")
    if failures:
        print(f"dockerfile-check: {failures} problem(s); see the standard in scripts/dockerfile_check.py")
        return 1
    print(f"dockerfile-check: {len(paths)} Dockerfile(s) comply")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
