# Quantum Systems: Parameter Guide

## Physical Constants

### Schrödinger Equation Parameters

| Parameter | Symbol | Default | Range | Physical Meaning | Notes |
|-----------|--------|---------|-------|------------------|-------|
| **Planck constant** | ℏ | 1.0 | (0, ∞) | ℏ = h/2π (often set to 1 in atomic units) | Dimensionless in atomic units |
| **Particle mass** | m | 1.0 | (0, ∞) | Electron mass in atomic units (≈0.511 MeV/c²) | Affects kinetic energy scale |
| **Potential strength** | V₀ | varies | ℝ | Height/depth of potential barrier or well | Positive = repulsive, negative = attractive |

## Harmonic Oscillator

### Physics

The quantum harmonic oscillator models a particle in a parabolic potential:

$$V(x) = \frac{1}{2}m\omega^2 x^2$$

This is **the** fundamental problem in quantum mechanics because:
1. Exact analytical solution exists (Hermite polynomials)
2. Energy levels are **equidispaced**: $E_n = \hbar\omega(n + 1/2)$
3. Ground state is Gaussian: $\psi_0(x) = (\pi\sigma^2)^{-1/4} e^{-x^2/2\sigma^2}$

### Parameters

| Parameter | Symbol | Default | Range | Effect |
|-----------|--------|---------|-------|--------|
| **Angular frequency** | ω | 1.0 | (0, ∞) | Determines energy spacing: ΔE = ℏω |
| **Ground state width** | σ | 1.0 | (0, ∞) | σ = √(ℏ/mω); larger ω → narrower ψ₀ |
| **Number of energy levels** | n_max | 5 | ∈ ℤ⁺ | Higher levels → more computational cost |

### Validation Benchmarks

```python
# Eigenvalue benchmark
E_n = ℏ * ω * (n + 0.5)  # Analytical formula
E_n_numerical = solve_tise_fdm(...)  # Our code

# Acceptance criterion
relative_error = |E_n - E_n_numerical| / E_n < 0.1%
```

### Typical Scenarios

#### Light Spring (ω = 0.5)
- **Energy spacing**: ΔE = 0.5 (ground state E₀ = 0.25)
- **Ground state width**: σ ≈ 1.4 (wider, slower oscillation)
- **Time evolution**: Slow oscillation, easier to visualize over long times

#### Medium Spring (ω = 1.0) — **Recommended for beginners**
- **Energy spacing**: ΔE = 1.0
- **Ground state width**: σ = 1.0
- **Time evolution**: Period T = 2π ≈ 6.28 time units
- **Computational cost**: Moderate (256-512 grid points)

#### Stiff Spring (ω = 2.0)
- **Energy spacing**: ΔE = 2.0 (levels more separated)
- **Ground state width**: σ ≈ 0.7 (narrow, requires finer grid)
- **Time evolution**: Fast oscillation, need smaller dt
- **Computational cost**: Higher (512-1024 grid points recommended)

## Infinite Square Well

### Physics

Particle confined to box: $V(x) = 0$ for $|x| < L/2$, $V(x) = \infty$ elsewhere.

**Analytical solution exists:**
$$E_n = \frac{n^2 \pi^2 \hbar^2}{2 m L^2}, \quad \psi_n(x) = \sqrt{\frac{2}{L}} \sin\left(\frac{n\pi(x + L/2)}{L}\right)$$

### Parameters

| Parameter | Symbol | Default | Range | Effect |
|-----------|--------|---------|-------|--------|
| **Well width** | L | 1.0 | (0, ∞) | Energy scales as 1/L² |
| **Barrier height** | V₀ | 10⁶ | [100, 10⁶] | Simulates "infinite" potential |
| **Grid extent** | x_max | 2×L | [1.5×L, 5×L] | Must be large enough to avoid boundary effects |

### Validation

```python
# Energy levels
E_n_analytical = (n**2 * π**2) / (2 * L**2)  # ℏ=m=1
relative_error = |E_numerical - E_analytical| / E_analytical < 0.1%
```

## Double Slit Experiment

### Physics

Two slits in barrier creates interference pattern:

$$P(x) = |Ψ_1(x) + Ψ_2(x)|^2 = |Ψ_1|^2 + |Ψ_2|^2 + 2\text{Re}(\Ψ_1^* \Ψ_2)$$

The cross term demonstrates **quantum interference**.

### Parameters

