"""Health check for a Lean/Mathlib project: is this machine able to build and check it, reproducibly?

Each check answers one question and records what it found, so a failure says what is missing. Required checks
decide the exit status. Informational checks report and never fail the run.

Checks, in order:
1. elan:       the version manager is on PATH or under ELAN_HOME.
2. toolchain:  the project's lean-toolchain is installed locally (no download happens here).
3. bundled:    the toolchain ships the four binaries the Comparator needs (leanexport, leanchecker, nanoda_bin, con-ron).
4. manifest:   lake-manifest.json pins Mathlib to a full 40-character commit.
5. sandbox:    bubblewrap can start a sandbox with its own /proc. A container without security.nesting fails here.
6. cache:      the Mathlib binary cache is reachable (informational: an offline run skips it on purpose).

Usage:
    uv run python scripts/lean_health.py --project ~/.cache/math-trace/palomar-sidorenko --report health.json
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

import httpx
import typer

app = typer.Typer(help="Check that this machine can build and verify a Lean/Mathlib project.", add_completion=False)

COMPARATOR_TOOLS: tuple[str, ...] = ("leanexport", "leanchecker", "nanoda_bin", "con-ron")
MATHLIB_CACHE = "https://cache.mathlib.org/"
FULL_COMMIT = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class Check:
    name: str
    required: bool
    passed: bool
    detail: str


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False, timeout=120)


def elan_home() -> Path:
    return Path(os.environ.get("ELAN_HOME", Path.home() / ".elan"))


def check_elan(which: str | None) -> Check:
    """Required: elan must run. Looks on PATH first, then under ELAN_HOME/bin."""
    binary = which or str(elan_home() / "bin" / "elan")
    if not shutil.which(binary) and not Path(binary).is_file():
        return Check("elan", True, False, f"not found on PATH or at {binary}; run `just install-elan`")
    done = run([binary, "--version"])
    if done.returncode != 0:
        return Check("elan", True, False, f"{binary} --version exited {done.returncode}")
    return Check("elan", True, True, done.stdout.strip())


def project_toolchain(project: Path) -> str | None:
    file = project / "lean-toolchain"
    return file.read_text(encoding="utf-8").strip() if file.is_file() else None


def check_toolchain(project: Path, elan: str) -> Check:
    """Required: the pinned toolchain is installed. Listing toolchains never downloads one."""
    pinned = project_toolchain(project)
    if pinned is None:
        return Check("toolchain", True, False, f"no lean-toolchain file in {project}")
    done = run([elan, "toolchain", "list"])
    installed = {line.split()[0] for line in done.stdout.splitlines() if line.strip()}
    if pinned in installed:
        return Check("toolchain", True, True, f"{pinned} is installed")
    return Check("toolchain", True, False, f"{pinned} is not installed; elan fetches it on first use from the project")


def check_bundled_tools(project: Path, elan: str) -> Check:
    """Required: the pinned toolchain bundles the binaries the Comparator uses. The script refuses without them."""
    done = run([elan, "run", project_toolchain(project) or "stable", "lean", "--print-prefix"], cwd=project)
    if done.returncode != 0:
        return Check("bundled", True, False, f"could not find the toolchain prefix: {done.stderr.strip()[:200]}")
    bin_dir = Path(done.stdout.strip()) / "bin"
    missing = [tool for tool in COMPARATOR_TOOLS if not (bin_dir / tool).is_file()]
    if missing:
        return Check("bundled", True, False, f"toolchain bundles no {', '.join(missing)} in {bin_dir}")
    return Check("bundled", True, True, f"all {len(COMPARATOR_TOOLS)} Comparator tools in {bin_dir}")


def mathlib_rev(manifest: dict) -> str | None:
    for package in manifest.get("packages", []):
        if package.get("name") == "mathlib":
            return str(package.get("rev") or "")
    return None


def check_manifest(project: Path) -> Check:
    """Required: Mathlib is pinned to a full commit, so the same build can be fetched again."""
    file = project / "lake-manifest.json"
    if not file.is_file():
        return Check("manifest", True, False, f"no lake-manifest.json in {project}")
    try:
        manifest = json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return Check("manifest", True, False, f"lake-manifest.json is not valid JSON: {error}")
    rev = mathlib_rev(manifest)
    if rev is None:
        return Check("manifest", True, False, "lake-manifest.json does not pin mathlib")
    if not FULL_COMMIT.match(rev):
        return Check("manifest", True, False, f"mathlib is pinned to {rev!r}, not a full 40-character commit")
    return Check("manifest", True, True, f"mathlib pinned to {rev}")


def check_sandbox() -> Check:
    """Required: bubblewrap can make a sandbox with its own /proc, as the Comparator needs."""
    if not shutil.which("bwrap"):
        return Check("sandbox", True, False, "bwrap is not installed; `sudo apt install bubblewrap`")
    done = run(["bwrap", "--unshare-user", "--ro-bind", "/", "/", "--proc", "/proc", "--dev", "/dev", "true"])
    if done.returncode != 0:
        return Check("sandbox", True, False, f"bwrap cannot start a sandbox: {done.stderr.strip()[:200]}")
    return Check("sandbox", True, True, "bwrap starts a sandbox with its own /proc")


def check_cache(client: httpx.Client) -> Check:
    """Informational: the Mathlib cache is reachable. An offline run does not need it, so this never fails a run."""
    try:
        response = client.get(MATHLIB_CACHE, timeout=15.0)
    except httpx.HTTPError as error:
        return Check(
            "cache", False, False, f"not reachable ({type(error).__name__}); fetch during provisioning instead"
        )
    return Check("cache", False, response.status_code < 500, f"{MATHLIB_CACHE} answered {response.status_code}")


def gather(project: Path, which: str | None, with_cache: bool) -> list[Check]:
    elan_check = check_elan(which)
    checks = [elan_check]
    elan = which or str(elan_home() / "bin" / "elan")
    if elan_check.passed:
        toolchain = check_toolchain(project, elan)
        checks.append(toolchain)
        # Only after the toolchain check passes: `elan run` would download a missing toolchain, and a health check must not change the machine.
        if toolchain.passed:
            checks.append(check_bundled_tools(project, elan))
        else:
            checks.append(Check("bundled", True, False, "not checked: the pinned toolchain is not installed"))
    checks.append(check_manifest(project))
    checks.append(check_sandbox())
    if with_cache:
        with httpx.Client(headers={"User-Agent": "math-trace-lean-health"}) as client:
            checks.append(check_cache(client))
    return checks


def verdict(checks: list[Check]) -> bool:
    """True when every required check passed. Informational checks do not count."""
    return all(c.passed for c in checks if c.required)


@app.command()
def main(
    project: Path = typer.Option(..., "--project", help="The Lean project to check (the folder with lean-toolchain)."),
    report: Path = typer.Option(..., "--report", help="Where to write the JSON report."),
    elan: str = typer.Option(
        ..., "--elan", help="The elan binary to use; pass an empty string to look under ELAN_HOME."
    ),
    cache: bool = typer.Option(..., "--cache", help="Also check that the Mathlib cache is reachable."),
) -> None:
    """Run the checks, write the JSON report, and exit 1 when a required check fails."""
    project = project.expanduser().resolve()
    checks = gather(project, elan or None, cache)
    ok = verdict(checks)
    payload = {"project": str(project), "passed": ok, "checks": [asdict(c) for c in checks]}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for check in checks:
        mark = "ok  " if check.passed else ("FAIL" if check.required else "info")
        typer.echo(f"{mark} {check.name:<10} {check.detail}")
    typer.echo("lean health: " + ("passed" if ok else "FAILED") + f" (report: {report})")
    if not ok:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
