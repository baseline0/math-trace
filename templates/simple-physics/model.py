"""
Physics domain example: Harmonic Oscillator

Export key formulas to JSON for Typst rendering.
Edit this file to add your own equations.
"""

import json
import sympy as sp

def export_formulas() -> dict:
    """Define physics formulas and export to JSON."""

    # Define symbols
    x, t, m, k, omega, A, phi = sp.symbols('x t m k omega A phi', real=True)

    formulas = {
        "restoring_force": {
            "latex": sp.latex(-k * x),
            "description": "Hooke's law: restoring force proportional to displacement",
            "source_line": 18,
        },
        "equation_of_motion": {
            "latex": sp.latex(sp.Eq(m * sp.diff(x, t, 2), -k * x)),
            "description": "Newton's second law for harmonic oscillator",
            "source_line": 22,
        },
        "angular_frequency": {
            "latex": sp.latex(sp.Eq(omega, sp.sqrt(k / m))),
            "description": "Angular frequency of oscillation",
            "source_line": 26,
        },
        "general_solution": {
            "latex": sp.latex(sp.Eq(x, A * sp.cos(omega * t + phi))),
            "description": "General solution: oscillation with amplitude A and phase φ",
            "source_line": 30,
        },
        "total_energy": {
            "latex": sp.latex(sp.Eq(sp.Symbol('E'), sp.Rational(1, 2) * k * A**2)),
            "description": "Total mechanical energy (constant)",
            "source_line": 34,
        },
    }

    return formulas


if __name__ == '__main__':
    formulas = export_formulas()
    with open('physics_equations.json', 'w') as f:
        json.dump(formulas, f, indent=2)
    print(f"✅ Exported {len(formulas)} formulas to physics_equations.json")
