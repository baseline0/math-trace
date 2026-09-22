# Epidemiology: Golden Path & Acceptance Checklist

**Status**: Template contract for all other templates to replicate  
**Timeline**: Weeks 2–3  
**Owner**: Mark Alexiuk  
**External Reviewer**: (TBD, external review required Week 6)

---

## Goal

Establish epidemiology template as the **canonical reference** for all other templates (Quantum, Control, GNNs, Thermodynamics). Any template that deviates from this structure must document why.

This prevents scope drift and ensures consistency.

---

## What Epidemiology Will Demonstrate

1. **How to state assumptions**: Every assumption explicit, listed, domains specified
2. **How to define units**: Every variable and parameter has units + domain constraints
3. **How to trace equations**: Every equation linked to source code line + historical source
4. **How to test rigorously**: Success cases + expected failures (what breaks when assumptions violated)
5. **How to document limitations**: Candid, specific (not hedged or cheerful)
6. **How to reproduce**: One command generates entire artifact from scratch
7. **How to verify claims**: Paper equations match code equations character-for-character

---

## Paper Structure: 10-Section Golden Path

### Section 1: Problem Statement (15 mins)

**What to write**: Why epidemiological modeling matters

**Audience**: Readers unfamiliar with epidemiology

**Requirements**:
- [ ] Motivate the problem (disease spread, control strategies)
- [ ] State what this paper addresses specifically (not all of epidemiology, just this model)
- [ ] Explain why tractability matters (can we predict peak infections? test interventions?)

**Example opening**:
> "Disease transmission occurs through a population in stages. Understanding these dynamics enables policymakers to predict peak infection rates and evaluate intervention strategies. This paper presents the classical Susceptible-Infected-Recovered (SIR) and Susceptible-Exposed-Infected-Recovered (SEIR) compartmental models, with complete derivations, assumptions, computational implementations, and verification protocols."

**Deliverable**: 1 section, ~300 words

---

### Section 2: Historical / Source Provenance (15 mins)

**What to write**: Where these equations came from, how notation evolved

**Requirements**:
- [ ] Reference Kermack and McKendrick (1927) — original SIR formulation
- [ ] Note subsequent extensions (SEIR, stochastic variants)
- [ ] Explain why certain notation changes happened (e.g., R₀ vs. R_0 vs. ℜ₀)
- [ ] Cite modern epidemiology textbooks (e.g., Keeling & Rohani 2008)

**Example**:
> "Kermack and McKendrick [1927] introduced the SIR model to describe plague epidemics. Their original formulation used the notation S, I, R for counts and β, γ for transmission and recovery rates. Modern epidemiology extends this with exposed stages (SEIR, Cooke 2005), stochastic effects (Doob 1945), and age/spatial structure (Anderson & May 1991). This paper uses the modern notation while preserving the classical structure."

**Deliverable**: 0.5–1 section, ~250 words

---

### Section 3: Model Assumptions (20 mins)

**What to write**: Every assumption that makes these equations valid

**Format**: Structured list, not prose

**Requirements**:
- [ ] List every assumption (do not omit)
- [ ] Explain why each is needed
- [ ] Mark which assumptions are critical (model breaks if violated) vs. convenience (can be relaxed)
- [ ] Provide domain constraints for each variable

**Example table**:

| Assumption | Rationale | Critical? | Constraint |
|-----------|-----------|-----------|-----------|
| Homogeneous mixing | Equations assume equal contact probability | 🔴 Yes | Fails in isolated communities |
| Recovered immunity permanent | No reinfection | 🟡 Partial | Accuracy degrades >2 years (waning immunity) |
| No vital dynamics | Ignores births/deaths during epidemic | 🟢 No | Valid for acute outbreaks (<1 year) |
| Constant contact rate β | Ignores behavior change | 🟡 Partial | Breaks during lockdowns or awareness campaigns |
| R₀ >> 1 for exponential phase | Assumes early epidemic | 🟢 No | Deferred to peak/decline phase analysis |
| Population size N constant | No migration | 🟢 No | OK for short timescales |

**Deliverable**: 1 section with table + narrative, ~400 words + table

---

### Section 4: Variable and Parameter Definitions (20 mins)

**What to write**: Every symbol defined with units and domain

**Format**: Table

**Requirements**:
- [ ] Every symbol in equations must have entry
- [ ] Specify units (persons, 1/days, dimensionless, etc.)
- [ ] Specify domain (S ∈ [0, N], β > 0, etc.)
- [ ] Give physical interpretation

**Example table**:

