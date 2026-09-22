# math-trace Roadmap: Reaching Production Maturity

**Goal**: Build math-trace into a widely-adopted framework for publication-quality mathematical research with full formula-to-code traceability.

**Current Status**: Phase 3 complete (fleet integration + governance). **Phase 4 ACCELERATED**: All 5 production templates complete (26 equations, 1,700 LOC). Phase 4 continuation + Phase 5-6 roadmap below.

---

## Phase 1: Foundation ✅ Complete

- [x] Core library (src/math_trace/)
- [x] SymPy formula export
- [x] LaTeX → Typst conversion
- [x] Example: membrane-dynamics (stochastic P systems)
- [x] End-to-end build pipeline (model → figures → PDF)
- [x] PyPI packaging
- [x] GitHub CI/CD (test-templates.yml, publish.yml)

---

## Phase 2: Template Ecosystem ✅ Complete

- [x] 2 templates: simple-physics, biochemistry
- [x] TEMPLATE-USAGE.md documentation
- [x] Template validation CI/CD
- [x] Lean formalization support (optional)
- [x] Palomar registry metadata (optional)

---

## Phase 3: Fleet Integration ✅ Complete

- [x] .fleet/config.yaml — governance model
- [x] .fleet/BOUNDARIES.md — governance policies
- [x] catalog-info.yaml — fleet metadata
- [x] Dependency management (uv.lock auto-update)
- [x] MCP coordination (rope-mcp, vscode-workspace-mcp)
- [x] Audit logging infrastructure
- [x] Cost tracking + monthly metrics

---

## Phase 4: Hardening & User Experience 🚀 In Progress

### 4a: Installation & Onboarding ✅ Complete

**Status**: One-command setup (`just setup`) implemented with Python 3.13 standardization.

**Completed**:
- [x] Environment detection script (`scripts/check-env.sh`)
- [x] `just setup` recipe (Typst install + uv sync)
- [x] Platform-specific install instructions (macOS/Linux/Windows WSL)
- [x] Updated README with quick-start callout

**Next**: Extend setup script for template-specific dependencies (Lean, Plotly, Streamlit)

### 4b: Complete 5 Production Templates ✅ Complete

**Status**: All 5 templates shipped with equation-to-code traceability, scenarios, and validation.

**Completed Templates**:
- [x] **Quantum Systems** (450 LOC, 5 equations, Schrödinger solver with analytical benchmarks)
- [x] **Epidemiology** (320 LOC, 6 equations, SIR/SEIR disease modeling)
- [x] **Control Systems** (280 LOC, 5 equations, PID + state-space LTI)
- [x] **Graph Neural Networks** (350 LOC, 5 equations, message passing + attention)
- [x] **Thermodynamics** (300 LOC, 5 equations, ideal gas + Carnot cycle)

**Batch-creation pattern proven**: All 5 templates follow identical structure (src/model.py → scenarios → tests → config.toml → equations.json).

### 4c: Write Papers & Extend Scenarios ⏳ Ready to Start

**Why**: Templates have core code but need publication-quality papers (paper.typ) and enriched scenarios to demonstrate full value.

**Strategy**: Start with **one reference paper** (Epidemiology recommended—highest impact), then batch remaining 4 papers using proven template.

#### Write paper.typ for each template (3-4 hrs per template, 2 hrs for remaining 4)

**Recommended Structure (IEEE format):**
```typst
= Abstract
  - Background (1-2 sentences)
  - Problem (specific computational gap)
  - Approach (methods + implementation)
  - Results (quantitative outcomes)
  - Implications (broader impact)

= Introduction
  - Why this domain matters
  - Existing tools (and limitations)
  - Your contributions (3 bullet points)

= Mathematical Framework
  - Core equations (numbered, with citations)
  - Notation table (symbol, description, units)

= Implementation
  - Architecture diagram (auto-generated from code)
  - Key algorithms (code listings with equation refs)
  - Validation strategy (tests, benchmarks)

= Results
  - Benchmark 1: Analytical comparison
  - Benchmark 2: Real-world scenario
  - Figures (auto-generated from simulations)

= Discussion
  - Limitations (honest, specific)
  - Extensions (3-5 concrete ideas)
  - Reproducibility (how to replicate)

= Conclusion
  - Summary (1 paragraph)
  - Impact (who benefits)
  - Call to action (GitHub link)
```

**Writing order** (sequential, then parallel):
1. **Week 1-2**: Epidemiology paper (reference template) — **4-6 hrs**
2. **Week 3-4**: Remaining 4 papers (Quantum, Control, GNNs, Thermodynamics) — **2-3 hrs each**

**Tasks**:
- [ ] **Phase 4c-1: Epidemiology reference paper** (4-6 hrs)
  - [ ] Write Abstract (1 hr)
  - [ ] Write Introduction + Framework (1 hr)
  - [ ] Write Implementation section with code refs (1.5 hrs)
  - [ ] Generate figures + Results section (1.5 hrs)
  - [ ] Write Discussion + Conclusion (1 hr)
  - [ ] Peer review + refinements (0.5 hrs)
- [ ] **Phase 4c-2: Quantum Systems paper** (2-3 hrs, use Epidemiology template)
- [ ] **Phase 4c-3: Control Systems paper** (2-3 hrs)
- [ ] **Phase 4c-4: GNN paper** (2-3 hrs)
- [ ] **Phase 4c-5: Thermodynamics paper** (2-3 hrs)

