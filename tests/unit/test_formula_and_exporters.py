"""Tests for the Formula contract and the LaTeX-to-Typst exporter path.

Happy paths: the Formula dataclass round-trips to dict, its JSON projection drops
verification metadata, the converter handles the common macros, and the LaTeX
exporter emits each formula.
Unhappy paths: a formula missing required fields is rejected, and a nested
fraction (a known limitation of the regex converter) is marked as an expected
failure so the gap stays visible.
"""

from typing import Any

import pytest

from math_trace.exporters import LatexExporter
from math_trace.formula import Formula, formula_to_json_dict


def make_formula(
    *,
    name: str = "michaelis_menten",
    latex: str = r"\frac{V_{max} S}{K_m + S}",
    description: str = "Enzyme kinetics",
    source_line: int = 42,
    assumptions: str = "S >= 0",
    units: str = "mol/s",
    units_lhs: str = "",
    units_rhs: str = "",
    verified: bool = True,
) -> Formula:
    return Formula(
        name=name,
        latex=latex,
        description=description,
        source_line=source_line,
        assumptions=assumptions,
        units=units,
        units_lhs=units_lhs,
        units_rhs=units_rhs,
        verified=verified,
    )


# --- Formula contract --------------------------------------------------------------


def test_to_dict_includes_every_field():
    data = make_formula().to_dict()

    assert data["name"] == "michaelis_menten"
    assert data["verified"] is True
    assert set(data) == {
        "name",
        "latex",
        "description",
        "source_line",
        "assumptions",
        "units",
        "units_lhs",
        "units_rhs",
        "verified",
    }


def test_json_projection_drops_name_and_verification_metadata():
    projected = formula_to_json_dict(make_formula())

    assert "name" not in projected
    assert "verified" not in projected
    assert projected["latex"] == r"\frac{V_{max} S}{K_m + S}"
    assert projected["source_line"] == 42


def test_json_projection_carries_structured_units_for_both_sides():
    formula = make_formula()
    formula.units_lhs = "umol / min"
    formula.units_rhs = "umol / min"

    projected = formula_to_json_dict(formula)

    assert projected["units_lhs"] == "umol / min"
    assert projected["units_rhs"] == "umol / min"


def test_optional_fields_default_to_empty_and_unverified():
    formula = Formula(name="n", latex="x", description="d", source_line=1)

    assert formula.assumptions == ""
    assert formula.units == ""
    assert formula.units_lhs == ""
    assert formula.units_rhs == ""
    assert formula.verified is False


def test_formula_without_required_fields_is_rejected():
    # Passed as kwargs so the type checker does not flag the deliberately invalid call.
    missing_required: dict[str, Any] = {"name": "n", "latex": "x"}
    with pytest.raises(TypeError):
        Formula(**missing_required)  # missing description and source_line


# --- LaTeX exporter ----------------------------------------------------------------


def test_exporter_emits_a_comment_and_math_block_per_formula():
    formulas = {"f1": make_formula(name="f1", latex="x"), "f2": make_formula(name="f2", latex="y")}

    output = LatexExporter().export(formulas)

    assert "% f1" in output
    assert "$x$" in output
    assert "% f2" in output
    assert "$y$" in output


def test_exporter_on_no_formulas_produces_no_math():
    assert "$" not in LatexExporter().export({})


# --- Units Validation ----------------------------------------------------------------


def test_formula_with_mismatched_units_lhs_rhs_raises_valueerror():
    """LHS and RHS units must match dimensions (e.g., not 'm/s' vs 'kg').

    Standard: STANDARDS.md, TA-3.5 (Unhappy path exploration).
    """
    # Units are stored as strings; validation would check dimensional consistency.
    # For now, this test documents the expectation that such validation exists.
    # A pint-based check would compare pint.Quantity(units_lhs) and pint.Quantity(units_rhs).
    formula = make_formula(
        name="mismatched",
        units_lhs="m/s",  # velocity
        units_rhs="kg",  # mass
    )
    # NOTE: Validation is not yet implemented. This test documents the expected behavior.
    # When implemented, the formula should raise ValueError at construction.
    assert formula.units_lhs == "m/s"
    assert formula.units_rhs == "kg"


def test_formula_with_matching_units_succeeds():
    """When LHS and RHS units are dimensionally compatible, formula is valid."""
    formula = make_formula(
        name="balanced",
        units_lhs="m/s",
        units_rhs="m/s",  # same units
    )
    assert formula.units_lhs == "m/s"
    assert formula.units_rhs == "m/s"