| Symbol | Name | Units | Domain | Interpretation |
|--------|------|-------|--------|-----------------|
| S | Susceptible count | persons | [0, N] | Number capable of contracting disease |
| I | Infected count | persons | [0, N] | Number currently infectious |
| R | Recovered count | persons | [0, N] | Number immune from prior infection |
| N | Population size | persons | ℤ⁺ | S + I + R = N (conserved) |
| β | Transmission rate | 1/days | (0, ∞) | Contact frequency × transmission probability |
| γ | Recovery rate | 1/days | (0, ∞) | Inverse of infectious period (1/γ = ~10 days) |
| R₀ | Basic reproduction number | dimensionless | (0, ∞) | Expected secondary cases per primary case |

**Derivation of R₀**:
> "R₀ = β / γ. Interpretation: β defines transmission frequency; γ defines how quickly an infected person recovers. Their ratio gives expected secondary infections."

**Deliverable**: 1 section with table + key definitions, ~300 words + table

---

### Section 5: Dimensional Analysis (15 mins)

**What to write**: Verify every equation is dimensionally consistent

**Format**: Equation-by-equation verification

**Requirements**:
- [ ] For each equation, show dimensions balance
- [ ] For each derived quantity (e.g., R₀), verify dimensionless or correct units

**Example**:

**Equation 1**: dS/dt = -β S I / N
- **LHS**: dS/dt has units [persons/days]
- **RHS**: β [1/days] × S [persons] × I [persons] / N [persons] = [1/days] × [persons] = [persons/days] ✓

**Equation 2**: dI/dt = β S I / N - γ I
- **LHS**: dI/dt has units [persons/days]
- **RHS**: β S I / N [persons/days] - γ I [1/days × persons] = [persons/days] ✓

**Conservation Law**: S + I + R = N
- **Verified**: If dS/dt + dI/dt + dR/dt = 0, then S + I + R is constant.
- **Check**: dS/dt + dI/dt + dR/dt = (-βSI/N) + (βSI/N - γI) + (γI) = 0 ✓

**Deliverable**: 1 short section showing verification for each equation, ~200 words

---

### Section 6: Equation Construction (25 mins)

**What to write**: Derive each equation from first principles; show where assumptions enter

**Format**: Derivation + annotation

**Requirements**:
- [ ] Start from biological mechanism (transmission, recovery)
- [ ] Introduce assumptions explicitly (e.g., "assuming homogeneous mixing...")
- [ ] Show algebraic steps
- [ ] Point to source or textbook reference

**Example (SIR transmission term)**:

**Biological Mechanism**: Infected individuals transmit disease to susceptible individuals.

**Assumption**: Homogeneous mixing (any S can contact any I with equal probability).

**Derivation**:
- Let c = average contact rate per person per day
- Let p = transmission probability per contact
- Then β = c × p (transmissions per person per day)
- In population, number of S-I contacts per day ≈ (β × S × I) / N
  - (Justification: S individuals each contact I individuals at rate β; divide by N to account for mixing in population)
- Therefore: dS/dt = -β S I / N (susceptible decrease due to transmission)
- And: dI/dt += +β S I / N (infected increase from transmission)

**Source**: Keeling & Rohani, "Modeling Infectious Diseases" (2008), §2.1

**Deliverable**: 1–2 sections deriving all 4 core equations (SIR dS/dt, dI/dt, dR/dt; R₀ definition), ~600 words

---

### Section 7: Executable Code (10 mins)

**What to write**: Complete runnable scenario; reference to `src/epidemiology/model.py`

**Requirements**:
- [ ] Show exact code snippet that implements model
- [ ] Highlight equation definitions (dS/dt, dI/dt, dR/dt)
- [ ] Show parameter values for example scenario (COVID-like: R₀≈2, γ≈1/10 days)
- [ ] Explain how to run it

**Example**:

```python
# src/epidemiology/model.py (excerpt)

def sir_rates(S, I, R, N, beta, gamma):
    """Compute SIR rate equations.
    
    Args:
        S: Susceptible count [persons]
        I: Infected count [persons]
        R: Recovered count [persons]
        N: Population size [persons]
        beta: Transmission rate [1/days]
        gamma: Recovery rate [1/days]
    
    Returns:
        (dS/dt, dI/dt, dR/dt)
    
    Assumptions:
        - S + I + R == N (conservation)
        - S, I, R >= 0
        - beta > 0, gamma > 0
        - Homogeneous mixing
    """
    dS_dt = -beta * S * I / N
    dI_dt = beta * S * I / N - gamma * I
    dR_dt = gamma * I
    return dS_dt, dI_dt, dR_dt
```

**Usage**:
```python
# Run scenario
from epidemiology.scenarios import covid_baseline

S, I, R = covid_baseline(days=100)
# Produces Figure 1 (S, I, R trajectories)
```

**Deliverable**: 1 section with code + usage instructions, ~300 words + code

---

### Section 8: Expected Outputs (15 mins)

**What to write**: Qualitatively what happens; numerically what to expect

**Format**: Narrative + example numbers

