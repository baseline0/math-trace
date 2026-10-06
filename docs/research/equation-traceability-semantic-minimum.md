# Equation Traceability: Semantic Minimum Standard

**Date**: 2026-09-30
**Evidence Base**: Epidemiology reference contract (MATH-TRACE-REFERENCE-HARDENING-001) + Quantum harmonic oscillator reference contract (MATH-TRACE-QUANTUM-SYSTEMS-REFERENCE-CONTRACT-001)
**Status**: DESIGN REFERENCE (no shared framework authorized yet)

---

## Introduction

Two materially different reference domains have been implemented using domain-specific approaches:

1. **Epidemiology (SIR/SEIR)**: Analytical compartmental model with deterministic outputs
2. **Quantum (Harmonic Oscillator)**: Numerical PDE with discretization and propagation error

Both satisfy a common semantic contract for equation traceability, but through different implementations, file layouts, artifact formats, and documentation styles.

This document defines the **semantic minimum**—the essential metadata required for credible equation traceability—without prescribing how any domain must implement it.

---

## Semantic Minimum: Six Required Fields

Every equation in a reference template must have:

### 1. Equation Identity and Display Form

**Purpose**: Unique, unambiguous identification and readability.

**Required content**:
- `equation_id`: A unique identifier (e.g., `sir_beta_transmission`, `quantum_eigenvalue_formula`)
- `display_name`: Human-readable name (e.g., "Frequency-Dependent Transmission", "Harmonic Oscillator Eigenvalue Spectrum")
- `expression`: The equation in a standard form (LaTeX, SymPy, or plain-text mathematical notation)

**Example (Epidemiology)**:
```yaml
equation_id: sir_frequency_dependent_transmission
display_name: Frequency-Dependent Transmission Rate
expression: "dI/dt = β * S * I / N - γ * I"
```

**Example (Quantum)**:
```yaml
equation_id: quantum_harmonic_eigenvalue_spectrum
display_name: Harmonic Oscillator Energy Eigenvalues
expression: "E_n = ℏ * ω * (n + 1/2)"
```

### 2. Symbol Definitions with Units and Conventions

**Purpose**: Eliminate ambiguity in what each symbol means and what units/conventions apply.

**Required content**:
- `symbol_definitions`: List of {symbol, meaning, units_or_convention}

**Example (Epidemiology)**:
```yaml
symbol_definitions:
  - symbol: "β"
    meaning: "Transmission rate (force of infection)"
    convention: "Per-capita rate; individuals/contact/time"
  - symbol: "S, I, R, N"
    meaning: "Susceptible, Infected, Recovered, total population"
    convention: "Counts; dimensionless (normalized by N)"
  - symbol: "γ"
    meaning: "Recovery rate"
    convention: "Per-capita rate; time^-1"
```

**Example (Quantum)**:
```yaml
symbol_definitions:
  - symbol: "ℏ"
    meaning: "Reduced Planck constant"
    convention: "Atomic units (set to 1.0 in this implementation)"
  - symbol: "ω"
    meaning: "Angular frequency of harmonic potential"
    convention: "Atomic units (default ω=1.0); 1 a.u. ≈ 2.42e17 Hz"
  - symbol: "n"
    meaning: "Quantum state index"
    convention: "Integer n=0,1,2,... (ground state n=0)"
  - symbol: "E_n"
    meaning: "Energy eigenvalue for state n"
    convention: "Atomic units (Hartree); 1 a.u. ≈ 27.2 eV"
```

### 3. Explicit Assumptions and Limitations

**Purpose**: Define the scope under which the equation is valid.

**Required content**:
- `assumptions`: List of explicit domain/applicability statements
- `limitations`: List of known boundaries or simplifications