**Status per template**:
- Quantum: Core ✅, Paper ⏳, Scenarios ⏳
- Epidemiology: Core ✅, Paper ⏳, Scenarios ⏳
- Control: Core ✅, Paper ⏳, Scenarios ⏳
- GNNs: Core ✅, Paper ⏳, Scenarios ⏳
- Thermodynamics: Core ✅, Paper ⏳, Scenarios ⏳

#### Extend scenarios (2-3 hrs per template, priority-ordered)

**Scenario Expansion Table:**

| Template | Current | Extend To | Effort | Priority |
|----------|---------|-----------|--------|----------|
| **Epidemiology** | COVID (SIR) | Measles (SEIR, R₀≈15), Ebola (stochastic) | 2-3 hrs | 🔴 HIGH |
| **GNNs** | Karate Club (34 nodes) | Cora (citation, 2.7k nodes), attention visualization | 2-3 hrs | 🔴 HIGH |
| **Quantum** | Harmonic oscillator | Double-slit interference, tunneling barrier | 2-3 hrs | 🟡 MEDIUM |
| **Control** | PID controller | Mass-spring-damper (analytical 2nd order), Bode plot | 2-3 hrs | 🟡 MEDIUM |
| **Thermodynamics** | Ideal gas + Carnot | Polytropic processes, phase diagrams (P-V, T-S) | 2-3 hrs | 🟡 MEDIUM |

**Recommendation:** Pick **one extension per template** (not all) for Phase 4. Additional extensions become Phase 5 work.

**Tasks**:
- [ ] **Phase 4c-6: Epidemiology scenarios** (Measles + Ebola, 2-3 hrs)
- [ ] **Phase 4c-7: GNN scenarios** (Cora + attention viz, 2-3 hrs)
- [ ] **Phase 4c-8: Quantum scenarios** (Double-slit + tunneling, 2-3 hrs)
- [ ] **Phase 4c-9: Control scenarios** (Mass-spring-damper, 2-3 hrs)
- [ ] **Phase 4c-10: Thermodynamics scenarios** (Polytropic + phase diagrams, 2-3 hrs)

### 4d: Test Suite Completion ⏳ Ready to Start

**Why**: Bring all 5 templates to 90%+ test coverage with validation against analytical solutions.

**Test Strategy** (per template, 2-3 hrs):

**Test Categories:**
1. **Model accuracy tests** — Verify equations match analytical solutions
   - Epidemiology: SIR equilibrium S* = N/R₀
   - Quantum: Harmonic oscillator energies E_n = ℏω(n + 1/2)
   - Control: Pole location, settling time formulas
   - GNNs: Cross-entropy loss decreases with training
   - Thermodynamics: Carnot efficiency bounds (0 ≤ η < 1)

2. **Conservation law tests** — Verify physical invariants
   - Quantum: Wavefunction normalization ∫|ψ|²dx = 1
   - Epidemiology: Population conservation S + I + R = N
   - Thermodynamics: Energy conservation (First Law)
   - Control: Lyapunov stability (poles in left half-plane)

3. **Scenario validation** — Numerical vs. analytical
   - Run scenario, compare output to known analytical solution
   - Target: error < 1e-3 relative to analytical baseline

4. **Edge cases** — Robustness
   - Zero/negative parameters (should raise ValueError)
   - NaN propagation (should handle gracefully)
   - Boundary conditions (e.g., T_hot = T_cold → undefined efficiency)

**Tooling:**
```bash
# Generate coverage report
just test-coverage  # Target: 90%+ line coverage

# View gaps interactively
coverage html  # Open htmlcov/index.html in browser
```

**Tasks per template** (2-3 hrs):
- [ ] **Phase 4d-1: Quantum test suite** (90%+ coverage)
  - [ ] Eigenvalue accuracy (TISE vs. analytical)
  - [ ] Energy conservation (TDSE)
  - [ ] Normalization constraint
  - [ ] Scenario validation (harmonic oscillator)
- [ ] **Phase 4d-2: Epidemiology test suite** (90%+ coverage)
  - [ ] R₀ calculation accuracy
  - [ ] SIR equilibrium validation
  - [ ] Population conservation
  - [ ] Scenario validation (COVID baseline)
- [ ] **Phase 4d-3: Control test suite** (90%+ coverage)
  - [ ] Pole stability checks
  - [ ] Settling time accuracy
  - [ ] PID controller gains
  - [ ] Scenario validation (DC motor)
- [ ] **Phase 4d-4: GNN test suite** (90%+ coverage)
  - [ ] Message aggregation correctness
  - [ ] Attention weight normalization
  - [ ] Classification loss convergence
  - [ ] Scenario validation (Karate Club accuracy)
- [ ] **Phase 4d-5: Thermodynamics test suite** (90%+ coverage)
  - [ ] Carnot efficiency bounds
  - [ ] Energy conservation (First Law)
  - [ ] Entropy monotonicity
  - [ ] Scenario validation (Ideal Gas law)

### 4e: GitHub Release v1.0 ⏳ Ready to Start

**Why**: First official release with all 5 templates, complete documentation, and CI/CD validation.

**Pre-release Checklist** (before tagging):
- [ ] All 5 templates complete (papers + scenarios + tests)
- [ ] README.md updated with quickstart (`just setup && just build`)
- [ ] CITATION.cff created (for academic citation)
- [ ] LICENSE.md verified (MIT or Apache 2.0)
- [ ] CHANGELOG.md drafted
- [ ] All tests passing (`just test`)
- [ ] Coverage ≥90% across all templates (`just test-coverage`)
- [ ] GitHub release branch ready for review

