"""Unit tests for the read-only lean-hardness-probe report adapter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from math_trace.hardness_reports import (
    load_hardness,
    resolve_probe_root,
)


def _make_probe_root(tmp_path: Path) -> Path:
    root = tmp_path / "probe"
    reports = root / "reports"
    attempts = reports / "attempts"
    attempts.mkdir(parents=True)
    summary = {
        "alpha": {
            "leanFiles": 2,
            "stubs": 1,
            "targets": ["target_one", "target_two"],
            "meanElapsedMs": 4.5,
            "maxBranches": 2,
            "maxBacktracks": 1,
            "meanProofSteps": 3.25,
            "meanTacticHits": 2.0,
            "frictions": {"bridgeLemma": 2},
            "attempts": {"error": 1, "ok": 1},
            "attemptFrictions": {"bridgeLemma": 1},
        },
        "beta": {
            "leanFiles": 1,
            "stubs": 0,
            "targets": [],
            "meanElapsedMs": 0.0,
            "maxBranches": 0,
            "maxBacktracks": 0,
            "meanProofSteps": 0.0,
            "meanTacticHits": 0.0,
            "frictions": {},
            "attempts": {},
            "attemptFrictions": {},
        },
    }
    (reports / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    attempt = {
        "caseId": "alpha",
        "targetName": "target_one",
        "script": "attempts/alpha/01.lean",
        "status": "error",
        "exitCode": 1,
        "friction": "bridgeLemma",
        "elapsedMs": 4.5,
        "proofSteps": 3,
        "tacticHits": 2,
        "backtracks": 1,
        "branches": 2,
        "goals": 1,
        "goalsBefore": 1,
        "goalsText": ["True"],
        "goalsBeforeText": ["True"],
        "errorMessage": "type mismatch",
    }
    (attempts / "alpha.jsonl").write_text(json.dumps(attempt) + "\n", encoding="utf-8")
    (attempts / "orphan.jsonl").write_text(
        json.dumps({**attempt, "caseId": "orphan", "targetName": "orphan_target"}) + "\n",
        encoding="utf-8",
    )
    return root


def test_resolve_probe_root_uses_explicit_argument(tmp_path: Path) -> None:
    root = tmp_path / "custom-probe"
    assert resolve_probe_root(root) == root.resolve(strict=False)


def test_resolve_probe_root_uses_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    env_root = tmp_path / "env-probe"
    monkeypatch.setenv("LEAN_HARDNESS_PROBE_ROOT", str(env_root))
    assert resolve_probe_root() == env_root.resolve(strict=False)


def test_load_hardness_parses_summary_and_attempts(tmp_path: Path) -> None:
    root = _make_probe_root(tmp_path)
    report = load_hardness(root)

    assert report.root == root.resolve(strict=False)
    assert report.total_stubs == 1
    assert report.total_telemetry_records == 2
    assert [case.case_id for case in report.cases] == ["alpha", "beta", "orphan"]

    alpha = report.cases[0]
    assert alpha.stubs == 1
    assert alpha.max_backtracks == 1
    assert alpha.mean_proof_steps == 3.25
    assert alpha.attempt_count == 1
    assert alpha.attempt_records[0].target_name == "target_one"
    assert alpha.attempt_records[0].goals_text == ("True",)

    orphan = report.cases[2]
    assert orphan.case_id == "orphan"
    assert orphan.stubs == 0
    assert orphan.attempt_count == 1


def test_load_hardness_rejects_missing_summary(tmp_path: Path) -> None:
    root = tmp_path / "missing-probe"
    root.mkdir()
    with pytest.raises(FileNotFoundError):
        load_hardness(root)
