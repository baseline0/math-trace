"""Quantum Systems: Computational framework for Schrödinger equation solvers."""

__version__ = "1.0.0"
__author__ = "math-trace Contributors"

from .model import (
    solve_tise_fdm,
    propagate_ssfm,
    normalize_wavefunction,
    expectation_value,
    total_energy,
    probability_density,
    harmonic_potential,
    infinite_square_well,
    double_slit_potential,
    tunneling_barrier,
    QuantumState,
)

__all__ = [
    "solve_tise_fdm",
    "propagate_ssfm",
    "normalize_wavefunction",
    "expectation_value",
    "total_energy",
    "probability_density",
    "harmonic_potential",
    "infinite_square_well",
    "double_slit_potential",
    "tunneling_barrier",
    "QuantumState",
]
