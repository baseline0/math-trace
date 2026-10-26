"""Key quantum-computing formulas, each with a source and a sympy check (quantum-computing workplan, W6).

A formula holds when its residual simplifies to zero. Matrix residuals hold when every entry does. The sources are
textbook and paper references; section pinpoints are not given here and should be confirmed against the source.

The catalog, catalogs/quantum_formulas.json, is written by this module (python -m math_trace.quantum_formulas). It holds
only formulas whose residual holds, so a consumer cannot receive a formula that fails its check. equations-history
ingests it through the formula catalog contract. Each entry's source_line is the line where its QuantumFormula( call
starts in this file.
"""

import json
import math
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import sympy as sp

from math_trace.constants import REPO_ROOT
from math_trace.formula import caller_line

NIELSEN_CHUANG = "Nielsen & Chuang (2010), Quantum Computation and Quantum Information, 10th anniversary ed."
GROVER = "Grover (1996), A fast quantum mechanical algorithm for database search, STOC"
SHOR = "Shor (1997), Polynomial-time algorithms for prime factorization and discrete logarithms, SIAM J. Comput."

CATALOG_PATH = REPO_ROOT / "catalogs" / "quantum_formulas.json"

theta, phi = sp.symbols("theta phi", real=True)
IMAG = sp.I


@dataclass(frozen=True)
class QuantumFormula:
    """One formula: its name, LaTeX, source, and the residual that must simplify to zero.

    description, assumptions and units are what the catalog carries. source_line is where this call starts in this file;
    left out, it is captured from the calling code.
    """

    name: str
    latex: str
    source: str
    residual: Callable[[], sp.Expr | sp.MatrixBase]
    description: str = ""
    assumptions: str = ""
    units: str = ""
    source_line: int | None = None

    def __post_init__(self) -> None:
        if self.source_line is None:
            object.__setattr__(self, "source_line", caller_line(sys._getframe(1)))

    def holds(self) -> bool:
        """True when the residual is zero. Complex exponentials and trig are expanded first, which plain simplify misses."""
        value = self.residual()
        if isinstance(value, sp.MatrixBase):
            return all(_is_zero(entry) for entry in value)
        return _is_zero(value)


def _is_zero(expr: sp.Expr) -> bool:
    return sp.simplify(sp.expand_complex(sp.expand_trig(expr))) == 0


def _bloch_state() -> sp.Matrix:
    """cos(theta/2)|0> + e^{i phi} sin(theta/2)|1>, as a column vector."""
    return sp.Matrix([sp.cos(theta / 2), sp.exp(IMAG * phi) * sp.sin(theta / 2)])


def _expectation(operator: sp.Matrix, state: sp.Matrix) -> sp.Expr:
    return (state.H * operator * state)[0]


X = sp.Matrix([[0, 1], [1, 0]])
Y = sp.Matrix([[0, -IMAG], [IMAG, 0]])
Z = sp.Matrix([[1, 0], [0, -1]])
ID2 = sp.eye(2)
HADAMARD = sp.Matrix([[1, 1], [1, -1]]) / sp.sqrt(2)
CNOT = sp.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])


def _rotation_z(angle: sp.Expr) -> sp.Matrix:
    return sp.diag(sp.exp(-IMAG * angle / 2), sp.exp(IMAG * angle / 2))


def _qft(n: int) -> sp.Matrix:
    omega = sp.exp(2 * sp.pi * IMAG / n)
    return sp.Matrix(n, n, lambda j, k: omega ** (j * k)) / sp.sqrt(n)