**Example (Epidemiology)**:
```yaml
assumptions:
  - "Closed population (no births, deaths, immigration)"
  - "Homogeneous mixing (well-mixed population)"
  - "Frequency-dependent transmission (β·S·I/N, not β·S·I)"
  - "Permanent immunity after recovery"
  - "Exponential recovery times (constant rate γ)"
  - "No vaccination, intervention, or behavior change"

limitations:
  - "No spatial structure (all-to-all contact)"
  - "No age/risk stratification"
  - "No stochastic effects (deterministic compartmental dynamics)"
  - "Parameter values must be population-specific"
```

**Example (Quantum)**:
```yaml
assumptions:
  - "Finite spatial domain x ∈ [-5, 5] (atomic units)"
  - "Time-independent harmonic potential V(x) = (1/2)*ω²*x²"
  - "Atomic units: ℏ=1, m=1, e=1"
  - "Finite-difference discretization on 512-point grid"
  - "Split-step Fourier time propagation (SSFM) with O(dt²) accuracy"

limitations:
  - "Boundary condition: ψ≈0 at domain edges (implicit Dirichlet)"
  - "Eigenvalue accuracy: O(dx²) error; ~0.1% relative error for first 5 levels at 512 points"
  - "Normalization: Trapezoidal quadrature error ~1e-7 to 1e-8"
  - "Finite-difference momentum operator: underestimates p² by ~20% due to boundary effects"
  - "Double-slit and tunneling potentials: implemented but not validated in this reference contract"
```

### 4. Validation Links to Tests or Artifacts

**Purpose**: Connect the equation to concrete evidence (test assertions, numerical results, or output artifacts).

**Required content**:
- `validation_links`: List of {test_id or artifact_id, assertion or measured_property}

**Example (Epidemiology)**:
```yaml
validation_links:
  - test_id: "test_r0_formula_consistency"
    assertion: "R₀ = β/γ is enforced in model definition"
  - test_id: "test_frequency_dependent_transmission"
    assertion: "Transmission follows β·S·I/N, not β·S·I"
  - artifact_id: "scenario_covid_parameters"
    measured_property: "R₀≈2.5 matches historical estimates"
```

**Example (Quantum)**:
```yaml
validation_links:
  - test_id: "TestHarmonicEigenvalues::test_eigenvalue_accuracy_first_5_levels"
    assertion: "E_n matches analytical values to 0.1% (1e-3 relative error)"
  - test_id: "TestNormalization::test_eigenstate_normalization"
    assertion: "∫|ψ|²dx = 1 ± 1e-6 for all eigenstates"
  - test_id: "TestEnergyConservation::test_ground_state_energy_conservation"
    assertion: "|E(t) - E(0)|/E(0) < 1e-6 over 10 oscillation periods"
  - test_id: "TestUncertaintyPrinciple"
    assertion: "Δx·Δp ≥ ℏ/2 for ground state"
```

### 5. Source Location in Code

**Purpose**: Enable traceability to the actual implementation.

**Required content**:
- `source_location`: File path, class/function name, and line number range

**Example (Epidemiology)**:
```yaml
source_location:
  file: "templates/epidemiology/src/model.py"
  class_or_function: "SIRModel"
  method: "compute_transmission_rate"
  lines: "45-62"
  reference: "Line 55: beta_SI = beta * S * I / N"
```

**Example (Quantum)**:
```yaml
source_location:
  file: "templates/quantum-systems/src/model.py"
  class_or_function: "QuantumHarmonicOscillator"
  method: "harmonic_potential"
  lines: "78-85"
  reference: "Line 82: V = 0.5 * omega**2 * x**2"
```

### 6. Scope Boundaries

**Purpose**: Clarify what is in and out of scope for this reference.

**Required content**:
- `in_scope`: Equations, scenarios, and validations that are part of this reference
- `out_of_scope`: Existing code or related topics that are deliberately excluded

