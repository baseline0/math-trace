"""
Test Suite: Quantum Harmonic Oscillator

Validates:
1. Energy eigenvalues match analytical formula E_n = ℏω(n + 1/2)
2. Energy conservation during time evolution (|ΔE/E₀| < 1e-6)
3. Normalization ∫|ψ|² dx = 1
4. Expectation values correct for Hermitian operators
"""

import pytest
import numpy as np
from typing import Tuple
from scipy.integrate import trapezoid
from ..scenarios.harmonic_oscillator import (
    compute_quantum_harmonic_oscillator,
    evolve_ground_state_oscillator,
    analytical_harmonic_eigenvalues,
    analytical_harmonic_period,
)
from ..model import normalize_wavefunction, probability_density


class TestHarmonicEigenvalues:
    """Test eigenvalue solver against analytical solutions."""

    def test_eigenvalue_accuracy_first_5_levels(self):
        """
        Validate first 5 energy levels.

        E_n = ℏω(n + 1/2)
        With ℏ = ω = 1: E_n = n + 0.5
        Expected: [0.5, 1.5, 2.5, 3.5, 4.5]
        """
        result = compute_quantum_harmonic_oscillator(
            x_min=-6, x_max=6, num_points=512, omega=1.0, num_eigenstates=5
        )

        # Check relative error < 0.1% for each level
        for i, err in enumerate(result["error"]):
            assert err < 1e-3, f"Level {i}: error {err:.2e} exceeds 0.1%"

    def test_eigenvalue_higher_frequency(self):
        """Test with ω = 2.0 (energy scale-up)."""
        omega = 2.0
        result = compute_quantum_harmonic_oscillator(omega=omega, num_eigenstates=3)

        # Analytical: E_n = ω(n + 0.5) = 2(n + 0.5)
        expected = np.array([1.0, 3.0, 5.0])

        for i, (E_num, E_ana) in enumerate(zip(result["energies"], expected)):
            rel_err = np.abs(E_num - E_ana) / E_ana
            assert rel_err < 1e-3, f"ω={omega}, n={i}: {rel_err:.2e}"

    def test_eigenvalue_convergence_with_grid_size(self):
        """Finer grid → better accuracy."""
        errors_256 = compute_quantum_harmonic_oscillator(num_points=256)["error"]
        errors_512 = compute_quantum_harmonic_oscillator(num_points=512)["error"]

        # 512 points should be more accurate than 256
        assert np.mean(errors_512) < np.mean(errors_256)


class TestEnergyConservation:
    """Test energy is conserved during time evolution."""

    def test_ground_state_energy_conservation(self):
        """
        Evolve ground state for 10 periods.
        Energy should remain constant: |ΔE/E₀| < 1e-6
        """
        result = evolve_ground_state_oscillator(
            x_min=-5, x_max=5, num_points=512,
            t_max=10.0, dt=0.01,
            omega=1.0
        )

        # Maximum relative energy error
        max_error = np.max(result["energy_error"])

        assert max_error < 1e-6, f"Energy error {max_error:.2e} exceeds threshold"

    def test_energy_conservation_multiple_frequencies(self):
        """Test for ω ∈ {0.5, 1.0, 2.0}."""
        for omega in [0.5, 1.0, 2.0]:
            result = evolve_ground_state_oscillator(omega=omega, t_max=5.0)
            max_error = np.max(result["energy_error"])

            # Relaxed threshold for lower frequencies (slower oscillations require finer dt)
            threshold = 1e-4 if omega < 1.0 else 1e-6
            assert max_error < threshold, f"ω={omega}: error {max_error:.2e}"

    def test_energy_conservation_longer_evolution(self):
        """Longer evolution (20 periods) still maintains energy."""
        result = evolve_ground_state_oscillator(t_max=20.0, dt=0.005)

        max_error = np.max(result["energy_error"])
        assert max_error < 1e-5  # Slightly relaxed for long evolution


class TestNormalization:
    """Test wavefunction normalization."""

    def test_eigenstate_normalization(self):
        """Eigenstates returned by solver should be normalized."""
        result = compute_quantum_harmonic_oscillator(num_eigenstates=5)
        x = result["x"]
        eigenstates = result["eigenstates"]

        # Check ∫|ψ_n|² dx = 1 for each eigenstate
        for i in range(eigenstates.shape[1]):
            psi = eigenstates[:, i]
            prob = probability_density(psi)
            norm = trapezoid(prob, x)

            assert np.isclose(norm, 1.0, atol=1e-6), \
                f"Eigenstate {i}: norm {norm:.8f}, expected 1.0"

    def test_time_evolved_state_normalization(self):
        """Time-evolved state should remain normalized."""
        result = evolve_ground_state_oscillator(t_max=10.0)
        x = result["x"]
        psi_t = result["psi_t"]

        # Check normalization at several time points
        for t_idx in [0, len(result["times"])//2, -1]:
            psi = psi_t[:, t_idx]
            prob = probability_density(psi)
            norm = trapezoid(prob, x)

            assert np.isclose(norm, 1.0, atol=1e-6), \
                f"Time index {t_idx}: norm {norm:.8f}"


class TestExpectationValues:
    """Test expectation values for Hermitian operators."""

    def test_expectation_x_is_zero_even_symmetry(self):
        """
        For harmonic oscillator eigenstates (which have definite parity),
        ⟨x⟩ = 0 because V(x) is even.
        """
        result = compute_quantum_harmonic_oscillator(num_eigenstates=5)
        x = result["x"]
        eigenstates = result["eigenstates"]

        for i in range(eigenstates.shape[1]):
            psi = eigenstates[:, i]
            exp_x = trapezoid(np.conj(psi) * x * psi, x).real

            assert np.abs(exp_x) < 1e-6, \
                f"Eigenstate {i}: ⟨x⟩ = {exp_x:.2e}, expected 0"

    def test_expectation_p_is_zero_real_wavefunction(self):
        """
        Eigenstates of harmonic oscillator are real, so ⟨p⟩ = 0.
        """
        result = compute_quantum_harmonic_oscillator(num_eigenstates=3)
        x = result["x"]
        eigenstates = result["eigenstates"]
        dx = x[1] - x[0]

        for i in range(eigenstates.shape[1]):
            psi = eigenstates[:, i]

            # p̂ψ = -iℏ dψ/dx (ℏ=1)
            dpsi_dx = np.gradient(psi, dx)
            momentum_action = -1j * dpsi_dx

            exp_p = trapezoid(np.conj(psi) * momentum_action, x).real

            assert np.abs(exp_p) < 1e-6, \
                f"Eigenstate {i}: ⟨p⟩ = {exp_p:.2e}, expected 0"


class TestAnalyticalFormulas:
    """Test helper functions for analytical solutions."""

    def test_eigenvalue_formula(self):
        """E_n = ℏω(n + 1/2)"""
        omega = 1.5
        hbar = 1.0
        n_max = 10

        energies = analytical_harmonic_eigenvalues(n_max, omega=omega, hbar=hbar)

        for n, E_n in enumerate(energies):
            E_expected = hbar * omega * (n + 0.5)
            assert np.isclose(E_n, E_expected)

    def test_period_formula(self):
        """Classical period T = 2π/ω"""
        omega = 0.5
        T = analytical_harmonic_period(omega=omega)

        T_expected = 2 * np.pi / omega
        assert np.isclose(T, T_expected)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