FORMULAS: tuple[QuantumFormula, ...] = (
    QuantumFormula(
        name="state_normalisation",
        latex=r"|\alpha|^2 + |\beta|^2 = 1 \text{ for } \alpha|0\rangle + \beta|1\rangle",
        source=NIELSEN_CHUANG + ", ch. 2 (postulate 1)",
        residual=lambda: sp.cos(theta / 2) * sp.cos(theta / 2) + sp.sin(theta / 2) * sp.sin(theta / 2) - 1,
        description="A qubit state a|0> + b|1> has |a|^2 + |b|^2 = 1.",
        assumptions="single qubit, pure state",
    ),
    QuantumFormula(
        name="bloch_vector_x",
        latex=r"\langle\psi|X|\psi\rangle = \sin\theta\cos\phi",
        source=NIELSEN_CHUANG + ", ch. 2 (Bloch sphere)",
        residual=lambda: _expectation(X, _bloch_state()) - sp.sin(theta) * sp.cos(phi),
        description="The expectation of X in the Bloch-sphere state gives the x component sin(theta) cos(phi).",
        assumptions="pure single-qubit state with polar angle theta and azimuth phi",
    ),
    QuantumFormula(
        name="bloch_vector_y",
        latex=r"\langle\psi|Y|\psi\rangle = \sin\theta\sin\phi",
        source=NIELSEN_CHUANG + ", ch. 2 (Bloch sphere)",
        residual=lambda: _expectation(Y, _bloch_state()) - sp.sin(theta) * sp.sin(phi),
        description="The expectation of Y in the Bloch-sphere state gives the y component sin(theta) sin(phi).",
        assumptions="pure single-qubit state with polar angle theta and azimuth phi",
    ),
    QuantumFormula(
        name="bloch_vector_z",
        latex=r"\langle\psi|Z|\psi\rangle = \cos\theta",
        source=NIELSEN_CHUANG + ", ch. 2 (Bloch sphere)",
        residual=lambda: _expectation(Z, _bloch_state()) - sp.cos(theta),
        description="The expectation of Z in the Bloch-sphere state gives the z component cos(theta).",
        assumptions="pure single-qubit state with polar angle theta",
    ),
    QuantumFormula(
        name="born_rule_hadamard_plus",
        latex=r"p(0) = |\langle 0|H|0\rangle|^2 = \tfrac12",
        source=NIELSEN_CHUANG + ", ch. 2 (postulate 3, measurement)",
        residual=lambda: sp.Abs((HADAMARD * sp.Matrix([1, 0]))[0]) ** 2 - sp.Rational(1, 2),
        description="The Hadamard gate applied to |0> gives outcome 0 with probability one half.",
        units="dimensionless (probability)",
    ),
    QuantumFormula(
        name="hadamard_unitary",
        latex=r"H^\dagger H = I",
        source=NIELSEN_CHUANG + ", ch. 4 (single-qubit gates)",
        residual=lambda: HADAMARD.H * HADAMARD - ID2,
        description="The Hadamard matrix is unitary, so the gate preserves norm and can be inverted.",
    ),
    QuantumFormula(
        name="pauli_squares",
        latex=r"X^2 = Y^2 = Z^2 = I",
        source=NIELSEN_CHUANG + ", ch. 2 (Pauli operators)",
        residual=lambda: (X * X - ID2).col_join(Y * Y - ID2).col_join(Z * Z - ID2),
        description="Each Pauli matrix squares to the identity.",
    ),
    QuantumFormula(
        name="pauli_product",
        latex=r"XY = iZ",
        source=NIELSEN_CHUANG + ", ch. 2 (Pauli operators)",
        residual=lambda: X * Y - IMAG * Z,
        description="The product of the Pauli matrices X and Y is i times Z.",
    ),
    QuantumFormula(
        name="rotation_z_unitary",
        latex=r"R_z(\theta)^\dagger R_z(\theta) = I",
        source=NIELSEN_CHUANG + ", ch. 4 (single-qubit gates)",
        residual=lambda: _rotation_z(theta).H * _rotation_z(theta) - ID2,
        description="The z-rotation gate R_z(theta) is unitary for every angle theta.",
    ),
    QuantumFormula(
        name="bell_state_from_hadamard_and_cnot",
        latex=r"\mathrm{CNOT}(H\otimes I)|00\rangle = \tfrac{1}{\sqrt2}(|00\rangle + |11\rangle)",
        source=NIELSEN_CHUANG + ", ch. 4 (controlled-NOT, Bell states)",
        residual=lambda: (
            CNOT * sp.kronecker_product(HADAMARD, ID2) * sp.Matrix([1, 0, 0, 0]) - sp.Matrix([1, 0, 0, 1]) / sp.sqrt(2)
        ),
        description="A Hadamard on the first qubit followed by a CNOT prepares the Bell state (|00> + |11>)/sqrt(2).",
        assumptions="two qubits, starting in |00>",
    ),
    QuantumFormula(
        name="grover_two_qubits_one_iteration",
        latex=r"\sin^2\big((2k+1)\theta\big) = 1 \text{ with } \sin\theta = 1/\sqrt{N},\ N=4,\ k=1",
        source=GROVER + "; " + NIELSEN_CHUANG + ", ch. 6",
        residual=lambda: sp.sin(3 * sp.asin(sp.Rational(1, 2))) ** 2 - 1,
        description="With four items, one Grover iteration finds the marked item with certainty.",
        assumptions="N = 4 items, k = 1 iteration",
        units="dimensionless (probability)",
    ),
    QuantumFormula(
        name="shor_factor_from_order",
        latex=r"\gcd(a^{r/2}-1, N)\cdot\gcd(a^{r/2}+1, N) = N \text{ for } N=15,\ a=2,\ r=4",
        source=SHOR + "; " + NIELSEN_CHUANG + ", ch. 5",
        residual=lambda: sp.Integer(math.gcd(2**2 - 1, 15) * math.gcd(2**2 + 1, 15) - 15),
        description="For N = 15 and a = 2, the order r = 4 yields the factors 3 and 5.",
        assumptions="N = 15, a = 2, r = 4",
    ),
    QuantumFormula(
        name="qft_unitary_n4",
        latex=r"F_N^\dagger F_N = I,\quad F_N = \tfrac{1}{\sqrt N}\,[\omega^{jk}],\ \omega = e^{2\pi i/N},\ N=4",
        source=NIELSEN_CHUANG + ", ch. 5 (quantum Fourier transform)",
        residual=lambda: _qft(4).H * _qft(4) - sp.eye(4),
        description="The quantum Fourier transform on four amplitudes is unitary.",
        assumptions="N = 4",
    ),
)


