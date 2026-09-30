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
- [x] **Epidemiology** (320 LOC, 6 equations, SIR/SEIR disease modeling) — **Recent merge:** b9a8fa8 added contract tests + reproducibility hardening
- [x] **Control Systems** (280 LOC, 5 equations, PID + state-space LTI)
- [x] **Graph Neural Networks** (350 LOC, 5 equations, message passing + attention)
- [x] **Thermodynamics** (300 LOC, 5 equations, ideal gas + Carnot cycle)

**Batch-creation pattern proven**: All 5 templates follow identical structure (src/model.py → scenarios → tests → config.toml → equations.json).

**Important:** Epidemiology SIR/R0 reference hardening lane (MATH-TRACE-REFERENCE-HARDENING-001) was merged as of 2026-09-30, adding 17 contract tests + reproducibility validation. Phase 4c must reconcile against this baseline before writing papers.

### 4c: Reference Contract & Reconciliation ⏳ CRITICAL — START HERE

**Status**: Phase 4 backlog must be reconciled against recently merged epidemiology hardening lane (commit b9a8fa8, merged 2026-09-30).

**Context**: The epidemiology SIR/R0 reference hardening lane added 17 contract tests + reproducibility validation. This changed the baseline for Phase 4c work. A stashed template/scenario enhancement (stash 278e97a) also exists and must be classified before proceeding.

**Critical First Step**: Execute reconciliation discovery **before any new implementation lanes**.

#### **DISCOVERY LANE: MATH-TRACE-PHASE4-BASELINE-RECONCILIATION-001**

**Purpose**: Reconcile Phase 4 backlog with current main after merged hardening + stashed work.

**Mode**: Read-only inventory and planning (no source edits, no stash application, no release actions).

**Questions to Answer** (in order of priority):

1. **Epidemiology baseline**: What paper/reference artifacts already exist on main? Which Phase 4c-1 acceptance items (Abstract, Intro, Framework, Implementation, Results, Discussion, Conclusion, figures, reproducible build) are already satisfied by recent merges?

2. **Stash content**: What does stash 278e97a contain? Map its contents to backlog items 4c-6 through 4c-10 (scenario extensions). Is it one coherent cross-template enhancement or should it be decomposed by domain?

3. **Scientific contracts by template**: For each of 5 templates, identify:
   - Model governing equations, symbols, units/conventions, parameter meaning
   - Mathematical invariants (conservation, bounds, normalization, stability, limiting behavior, known analytic cases)
   - Existing tests that would catch scientifically meaningful mistakes (not just line coverage)
   - Critical gaps in contract validation

4. **Scenario expansion risks**: Assess each proposed scenario extension (Measles SEIR, Ebola stochastic, Cora GNN, Bode/mass-spring, etc.) for scientific and reproducibility complexity. Identify which are well-bounded vs. which introduce scope expansion.

5. **Release readiness**: Distinguish local readiness (clean main, artifact completeness) from irreversible publishing readiness (GitHub release, Zenodo archival, DOI issuance). What are the prerequisites for each?

**Deliverable**: Compact reconciliation packet + ranked recommendation of no more than 3 next bounded implementation lanes (in order of user value + strategic fit).

**Hard Boundaries**:
- ✅ Read-only (inventory, analysis, recommendations only)
- ✅ Do NOT apply, pop, drop, or alter stash 278e97a
- ✅ Do NOT edit TODO.md, source, tests, templates, docs, or metadata during this lane
- ✅ Do NOT run release, push, tag, GitHub, Zenodo, or publishing actions
- ✅ Do NOT create generic template frameworks or assumptions

**Expected Output Format**:
```
# Phase 4 Reconciliation Report

## Current Baseline (main SHA: xxx)

### Epidemiology Reference Status
- Paper artifacts: [list existing files]
- Contract satisfaction: [checklist of 8 acceptance items]
- Outstanding 4c-1 work: [specific gaps, if any]

### Stash 278e97a Classification
- File inventory: [list by template domain]
- Mapping to backlog: [which 4c tasks it addresses]
- Recommended structure: [single lane vs. split recommendation]

### Template Contract Gaps by Template
[For each of 5 templates: identified missing scientific invariants, test gaps]

### Scenario Expansion Risk Assessment
[For each proposed scenario: complexity level, prerequisite work, or "well-bounded ready to proceed"]

### Recommended Next Lanes (ranked by value)
1. [Lane 1 name + rationale]
2. [Lane 2 name + rationale]
3. [Lane 3 name + rationale]
```

**Timeline**: 2-3 hours (read-only analysis, no implementation)

---

## Simple Backlog Format (Post-Consultant Feedback)

### Now

- [ ] **MATH-TRACE-PHASE4-BASELINE-RECONCILIATION-001** — discovery
  Read-only inventory of current main, the merged epidemiology reference
  hardening result, and preserved template/scenario candidate work.
  Output: one recommended next bounded lane.

### Next — selected after reconciliation

- [ ] Next reference-contract lane — selected by reconciliation.
- [ ] Template/scenario candidate-work triage — split only if reconciliation
  finds distinct domain scopes.
- [ ] Remaining template reference-contract lanes — one at a time.

### Deferred — evidence required

Scenario expansions — only with explicit model, scope, provenance, and
reproducibility contract.

Release readiness — only after the intended v1 reference scope is complete.

Release execution, tag/push, GitHub release, Zenodo/DOI — separate,
explicit human-approved publishing lane.

---

## Design Rationale (Temporary)

See `TODO-PHASE4-REVISION-NOTES.md` for detailed consultant feedback on:

- Correct sequencing: reference contract → tests → scenarios → narrative (not papers first)
- Scientific contracts replacing 90% coverage targets
- Scenario expansion risks (each has hidden complexity)
- Two-stage release: readiness (read-only) + execution (after approval)
- Six-question manifest template for any implementation lane

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