**Release Workflow** (1-2 hrs):

**Step 1: Update version + metadata**
```bash
# Edit pyproject.toml
version = "1.0.0"

# Create CHANGELOG.md
cat > CHANGELOG.md << 'EOF'
# Changelog

## [1.0.0] - 2026-10-15

### Added
- **5 Production Templates** (26 equations, 1,700 LOC)
  - Quantum Systems: Schrödinger solver (FDM eigenvalues, SSFM time evolution)
  - Epidemiology: SIR/SEIR disease modeling (basic reproduction, intervention analysis)
  - Control Systems: State-space LTI + PID controller (pole stability, settling time)
  - Graph Neural Networks: Message passing + attention (node classification, loss computation)
  - Thermodynamics: Ideal gas + Carnot cycle (PVT relations, efficiency bounds)
- Installation automation: `just setup` (Python 3.13, Typst, uv)
- Fleet governance: `.fleet/config.yaml`, audit logging, cost tracking
- Test coverage: 90%+ on all templates
- Publication-quality papers: IEEE format with benchmarks + code references

### Changed
- Migrated from `np.trapz` to `scipy.integrate.trapezoid` (deprecation fix)
- Standardized Python version to 3.13 across all templates

### Fixed
- Justfile indentation (consistent 2-space base indentation)
- Missing `Callable` import in control-systems/src/model.py

### Deprecated
- Numpy trapezoid integration (prefer scipy.integrate.trapezoid)

### Security
- No breaking changes
- All dependencies pinned in uv.lock

## [0.1.0] - 2026-08-01
- Initial release: Quantum Systems + Epidemiology templates
EOF

# Create CITATION.cff
cat > CITATION.cff << 'EOF'
cff-version: 1.2.0
message: "If you use this software, please cite it as below."
title: "Computational Science Templates: Formula-to-Code Traceability"
version: 1.0.0
authors:
  - given-names: Mark
    family-names: Alexiuk
    orcid: "0000-0000-0000-0000"  # Update with your ORCID
repository-code: "https://github.com/your-org/computational-templates"
license: MIT
doi: "10.5281/zenodo.xxxxxxx"  # Get from Zenodo after release
keywords:
  - computational-science
  - reproducibility
  - formula-traceability
  - templates
  - sympy
  - typst
subjects:
  - "Science"
  - "Physics"
  - "Mathematics"
date-released: 2026-10-15
EOF
```

**Step 2: Commit + tag**
```bash
just commit  # Auto-generate message or use:
# MESSAGE="release: v1.0.0 - Five production templates + formula traceability" just commit

# Verify changes
git status
git log -1

# Tag the release
git tag -a v1.0.0 -m "Five production templates + formula traceability
- Quantum Systems (Schrödinger solver, 5 equations)
- Epidemiology (SIR/SEIR disease modeling, 6 equations)
- Control Systems (LTI state-space + PID, 5 equations)
- Graph Neural Networks (message passing + attention, 5 equations)
- Thermodynamics (ideal gas + Carnot, 5 equations)

Total: 26 equations, 1,700 LOC, 10 scenarios, 90%+ test coverage"

# Push to GitHub
git push origin main
git push origin v1.0.0
```

**Step 3: Create GitHub release**
- Go to GitHub → Releases → Draft New Release
- Tag: v1.0.0
- Title: "v1.0.0: Five Production Templates + Formula Traceability"
- Release notes (copy from CHANGELOG.md, add installation instructions)
- Attach: (optional) PDF of compiled papers
- **Publish release**

**Step 4: Register Zenodo DOI** (optional but recommended for academic visibility)
```bash
# Visit https://zenodo.org/account/settings/github/
# Connect GitHub account, enable auto-archival for releases
# After first release, Zenodo auto-generates DOI
# Copy DOI to CITATION.cff + README.md
```

**Tasks**:
- [ ] **Phase 4e-1: Version + metadata** (30 mins)
  - [ ] Update pyproject.toml version to 1.0.0
  - [ ] Create CHANGELOG.md
  - [ ] Create CITATION.cff
- [ ] **Phase 4e-2: Git tag + push** (15 mins)
  - [ ] Commit with `just commit`
  - [ ] Tag v1.0.0
  - [ ] Push origin main + tag
- [ ] **Phase 4e-3: GitHub release** (30 mins)
  - [ ] Draft release on GitHub
  - [ ] Write release notes
  - [ ] (Optional) Attach compiled papers as PDFs
  - [ ] Publish release
- [ ] **Phase 4e-4: Zenodo integration** (15 mins)
  - [ ] Register Zenodo account (if needed)
  - [ ] Enable GitHub auto-archival
  - [ ] Get DOI, update CITATION.cff + README

### 4f: Documentation Index ⏳ Ready to Start

**Why**: Help users navigate between templates and understand which to use for their domain.

**Deliverables** (1-2 hrs):

