"""
Minimal P-system model: rule 2a → b with stochastic mass-action kinetics.

This is the SOURCE OF TRUTH for all formulas in the paper and Lean.
Everything else is derived from this.
"""

import sympy as sp
import json
from dataclasses import dataclass
from pathlib import Path


# === Symbolic definitions (source of truth) ===
k = sp.Symbol('k', positive=True, real=True)
n_a = sp.Symbol('n_a', positive=True, integer=True)

# Rate law: r = k * C(n_a, 2) = k * n_a * (n_a - 1) / 2
rate_expr = k * sp.binomial(n_a, 2)
rate_simplified = sp.simplify(rate_expr)  # k*n_a*(n_a-1)/2


@dataclass
class Formula:
    """A formula with metadata for traceability."""
    name: str
    expr: sp.Expr
    description: str
    source_line: int

    def to_latex(self) -> str:
        """Convert SymPy expression to LaTeX string."""
        return sp.latex(self.expr)

    def to_dict(self) -> dict:
        """Export as dictionary for JSON serialization."""
        return {
            'latex': self.to_latex(),
            'sympy': str(self.expr),
            'description': self.description,
            'source_line': self.source_line,
        }


# Define all formulas used in the paper
FORMULAS = {
    'rate': Formula(
        name='rate',
        expr=rate_simplified,
        description='Transition rate for rule 2a → b under mass-action kinetics',
        source_line=25
    )
}


def export_json(output_path='membrane_equations.json'):
    """Export formulas as JSON for other build steps."""
    data = {
        name: formula.to_dict()
        for name, formula in FORMULAS.items()
    }
    Path(output_path).write_text(json.dumps(data, indent=2))
    return data


if __name__ == '__main__':
    export_json()
    print("✅ Exported membrane_equations.json")
    print(f"\nFormulas:")
    for name, formula in FORMULAS.items():
        print(f"  {name}: {formula.to_latex()}")
