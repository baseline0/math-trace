# Thermodynamics: Ideal Gas & Carnot Cycle

**Fundamental thermodynamic equations: PV=nRT, First Law, entropy, and Carnot efficiency.**

## Quick Start

```bash
cd templates/thermodynamics
python -m src.scenarios.ideal_gas
python -m src.scenarios.polytropic_processes
python -m src.scenarios.phase_diagrams
```

## Core Equations

| Equation | Formula | Code |
|----------|---------|------|
| **Ideal Gas** | PV = nRT | `ideal_gas_pressure()` |
| **Internal Energy** | U = n·C_v·T | `internal_energy()` |
| **First Law** | dU = δQ - δW | `first_law()` |
| **Entropy** | S = n·C_v·ln(T) + n·R·ln(V) + S₀ | `entropy()` |
| **Carnot η** | η = 1 - (T_c/T_h) | `carnot_efficiency()` |
| **Polytropic work** | W = (P₂V₂ - P₁V₁)/(1 - n), n ≠ 1 | `polytropic_work()` |
| **Maxwell relations** | (∂S/∂V)_T = (∂P/∂T)_V; (∂S/∂P)_T = -(∂V/∂T)_P | `maxwell_check()` |

## Scenarios

- **Ideal Gas**: PVT relations and thermodynamic properties (`src/scenarios/ideal_gas.py`)
- **Carnot Cycle**: reversible heat engine, efficiency, work extraction
- **Polytropic Processes** (`src/scenarios/polytropic_processes.py`): isobaric, isothermal, adiabatic, and isochoric paths of one ideal gas. Work, internal energy change, and heat. The tests check heat against independent expressions (zero on the adiabat, Q = nC_p·ΔT on the isobar), not the First Law as an identity
- **Phase Diagrams** (`src/scenarios/phase_diagrams.py`): P-V isotherms, T-S curves, and P-T isochores for an ideal gas, with both Maxwell relations checked by finite differences. An ideal gas has no phase transition, so there is no coexistence curve or critical point

Tests: `uv run pytest src/tests`

---

**Status**: Phase 1 foundation complete
**References**: Callen (1985), Kittel & Kroemer (1980)
