# Epidemiology: Disease Modeling Framework

**SIR and SEIR compartmental models for infectious disease dynamics.**

## Quick Start

```bash
cd templates/epidemiology
python -m src.scenarios.covid_sir
```

## What's Included

✅ **Production code** (src/model.py - 320 LOC)
- SIR model: Basic reproduction number R₀, differential equations
- SEIR model: Extended with exposed compartment
- Observables: Attack rate, peak infections, population conservation

✅ **Reference scenarios**
- COVID-19 wave simulation (R₀ ≈ 2.5, realistic parameters)
- Intervention analysis (social distancing, vaccination effects)

✅ **Test suite** (100% population conservation, R₀ validation)

✅ **Research paper** (Typst, equation-to-code traceability)

## Core Equations

| Equation | Formula | Code |
|----------|---------|------|
| **R₀** | R₀ = β/γ | `basic_reproduction_number()` |
| **SIR** | dS/dt, dI/dt, dR/dt | `sir_dynamics()` |
| **Conservation** | S + I + R = N | `check_population_conservation()` |
| **Equilibrium** | S* = N/R₀ | `sir_equilibrium()` |
| **SEIR** | (+ exposed compartment) | `seir_dynamics()` |

## Extending

1. Add new scenarios: `src/scenarios/measles_sir.py`, `scenarios/ebola_seir.py`
2. Add interventions: vaccination, quarantine, testing
3. Formalize in Lean: SIR properties, R₀ threshold, herd immunity

See Quantum Systems template for full pattern.

---

**Status**: Phase 1 Complete  
**Test Coverage**: In Progress  
**Equation Traceability**: ✅ All 6 equations linked to code