**1. TEMPLATE-INDEX.md** — Comparison table
```markdown
# Template Index

| Domain | Equations | LOC | Scenarios | Difficulty | Use Case |
|--------|-----------|-----|-----------|-----------|----------|
| Quantum Systems | 5 | 450 | 2 (harmonic, plus extensions) | 🟡 Intermediate | Quantum mechanics, wave equations |
| Epidemiology | 6 | 320 | 2 (COVID, plus extensions) | 🟢 Beginner | Disease modeling, compartmental analysis |
| Control Systems | 5 | 280 | 2 (PID + state-space) | 🟡 Intermediate | Robot control, feedback systems |
| Graph Neural Networks | 5 | 350 | 2 (Karate Club, plus extensions) | 🔴 Advanced | Node classification, graph learning |
| Thermodynamics | 5 | 300 | 2 (Ideal gas, Carnot) | 🟡 Intermediate | Heat cycles, statistical mechanics |
```

**2. TEMPLATE-SELECTION.md** — Decision flowchart
```markdown
# Choosing Your Template

**Are you modeling change over time?**
→ Yes: Physics (Quantum, Thermodynamics), Control Systems
→ No: Network phenomena (GNNs), Static systems

**Is your system discrete (e.g., counts, networks) or continuous (e.g., PDEs)?**
→ Discrete: Epidemiology (SIR compartments), GNNs (nodes/edges)
→ Continuous: Quantum (wavefunctions), Control (differential equations)

**Do you need formal proofs?**
→ Yes: Quantum Systems, Thermodynamics (conservation laws)
→ No: Epidemiology, Control, GNNs

**Are you new to this domain?**
→ Yes: Start with Epidemiology (intuitive) or Quantum (well-studied)
→ No: Pick by field specialty
```

**3. Update README.md** — Template gallery section
```markdown
## 🎯 Quick Template Gallery

### For Epidemiologists & Public Health
→ **Epidemiology template**: SIR/SEIR disease modeling, intervention analysis
Start here: `cd templates/epidemiology && just paper`

### For Physicists & Quantum Researchers
→ **Quantum Systems template**: Schrödinger solver (FDM eigenvalues, SSFM time evolution)
Start here: `cd templates/quantum-systems && just paper`

### For Control Engineers
→ **Control Systems template**: LTI state-space, PID controller design
Start here: `cd templates/control-systems && just paper`

### For ML / Graph Specialists
→ **Graph Neural Networks template**: Message passing, attention mechanisms
Start here: `cd templates/gnns && just paper`

### For Thermodynamicists
→ **Thermodynamics template**: Ideal gas, Carnot cycles, entropy
Start here: `cd templates/thermodynamics && just paper`
```

**Tasks**:
- [ ] **Phase 4f-1: Create TEMPLATE-INDEX.md** (30 mins)
  - [ ] Comparison table (equations, LOC, scenarios, difficulty)
  - [ ] Key features per template
- [ ] **Phase 4f-2: Create TEMPLATE-SELECTION.md** (30 mins)
  - [ ] Decision flowchart (time-dependent, discrete/continuous, formal proofs, beginner-friendly)
  - [ ] Example use cases
- [ ] **Phase 4f-3: Update README.md** (30 mins)
  - [ ] Add "Quick Template Gallery" section
  - [ ] Each template gets 1-2 sentences + quick-start command
  - [ ] Link to TEMPLATE-SELECTION.md for guidance

---

## Phase 5: Ecosystem Expansion & Specialization 🌱 Planned

**Status**: 5 core templates complete (26 equations, 1,700 LOC). Phase 5 deepens them + adds specialized domains.

**Strategic Question (Answer Before Starting Phase 5):**
> Are you targeting academic adoption, industry adoption, or both?
> - **Academic**: Emphasize citations, Zenodo DOIs, arXiv integration, IEEE format papers
> - **Industry**: Emphasize production readiness, CI/CD, test coverage, "time-to-first-simulation"
> - **Both**: Do both (but this increases scope by ~30%)

**Recommendation**: Start with **academic adoption** (papers, Zenodo, citations), then add industry features (Streamlit dashboards, Overleaf) in subsequent iterations.

### 5a: Complete Papers for 5 Core Templates ⏳ Ready to Start

**Status**: Core code complete. Now adding publication-quality papers + extended scenarios.

**Dependencies** (from Phase 4):
- Phase 4c: Write papers for 5 templates
- Phase 4d: Bring test coverage to 90%+
- Phase 4e: Release v1.0.0

**Phase 5a Additions** (beyond Phase 4):
- Extended scenarios (2+ per template): Measles/Ebola (Epi), Double-slit/Tunneling (Quantum), Cora/Pubmed (GNNs), etc.
- Supplementary materials (analytical derivations, benchmark datasets)
- Reproducibility instructions (how to regenerate all figures)
- Zenodo DOI integration (one DOI per template)

**Estimated**: 3-4 weeks (includes Phase 4 paper writing + Phase 5 extensions)

### 5b: Add 3-5 Specialized Templates ⏳ Planned

**Target**: Deepen framework with specialized but related domains. Scale from 5 → 10 templates.

**Selection Strategy:**
1. **Demand**: Are researchers actively looking for templates in this domain?
2. **Complexity**: Can implementation + scenarios fit in <500 LOC?
3. **Validation**: Do analytical solutions or benchmark datasets exist?
4. **Connectivity**: Does template link to existing domains (leverage shared concepts)?

**Recommended Specialized Templates** (in priority order):

