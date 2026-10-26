# Control Systems: Linear Systems & PID Control

**State-space analysis and feedback controller design.**

## Quick Start

```bash
cd templates/control-systems
python -m src.scenarios.dc_motor
python -m src.scenarios.mass_spring_damper
python -m src.scenarios.bode_plot_analysis
```

## Core Equations

| Equation | Formula | Code |
|----------|---------|------|
| **State-space** | ẋ = Ax + Bu; y = Cx + Du | `LinearSystem` |
| **PID Control** | u = K_p·e + K_i·∫e + K_d·ė | `PIDController` |
| **Steady-state error** | e_ss = 1/(1+K_p) | `steady_state_error()` |
| **Settling time** | t_s ≈ 4/(ζ·ω_n) | `second_order_response()` |
| **Stability** | Re(λ) < 0 for all poles | `is_stable()` |
| **Damping ratio** | ζ = c / (2√(km)) | `damping_ratio()` |
| **Overshoot** | M_p = 100·exp(-πζ/√(1-ζ²)) | `percent_overshoot()` |
| **Resonance peak** | M_r = 1 / (2ζ√(1-ζ²)) | `resonance_peak()` |
| **-3 dB bandwidth** | ω_bw = ω_n√(1-2ζ²+√(2-4ζ²+4ζ⁴)) | `bandwidth_3db()` |

## Scenarios

- **DC Motor** (REFERENCE CONTRACT): Speed control via PID; realistic J, b, K parameters; deterministic baseline with reproducible contract tests
  - Reference scenario documentation: `src/scenarios/dc_motor.py`
  - Contract tests: `src/tests/test_dc_motor_contract.py` (6 contract categories, 14 behavioral tests with explicit finite-horizon semantics)
  - Baseline metrics: `baseline_metrics.json` (captured performance data with full parameterization; finite-horizon interpretation: settling_time status + terminal_tracking_error, not asymptotic steady-state)

- **Mass-Spring-Damper**: m·ẍ + c·ẋ + k·x = F. Damping regimes, the overshoot formula checked against a simulated step, and convergence to F/k
  - Scenario: `src/scenarios/mass_spring_damper.py`; tests: `src/tests/test_mass_spring_damper.py`

- **Bode Plot Analysis**: Frequency response of the second-order prototype. Resonance peak, its frequency, and -3 dB bandwidth, each checked against the closed form. The prototype has no delay or extra poles, so it has no gain or phase margins
  - Scenario: `src/scenarios/bode_plot_analysis.py`; tests: `src/tests/test_bode_plot_analysis.py`

---

**Status**: Phase 1 foundation complete; DC Motor reference contract hardened
**References**: Ogata (2010), Franklin et al. (2010)
