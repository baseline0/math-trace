"""Quantum systems model definitions and equation generation."""

import json
import sys
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
    """Define quantum system formulas with metadata."""
    formulas = {
        "schrodinger": Formula(
            name="schrodinger",
            latex=r"i\hbar\frac{\partial \Psi}{\partial t} = \hat{H}\Psi",
            description="Time-dependent Schrödinger equation",
            source_line=14,
            assumptions="non-relativistic quantum mechanics",
            units="energy (eV)",
            verified=False,
        ),
        "hamiltonian": Formula(
            name="hamiltonian",
            latex=r"\hat{H} = \frac{\hat{p}^2}{2m} + V(\hat{x})",
            description="Quantum Hamiltonian: kinetic + potential energy operators",
            source_line=21,
            assumptions="single particle, no spin",
            units="energy (eV)",
            verified=False,
        ),
    }
    return formulas


if __name__ == "__main__":
    formulas = export_formulas()

    # Export JSON (without verification metadata)
    json_data = {name: formula_to_json_dict(f) for name, f in formulas.items()}

    output_file = Path(__file__).parent.parent / "quantum_systems_equations.json"
    with open(output_file, "w") as f:
        json.dump(json_data, f, indent=2)
    print(f"✓ Generated {output_file}")
