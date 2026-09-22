# Thermodynamics: Ideal Gas & Carnot Cycle

**Fundamental thermodynamic equations: PV=nRT, First Law, entropy, and Carnot efficiency.**

## Quick Start

```bash
python -m src.scenarios.ideal_gas
```

## Core Equations

| Equation | Formula | Code |
|----------|---------|------|
| **Ideal Gas** | PV = nRT | `ideal_gas_pressure()` |
| **Internal Energy** | U = n·C_v·T | `internal_energy()` |
| **First Law** | dU = δQ - δW | `first_law()` |
| **Entropy** | S = n·C_v·ln(T) + n·R·ln(V) + S₀ | `entropy()` |
| **Carnot η** | η = 1 - (T_c/T_h) | `carnot_efficiency()` |

---

**Status**: Phase 1 foundation complete  
**References**: Callen (1985), Kittel & Kroemer (1980)