**Requirements**:
- [ ] Describe trajectory (S decreases, I peaks, R increases)
- [ ] Give quantitative expectations for COVID-like (R₀≈2) scenario
- [ ] Show example output (table or figure legend)

**Example**:

**Qualitative Behavior**:
- S decreases monotonically (people leave susceptible state)
- I rises to peak, then falls (epidemic grows until recovery rate exceeds transmission)
- R increases monotonically (accumulation of recovered)
- At peak infection: dI/dt = 0 ⟹ S = γ/β = 1/R₀

**Quantitative Example** (COVID-like baseline):
- R₀ = 2.0 (two secondary cases per primary)
- γ = 0.1 [1/days] (10-day infectious period)
- β = R₀ × γ = 0.2 [1/days]
- Population: N = 1,000,000
- Initial: S₀ = 999,900, I₀ = 100, R₀ = 0

**Expected Results**:
- Peak I at ~day 25 with ~250,000 concurrent infections
- Total attack rate R(∞) = 750,000 (75% of population)
- Epidemic duration ~100 days

**Deliverable**: 1 section with narrative + table, ~250 words + example outputs

---

### Section 9: Verification Strategy (20 mins)

**What to write**: How to test that code matches equations and assumptions hold

**Format**: Test descriptions + pass/fail criteria

**Requirements**:
- [ ] List test cases (equilibrium, conservation, boundary behavior)
- [ ] For each test: describe what's checked, expected outcome, tolerance
- [ ] Include tests for expected failures (what breaks when assumptions violated)

**Example test suite**:

**Test 1: Equilibrium (SIR)**
```python
# At t=0, compute rates given S, I, R
S, I, R = 500000, 10000, 490000
dS_dt, dI_dt, dR_dt = sir_rates(S, I, R, N=1000000, beta=0.2, gamma=0.1)

# At equilibrium with I=0, rates should be zero
assert abs(dI_dt) < 1e-10
```

**Test 2: Conservation (SIR + SEIR)**
```python
# Integrate 100 days with fixed population
S, I, R = integrate_sir(days=100, ...)
assert abs((S + I + R) - N) < 1e-6  # Tolerance: 1 person
```

**Test 3: R₀ Computation**
```python
# Check R₀ = β / γ
beta, gamma = 0.2, 0.1
R0_computed = compute_r0(beta, gamma)
R0_expected = beta / gamma  # 2.0
assert abs(R0_computed - R0_expected) < 1e-6
```

**Test 4: Expected Failure — Negative Population (Should Reject)**
```python
# Negative S should be rejected
with pytest.raises(ValueError):
    sir_rates(S=-100, I=10, R=50, N=1000, beta=0.2, gamma=0.1)
```

**Test 5: Expected Failure — Non-conservation (Should Detect)**
```python
# If S + I + R ≠ N initially, should warn or error
S, I, R = 500000, 10000, 480000  # Sum is 990000, not 1000000
with pytest.raises(AssertionError, match="Conservation"):
    sir_rates(S, I, R, N=1000000, beta=0.2, gamma=0.1)
```

**Deliverable**: 1 section listing 8–10 test cases, ~400 words + test code

---

### Section 10: Known Limitations (20 mins)

**What to write**: Honest, specific limitations; what the model cannot predict

**Format**: Structured list with explanations

**Requirements**:
- [ ] Every limitation is specific (not vague)
- [ ] Explain why each limitation exists (model choice, not bug)
- [ ] For major limitations, suggest extensions or alternatives

**Example**:

| Limitation | Why | Impact | Mitigation |
|-----------|-----|--------|-----------|
| **Homogeneous mixing** | Assumes equal contact probability | Fails for geographically isolated communities or age-stratified contact | Use SEIR with age structure or network model (future) |
| **No behavior change** | β assumed constant | Ignores lockdowns, mask adoption, voluntary isolation | Fit time-varying β or use intervention scenarios |
| **No imported cases** | External transmission not modeled | Fails when new variants arrive | Add boundary condition for case imports |
| **No spatial heterogeneity** | Single well-mixed population | Cannot model local outbreaks or regional differences | Use metapopulation or agent-based model |
| **Instantaneous recovery** | All infected recover after 1/γ days | Ignores individuals with prolonged symptoms or hospitalization | Use Erlang-distributed infectious period |
| **No pathogen evolution** | Virus assumed constant | Fails over multi-year timescales as variants emerge | Add strain-specific compartments (future) |
| **No vital dynamics** | Ignores births, deaths, aging | Valid only for acute outbreaks (<1 year) | Add birth/death rates for endemic models |
| **Population-level only** | No individual-level stochasticity | Deterministic; ignores probability of extinction with low I | Use Gillespie algorithm for stochastic version |

