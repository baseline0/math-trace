"""Key quantum-computing formulas, each with a source and a sympy check (quantum-computing workplan, W6).

A formula holds when its residual simplifies to zero. Matrix residuals hold when every entry does. The sources are
textbook and paper references; section pinpoints are not given here and should be confirmed against the source.
"""

from collections.abc import Callable
from dataclasses import dataclass

import sympy as sp

NIELSEN_CHUANG = "Nielsen & Chuang (2010), Quantum Computation and Quantum Information, 10th anniversary ed."
GROVER = "Grover (1996), A fast quantum mechanical algorithm for database search, STOC"
SHOR = "Shor (1997), Polynomial-time algorithms for prime factorization and discrete logarithms, SIAM J. Comput."

theta, phi = sp.symbols("theta phi", real=True)
IMAG = sp.I


@dataclass(frozen=True)
class QuantumFormula:
    """One formula: its name, its LaTeX, where it comes from, and the residual that must simplify to zero."""

    name: str
    latex: str
    source: str
    residual: Callable[[], sp.Expr | sp.MatrixBase]

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
    ),
    QuantumFormula(
        name="bloch_vector_x",
        latex=r"\langle\psi|X|\psi\rangle = \sin\theta\cos\phi",
        source=NIELSEN_CHUANG + ", ch. 2 (Bloch sphere)",
        residual=lambda: _expectation(X, _bloch_state()) - sp.sin(theta) * sp.cos(phi),
    ),
    QuantumFormula(
        name="bloch_vector_y",
        latex=r"\langle\psi|Y|\psi\rangle = \sin\theta\sin\phi",
        source=NIELSEN_CHUANG + ", ch. 2 (Bloch sphere)",
        residual=lambda: _expectation(Y, _bloch_state()) - sp.sin(theta) * sp.sin(phi),
    ),
    QuantumFormula(
        name="bloch_vector_z",
        latex=r"\langle\psi|Z|\psi\rangle = \cos\theta",
        source=NIELSEN_CHUANG + ", ch. 2 (Bloch sphere)",
        residual=lambda: _expectation(Z, _bloch_state()) - sp.cos(theta),
    ),
    QuantumFormula(
        name="born_rule_hadamard_plus",
        latex=r"p(0) = |\langle 0|H|0\rangle|^2 = \tfrac12",
        source=NIELSEN_CHUANG + ", ch. 2 (postulate 3, measurement)",
        residual=lambda: sp.Abs((HADAMARD * sp.Matrix([1, 0]))[0]) ** 2 - sp.Rational(1, 2),
    ),
    QuantumFormula(
        name="hadamard_unitary",
        latex=r"H^\dagger H = I",
        source=NIELSEN_CHUANG + ", ch. 4 (single-qubit gates)",
        residual=lambda: HADAMARD.H * HADAMARD - ID2,
    ),
    QuantumFormula(
        name="pauli_squares",
        latex=r"X^2 = Y^2 = Z^2 = I",
        source=NIELSEN_CHUANG + ", ch. 2 (Pauli operators)",
        residual=lambda: (X * X - ID2).col_join(Y * Y - ID2).col_join(Z * Z - ID2),
    ),
    QuantumFormula(
        name="pauli_product",
        latex=r"XY = iZ",
        source=NIELSEN_CHUANG + ", ch. 2 (Pauli operators)",
        residual=lambda: X * Y - IMAG * Z,
    ),
    QuantumFormula(
        name="rotation_z_unitary",
        latex=r"R_z(\theta)^\dagger R_z(\theta) = I",
        source=NIELSEN_CHUANG + ", ch. 4 (single-qubit gates)",
        residual=lambda: _rotation_z(theta).H * _rotation_z(theta) - ID2,
    ),
    QuantumFormula(
        name="bell_state_from_hadamard_and_cnot",
        latex=r"\mathrm{CNOT}(H\otimes I)|00\rangle = \tfrac{1}{\sqrt2}(|00\rangle + |11\rangle)",
        source=NIELSEN_CHUANG + ", ch. 4 (controlled-NOT, Bell states)",
        residual=lambda: (
            CNOT * sp.kronecker_product(HADAMARD, ID2) * sp.Matrix([1, 0, 0, 0]) - sp.Matrix([1, 0, 0, 1]) / sp.sqrt(2)
        ),
    ),
    QuantumFormula(
        name="grover_two_qubits_one_iteration",
        latex=r"\sin^2\big((2k+1)\theta\big) = 1 \text{ with } \sin\theta = 1/\sqrt{N},\ N=4,\ k=1",
        source=GROVER + "; " + NIELSEN_CHUANG + ", ch. 6",
        residual=lambda: sp.sin(3 * sp.asin(sp.Rational(1, 2))) ** 2 - 1,
    ),
    QuantumFormula(
        name="shor_factor_from_order",
        latex=r"\gcd(a^{r/2}-1, N)\cdot\gcd(a^{r/2}+1, N) = N \text{ for } N=15,\ a=2,\ r=4",
        source=SHOR + "; " + NIELSEN_CHUANG + ", ch. 5",
        residual=lambda: sp.gcd(2**2 - 1, 15) * sp.gcd(2**2 + 1, 15) - 15,
    ),
    QuantumFormula(
        name="qft_unitary_n4",
        latex=r"F_N^\dagger F_N = I,\quad F_N = \tfrac{1}{\sqrt N}\,[\omega^{jk}],\ \omega = e^{2\pi i/N},\ N=4",
        source=NIELSEN_CHUANG + ", ch. 5 (quantum Fourier transform)",
        residual=lambda: _qft(4).H * _qft(4) - sp.eye(4),
    ),
)


def by_name(name: str) -> QuantumFormula:
    """The formula with this name. Unknown names raise KeyError, so a typo cannot pass silently."""
    for formula in FORMULAS:
        if formula.name == name:
            return formula
    raise KeyError(name)
