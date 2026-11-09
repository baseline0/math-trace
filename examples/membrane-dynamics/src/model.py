"""
Minimal P-system model: rule 2a → b with stochastic mass-action kinetics.

This is the SOURCE OF TRUTH for all formulas in the paper and Lean.
Everything else is derived from this.
"""

import json
from pathlib import Path

import sympy as sp

from math_trace.equation_identity import expr_hash
from math_trace.formula import Formula

# === Symbolic definitions (source of truth) ===
k = sp.Symbol("k", positive=True, real=True)
n_a = sp.Symbol("n_a", positive=True, integer=True)

# Rate law: r = k * C(n_a, 2) = k * n_a * (n_a - 1) / 2
rate_expr = k * sp.binomial(n_a, 2)
rate_simplified = sp.simplify(rate_expr)  # k*n_a*(n_a-1)/2

# SymPy expression behind each formula, keyed by formula name. Formula stores only the LaTeX.
EXPRESSIONS = {"rate": rate_simplified}

# Define all formulas used in the paper. source_line is captured from the Formula( call.
FORMULAS = {
    "rate": Formula(
        name="rate",
        latex=sp.latex(rate_simplified),
        description="Transition rate for rule 2a → b under mass-action kinetics",
    )
}


def export_json(output_path: str | Path = "membrane_equations.json"):
    """Export formulas as JSON for other build steps."""
    data = {
        name: {
            "latex": formula.latex,
            "sympy": str(EXPRESSIONS[name]),
            "description": formula.description,
            "source_line": formula.source_line,
            "expr_hash": expr_hash(EXPRESSIONS[name]),
        }
        for name, formula in FORMULAS.items()
    }
    Path(output_path).write_text(json.dumps(data, indent=2))
    return data


if __name__ == "__main__":
    export_json()
    print("✅ Exported membrane_equations.json")
    print("\nFormulas:")
    for name, formula in FORMULAS.items():
        print(f"  {name}: {formula.latex}")