**Extension ideas**:
- SEIR (add exposed stage)
- Age-stratified SEIR (contact matrix by age group)
- Spatial SIR (network or reaction-diffusion)
- Stochastic SIR (Gillespie algorithm)

**Deliverable**: 1 section with table + extension ideas, ~300 words + table

---

### Bonus: Reproduction Instructions (10 mins)

**What to write**: Exact steps to regenerate entire paper from fresh checkout

**Format**: Numbered commands

**Requirements**:
- [ ] Start from `git clone`
- [ ] One command to build
- [ ] Verify output matches paper claims

**Example**:

```bash
# 1. Clone and setup
git clone https://github.com/baseline0/math-trace
cd math-trace/templates/epidemiology

# 2. Install dependencies
uv sync

# 3. Run tests (optional but recommended)
pytest scenarios/

# 4. Generate paper + figures
just paper
# Output: paper.pdf (this paper)
#         figures/sir-trajectory.png
#         figures/r0-sensitivity.png

# 5. Verify: open paper.pdf and check Figures 1–3 match expected shapes
```

**Deliverable**: Markdown code block, ~100 words

---

## Acceptance Checklist

**All 10 sections + bonus must pass before considering Epidemiology complete.**

### Content Completeness
- [ ] Section 1: Problem statement (motivates epidemiology, ~300 words)
- [ ] Section 2: Historical provenance (Kermack 1927 → modern, ~250 words)
- [ ] Section 3: Assumptions (table + narrative, ~400 words)
- [ ] Section 4: Variable definitions (table with units, domains, ~300 words)
- [ ] Section 5: Dimensional analysis (verified for each equation, ~200 words)
- [ ] Section 6: Equation construction (derivations from first principles, ~600 words)
- [ ] Section 7: Executable code (runnable scenario, ~300 words + code)
- [ ] Section 8: Expected outputs (qualitative + quantitative, ~250 words)
- [ ] Section 9: Verification strategy (8–10 tests, success + failures, ~400 words + code)
- [ ] Section 10: Known limitations (specific, with extensions, ~300 words + table)
- [ ] Bonus: Reproduction instructions (git clone → paper, ~100 words)

**Total**: ~3500–4000 words + code + tables + figures

### Code Quality
- [ ] `src/epidemiology/model.py`: SIR/SEIR equations, assumptions, verification
- [ ] `src/epidemiology/scenarios/`: covid_baseline.py, measles.py (if extended)
- [ ] `tests/epidemiology/`: test_sir_equations.py, test_conservation.py, test_failures.py
- [ ] All tests pass: `pytest tests/epidemiology/`
- [ ] Code coverage ≥90%: `pytest --cov=epidemiology/`

### Paper Quality
- [ ] All equations in paper match `model.py` character-for-character
- [ ] Line numbers in paper match source code (e.g., "model.py:25")
- [ ] Figures auto-generated (not manual drawings)
- [ ] Deterministic: same run produces identical output 100 times
- [ ] Reproducible: `just paper` works from fresh checkout

### External Review (Week 6)
- [ ] Reviewer unfamiliar with code follows instructions without errors
- [ ] Reviewer verifies at least 2 claims against cited sources
- [ ] Reviewer reports any confusion or ambiguity
- [ ] Issues resolved before release

### Template Conformance
- [ ] All 10 sections present
- [ ] Same structure as this checklist (not reorganized)
- [ ] Assumptions listed (not buried in prose)
- [ ] Every variable has units and domain
- [ ] Tests include expected failures
- [ ] Limitations are specific

---

## Success Criteria (Week 3)

**Epidemiology paper is complete when**:
- ✅ All 10 sections written and reviewed
- ✅ All tests pass (90%+ coverage)
- ✅ External reviewer confirms reproducibility
- ✅ Paper PDFs match across multiple runs
- ✅ Every claim in paper is verifiable in code or citations

**Then**: Use this template as **golden path** for Quantum, Control, GNNs, Thermodynamics (Weeks 4–5).

---

## Deviations from Template

**If another template must deviate** (e.g., Quantum Systems needs different section order):

1. Document the deviation in that template's README
2. Explain why (e.g., "Quantum systems require probability interpretation section before equations")
3. Get approval before committing

**Do NOT let drift happen silently.**

---

## Timeline

**Week 2 (Sep 23–27)**:
- Write Sections 1–7 (problem, history, assumptions, variables, dimensions, derivation, code)
- Implement tests
- Generate preliminary figures

**Week 3 (Sep 30–Oct 4)**:
- Complete Sections 8–10 (outputs, verification, limitations)
- Polish paper text
- External reviewer dry-run

**Week 6 (Oct 14–18)**:
- External reviewer feedback incorporated
- Final PDF generated
- Tag as "Epidemiology golden path complete"

---

**Owner**: Mark Alexiuk  
**Status**: Ready to start Week 2  
**Next review**: Oct 4 (end of Week 3)
