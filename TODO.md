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

**Immediate (This Week)**:

**Write paper.typ for each template** (3-4 hrs per template):
- [ ] Quantum Systems: Schrödinger solver paper + benchmark results
- [ ] Epidemiology: Disease dynamics paper + intervention effectiveness
- [ ] Control Systems: Linear systems + PID tuning paper
- [ ] Graph Neural Networks: GNN message passing + attention paper
- [ ] Thermodynamics: Thermodynamic cycle + efficiency paper

**Extend scenarios** (2-3 hrs per template):
- [ ] Quantum: Add double-slit interference + tunneling barrier scenarios
- [ ] Epidemiology: Add Measles (R₀ ≈ 15) + Ebola scenarios
- [ ] Control: Add mass-spring-damper (analytical 2nd order system)
- [ ] GNNs: Add Cora citation network (2.7k nodes) + attention visualization
- [ ] Thermodynamics: Add polytropic processes + phase diagrams

**Status per template**:
- Quantum: Core ✅, Paper ⏳, Scenarios ⏳
- Epidemiology: Core ✅, Paper ⏳, Scenarios ⏳
- Control: Core ✅, Paper ⏳, Scenarios ⏳
- GNNs: Core ✅, Paper ⏳, Scenarios ⏳
- Thermodynamics: Core ✅, Paper ⏳, Scenarios ⏳

### 4d: Test Suite Completion ⏳ Ready to Start

**Why**: Bring all 5 templates to 90%+ test coverage with validation against analytical solutions.

**Per template** (2-3 hrs):
- [ ] Add eigenvalue/R₀/pole/loss accuracy tests
- [ ] Add conservation law tests (energy, population, normalization)
- [ ] Add scenario validation (numerical vs. analytical)
- **Target**: 90%+ coverage on src/model.py

### 4e: GitHub Release v1.0 ⏳ Ready to Start

**Why**: First official release with all 5 templates, complete documentation, and CI/CD validation.

**Steps**:
- [ ] Bump version to 1.0.0 in pyproject.toml
- [ ] Create CHANGELOG.md summarizing 5 templates
- [ ] Tag: `git tag -a v1.0.0 -m "Five production templates + formula traceability"`
- [ ] Push: `git push origin v1.0.0`
- [ ] GitHub release notes + citation instructions

### 4f: Documentation Index ⏳ Ready to Start

**Why**: Help users navigate between templates and understand which to use for their domain.

**Create**:
- [ ] TEMPLATE-INDEX.md with comparison table (equations, LOC, scenarios, difficulty)
- [ ] TEMPLATE-SELECTION.md ("Choose your template" flowchart)
- [ ] Update main README.md with template gallery

---

## Phase 5: Ecosystem Expansion & Specialization 🌱 Planned

**Status**: 5 core templates complete (26 equations, 1,700 LOC). Phase 5 deepens them + adds specialized domains.

### 5a: Complete Papers for 5 Core Templates ⏳ Ready to Start

**Status**: Core code complete. Now adding publication-quality papers + extended scenarios.

**Next** (from Phase 4 continuation):
- Write paper.typ for each template (IEEE format, benchmarks included)
- Extend scenarios (double-slit for Quantum, Measles for Epidemiology, etc.)
- Bring test coverage to 90%+
- Release v1.0.0 with all 5 templates

**Estimated**: 3-4 weeks (parallel work across 5 templates)

### 5b: Add 3-5 Specialized Templates ⏳ Planned

**Target**: Deepen framework with specialized but related domains.

**Candidates** (in priority order):

| Domain | Relevance | Est. Effort | Connects to |
|--------|-----------|-------------|------------|
| **Optimization** | High (ML fundamental) | 5 hrs | GNNs, Control |
| **Fluid Dynamics** | Medium (CFD, physics) | 7 hrs | Thermodynamics |
| **Quantum Computing** | High (frontier ML) | 6 hrs | Quantum Systems |
| **Robotics (Kinematics)** | Medium (engineering) | 6 hrs | Control Systems |
| **Protein Folding** | High (biology, AI) | 7 hrs | GNNs, Optimization |
| **Robotics** | Medium (kinematics) | 6 hrs | requires_review |

**Next Action**: Start with **Quantum Systems** or **Epidemiology** (high relevance, moderate effort).

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

### 5c: Interactive Visualization & Exploration

**Why**: Current output is static PDF. Researchers want interactive parameter sweeps, animations, sensitivity analysis.

**Candidates**:
- [ ] **Jupyter notebook exporter** — convert model → interactive notebook
- [ ] **Streamlit dashboard** — parameter sweep UI
- [ ] **3D visualization** (Plotly for 3D surfaces)
- **Effort**: 8-12 hrs | **Priority**: Low (post-Phase 5a)

### 5d: Integration with External Tools

**Candidates**:
- [ ] **Overleaf + Git sync** — push templates to Overleaf projects
- [ ] **arXiv metadata** — auto-generate arXiv submission YAML
- [ ] **Zenodo/Figshare** — upload papers + data + formulas
- [ ] **Palomar registry** — systematic registration of all proofs
- **Effort per integration**: 4-6 hrs | **Priority**: Low

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

## Immediate Next Steps (This Week)

1. **4a: Auto-environment detection** (fleet agent)
   - `scripts/check-env.sh` + `just setup` recipe
   - 2-3 hrs to implement

2. **4a: Getting Started guide** (human)
   - 3-4 hrs to write
   - Link from README

3. **4b: "Your First Paper" tutorial** (human)
   - 4-5 hrs to write + test
   - Screenshots + step-by-step

4. **4c: Property tests for templates** (fleet agent)
   - Validate model.py, formulas.typ, simulate.py
   - 2-3 hrs to implement

**Owner**: mark-alexiuk (human) + fleet agents (fixable tasks)

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

**Last Updated**: 2026-09-21  
**Next Review**: 2026-10-21  
**Version**: 1.0
