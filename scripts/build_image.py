"""Build the math-trace container image with a pinned fleet-base snapshot (ADR-021, canonical in fleet-coordination docs/adr/ADR-021-SIBLING-PATH-SOURCES.md; SIB-5).

The snapshot is exported per build from one fleet-base commit and is never tracked (.sibling/ is ignored). The commit
must be on origin/main, or the build refuses, so an image never records a commit nobody can fetch.

Environment:
    FLEET_BASE      the canonical fleet-base git checkout (default: ~/projects/fleet-base; the workspace sibling has no .git)
    FLEET_BASE_SHA  the fleet-base commit to pin (default: origin/main of FLEET_BASE)
    IMAGE           the image tag (default: math-trace:local)
    NO_CACHE        set to 1 to pass --no-cache to docker build
"""

from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=check)


def main() -> int:
    fleet_base = Path(os.environ.get("FLEET_BASE", Path.home() / "projects" / "fleet-base"))
    image = os.environ.get("IMAGE", "math-trace:local")
    _git(fleet_base, "fetch", "-q", "origin")
    sha = os.environ.get("FLEET_BASE_SHA") or _git(fleet_base, "rev-parse", "origin/main").stdout.strip()

    on_origin = _git(fleet_base, "merge-base", "--is-ancestor", sha, "origin/main", check=False)
    if on_origin.returncode != 0:
        print(f"refuse: fleet-base {sha} is not on origin/main (SIB-5). Push fleet-base, then build.", file=sys.stderr)
        return 1

    dest = REPO / ".sibling" / "fleet-base"
    shutil.rmtree(REPO / ".sibling", ignore_errors=True)
    dest.mkdir(parents=True)
    archive = subprocess.run(["git", "-C", str(fleet_base), "archive", sha], capture_output=True, check=True)
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
        tar.extractall(dest, filter="data")

    no_cache = ["--no-cache"] if os.environ.get("NO_CACHE") == "1" else []
    subprocess.run(
        ["docker", "build", *no_cache, "--build-arg", f"FLEET_BASE_SHA={sha}", "-t", image, str(REPO)], check=True
    )
    print(f"built {image} from fleet-base {sha}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
