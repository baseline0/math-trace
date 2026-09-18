"""
Biochemistry domain example: Michaelis-Menten Enzyme Kinetics

Export key formulas to JSON for Typst rendering.
Edit this file to add your own equations.
"""

import json
import sympy as sp

def export_formulas() -> dict:
    """Define biochemistry formulas and export to JSON."""

    # Define symbols
    v, Vmax, Km, S = sp.symbols('v V_max K_m S', positive=True, real=True)
    k1, k_minus1, k2, E, ES, P = sp.symbols('k_1 k_{-1} k_2 E ES P', real=True)

    formulas = {
        "michaelis_menten": {
            "latex": sp.latex(sp.Eq(v, (Vmax * S) / (Km + S))),
            "description": "Michaelis-Menten equation: reaction velocity vs substrate concentration",
            "source_line": 15,
        },
        "max_velocity": {
            "latex": sp.latex(sp.Eq(sp.Symbol('V_max'), k2 * sp.Symbol('E_0'))),
            "description": "Maximum velocity proportional to enzyme concentration",
            "source_line": 19,
        },
        "michaelis_constant": {
            "latex": sp.latex(sp.Eq(Km, (k_minus1 + k2) / k1)),
            "description": "Michaelis constant relates binding and turnover rates",
            "source_line": 23,
        },
        "enzyme_mechanism": {
            "latex": sp.latex(sp.Symbol('E') + sp.Symbol('S') + sp.Symbol('\\rightarrow') + sp.Symbol('ES') + sp.Symbol('\\rightarrow') + sp.Symbol('E') + sp.Symbol('P')),
            "description": "Three-step enzyme mechanism (binding → catalysis → release)",
            "source_line": 27,
        },
        "turnover_number": {
            "latex": sp.latex(sp.Eq(sp.Symbol('k_{cat}'), k2)),
            "description": "Turnover number: catalytic events per enzyme per second",
            "source_line": 31,
        },
        "specificity": {
            "latex": sp.latex(sp.Eq(sp.Symbol('k_{cat}/K_m'), k2 / Km)),
            "description": "Catalytic efficiency: how selective and fast the enzyme is",
            "source_line": 35,
        },
    }

    return formulas


if __name__ == '__main__':
    formulas = export_formulas()
    with open('biochemistry_equations.json', 'w') as f:
        json.dump(formulas, f, indent=2)
    print(f"✅ Exported {len(formulas)} formulas to biochemistry_equations.json")