def by_name(name: str) -> QuantumFormula:
    """The formula with this name. Unknown names raise KeyError, so a typo cannot pass silently."""
    for formula in FORMULAS:
        if formula.name == name:
            return formula
    raise KeyError(name)


def export_equation_metadata(formulas: tuple[QuantumFormula, ...] = FORMULAS) -> dict[str, dict[str, Any]]:
    """The catalog entries for ``formulas``, in the shape the formula catalog contract requires.

    Raises ValueError, naming each formula, when a residual does not hold or a formula has no description. A
    catalog therefore never contains a formula that fails its own check.
    """
    failing = [formula.name for formula in formulas if not formula.holds()]
    if failing:
        raise ValueError(f"residual does not hold for: {', '.join(failing)}")
    undescribed = [formula.name for formula in formulas if not formula.description.strip()]
    if undescribed:
        raise ValueError(f"no description for: {', '.join(undescribed)}")
    return {
        formula.name: {
            "latex": formula.latex,
            "description": formula.description,
            "source_line": formula.source_line,
            "assumptions": formula.assumptions,
            "units": formula.units,
        }
        for formula in formulas
    }


if __name__ == "__main__":
    metadata = export_equation_metadata()
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CATALOG_PATH, "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(f"✅ Exported {len(metadata)} formulas to {CATALOG_PATH.relative_to(REPO_ROOT)}")
