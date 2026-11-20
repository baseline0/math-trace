"""Unit tests for the lean-hardness dashboard routes."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from math_trace.server import app


def _make_probe_root(tmp_path: Path) -> Path:
    root = tmp_path / "probe"
    reports = root / "reports"
    attempts = reports / "attempts"
    attempts.mkdir(parents=True)
    summary = {
        "alpha": {
            "leanFiles": 1,
            "stubs": 0,
            "targets": ["toy"],
            "meanElapsedMs": 1.0,
            "maxBranches": 0,
            "maxBacktracks": 0,
            "meanProofSteps": 1.0,
            "meanTacticHits": 1.0,
            "frictions": {},
            "attempts": {},
            "attemptFrictions": {},
        }
    }
    (reports / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    return root


def test_hardness_summary_endpoint_returns_case_data(tmp_path: Path) -> None:
    root = _make_probe_root(tmp_path)
    client = TestClient(app)

    response = client.get("/api/hardness/summary", params={"root": str(root)})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["totalStubs"] == 0
    assert body["cases"][0]["case_id"] == "alpha"


def test_hardness_case_endpoint_returns_404_for_unknown_case(tmp_path: Path) -> None:
    root = _make_probe_root(tmp_path)
    client = TestClient(app)

    response = client.get("/api/hardness/cases/missing", params={"root": str(root)})

    assert response.status_code == 404


def test_hardness_dashboard_renders(tmp_path: Path) -> None:
    root = _make_probe_root(tmp_path)
    client = TestClient(app)

    response = client.get("/hardness", params={"root": str(root)})

    assert response.status_code == 200
    assert "Lean hardness probe dashboard" in response.text