**Example (Epidemiology)**:
```yaml
in_scope:
  - "SIR and SEIR compartmental models"
  - "Frequency-dependent transmission (β·S·I/N)"
  - "R₀ = β/γ formula and interpretation"
  - "Parameter provenance (COVID-19, Measles, Ebola scenarios)"
  - "17 contract tests validating model structure and reproducibility"

out_of_scope:
  - "Spatial epidemic models (metapopulation dynamics)"
  - "Stochastic SEIR (Gillespie algorithm)"
  - "Age-stratified or risk-stratified variants"
  - "Vaccination or intervention strategies"
  - "Future scenario expansions (dengue, influenza, etc.)"
```

**Example (Quantum)**:
```yaml
in_scope:
  - "Harmonic oscillator (TISE and TDSE)"
  - "Eigenvalue spectrum: E_n = ℏω(n+1/2)"
  - "Normalization, energy conservation, uncertainty principle"
  - "6 physics-contract tests covering 20 test cases"
  - "Numerical methods: FDM (eigenvalues), SSFM (time evolution)"

out_of_scope:
  - "Double-slit interference (potential exists; not validated)"
  - "Quantum tunneling (potential exists; not validated)"
  - "3D Schrödinger equation"
  - "Relativistic quantum mechanics"
  - "Interactive visualizations or parameter sweeps"
```

---

## Implementation Diversity: How Two Domains Satisfy the Minimum

Both references satisfy the semantic minimum through **domain-specific implementations**.

### Epidemiology: Artifact-Centric Approach
- **Validation artifacts**: Scenario JSON files with parameter sets and expected outputs
- **Equation storage**: `equations.json` (machine-readable export from model.py)
- **Test framework**: 17 pytest contract tests grouped by risk category
- **Documentation**: `README.md`, `paper.typ` (Typst paper), `PARAMETERS.md`
- **Assumptions**: Embedded in paper narrative and test docstrings

### Quantum: Test-Centric Approach
- **Validation artifacts**: Test assertions with numerical tolerances
- **Equation storage**: Source code (`model.py`) + documentation (`PARAMETERS.md`)
- **Test framework**: 6 contract categories (20 tests) with explicit failure-mode mapping
- **Documentation**: `PARAMETERS.md` (189 lines with tolerance provenance), `README.md`
- **Assumptions**: Explicit table in PARAMETERS.md with numerical justification

### Key Insight

Both implementations satisfy the six required semantic fields without forcing identical file layouts, export schemas, or build tools. This flexibility is a feature, not a bug.

---

## When to Build Shared Tooling

A shared framework, export schema, or cross-domain index is authorized **only if all three conditions are met**:

1. **A third domain independently arrives at the same semantic structure** (not forced by tooling)
2. **Concrete user need exists** (e.g., cross-domain equation index, citation generation, automated format conversion)
3. **Maintenance cost is justified by real usage** (not speculative)

**Until then**: Keep domain-specific implementations. Document the semantic minimum as a design reference.

---

## Explicit Non-Authorization

This document identifies a semantic minimum observed across two validated reference domains. It does **not** authorize:

- A shared file layout, export schema, or build tool
- A generic equation-trace framework or CLI
- Cross-domain paper or artifact generation infrastructure
- Any implementation work until a third domain independently validates the same semantic fields and a concrete user need emerges

**Future work must demonstrate**:
1. A third reference domain with independently derived equation traceability
2. A specific user or stakeholder need for shared tooling
3. A cost-benefit analysis showing maintenance burden is justified

---

## Summary: No Shared Framework Yet

| Question | Answer |
|----------|--------|
| Does a semantic minimum exist? | **Yes** — six required fields |
| Should domains use identical layouts? | **No** — domain-specific implementations are fine |
| Should we build a shared export schema? | **Not yet** — wait for third domain + user need |
| Should we build paper-build infrastructure? | **Not yet** — each domain should choose its own artifact strategy |
| What should we do now? | **Document the semantic minimum (this note) and use it as a design reference for future templates** |

---

**Document Status**: REFERENCE (no framework changes authorized)
**Next Review**: After third domain reference contract is complete
**Audience**: Math-trace contributors, portfolio-ops governance
**Last Updated**: 2026-09-30
