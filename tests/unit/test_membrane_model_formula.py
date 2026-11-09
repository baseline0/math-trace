"""The membrane example uses math_trace's Formula and equation identity, not a local copy."""

import sys

import sympy as sp

from math_trace.constants import REPO_ROOT
from math_trace.equation_identity import expr_hash

MODEL_SRC = REPO_ROOT / "examples" / "membrane-dynamics" / "src"
sys.path.insert(0, str(MODEL_SRC))

from model import EXPRESSIONS, FORMULAS, export_json  # noqa: E402

from math_trace.formula import Formula  # noqa: E402


def _formula_call_lines() -> list[int]:
    """1-based line numbers of code (not comments) in model.py that open a Formula( call."""
    lines = (MODEL_SRC / "model.py").read_text(encoding="utf-8").splitlines()
    return [i for i, line in enumerate(lines, 1) if "Formula(" in line and not line.lstrip().startswith("#")]


def test_formula_is_math_trace_class():
    assert isinstance(FORMULAS["rate"], Formula)


def test_source_line_is_line_of_formula_call():
    calls = _formula_call_lines()
    assert len(calls) == 1
    assert FORMULAS["rate"].source_line == calls[0]


def test_export_reports_source_line_of_formula_call(tmp_path):
    import json

    out = tmp_path / "equations.json"
    export_json(out)
    loaded = json.loads(out.read_text())
    assert loaded["rate"]["source_line"] == _formula_call_lines()[0]


def test_expr_hash_stable_across_operand_order():
    a, b = sp.symbols("a b", positive=True)
    assert expr_hash(a + b) == expr_hash(b + a)
    assert expr_hash(a * b) == expr_hash(b * a)
    assert expr_hash(a * b) != expr_hash(a + b)


def test_model_expr_hash_ignores_operand_order():
    k, n_a = sp.symbols("k n_a", positive=True, real=True)
    assert expr_hash(k * n_a) == expr_hash(n_a * k)
    assert expr_hash(EXPRESSIONS["rate"]) == expr_hash(EXPRESSIONS["rate"])
