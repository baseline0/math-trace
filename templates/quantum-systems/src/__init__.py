"""Quantum Systems: Computational framework for Schrödinger equation solvers."""

__version__ = "1.0.0"
__author__ = "math-trace Contributors"

from .model import (
    QuantumState,
    double_slit_potential,
    expectation_value,
    harmonic_potential,
    infinite_square_well,
    normalize_wavefunction,
    probability_density,
    propagate_ssfm,
    solve_tise_fdm,
    total_energy,
    tunneling_barrier,
)

__all__ = [
    "QuantumState",
    "double_slit_potential",
    "expectation_value",
    "harmonic_potential",
    "infinite_square_well",
    "normalize_wavefunction",
    "probability_density",
    "propagate_ssfm",
    "solve_tise_fdm",
    "total_energy",
    "tunneling_barrier",
]
