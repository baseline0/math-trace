"""The Lean health checks must fail on what is actually missing, and only required checks may fail a run."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture
def health(request: pytest.FixtureRequest) -> ModuleType:
    script = Path(request.config.rootpath) / "scripts" / "lean_health.py"
    spec = importlib.util.spec_from_file_location("lean_health", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _manifest(tmp_path: Path, rev: str | None) -> Path:
    packages = [{"name": "other", "rev": "x"}]
    if rev is not None:
        packages.append({"name": "mathlib", "rev": rev})
    (tmp_path / "lake-manifest.json").write_text(json.dumps({"packages": packages}), encoding="utf-8")
    return tmp_path


def test_a_full_commit_pin_passes(health: ModuleType, tmp_path: Path) -> None:
    project = _manifest(tmp_path, "065356127b1dc0016f66b7283ce0ce2c4055aa55")

    check = health.check_manifest(project)

    assert check.passed and check.required


@pytest.mark.parametrize("rev", ["main", "065356127", "065356127B1DC0016F66B7283CE0CE2C4055AA55"])
def test_a_floating_or_short_pin_is_refused(health: ModuleType, tmp_path: Path, rev: str) -> None:
    project = _manifest(tmp_path, rev)

    check = health.check_manifest(project)

    assert not check.passed
    assert "40-character" in check.detail


def test_a_manifest_without_mathlib_is_refused(health: ModuleType, tmp_path: Path) -> None:
    project = _manifest(tmp_path, None)

    assert not health.check_manifest(project).passed


def test_a_missing_manifest_is_refused(health: ModuleType, tmp_path: Path) -> None:
    check = health.check_manifest(tmp_path)

    assert not check.passed
    assert "no lake-manifest.json" in check.detail


def test_the_toolchain_is_read_from_the_project(health: ModuleType, tmp_path: Path) -> None:
    (tmp_path / "lean-toolchain").write_text("leanprover/lean4:v4.35.0-rc2\n", encoding="utf-8")

    assert health.project_toolchain(tmp_path) == "leanprover/lean4:v4.35.0-rc2"
    assert health.project_toolchain(tmp_path / "missing") is None


def test_an_informational_failure_does_not_fail_the_run(health: ModuleType) -> None:
    checks = [
        health.Check("elan", True, True, ""),
        health.Check("cache", False, False, "not reachable"),
    ]

    assert health.verdict(checks)


def test_a_required_failure_fails_the_run(health: ModuleType) -> None:
    checks = [
        health.Check("elan", True, True, ""),
        health.Check("sandbox", True, False, "bwrap cannot start"),
    ]

    assert not health.verdict(checks)


def test_the_comparator_tools_are_the_four_the_script_refuses_without(health: ModuleType) -> None:
    assert health.COMPARATOR_TOOLS == ("leanexport", "leanchecker", "nanoda_bin", "con-ron")
