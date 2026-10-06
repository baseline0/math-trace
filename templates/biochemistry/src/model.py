"""
Biochemistry domain example: Michaelis-Menten Enzyme Kinetics

Export key formulas to JSON for Typst rendering.
Edit this file to add your own equations.
"""

import importlib.util
import json
from pathlib import Path

import sympy as sp

# Load formula.py directly without triggering __init__.py
formula_path = Path(__file__).parent.parent.parent.parent / "src" / "math_trace" / "formula.py"
spec = importlib.util.spec_from_file_location("formula", formula_path)
formula_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(formula_mod)
Formula = formula_mod.Formula
formula_to_json_dict = formula_mod.formula_to_json_dict


def export_formulas() -> dict[str, Formula]:
    """Define biochemistry formulas with full metadata."""

    # Define symbols
    v, Vmax, Km, S = sp.symbols("v V_max K_m S", positive=True, real=True)
    k1, k_minus1, k2, E, ES, P = sp.symbols("k_1 k_{-1} k_2 E ES P", real=True)

    formulas = {
        "michaelis_menten": Formula(
            name="michaelis_menten",
            latex=sp.latex(sp.Eq(v, (Vmax * S) / (Km + S))),
            description="Michaelis-Menten equation: reaction velocity vs substrate concentration",
            source_line=27,
            assumptions="Quasi-steady-state assumption (d[ES]/dt ≈ 0)",
            units="μmol/min",
            verified=True,
        ),
        "max_velocity": Formula(
            name="max_velocity",
            latex=sp.latex(sp.Eq(sp.Symbol("V_max"), k2 * sp.Symbol("E_0"))),
            description="Maximum velocity proportional to enzyme concentration",
            source_line=34,
            assumptions="[S] >> Km at saturation",
            units="μmol/min",
            verified=True,
        ),
        "michaelis_constant": Formula(
            name="michaelis_constant",
            latex=sp.latex(sp.Eq(Km, (k_minus1 + k2) / k1)),
            description="Michaelis constant relates binding and turnover rates",
            source_line=41,
            assumptions="Pre-equilibrium binding",
            units="mM",
            verified=True,
        ),
        "enzyme_mechanism": Formula(
            name="enzyme_mechanism",
            latex=r"E + S \rightarrow ES \rightarrow E + P",
            description="Three-step enzyme mechanism (binding → catalysis → release)",
            source_line=48,
            assumptions="Reaction reaches steady state",
            units="dimensionless",
            verified=False,
        ),
        "turnover_number": Formula(
            name="turnover_number",
            latex=sp.latex(sp.Eq(sp.Symbol("k_{cat}"), k2)),
            description="Turnover number: catalytic events per enzyme per second",
            source_line=55,
            assumptions="First-order reaction at catalytic step",
            units="s^-1",
            verified=True,
        ),
        "specificity": Formula(
            name="specificity",
            latex=sp.latex(sp.Eq(sp.Symbol("k_{cat}/K_m"), k2 / Km)),
            description="Catalytic efficiency: how selective and fast the enzyme is",
            source_line=62,
            assumptions="Low substrate concentration regime",
            units="mM^-1 s^-1",
            verified=True,
        ),
    }

    return formulas


if __name__ == "__main__":
    formulas = export_formulas()

    # Export JSON (without verification metadata)
    json_data = {name: formula_to_json_dict(f) for name, f in formulas.items()}

    output_file = Path(__file__).parent.parent / "biochemistry_equations.json"
    with open(output_file, "w") as f:
        json.dump(json_data, f, indent=2)
    print(f"✅ Exported {len(formulas)} formulas to biochemistry_equations.json")
