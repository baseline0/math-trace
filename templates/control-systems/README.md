# Control Systems: Linear Systems & PID Control

**State-space analysis and feedback controller design.**

## Quick Start

```bash
cd templates/control-systems
python -m src.scenarios.dc_motor
```

## Core Equations

| Equation | Formula | Code |
|----------|---------|------|
| **State-space** | ẋ = Ax + Bu; y = Cx + Du | `LinearSystem` |
| **PID Control** | u = K_p·e + K_i·∫e + K_d·ė | `PIDController` |
| **Steady-state error** | e_ss = 1/(1+K_p) | `steady_state_error()` |
| **Settling time** | t_s ≈ 4/(ζ·ω_n) | `second_order_response()` |
| **Stability** | Re(λ) < 0 for all poles | `is_stable()` |

## Scenarios

- **DC Motor** (REFERENCE CONTRACT): Speed control via PID; realistic J, b, K parameters; deterministic baseline with reproducible contract tests
  - Reference scenario documentation: `src/scenarios/dc_motor.py`
  - Contract tests: `src/tests/test_dc_motor_contract.py` (6 contract categories, 14 behavioral tests with explicit finite-horizon semantics)
  - Baseline metrics: `baseline_metrics.json` (captured performance data with full parameterization; finite-horizon interpretation: settling_time status + terminal_tracking_error, not asymptotic steady-state)
  
- **Mass-Spring-Damper**: Fundamental 2nd order system; ζ effects on response

---

**Status**: Phase 1 foundation complete; DC Motor reference contract hardened  
**References**: Ogata (2010), Franklin et al. (2010)
