"""Stable equation ids and provenance: catalog-compatible, additive, and drift-checked."""

import json
import runpy
import subprocess

import sympy as sp

import math_trace.constants as constants
import math_trace.equation_provenance as provenance
from math_trace.equation_provenance import (
    PROVENANCE_PATH,
    _verification_for,
    export_equation_provenance,
    formula_expr_hash,
)
from math_trace.quantum_formulas import FORMULAS, QuantumFormula, theta
from math_trace.verification import VerificationStatus


def test_export_is_deterministic_for_a_fixed_commit():
    first = export_equation_provenance(commit="abc123")
    second = export_equation_provenance(commit="abc123")
    assert first == second
    assert first["source_commit"] == "abc123"


def test_every_formula_has_a_stable_id_and_relative_source():
    payload = export_equation_provenance(commit="abc123")
    assert len(payload["equations"]) == len(FORMULAS)
    for name, record in payload["equations"].items():
        assert record["id"] == f"math-trace/{name}"
        assert record["expr_hash"].startswith("sha256:")
        assert record["source_file"].startswith("src/")
        assert record["line"] > 0
        assert record["holds"] is True
        assert record["verification"]["statuses"] == [VerificationStatus.SYMBOLIC_VERIFIED.value]
        assert record["verification"]["records"][0]["by"] == "sympy residual check"


def test_verification_is_narrow_and_omits_unverified_statuses():
    payload = export_equation_provenance(commit="abc123")

    for record in payload["equations"].values():
        statuses = set(record["verification"]["statuses"])
        assert statuses == {VerificationStatus.SYMBOLIC_VERIFIED.value}
        assert VerificationStatus.SOURCE_VERIFIED.value not in statuses
        assert VerificationStatus.FORMALLY_VERIFIED.value not in statuses


def test_an_unverified_formula_gets_no_status():
    formula = QuantumFormula(
        name="x",
        latex="a",
        source="one",
        residual=lambda: sp.Integer(1),
        source_line=1,
    )

    assert _verification_for(formula, holds=False) == {"statuses": [], "records": []}


def test_unset_verification_metadata_is_omitted():
    formula = QuantumFormula(
        name="x",
        latex="a",
        source="one",
        residual=lambda: sp.Integer(0),
        source_line=1,
    )

    record = _verification_for(formula, holds=True)["records"][0]

    assert "date" not in record
    assert "tolerance" not in record


def test_hash_tracks_mathematics_not_source_text():
    original = QuantumFormula(
        name="x",
        latex="a",
        source="one",
        residual=lambda: sp.sin(theta) - sp.cos(theta),
        source_line=1,
    )
    moved = QuantumFormula(
        name="x",
        latex="b",
        source="two",
        residual=lambda: sp.sin(theta) - sp.cos(theta),
        source_line=999,
    )
    assert formula_expr_hash(original) == formula_expr_hash(moved)


def test_formal_claims_carry_theorem_digests():
    payload = export_equation_provenance(commit="abc123")
    theorem_records = [c for c in payload["formal_claims"] if c.get("theorem_sha256")]
    assert theorem_records
    assert all(c["theorem_path"] and c["theorem_name"] for c in theorem_records)


def test_committed_artifact_matches_the_emitter():
    artifact = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))
    expected = export_equation_provenance(commit=artifact["source_commit"])
    assert artifact == expected


def test_git_commit_returns_none_when_git_cannot_run(monkeypatch):
    def fail(*_args, **_kwargs):
        raise OSError("git missing")

    monkeypatch.setattr(provenance.subprocess, "run", fail)

    assert provenance.git_commit() is None


def test_git_commit_returns_none_for_empty_output(monkeypatch):
    monkeypatch.setattr(
        provenance.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(args=[], returncode=0, stdout="\n", stderr=""),
    )

    assert provenance.git_commit() is None


def test_git_commit_returns_the_short_sha(monkeypatch):
    monkeypatch.setattr(
        provenance.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(args=[], returncode=0, stdout="abc1234\n", stderr=""),
    )

    assert provenance.git_commit() == "abc1234"


def test_main_writes_the_artifact_and_reports_the_count(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(provenance, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(provenance, "PROVENANCE_PATH", tmp_path / "artifacts" / "equation_provenance.json")
    monkeypatch.setattr(provenance, "git_commit", lambda: "abc123")

    provenance.main()

    payload = json.loads(provenance.PROVENANCE_PATH.read_text(encoding="utf-8"))
    assert payload["source_commit"] == "abc123"
    assert len(payload["equations"]) == len(FORMULAS)
    assert "Exported provenance" in capsys.readouterr().out


def test_module_entrypoint_writes_the_artifact(tmp_path, monkeypatch):
    monkeypatch.setattr(constants, "REPO_ROOT", tmp_path)

    runpy.run_module("math_trace.equation_provenance", run_name="__main__")

    assert (tmp_path / "artifacts" / "equation_provenance.json").is_file()
