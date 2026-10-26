"""The quantum formula catalog: the committed file matches the emitter, and the emitter refuses formulas that are wrong.

The formulas themselves are checked in test_quantum_formulas.py. These tests check what a consumer receives: the source
lines name real QuantumFormula( calls, and a failing or undescribed formula cannot reach the catalog.
"""

import json
from pathlib import Path

import pytest
import sympy as sp

from math_trace import quantum_formulas
from math_trace.code_refs import call_lines
from math_trace.quantum_formulas import CATALOG_PATH, FORMULAS, QuantumFormula, export_equation_metadata

MODULE_SOURCE = Path(quantum_formulas.__file__).read_text()


def test_committed_catalog_matches_the_emitter() -> None:
    assert json.loads(CATALOG_PATH.read_text()) == export_equation_metadata()


def test_every_source_line_is_a_quantum_formula_call() -> None:
    lines = {entry["source_line"] for entry in export_equation_metadata().values()}

    assert lines == call_lines(MODULE_SOURCE, "QuantumFormula")


def test_catalog_entries_carry_the_contract_fields() -> None:
    for name, entry in json.loads(CATALOG_PATH.read_text()).items():
        assert set(entry) == {"latex", "description", "source_line", "assumptions", "units"}, name
        assert entry["description"].strip(), name
        assert entry["source_line"] >= 1, name


def test_a_formula_with_a_false_residual_is_refused() -> None:
    wrong = QuantumFormula(
        name="wrong_bloch_x",
        latex=r"\langle\psi|X|\psi\rangle = \cos\theta",
        source="test",
        residual=lambda: sp.sin(quantum_formulas.theta) - sp.cos(quantum_formulas.theta),
        description="A deliberately wrong formula.",
    )

    with pytest.raises(ValueError, match="residual does not hold for: wrong_bloch_x"):
        export_equation_metadata((wrong,))


def test_a_formula_without_a_description_is_refused() -> None:
    undescribed = QuantumFormula(
        name="undescribed",
        latex=r"H^\dagger H = I",
        source="test",
        residual=lambda: quantum_formulas.HADAMARD.H * quantum_formulas.HADAMARD - quantum_formulas.ID2,
    )

    with pytest.raises(ValueError, match="no description for: undescribed"):
        export_equation_metadata((undescribed,))


def test_the_catalog_covers_every_formula() -> None:
    assert set(export_equation_metadata()) == {formula.name for formula in FORMULAS}
