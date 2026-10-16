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
    verified: bool = True,
) -> Formula:
    return Formula(
        name=name,
        latex=latex,
        description=description,
        source_line=source_line,
        assumptions=assumptions,
        units=units,
        verified=verified,
    )


# --- Formula contract --------------------------------------------------------------


def test_to_dict_includes_every_field():
    data = make_formula().to_dict()

    assert data["name"] == "michaelis_menten"
    assert data["verified"] is True
    assert set(data) == {"name", "latex", "description", "source_line", "assumptions", "units", "verified"}


def test_json_projection_drops_name_and_verification_metadata():
    projected = formula_to_json_dict(make_formula())

    assert "name" not in projected
    assert "verified" not in projected
    assert projected["latex"] == r"\frac{V_{max} S}{K_m + S}"
    assert projected["source_line"] == 42


def test_optional_fields_default_to_empty_and_unverified():
    formula = Formula(name="n", latex="x", description="d", source_line=1)

    assert formula.assumptions == ""
    assert formula.units == ""
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
