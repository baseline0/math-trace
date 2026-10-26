"""
Scenario: Bode Plot Analysis (Intermediate)

Frequency response of the second-order prototype H(s) = ω_n² / (s² + 2ζω_n·s + ω_n²).
Magnitude and phase versus frequency show how damping shapes the resonance peak and the bandwidth.

Scope: this is the prototype with no delay or extra poles, so it has no finite gain or phase margins.
The analysis reports the resonance peak, its frequency, and the -3 dB bandwidth.
"""

import numpy as np


def frequency_response(omega: np.ndarray, omega_n: float, zeta: float) -> np.ndarray:
    """
    Complex frequency response H(jω) = ω_n² / (ω_n² - ω² + j·2ζω_n·ω).

    Args:
        omega: Angular frequencies in rad/s
        omega_n: Natural frequency in rad/s
        zeta: Damping ratio, dimensionless

    Returns:
        Complex H(jω) at each frequency
    """
    return omega_n**2 / (omega_n**2 - omega**2 + 1j * 2.0 * zeta * omega_n * omega)


def magnitude_db(response: np.ndarray) -> np.ndarray:
    """Magnitude in decibels, 20·log10(|H|)."""
    return 20.0 * np.log10(np.abs(response))


def phase_deg(response: np.ndarray) -> np.ndarray:
    """Phase in degrees, in the range (-180, 0] for this prototype."""
    return np.degrees(np.angle(response))


def resonance_frequency(omega_n: float, zeta: float) -> float | None:
    """Peak frequency ω_r = ω_n·√(1 - 2ζ²). None when ζ ≥ 1/√2, where the magnitude has no peak."""
    if zeta >= 1.0 / np.sqrt(2.0):
        return None
    return float(omega_n * np.sqrt(1.0 - 2.0 * zeta**2))


def resonance_peak(zeta: float) -> float:
    """Peak magnitude M_r = 1 / (2ζ·√(1 - ζ²)), as a ratio to the DC gain. 1.0 when there is no peak."""
    if zeta >= 1.0 / np.sqrt(2.0):
        return 1.0
    return float(1.0 / (2.0 * zeta * np.sqrt(1.0 - zeta**2)))


def bandwidth_3db(omega_n: float, zeta: float) -> float:
    """-3 dB bandwidth ω_bw = ω_n·√(1 - 2ζ² + √(2 - 4ζ² + 4ζ⁴))."""
    inner = 1.0 - 2.0 * zeta**2 + np.sqrt(2.0 - 4.0 * zeta**2 + 4.0 * zeta**4)
    return float(omega_n * np.sqrt(inner))


def analyse(omega_n: float, zeta: float, omega: np.ndarray | None = None) -> dict:
    """
    Compute the Bode summary on a frequency grid and compare it with the closed-form values.

    Returns a dict with the grid, magnitude and phase, the analytic and grid-measured resonance,
    the analytic and grid-measured bandwidth, and the phase at ω_n.
    """
    if omega is None:
        omega = np.logspace(-2, 2, 20001) * omega_n

    response = frequency_response(omega, omega_n, zeta)
    magnitude = np.abs(response)
    grid_peak_index = int(np.argmax(magnitude))

    analytic_peak_frequency = resonance_frequency(omega_n, zeta)
    above_half_power = magnitude >= 1.0 / np.sqrt(2.0)
    grid_bandwidth = float(omega[np.where(above_half_power)[0][-1]])

    phase_at_natural = phase_deg(frequency_response(np.array([omega_n]), omega_n, zeta))[0]

    return {
        "omega": omega,
        "magnitude_db": magnitude_db(response),
        "phase_deg": phase_deg(response),
        "omega_n": omega_n,
        "zeta": zeta,
        "analytic_peak_db": 20.0 * np.log10(resonance_peak(zeta)),
        "grid_peak_db": float(magnitude_db(response)[grid_peak_index]),
        "analytic_peak_frequency": analytic_peak_frequency,
        "grid_peak_frequency": float(omega[grid_peak_index]),
        "analytic_bandwidth_3db": bandwidth_3db(omega_n, zeta),
        "grid_bandwidth_3db": grid_bandwidth,
        "phase_at_natural_frequency_deg": float(phase_at_natural),
    }


if __name__ == "__main__":
    print("=" * 70)
    print("Bode Plot Analysis: second-order prototype, ω_n = 1 rad/s")
    print("=" * 70)

    for zeta in (0.1, 0.3, 0.7):
        result = analyse(omega_n=1.0, zeta=zeta)
        print(f"\nζ = {zeta}")
        print(f"  Resonance peak: {result['grid_peak_db']:.2f} dB at ω = {result['grid_peak_frequency']:.3f} rad/s")
        print(f"  -3 dB bandwidth: {result['grid_bandwidth_3db']:.3f} rad/s")
        print(f"  Phase at ω_n: {result['phase_at_natural_frequency_deg']:.1f}°")

    print("\n✅ Bode analysis scenario complete")
