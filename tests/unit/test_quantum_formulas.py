"""Each key quantum formula holds under sympy, and a wrong version of it is caught.

The positive cases check the formulas in math_trace.quantum_formulas. The negative cases build a deliberately wrong
residual for each family and assert that the check fails, so a sign or angle error cannot pass silently.
"""

import pytest
import sympy as sp

from math_trace.quantum_formulas import FORMULAS, QuantumFormula, by_name, phi, theta


@pytest.mark.parametrize("formula", FORMULAS, ids=lambda f: f.name)
def test_formula_holds_under_sympy(formula: QuantumFormula):
    assert formula.holds(), f"{formula.name} does not simplify to zero"


@pytest.mark.parametrize("formula", FORMULAS, ids=lambda f: f.name)
def test_every_formula_names_a_source_and_latex(formula: QuantumFormula):
    assert formula.source.strip()
    assert formula.latex.strip()


def test_names_are_unique():
    names = [formula.name for formula in FORMULAS]
    assert len(names) == len(set(names))


def test_an_unknown_name_raises_rather_than_passing_silently():
    with pytest.raises(KeyError):
        by_name("no_such_formula")


def test_a_wrong_bloch_x_component_is_caught():
    wrong = QuantumFormula(
        name="bloch_x_wrong",
        latex="",
        source="test",
        residual=lambda: sp.cos(theta) * sp.cos(phi) - sp.sin(theta) * sp.cos(phi),
    )
    assert wrong.holds() is False


def test_a_wrong_hadamard_sign_is_caught():
    wrong = QuantumFormula(
        name="hadamard_wrong",
        latex="",
        source="test",
        residual=lambda: (
            sp.Matrix([[1, -1], [1, 1]]) / sp.sqrt(2) * sp.Matrix([[1, 1], [1, -1]]) / sp.sqrt(2) - sp.eye(2)
        ),
    )
    assert wrong.holds() is False


def test_a_wrong_grover_iteration_count_is_caught():
    # One iteration on N=4 succeeds with probability 1; zero iterations gives sin^2(theta) = 1/4, not 1.
    wrong = QuantumFormula(
        name="grover_zero_iterations",
        latex="",
        source="test",
        residual=lambda: sp.sin(1 * sp.asin(sp.Rational(1, 2))) ** 2 - 1,
    )
    assert wrong.holds() is False


def test_a_wrong_pauli_product_sign_is_caught():
    wrong = QuantumFormula(
        name="pauli_product_wrong",
        latex="",
        source="test",
        residual=lambda: (
            sp.Matrix([[0, 1], [1, 0]]) * sp.Matrix([[0, -sp.I], [sp.I, 0]]) + sp.I * sp.Matrix([[1, 0], [0, -1]])
        ),
    )
    assert wrong.holds() is False
