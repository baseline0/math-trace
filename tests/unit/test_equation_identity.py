"""Equation identity: the hash follows the mathematics, not the way it is written or where it lives."""

import sympy as sp

from math_trace.equation_identity import EquationId, expr_hash

V, E, P, L = sp.symbols("V E P L", positive=True)


def test_operand_order_does_not_change_the_hash() -> None:
    assert expr_hash(V + E + P * L) == expr_hash(P * L + E + V)


def test_spacing_and_parse_form_do_not_change_the_hash() -> None:
    assert expr_hash("V + E + P*L") == expr_hash("P * L+E+V")


def test_a_change_to_the_mathematics_changes_the_hash() -> None:
    assert expr_hash(V + E + P * L) != expr_hash(V + E + P**2 * L)


def test_a_recorded_identity_matches_its_own_expression_and_not_a_changed_one() -> None:
    eq = EquationId.from_expr("f3_bound", V + E + P * L, "src/model.py", "f3_bound", 12, "abc1234")
    assert eq.matches(P * L + V + E)
    assert not eq.matches(V + E + P**2 * L)


def test_moving_the_source_does_not_change_the_identity() -> None:
    a = EquationId.from_expr("f3_bound", V + E + P * L, "src/model.py", "f3_bound", 12, "abc1234")
    b = EquationId.from_expr("f3_bound", V + E + P * L, "src/other.py", "g", 90, "def5678")
    assert a.expr_hash == b.expr_hash
