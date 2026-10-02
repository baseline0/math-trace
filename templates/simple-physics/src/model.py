"""
Physics domain example: Harmonic Oscillator

Export key formulas to JSON for Typst rendering.
Edit this file to add your own equations.
"""

import json
import sys
import sympy as sp
from pathlib import Path
import importlib.util

# Load formula.py directly without triggering __init__.py
formula_path = Path(__file__).parent.parent.parent.parent / 'src' / 'math_trace' / 'formula.py'
spec = importlib.util.spec_from_file_location("formula", formula_path)
formula_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(formula_mod)
Formula = formula_mod.Formula
formula_to_json_dict = formula_mod.formula_to_json_dict


def export_formulas() -> dict[str, Formula]:
    """Define physics formulas with full metadata."""

    # Define symbols
    x, t, m, k, omega, A, phi = sp.symbols('x t m k omega A phi', real=True)

    formulas = {
        "restoring_force": Formula(
            name="restoring_force",
            latex=sp.latex(-k * x),
            description="Hooke's law: restoring force proportional to displacement",
            source_line=24,
            assumptions="x is displacement, k is spring constant",
            units="Force (N)",
            verified=True,
        ),
        "equation_of_motion": Formula(
            name="equation_of_motion",
            latex=sp.latex(sp.Eq(m * sp.diff(x, t, 2), -k * x)),
            description="Newton's second law for harmonic oscillator",
            source_line=31,
            assumptions="m > 0, k > 0, no damping",
            units="Force (N)",
            verified=True,
        ),
        "angular_frequency": Formula(
            name="angular_frequency",
            latex=sp.latex(sp.Eq(omega, sp.sqrt(k / m))),
            description="Angular frequency of oscillation",
            source_line=38,
            assumptions="m > 0, k > 0",
            units="rad/s",
            verified=True,
        ),
        "general_solution": Formula(
            name="general_solution",
            latex=sp.latex(sp.Eq(x, A * sp.cos(omega * t + phi))),
            description="General solution: oscillation with amplitude A and phase φ",
            source_line=45,
            assumptions="A is amplitude, φ is initial phase",
            units="meters (m)",
            verified=True,
        ),
        "total_energy": Formula(
            name="total_energy",
            latex=sp.latex(sp.Eq(sp.Symbol('E'), sp.Rational(1, 2) * k * A**2)),
            description="Total mechanical energy (constant)",
            source_line=52,
            assumptions="no dissipation",
            units="Joules (J)",
            verified=True,
        ),
    }

    return formulas


if __name__ == '__main__':
    formulas = export_formulas()

    # Export JSON (without verification metadata)
    json_data = {name: formula_to_json_dict(f) for name, f in formulas.items()}

    output_file = Path(__file__).parent.parent / 'physics_equations.json'
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    print(f"✅ Exported {len(formulas)} formulas to physics_equations.json")
