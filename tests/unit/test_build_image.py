"""The image build must refuse an unpublished fleet-base commit and pin the one it exports. Git and Docker are stubbed."""

from __future__ import annotations

import importlib.util
import io
import re
import subprocess
import sys
import tarfile
from pathlib import Path
from types import ModuleType

import pytest

from math_trace.constants import REPO_ROOT

PINNED_SHA = "a" * 40


@pytest.fixture
def build_image() -> ModuleType:
    script = REPO_ROOT / "scripts" / "build_image.py"
    spec = importlib.util.spec_from_file_location("build_image", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def fake_repo(tmp_path: Path, build_image: ModuleType, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the build at a scratch checkout so the snapshot never lands in the real repo."""
    repo = tmp_path / "math-trace"
    repo.mkdir()
    monkeypatch.setattr(build_image, "REPO", repo)
    monkeypatch.setenv("FLEET_BASE", str(tmp_path / "fleet-base"))
    monkeypatch.setenv("FLEET_BASE_SHA", PINNED_SHA)
    return repo


def _stub_git(monkeypatch: pytest.MonkeyPatch, build_image: ModuleType, on_origin: bool) -> list[tuple[str, ...]]:
    """Stub `_git`: fetch and rev-parse succeed; merge-base reports whether the pinned SHA is on origin/main."""
    calls: list[tuple[str, ...]] = []

    def fake_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        calls.append(args)
        returncode = 0 if (args[0] != "merge-base" or on_origin) else 1
        stdout = PINNED_SHA if args[0] == "rev-parse" else ""
        return subprocess.CompletedProcess(args, returncode, stdout=stdout, stderr="")

    monkeypatch.setattr(build_image, "_git", fake_git)
    return calls


def test_a_fleet_base_commit_not_on_origin_main_is_refused_before_any_build(
    build_image: ModuleType,
    fake_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A snapshot the registry cannot reproduce must never be built, so the refusal happens before export or docker."""
    _stub_git(monkeypatch, build_image, on_origin=False)
    ran: list[list[str]] = []
    monkeypatch.setattr(subprocess, "run", lambda argv, **kw: ran.append(argv))

    assert build_image.main() == 1

    assert ran == [], "no archive export or docker build may run for an unpublished fleet-base commit"
    assert not (fake_repo / ".sibling").exists()
    assert "not on origin/main" in capsys.readouterr().err


def test_the_build_exports_and_pins_the_sha_it_checked(
    build_image: ModuleType,
    fake_repo: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The snapshot exported and the docker build argument must be the same commit that passed the origin check."""
    _stub_git(monkeypatch, build_image, on_origin=True)
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w") as tar:
        payload = b"[project]\nname = 'fleet-base'\n"
        info = tarfile.TarInfo("pyproject.toml")
        info.size = len(payload)
        tar.addfile(info, io.BytesIO(payload))
    ran: list[tuple[list[str], bool]] = []

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        ran.append((argv, bool(kwargs.get("capture_output"))))
        stdout = archive.getvalue() if argv[:2] == ["git", "-C"] and "archive" in argv else b""
        return subprocess.CompletedProcess(argv, 0, stdout=stdout, stderr=b"")

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert build_image.main() == 0

    docker = next(argv for argv, _ in ran if argv[:2] == ["docker", "build"])
    assert f"FLEET_BASE_SHA={PINNED_SHA}" in docker
    assert (fake_repo / ".sibling" / "fleet-base" / "pyproject.toml").is_file()


def test_the_sibling_snapshot_is_ignored_by_git() -> None:
    """The exported fleet-base snapshot is a build input, never a tracked file, so its directory is git-ignored."""
    ignored = {line.strip() for line in (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()}
    assert ".sibling/" in ignored


def test_the_image_label_records_the_pinned_fleet_base_sha() -> None:
    """The image must say which fleet-base commit it was built from, so the pin can be read back from the image."""
    dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert re.search(r"^ARG FLEET_BASE_SHA$", dockerfile, re.MULTILINE)
    assert re.search(r'^LABEL fleet\.sibling\.fleet-base="\$\{FLEET_BASE_SHA\}"$', dockerfile, re.MULTILINE)
    assert re.search(r"^COPY \.sibling/fleet-base /fleet-base$", dockerfile, re.MULTILINE)
