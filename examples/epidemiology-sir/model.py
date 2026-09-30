"""
SIR Model: Basic Reproduction Number R₀ from First Principles

This is the SOURCE OF TRUTH for all formulas in the paper.
All equations, parameters, and assumptions are defined here.

User question: How does R₀ arise in a simple SIR model, what assumptions
does it encode, and how does it relate to the model equations?

Model structure:
  - S (Susceptible): Can contract disease
  - I (Infected): Currently infectious
  - R (Recovered): Immune from prior infection
  - N = S + I + R (constant population, no births/deaths)

Equations:
  dS/dt = -β S I / N    (transmission: susceptible → infected)
  dI/dt = β S I / N - γ I   (balance: new infections vs. recovery)
  dR/dt = γ I           (recovery: infected → recovered)

Key parameter: R₀ = β / γ (basic reproduction number)
  Interpretation: Expected secondary infections from one primary case
"""

import sympy as sp
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any


# === SYMBOLIC DEFINITIONS (SOURCE OF TRUTH) ===

# State variables
S = sp.Symbol('S', positive=True, real=True)  # Susceptible count [persons]
I = sp.Symbol('I', positive=True, real=True)  # Infected count [persons]
R = sp.Symbol('R', positive=True, real=True)  # Recovered count [persons]
N = sp.Symbol('N', positive=True, real=True)  # Population size [persons]

# Parameters
beta = sp.Symbol('beta', positive=True, real=True)  # Transmission rate [1/days]
gamma = sp.Symbol('gamma', positive=True, real=True)  # Recovery rate [1/days]

# Derived quantity
R0 = beta / gamma  # Basic reproduction number [dimensionless]

# Rate equations (ODEs)
dS_dt = -beta * S * I / N
dI_dt = beta * S * I / N - gamma * I
dR_dt = gamma * I

# Conservation law
conservation = S + I + R - N  # Should equal 0


@dataclass
class Formula:
    """Formula with metadata for traceability."""
    name: str
    sympy_expr: sp.Expr
    latex_str: str
    description: str
    units: str
    assumptions: list

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'latex': self.latex_str,
            'sympy': str(self.sympy_expr),
            'description': self.description,
            'units': self.units,
            'assumptions': self.assumptions,
        }


# Formulas used in paper
FORMULAS = {
    'dS_dt': Formula(
        name='dS_dt',
        sympy_expr=dS_dt,
        latex_str=sp.latex(dS_dt),
        description='Rate of change of susceptible population',
        units='persons/days',
        assumptions=['Homogeneous mixing', 'No births/deaths', 'No behavior change'],
    ),
    'dI_dt': Formula(
        name='dI_dt',
        sympy_expr=dI_dt,
        latex_str=sp.latex(dI_dt),
        description='Rate of change of infected population',
        units='persons/days',
        assumptions=['Homogeneous mixing', 'Exponential recovery', 'No behavior change'],
    ),
    'dR_dt': Formula(
        name='dR_dt',
        sympy_expr=dR_dt,
        latex_str=sp.latex(dR_dt),
        description='Rate of change of recovered population',
        units='persons/days',
        assumptions=['Constant recovery rate γ'],
    ),
    'R0': Formula(
        name='R0',
        sympy_expr=R0,
        latex_str=sp.latex(R0),
        description='Basic reproduction number: expected secondary infections per primary case',
        units='dimensionless',
        assumptions=['Early exponential phase', 'No behavior change', 'Homogeneous mixing'],
    ),
}


def export_formulas(output_file: Path = None) -> Dict[str, Any]:
    """Export all formulas as JSON for reproducibility and traceability."""
    formulas_dict = {name: formula.to_dict() for name, formula in FORMULAS.items()}
    result = {
        'model': 'SIR (Susceptible-Infected-Recovered)',
        'user_question': 'How does R₀ arise in a simple SIR model?',
        'equations': formulas_dict,
        'parameters': {
            'beta': {
                'name': 'Transmission rate',
                'units': '1/days',
                'domain': '(0, ∞)',
                'interpretation': 'Contact frequency × transmission probability',
            },
            'gamma': {
                'name': 'Recovery rate',
                'units': '1/days',
                'domain': '(0, ∞)',
                'interpretation': 'Inverse of infectious period (1/γ)',
            },
        },
        'conservation_law': str(conservation),
    }

    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

    return result


if __name__ == '__main__':
    # Export formulas on run
    output_path = Path(__file__).parent / 'generated' / 'sir_equations.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    export_formulas(output_path)
    print(f"✅ Exported formulas to {output_path}")

    # Verify symbolic expressions
    print("\n=== SIR Model Equations ===")
    for name, formula in FORMULAS.items():
        print(f"\n{name}:")
        print(f"  LaTeX: {formula.latex_str}")
        print(f"  Description: {formula.description}")
        print(f"  Units: {formula.units}")