| Domain | Relevance | Effort | Connects to | Why Now |
|--------|-----------|--------|------------|----------|
| **Optimization** | 🔴 HIGH | 5 hrs | GNNs, Control | ML fundamental; gradient descent, linear programming |
| **Quantum Computing** | 🔴 HIGH | 6 hrs | Quantum Systems | Frontier ML; Qiskit circuits, variational quantum eigensolver |
| **Protein Folding** | 🔴 HIGH | 7 hrs | GNNs, Optimization | Biology + AI intersection; AlphaFold-inspired architectures |
| **Fluid Dynamics** | 🟡 MEDIUM | 7 hrs | Thermodynamics | CFD applications; Navier-Stokes, Lattice Boltzmann |
| **Computational Biology** | 🟡 MEDIUM | 6 hrs | GNNs, Optimization | Gene networks, phylogenetics, mutation models |

**Not Recommended Yet** (post-Phase 5):
- Robotics/Kinematics: Large scope (~8 hrs), overlaps with Control
- Economics/Game Theory: Niche audience, less mathematical rigor expected

**Batch Creation Pattern** (proven for 5 core templates):
```
For each new template:
1. src/model.py (5-6 core equations, ~100-150 LOC)
2. src/scenarios/ (2-3 reference implementations, ~150-200 LOC)
3. src/tests/ (validation against analytical benchmarks, ~100-150 LOC)
4. config.toml, equations.json, README.md
5. (Phase 5) paper.typ, extended scenarios, Jupyter notebooks
```

**Timeline**:
- **Weeks 1-2**: Optimization + Quantum Computing (parallel, high relevance)
- **Weeks 3-4**: Protein Folding (complex, but high impact)
- **Weeks 5-6**: Fluid Dynamics (if time permits)

**Tasks**:
- [ ] **Phase 5b-1: Optimization template** (5 hrs)
  - [ ] src/model.py: Linear programming, gradient descent, genetic algorithms (5 equations)
  - [ ] Scenarios: Rosenbrock function, constrained optimization
  - [ ] Tests + config + equations.json
- [ ] **Phase 5b-2: Quantum Computing template** (6 hrs)
  - [ ] src/model.py: Quantum gates, Bloch sphere, VQE algorithm (5 equations)
  - [ ] Scenarios: Simple circuit simulation, variational optimization
  - [ ] Tests + config + equations.json
- [ ] **Phase 5b-3: Protein Folding template** (7 hrs)
  - [ ] src/model.py: Energy minimization, contact map, secondary structure (5-6 equations)
  - [ ] Scenarios: Simplified fold simulation, Ramachandran plot
  - [ ] Tests + config + equations.json

### 5b: Lean Formalization (Systematic)

**Why**: Optional but high-value. Lean proofs increase credibility for research papers.

**Current State**:
- membrane-dynamics has Lean scaffold
- simple-physics, biochemistry do not

**Plan**:
- [ ] Create `templates/*/lean/README.md` template
- [ ] Add Lean 4 proof scaffolding to each new template
- [ ] Document Palomar registry integration
- **Effort per template**: 4 hrs | **Priority**: Low (optional)

### 5c: Interactive Visualization & Exploration ⏳ Post-Phase 5a

**Why**: Current output is static PDF. Researchers want interactive parameter sweeps, animations, sensitivity analysis.

**Recommended Stack:**
- **Jupyter notebooks**: Exploratory analysis, parameter sweeps, sensitivity analysis
- **Streamlit**: Web dashboards for real-time parameter tuning
- **Plotly 3D**: High-dimensional visualizations (wavefunctions, phase spaces, attractors)

**Example: Streamlit Dashboard for Epidemiology**
```python
# app.py
import streamlit as st
from epidemiology.model import sir_model

st.title("SIR Epidemic Model")

# Sidebar controls
R0 = st.slider("R₀ (basic reproduction number)", 0.5, 5.0, 2.0)
gamma = st.slider("Recovery rate (γ)", 0.1, 0.5, 0.2)
N_infected_0 = st.slider("Initial infected", 1, 100, 10)

# Simulate
S, I, R = sir_model(R0=R0, gamma=gamma, I0=N_infected_0, days=100)

# Plot
st.line_chart({
    "Susceptible": S,
    "Infected": I,
    "Recovered": R
})

# Show metrics
st.metric("Peak Infections", I.max())
st.metric("Attack Rate", 100 * (R.max() / N))
```

**Phase 5c Tasks** (8-12 hrs, post-Phase 5a):

**Sub-phase 5c-1: Jupyter Notebook Exporter** (4 hrs)
- [ ] Template: `templates/*/notebooks/explore.ipynb`
- [ ] Auto-generate from scenarios
- [ ] Include parameter sweep examples
- [ ] Implement for Epidemiology + Quantum (proofs of concept)

**Sub-phase 5c-2: Streamlit Dashboards** (6 hrs)
- [ ] `streamlit_apps/epidemic_simulator.py` (Epidemiology)
- [ ] `streamlit_apps/quantum_solver.py` (Quantum Systems)
- [ ] Deploy to Streamlit Cloud (free tier)
- [ ] Link from README + GitHub Pages

**Sub-phase 5c-3: 3D Plotly Visualizations** (2-4 hrs)
- [ ] Quantum: Wavefunction |ψ|² surface plots
- [ ] Control: Phase portrait trajectories
- [ ] GNNs: 3D node embedding space
- [ ] Thermodynamics: P-V-T surface (ideal gas law)

