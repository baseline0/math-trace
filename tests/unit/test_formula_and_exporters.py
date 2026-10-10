"""Tests for the Formula contract and the LaTeX-to-Typst exporter path.

Happy paths: the Formula dataclass round-trips to dict, its JSON projection drops
verification metadata, the converter handles the common macros, and the LaTeX
exporter emits each formula.
Unhappy paths: a formula missing required fields is rejected, and a nested
fraction (a known limitation of the regex converter) is marked as an expected
failure so the gap stays visible.
"""

import pytest

from math_trace.exporters import LatexExporter, LatexToTypstConverter
from math_trace.formula import Formula, formula_to_json_dict


def make_formula(**overrides) -> Formula:
    base = {
        "name": "michaelis_menten",
        "latex": r"\frac{V_{max} S}{K_m + S}",
        "description": "Enzyme kinetics",
        "source_line": 42,
        "assumptions": "S >= 0",
        "units": "mol/s",
        "verified": True,
    }
    base.update(overrides)
    return Formula(**base)


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
    with pytest.raises(TypeError):
        Formula(name="n", latex="x")  # missing description and source_line


# --- LaTeX to Typst converter -------------------------------------------------------


@pytest.mark.parametrize(
    ("latex", "typst"),
    [
        (r"\alpha + \beta", "α + β"),
        (r"\sqrt{x}", "sqrt(x)"),
        (r"\frac{a}{b}", "a / b"),
        (r"\pi r^2", "π r^2"),
    ],
)
def test_converter_handles_common_macros(latex, typst):
    assert LatexToTypstConverter().convert(latex) == typst


def test_converter_leaves_plain_text_unchanged():
    assert LatexToTypstConverter().convert("x^2 + y") == "x^2 + y"


@pytest.mark.xfail(
    strict=True,
    reason="Known limitation: the regex converter does not handle nested fractions. "
    "Fix by replacing the regex with a brace-aware parser.",
)
def test_converter_handles_nested_fractions():
    assert LatexToTypstConverter().convert(r"\frac{\frac{a}{b}}{c}") == "(a / b) / c"


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
