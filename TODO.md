# math-trace Roadmap: Reaching Production Maturity

**Goal**: Build math-trace into a widely-adopted framework for publication-quality mathematical research with full formula-to-code traceability.

**Current Status**: Phase 3 complete (fleet integration + governance). Phase 4+ roadmap below.

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

### 4a: Installation & Onboarding ⏳ Ready to Start

**Why**: Users should be able to use math-trace without friction. Currently requires manual Typst installation and understanding of the build pipeline.

**Fixable (Fleet Agent)**:
- [ ] **Script: Auto-detect environment** (`scripts/check-env.sh`)
  - Detect Typst, Python, uv installation
  - Warn about missing dependencies
  - Provide install instructions per OS
  - **Effort**: 2 hrs | **Priority**: High

- [ ] **Justfile: `just setup` recipe**
  - Runs check-env.sh + `just install-typst` + `uv sync`
  - One-command environment setup
  - **Effort**: 1 hr | **Priority**: High

- [ ] **Docs: Getting Started Guide**
  - Screenshots of `just paper` workflow
  - Troubleshooting common issues
  - Platform-specific notes (macOS/Linux/Windows WSL)
  - **Effort**: 3 hrs | **Priority**: High

**Requires Review (mark-alexiuk)**:
- [ ] **Update README.md** with installation callout
  - Lead with "Install in 30 seconds"
  - Link to Getting Started guide
  - **Effort**: 1 hr | **Priority**: High

### 4b: Documentation & Examples 📚 Ready to Start

**Why**: Current documentation is good but scattered. Users need to understand:
1. How to start their own paper
2. How to add a new domain (biochem → biochemistry template usage)
3. How to formalize theorems
4. How to contribute new templates

**Fixable (Fleet Agent)**:
- [ ] **Generate API docs** (using pdoc or Sphinx)
  - Auto-generate from docstrings
  - Publish to docs/ or GitHub Pages
  - **Effort**: 3 hrs | **Priority**: Medium

- [ ] **Docs: "Your First Paper" Tutorial**
  - Step-by-step walkthrough using simple-physics template
  - Fork template → customize formulas → build PDF
  - **Effort**: 4 hrs | **Priority**: High

- [ ] **Docs: Template Authoring Guide**
  - How to structure model.py
  - SymPy → Typst conversion best practices
  - Simulation validation patterns
  - **Effort**: 5 hrs | **Priority**: High

**Requires Review (mark-alexiuk)**:
- [ ] **Publish docs to GitHub Pages**
  - Configure with GitHub Actions
  - Link from README
  - **Effort**: 2 hrs | **Priority**: Medium

### 4c: Testing & CI/CD Robustness ✅ Ready to Start

**Why**: Templates are validated but there are edge cases in formula conversion, Typst compilation, and simulation validation.

**Fixable (Fleet Agent)**:
- [ ] **Add template property tests**
  - Test that model.py exports valid JSON
  - Test that formulas.typ generates valid Typst
  - Test that simulate.py runs without crashing
  - **Effort**: 3 hrs | **Priority**: High

- [ ] **Expand test coverage**
  - Edge cases: empty formulas, very long formulas, special characters
  - Numerical edge cases: division by zero, negative parameters
  - **Effort**: 4 hrs | **Priority**: Medium

- [ ] **Test on multiple Python versions** (3.11, 3.12, 3.13)
  - Update CI/CD matrix in test-templates.yml
  - Verify numpy/sympy compatibility
  - **Effort**: 2 hrs | **Priority**: Medium

**Requires Review (mark-alexiuk)**:
- [ ] **Test on multiple OSes** (macOS, Ubuntu, Windows WSL)
  - If needed: fix path issues, shell commands
  - **Effort**: 3 hrs | **Priority**: Low

### 4d: Performance & Scaling ⏳ Ready to Start

**Why**: Current example has ~5 formulas. Large papers (50+ formulas, 100+ figures) should still build in <2 minutes.

**Fixable (Fleet Agent)**:
- [ ] **Benchmark current build times**
  - Profile model.py export, formula conversion, simulate.py, Typst compilation
  - Document baseline performance
  - **Effort**: 2 hrs | **Priority**: Medium

- [ ] **Optimize hot paths** (if bottlenecks found)
  - Cache LaTeX → Typst conversions
  - Parallelize figure generation
  - **Effort**: 4-6 hrs | **Priority**: Medium

**Requires Review (mark-alexiuk)**:
- [ ] **Large paper stress test**
  - Create synthetic example with 50+ formulas
  - Verify build completes in <2 min
  - **Effort**: 3 hrs | **Priority**: Low

---

## Phase 5: Ecosystem Expansion 🌱 Planned

### 5a: New Templates (Domains)

**Target**: Add 5 more templates to show framework versatility.

**Candidates** (in priority order):

| Domain | Relevance | Est. Effort | Fleet Category |
|--------|-----------|-------------|-----------------|
| **Quantum Systems** | High (physics + AI) | 6 hrs | requires_review |
| **Epidemiology** | High (timely, validated models) | 6 hrs | requires_review |
| **Control Systems** | High (engineering) | 6 hrs | requires_review |
| **Graph Neural Networks** | High (ML theory) | 6 hrs | requires_review |
| **Fluid Dynamics** | Medium (CFD niche) | 8 hrs | requires_review |
| **Thermodynamics** | Medium (physics) | 6 hrs | requires_review |
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