**Deployment Strategy**:
```bash
# Streamlit Cloud (free, auto-deploy from GitHub)
streamlit run streamlit_apps/epidemic_simulator.py
# Push to GitHub, connect via Streamlit Cloud

# Jupyter on GitHub Pages (static, no compute)
jupyter nbconvert notebooks/explore.ipynb --to html
git add docs/explore.html && git push

# GitHub Pages config
# .github/workflows/publish-docs.yml
# → Auto-convert .ipynb → .html on push
```

**Priority**: Low (Phase 5c is nice-to-have, not core to v1.0.0 release)

### 5d: Integration with External Tools ⏳ Post-Phase 5a

**Candidates** (in priority order):

| Integration | Effort | Impact | Use Case |
|-------------|--------|--------|----------|
| **Zenodo/Figshare DOI** | 4 hrs | 🔴 HIGH | Academic citability, compliance |
| **arXiv metadata** | 3 hrs | 🟡 MEDIUM | Supplement published papers |
| **Overleaf Git sync** | 5 hrs | 🟡 MEDIUM | Typst → LaTeX conversion for journals |
| **Palomar registry** | 6 hrs | 🟢 LOW | Formal proof discoverability (niche) |

**Priority Rationale:**
1. **Zenodo** (v1.0.0 release already uses this) — continue integration for future templates
2. **arXiv** — essential if you're publishing research papers using templates
3. **Overleaf** — deferred (most journals accept Typst via supplementary materials)
4. **Palomar** — deferred (low adoption; implement after Lean proofs are mature)

**Phase 5d Tasks** (4-6 hrs per integration, post-Phase 5a):

**Sub-phase 5d-1: Zenodo Auto-Upload** (4 hrs)
- [ ] Create GitHub Actions workflow: `trigger_zenodo_upload.yml`
- [ ] On GitHub release, auto-upload papers + datasets to Zenodo
- [ ] Extract DOI, update CITATION.cff + README
- [ ] Template: 1 per domain (Zenodo collection)

```yaml
# .github/workflows/zenodo_upload.yml
name: Zenodo Auto-Upload
on:
  release:
    types: [published]

jobs:
  upload:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Upload to Zenodo
        env:
          ZENODO_TOKEN: ${{ secrets.ZENODO_TOKEN }}
        run: |
          curl -X POST https://zenodo.org/api/deposit/depositions \
            -H "Authorization: Bearer $ZENODO_TOKEN" \
            -F "metadata=@zenodo_metadata.json" \
            -F "file=@papers/*.pdf"
```

**Sub-phase 5d-2: arXiv Metadata Generator** (3 hrs)
- [ ] Auto-generate `arXiv.yaml` from papers + equations
- [ ] Include: title, authors, abstract, keywords, supplementary materials link
- [ ] Template: usable for any template paper

```yaml
# arXiv.yaml (auto-generated)
title: "Disease Dynamics via SIR/SEIR Models: Computational Templates"
authors:
  - name: "Mark Alexiuk"
    affiliation: "your-org"
abstract: >
  We present computational templates for epidemiological modeling...
keywords:
  - "disease modeling"
  - "SIR/SEIR equations"
  - "reproducible research"
supplementary_materials:
  - url: "https://github.com/your-org/math-trace"
    type: "code"
  - url: "https://zenodo.org/record/xxxxx"
    type: "data"
```

**Sub-phase 5d-3: Overleaf Sync (Deferred)** (5 hrs, v1.1+)
- [ ] Create `scripts/sync_to_overleaf.sh`
- [ ] Push templates to Overleaf Git repos
- [ ] Enable collaboration + commenting

**Sub-phase 5d-4: Palomar Registry (Deferred)** (6 hrs, v2.0+)
- [ ] Create `lean/formalization.yaml` per template
- [ ] Submit to Palomar registry
- [ ] Include: theorem statement, proof, citations

**Priority**: Medium (post-Phase 5a; essential for academic impact)

---

## ✅ Approved Backlog (Phase 4-5)

**Status**: APPROVED FOR EXECUTION  
**Decision Date**: 2026-09-22  
**Rationale**: Strategic feedback integrated, 20-week timeline planned, resource allocation defined, critical path identified.

### Phase 4: Hardening (Weeks 1-9) — READY TO START

**Total Effort**: 37-52 hrs (4-6 weeks at 10-12 hrs/week)  
**Start Date**: ASAP (Week 1 = This week)  
**Target Release**: Week 9 (v1.0.0)

**Approved Tasks**:
- [x] Phase 4c: Write papers (IEEE format, batch workflow)
- [x] Phase 4d: Test suite to 90%+ coverage
- [x] Phase 4e: GitHub Release v1.0.0 (CHANGELOG, CITATION.cff, Zenodo DOI)
- [x] Phase 4f: Documentation index (TEMPLATE-INDEX, TEMPLATE-SELECTION)

**Approval Notes**:
- Clear: Exactly which template goes first (Epidemiology reference paper)
- Unblocked: All 5 core templates complete; no dependencies
- Measurable: 90%+ coverage, v1.0.0 release, GitHub release notes
- Resourced: ~10-12 hrs/week capacity assumed

### Phase 5: Expansion (Weeks 10-20) — APPROVED CONTINGENT

**Total Effort**: 50-70 hrs (dependent on Phase 4 completion)  
**Start Date**: After v1.0.0 release (Week 10)  
**Strategic Decision**: **Academic adoption first** (papers, Zenodo, citations), then industry features (Streamlit, Overleaf) in v1.2+

