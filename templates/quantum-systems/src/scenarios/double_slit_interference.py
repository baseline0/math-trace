"""
Scenario: Double-Slit Interference (Intermediate)

Far-field (Fraunhofer) pattern of a monochromatic matter wave through two slits of width w and
separation d, observed on a screen a distance L away. For small angles, with y the screen position:

    I(y) = I₀ · sinc²(π·w·y / (λ·L)) · cos²(π·d·y / (λ·L))

The cos² term gives the fringes, with spacing Δy = λ·L / d. The sinc² envelope from the single-slit
width w suppresses fringes outside the central lobe. The matter wavelength is the de Broglie wavelength
λ = h / (m·v).

Scope: this is the far-field closed form, not a time-dependent wavepacket simulation. It describes
where the fringes sit and how sharp they are, which is what the Schrödinger model predicts for the screen.
"""

import numpy as np
from scipy.signal import find_peaks

PLANCK = 6.62607015e-34  # J·s
ELECTRON_MASS = 9.1093837015e-31  # kg


def de_broglie_wavelength(mass: float, speed: float) -> float:
    """de Broglie wavelength λ = h / (m·v) in metres."""
    return float(PLANCK / (mass * speed))


def fringe_spacing(wavelength: float, screen_distance: float, separation: float) -> float:
    """Fringe spacing Δy = λ·L / d on the screen, in metres."""
    return float(wavelength * screen_distance / separation)


def intensity(y: np.ndarray, wavelength: float, screen_distance: float, width: float, separation: float) -> np.ndarray:
    """
    Relative intensity I(y)/I₀ at screen positions y, from the far-field two-slit formula.

    The value at y = 0 is 1 (the central maximum).
    """
    phase = np.pi * y / (wavelength * screen_distance)
    envelope_argument = width * phase
    envelope = np.ones_like(y, dtype=float)
    nonzero = envelope_argument != 0
    envelope[nonzero] = (np.sin(envelope_argument[nonzero]) / envelope_argument[nonzero]) ** 2
    interference = np.cos(separation * phase) ** 2
    return envelope * interference


def envelope_zero_spacing(wavelength: float, screen_distance: float, width: float) -> float:
    """Distance between successive zeros of the single-slit envelope, λ·L / w."""
    return float(wavelength * screen_distance / width)


def visibility(pattern: np.ndarray) -> float:
    """Fringe visibility V = (I_max - I_min) / (I_max + I_min) over the given samples."""
    i_max = float(np.max(pattern))
    i_min = float(np.min(pattern))
    return (i_max - i_min) / (i_max + i_min)


def fringe_peaks(y: np.ndarray, pattern: np.ndarray) -> np.ndarray:
    """Screen positions of the local maxima of the pattern, sorted by position."""
    peaks, _ = find_peaks(pattern)
    return y[peaks]


def simulate_scenario(
    speed: float = 2.0e6,
    screen_distance: float = 1.0,
    separation: float = 1.0e-6,
    width: float = 2.0e-7,
    half_span: float = 1.5e-3,
    samples: int = 60001,
) -> dict:
    """
    Electron double-slit pattern on a screen, with the analytic fringe spacing and the measured one.

    Defaults: electrons at 2×10⁶ m/s, slits 200 nm wide and 1 μm apart, screen 1 m away.
    """
    wavelength = de_broglie_wavelength(ELECTRON_MASS, speed)
    y = np.linspace(-half_span, half_span, samples)
    pattern = intensity(y, wavelength, screen_distance, width, separation)

    analytic_spacing = fringe_spacing(wavelength, screen_distance, separation)
    peaks = fringe_peaks(y, pattern)
    peaks = peaks[np.abs(peaks) < envelope_zero_spacing(wavelength, screen_distance, width) / 2]
    # Central fringes sit near multiples of Δy. For finite slit width the sinc² envelope slope pulls them toward
    # the centre, so the measured spacing is slightly below λL/d. For a narrow slit the envelope is flat and they match.
    central = np.sort(peaks[np.abs(peaks) <= 2.5 * analytic_spacing])
    measured_spacing = float(np.mean(np.diff(central))) if len(central) > 1 else float("nan")

    return {
        "y": y,
        "intensity": pattern,
        "wavelength": wavelength,
        "analytic_fringe_spacing": fringe_spacing(wavelength, screen_distance, separation),
        "measured_fringe_spacing": measured_spacing,
        "envelope_zero_spacing": envelope_zero_spacing(wavelength, screen_distance, width),
        "central_fringes": len(peaks),
        "visibility": visibility(pattern[np.abs(y) < envelope_zero_spacing(wavelength, screen_distance, width) / 2]),
    }


if __name__ == "__main__":
    result = simulate_scenario()

    print("=" * 70)
    print("Double-Slit Interference: electrons at 2×10⁶ m/s")
    print("=" * 70)
    print(f"\n  de Broglie wavelength: {result['wavelength']:.3e} m")
    print(
        f"  Fringe spacing (λL/d): analytic {result['analytic_fringe_spacing']:.3e} m, "
        f"measured {result['measured_fringe_spacing']:.3e} m"
    )
    print(f"  Envelope zero spacing (λL/w): {result['envelope_zero_spacing']:.3e} m")
    print(f"  Fringes in the central envelope lobe: {result['central_fringes']}")
    print(f"  Visibility inside the lobe: {result['visibility']:.4f}")

    print("\n✅ Double-slit scenario complete")
