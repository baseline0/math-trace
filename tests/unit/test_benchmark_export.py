"""Test export_benchmarks.py generation and JSON schema contracts for Lean validation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from math_trace.constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import export_benchmarks

runner = CliRunner()
pytestmark = pytest.mark.unit


def test_export_benchmarks_fixture(tmp_path: Path) -> None:
    out = tmp_path / "benchmarks_fixture.json"
    result = runner.invoke(export_benchmarks.app, ["--output", str(out), "--fixture"])
    assert result.exit_code == 0
    assert out.is_file()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data) >= 1
    for run in data:
        assert run["isFixture"] is True
        assert "runId" in run
        assert run["overheadBp"] <= 20000
        assert run["thresholdPpm"] >= 10000


def test_export_benchmarks_live(tmp_path: Path) -> None:
    out = tmp_path / "benchmarks_live.json"
    result = runner.invoke(export_benchmarks.app, ["--output", str(out), "--live"])
    assert result.exit_code == 0
    assert out.is_file()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert len(data) >= 1
    for run in data:
        assert run["isFixture"] is False
        assert "runId" in run
        assert run["overheadBp"] <= 20000
        assert run["thresholdPpm"] >= 10000