**Approved Tasks**:
- [x] Phase 5a: Complete papers + extended scenarios for 5 core templates
- [x] Phase 5b: Add 3-5 specialized templates (Optimization, Quantum Computing, Protein Folding as priority)
- [x] Phase 5c: Interactive visualizations (Jupyter + Streamlit, post-5a)
- [x] Phase 5d: Zenodo + arXiv integrations (post-5a, Overleaf deferred to v1.2)

**Approval Notes**:
- Conditional: Start after Phase 4 complete and v1.0.0 released
- Prioritized: High-relevance templates first (Optimization, QC, Protein Folding)
- Tiered: Core features (5c, 5d) optional/post-v1.1 (marked "Low priority")

---

## Execution Timeline & Sequencing 📅

**20-Week Plan (Phase 4 + Phase 5 roadmap):**

| Week(s) | Focus | Deliverable | Effort |
|---------|-------|-------------|--------|
| **1-2** | Phase 4c: Epidemiology reference paper | 1 complete paper.typ (IEEE format) | 4-6 hrs |
| **3-4** | Phase 4c: Remaining 4 papers (parallel) | All 5 papers complete | 2-3 hrs each |
| **5-6** | Phase 4d: Test suite completion | 90%+ coverage (all 5 templates) | 2-3 hrs each |
| **7-8** | Phase 4c: Extend scenarios (1 per template) | 5 extended scenario sets | 2-3 hrs each |
| **9** | Phase 4e: GitHub Release v1.0.0 | v1.0.0 tagged + Zenodo DOI | 2 hrs |
| **10** | Phase 4f: Documentation index | TEMPLATE-INDEX.md + SELECTION.md | 1.5 hrs |
| **11-12** | Phase 5b: Optimization + QC templates | 2 specialized templates (parallel) | 5-6 hrs each |
| **13** | Phase 5b: Protein Folding template | 1 specialized template | 7 hrs |
| **14-15** | Phase 5c-1: Jupyter notebook exporters | Interactive notebooks (Epi, Quantum) | 4 hrs |
| **16** | Phase 5c-2: Streamlit dashboards | Web UI (Epidemic simulator) | 4 hrs |
| **17-18** | Phase 5d: Zenodo + arXiv integrations | Auto-upload + metadata generation | 3-4 hrs each |
| **19-20** | Polish + User Feedback | v1.1 minor release, community updates | 2-3 hrs |

**Critical Path**:
1. **Weeks 1-4**: Write all papers (gates rest of timeline)
2. **Weeks 5-6**: Test suite (ensures quality before v1.0)
3. **Week 9**: v1.0.0 release (external announcement)
4. **Weeks 11-13**: Specialized templates (ecosystem growth)
5. **Weeks 14-18**: Visualizations + integrations (user experience)

**Parallelizable Work**:
- Paper writing (Weeks 1-4): All 5 templates can proceed in parallel
- Test suite (Weeks 5-6): Independent per template
- Scenario extension (Weeks 7-8): Independent per template
- Specialized templates (Weeks 11-13): Optimization + QC in parallel, Protein Folding sequential
- Visualizations (Weeks 14-16): Jupyter + Streamlit can proceed in parallel

**Resource Allocation** (assuming 1 person, ~20-25 hrs/week capacity):
- **Weeks 1-10** (Phase 4): ~15-18 hrs/week (core work, high focus)
- **Weeks 11-18** (Phase 5 expansion): ~20-25 hrs/week (multiple templates + integrations)
- **Weeks 19-20** (Refinement): ~10-12 hrs/week (polish + documentation)

**Dependencies & Blockers**:
- `scipy.integrate.trapezoid` migration → Complete before Week 5 tests
- `just setup` automation → Verify before Week 9 release
- GitHub Actions CI/CD → Ensure passing before Week 9 release
- Zenodo account setup → Must be done before Week 9 (auto-archive config)

**Success Criteria per Phase**:

**Phase 4 Success** (Week 9):
- ✅ All 5 templates have papers (IEEE format, benchmarks included)
- ✅ 90%+ test coverage on all templates
- ✅ v1.0.0 released on GitHub + Zenodo
- ✅ CITATION.cff + CHANGELOG.md published
- ✅ README with template gallery

**Phase 5 Success** (Week 20):
- ✅ 10 total templates (5 core + 3-5 specialized)
- ✅ Interactive Jupyter notebooks + Streamlit dashboards for 2+ templates
- ✅ Zenodo + arXiv integrations working
- ✅ Community feedback integrated (GitHub issues resolved)
- ✅ Minor release v1.1 published

---

## Phase 6: Community & Adoption 💫 Aspirational

### 6a: Showcase & Marketing

- [ ] **Create 3-5 high-profile example papers**
  - From published research (with permission)
  - Highlight formula traceability
  - Publish on blog + Twitter

- [ ] **Write "Why formula traceability matters" essay**
  - Link to reproducibility crisis
  - Show risk of formula → code divergence
  - Frame math-trace as solution

### 6b: Partnerships & Integration

- [ ] **Contact leading ML/physics journals**
  - Propose math-trace as supplementary material standard
  - Offer to review formula-traced papers

- [ ] **Reach out to Lean/Mathlib community**
  - Highlight Lean formalization capability
  - Propose as publication-quality theorem registry

### 6c: Conference Talks & Tutorials

- [ ] **Pitch talks to:** NeurIPS, ICML, ICLR, Scientific Python
- [ ] **Create tutorial notebooks** for workshops
- [ ] **Contribute to Scientific Python ecosystem guide**

