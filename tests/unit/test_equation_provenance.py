"""Stable equation ids and provenance: catalog-compatible, additive, and drift-checked."""

import json

import sympy as sp

from math_trace.equation_provenance import (
    PROVENANCE_PATH,
    export_equation_provenance,
    formula_expr_hash,
)
from math_trace.quantum_formulas import FORMULAS, QuantumFormula, theta


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
