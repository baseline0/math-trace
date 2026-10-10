"""Exact-output tests for the production LaTeX-to-Typst path (SymPyToTypst).

These pin the rendering bugs found by comparing against tex2typst: a Greek letter
fused to a macro name or to another letter (Typst reads "Eψ" as one unknown name),
and differentials quoted as text ("dS") instead of rendered as d S.

Happy paths: the fused and differential forms render as separate math tokens.
Unhappy paths: a fraction that only looks like a differential is left alone, and
a dangling brace does not raise.
"""

import pytest

from math_trace.generators import SymPyToTypst


@pytest.fixture
def converter() -> SymPyToTypst:
    return SymPyToTypst()


# --- Greek letters fused to macros and letters -------------------------------------


@pytest.mark.parametrize(
    ("latex", "typst"),
    [
        (r"E\psi", "E ψ"),
        (r"\partial\psi", "partial ψ"),
        (r"\hbar\psi", "ℏ ψ"),
        (r"\alpha\beta", "α β"),
    ],
)
def test_greek_letter_is_separated_from_adjacent_letters(converter, latex, typst):
    assert converter._latex_to_typst(latex) == typst


def test_text_inside_quotes_is_not_split(converter):
    assert converter._latex_to_typst(r"\text{Attack Rate}") == '"Attack Rate"'


# --- Differential fractions --------------------------------------------------------


@pytest.mark.parametrize(
    ("latex", "typst"),
    [
        (r"\frac{dS}{dt}", "(d S)/(d t)"),
        (r"\frac{dI}{dt}", "(d I)/(d t)"),
        (r"\frac{\partial\psi}{\partial t}", "(partial ψ)/(partial t)"),
        (r"\frac{d^2\psi}{dx^2}", "(d^2 ψ)/(d x^2)"),
    ],
)
def test_differential_fraction_renders_as_separate_terms(converter, latex, typst):
    assert converter._latex_to_typst(latex) == typst


def test_differential_fraction_inside_an_equation(converter):
    latex = r"\frac{dI}{dt} = \frac{\beta \cdot S \cdot I}{N} - \gamma \cdot I"

    assert converter._latex_to_typst(latex).startswith("(d I)/(d t) = ")


# --- Unhappy paths -----------------------------------------------------------------


def test_fraction_that_is_not_a_differential_stays_an_ordinary_fraction(converter):
    # "dog" is one word, not d followed by a single variable, so it is not a differential.
    assert converter._latex_to_typst(r"\frac{dog}{x}") == '("dog")/(x)'


def test_dangling_brace_does_not_raise(converter):
    # Unbalanced input is passed through rather than crashing the build.
    result = converter._latex_to_typst(r"\frac{dS}{dt")

    assert isinstance(result, str)