---

## Fleet-Specific Tasks

### Governance & Maintenance

These are pre-authorized fleet agent tasks:

**Weekly (Automated)**:
- [ ] `just fleet-check` — Validate all templates pass CI/CD
- [ ] Update uv.lock if security issues detected
- [ ] Run test-templates.yml on all templates

**Monthly (Automated)**:
- [ ] Update dependency versions in pyproject.toml
- [ ] Audit .fleet/audit.log for issues
- [ ] Report metrics to fleet dashboard

**Quarterly (Manual)**:
- [ ] Review template coverage (which domains missing?)
- [ ] Assess user feedback (GitHub issues)
- [ ] Plan Phase 5 template additions

### Cost Tracking

Track time in these categories:
- `template-validation` — CI/CD runs
- `dependency-updates` — uv.lock maintenance
- `ci-cd-maintenance` — GitHub Actions monitoring
- `documentation-sync` — README + TEMPLATE-USAGE updates
- `new-template-development` — adding new domains

---

## Success Metrics

### Phase 4 (Hardening)
- ✅ Installation: `just setup` works on macOS, Linux, Windows WSL
- ✅ Documentation: 3+ new guides (Getting Started, Your First Paper, Template Authoring)
- ✅ Tests: >90% pass rate across Python 3.11-3.13
- ✅ Performance: Large paper (50+ formulas) builds in <2 min

### Phase 5 (Expansion)
- ✅ Templates: 7+ total (currently 2, +5 planned)
- ✅ Domains: ML, physics, engineering, biology all represented
- ✅ Examples: 3+ published papers using math-trace
- ✅ Formalization: 3+ templates with Lean proofs

### Phase 6 (Community)
- ✅ GitHub stars: 500+
- ✅ Monthly downloads: 1000+
- ✅ Downstream citations: Papers published using math-trace
- ✅ Conference presence: 1+ talks per year

---

## Immediate Next Steps (Week 1-2: Phase 4c Start)

**FOCUS**: Write the first reference paper (Epidemiology) to establish the paper-writing workflow.

### Week 1 Tasks

**Primary**: Phase 4c-1 — Epidemiology reference paper (4-6 hrs)
- [ ] Abstract + Introduction (1 hr)
- [ ] Mathematical Framework section (1 hr)
- [ ] Implementation with code references (1.5 hrs)
- [ ] Generate figures + Results (1.5 hrs)
- [ ] Discussion + Conclusion (1 hr)
- [ ] Review + refinements (0.5 hrs)

**Rationale**: Once this template is proven, remaining 4 papers become 2-3 hrs each (batch-apply template).

**Supporting Work**:
- [ ] Verify all tests passing: `just test` (5 mins)
- [ ] Check coverage: `just test-coverage` (5 mins)
- [ ] Review epidemiology model.py for paper annotations (15 mins)

### Week 2 Tasks

**Once Week 1 paper is complete**:
- [ ] Batch-create remaining 4 papers (Weeks 3-4)
  - Quantum Systems paper (2-3 hrs)
  - Control Systems paper (2-3 hrs)
  - GNN paper (2-3 hrs)
  - Thermodynamics paper (2-3 hrs)

**Parallel work** (while writing papers):
- [ ] Update README.md with paper.typ section callout
- [ ] Create TEMPLATE-USAGE.md paper guidelines

---

## Phase 4 Execution Roadmap (Weeks 1-9)

**Owner**: mark-alexiuk (human lead)
**Resources**: Fleet agents for automated validation (just test, coverage)
**Target**: v1.0.0 release by Week 9

| Week | Task | Status | Est. Time |
|------|------|--------|-----------|
| 1-2 | Phase 4c: Epi reference paper + Weeks 3-4 papers | ⏳ | 14-18 hrs |
| 5-6 | Phase 4d: Test suite to 90%+ coverage | ⏳ | 10-15 hrs |
| 7-8 | Phase 4c: Extend scenarios (1 per template) | ⏳ | 10-15 hrs |
| 9 | Phase 4e + 4f: Release v1.0.0 + documentation | ⏳ | 3-4 hrs |

**Total Phase 4 effort**: 37-52 hrs (4-6 weeks at 10-12 hrs/week)

---

## Decision Log

### Why Phase 5 Before Phase 6?

**Rationale**: Ecosystem (templates) must be mature before marketing. It's easier to show 7 well-maintained templates than to market 2.

### Why Prioritize Installation/Docs?

**Rationale**: Current friction point for new users. "Just install and run" is critical for adoption.

### Why Optional Lean Formalization?

**Rationale**: Adds credibility but not required. Researchers using math-trace for PDFs don't need Lean proofs initially.

---

## How to Contribute

**Internal** (fleet-authorized):
- Fleet agents: Run tasks marked "Fixable (Fleet Agent)"
- mark-alexiuk: Review PRs tagged `[REVIEW-REQUESTED]`

**External** (community):
- File issues for bugs/feature requests
- Submit templates for new domains (via PR, requires review)
- Contribute documentation improvements

See CONTRIBUTING.md for detailed guidance.

---

**Last Updated**: 2026-09-22 (Phase 4-5 roadmap with detailed sequencing + execution timeline)
**Next Review**: 2026-10-20 (after Phase 4c-1 paper complete)  
**Version**: 1.1 (Roadmap + Execution Plan)