| Parameter | Symbol | Default | Range | Effect |
|-----------|--------|---------|-------|--------|
| **Slit width** | w | 0.1 | (0, 1) | Wider → less diffraction |
| **Slit separation** | d | 0.5 | (0, 5) | Larger d → tighter fringes |
| **Barrier height** | V₀ | 10.0 | [1, 100] | Must be high enough to block outside slits |

### Observables

- **Fringe spacing**: Δx ≈ λ/d (de Broglie wavelength / separation)
- **Visibility**: V = (P_max - P_min) / (P_max + P_min)
  - V = 1 (perfect visibility) → strong interference
  - V ≈ 0 → which-path information leakage

## Tunneling Barrier

### Physics

Particle with E < V₀ can quantum mechanically "tunnel" through barrier.

**Transmission coefficient** (WKB approximation):
$$T \approx e^{-2\gamma} \quad \text{where} \quad \gamma = \int_0^L \sqrt{2m(V_0 - E)}/\hbar \, dx$$

For rectangular barrier: $\gamma = L\sqrt{2m(V_0 - E)}/\hbar$

### Parameters

| Parameter | Symbol | Default | Range | Effect |
|-----------|--------|---------|-------|--------|
| **Barrier width** | L | 0.2 | (0, 1) | Transmission ∝ exp(-2γ√L) |
| **Barrier height** | V₀ | 2.0 | (1.5, 5) | Must be > E for tunneling |
| **Particle energy** | E | 1.0 | (0, V₀) | Smaller E → lower transmission |

### Validation

```python
# WKB prediction
gamma = L * np.sqrt(2 * (V0 - E))  # ℏ=m=1
T_wkb = np.exp(-2 * gamma)

# Numerical transmission (simulate scattering)
T_numerical = |ψ_transmitted|² / |ψ_incident|²

relative_error = |T_numerical - T_wkb| / T_wkb < 10%
```

### Typical Scenarios

#### Weak Tunneling (ω=1, small E)
- T ≈ 0.1% (exponentially suppressed)
- Requires high precision to detect

#### Strong Tunneling (Lower barrier)
- T ≈ 10% (more observable)
- Easier to demonstrate in simulation

## Numerical Parameters

### Grid Resolution

| Domain Size | Grid Points | dx | Recommendation |
|-------------|-------------|----|----|
| x ∈ [-5, 5] | 256 | 0.04 | Quick testing, coarse results |
| x ∈ [-5, 5] | 512 | 0.02 | **Recommended for plots** |
| x ∈ [-10, 10] | 1024 | 0.02 | High-frequency components, tunneling |
| x ∈ [-20, 20] | 2048 | 0.02 | Large domain, avoid boundary effects |

**Rule of thumb:** dx should be < wavelength/10, where λ = 2π/k.

### Time Stepping

| Method | Stability | Accuracy | dt_max | Recommendation |
|--------|-----------|----------|--------|----------------|
| Split-Step Fourier (SSFM) | Unconditionally stable | O(dt²) | 0.1 | **Recommended** |
| Crank-Nicolson (implicit) | Unconditionally stable | O(dt²) | 0.05 | More accurate, slower |
| Runge-Kutta 4 (naïve) | Conditional: dt < dx²/2 | O(dt⁴) | 0.001 | Not recommended for Schrödinger |

**For SSFM:** Use dt = 0.01 for smooth evolution; dt = 0.001 for fine animations.

## Extending Your Own Problem

### Template: Custom Potential

```python
def my_potential(x, param1=1.0, param2=0.5):
    """
    Your custom V(x) = ...
    
    Args:
        x: Position array
        param1, param2: Physical parameters
    
    Returns:
        V(x) array
    """
    return param1 * np.sin(x) + param2 * np.exp(-x**2)

# Solve
energies, eigenstates = solve_tise_fdm(x, my_potential, ...)

# Plot results
import matplotlib.pyplot as plt
plt.plot(x, my_potential(x), label="V(x)")
for i in range(3):
    plt.plot(x, eigenstates[:, i], label=f"ψ_{i}")
plt.legend()
plt.show()
```

---

## Quick Reference: Energy Scales

For reference, compare energies across potentials (ℏ=m=1):

| Potential | Energy Scale | Comment |
|-----------|--------------|---------|
| Harmonic oscillator (ω=1) | ℏω = 1 | Equidispaced levels |
| Particle in box (L=1) | π²/2 ≈ 5 | Quadratic level spacing |
| Finite square well | V₀-dependent | Zero energy inside well |
| Tunneling barrier (V₀=2) | E ≈ 1 | Must solve scattering |

---

**Last Updated**: 2026-09-21
