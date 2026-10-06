# Changelog

All notable changes to math-trace are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0-rc1] - 2026-10-06

### Added

#### Templates & Examples
- **5 core templates** with complete models, simulations, and papers:
  - Epidemiology (SIR/SEIR models)
  - Quantum Systems (particle-in-box, harmonic oscillator)
  - Control Systems (DC motor, PID controller)
  - Graph Neural Networks (message passing, attention)
  - Thermodynamics (ideal gas, Carnot cycle)

#### Testing & Quality
- Unit test suite: 144 tests passing, comprehensive happy-path coverage
- Formula generation tests with SymPy → LaTeX → Typst pipeline validation
- Template consistency checks (model definitions, papers, scenarios)
- pytest-cov integration for iterative coverage guidance

#### CLI & API
- FastAPI server with arXiv formula extraction (`/api/fetch-paper`, `/api/formulas`, `/api/preview`)
- Interactive dashboard with 2-column layout for formula exploration
- Docker Compose setup for easy deployment
- Typer CLI with auto-generated Justfile recipes

#### Documentation
- AGMAI-READY.md: public contract defining guarantees and limitations
- Architecture Decision Records (ADR-001 to ADR-003) in docs/adr/
- CONTRIBUTING.md with template contribution workflow
- Getting Started guide for users

#### Build & Release
- Justfile with recipes: `just paper`, `just test`, `just fmt`, `just check`, `just docker-up`
- Pre-commit hooks (P0-P3) for safety gates
- GitHub Actions workflows for linting, testing, and validation
- Ruff configuration aligned with fleet-base standards (E, W, F, I, UP, N, C4, SIM, RUF)

### Changed

#### Code Quality
- Upgraded ruff config: line-length 100 → 120, expanded lint rules
- Standardized all Python to 3.13+
- Implemented pragmatic test pyramid (unit → integration → e2e) over arbitrary coverage %

#### UI/UX
- Replaced deprecated Marp/presentation system with Revealjs + HTMX
- Streamlined dashboard to focus on formula extraction and verification
- Added live formula preview with MathJax rendering

#### Architecture
- Simplified server codebase (~600 lines removed, deprecated presentation backends)
- Moved formula generation to core library (generators.py, services.py)
- Separated auto-generated Justfile recipes from hand-curated ones

### Fixed

- SymPy nested brace handling in LaTeX-to-Typst converter
- Typst deprecated syntax (label: → `<label>`) in all templates
- Python version pinning to 3.13 across all templates
- Private key detection in pre-commit hooks
- Large file checking in CI pipeline

### Removed

- Deprecated Marp backend (presentation_generator.py)
- Presentation server module (replaced with Revealjs)
- Outdated Palomar registry stubs (deferred to v1.0.0)
- Python 3.10 compatibility hacks

### Known Limitations

- **SymPy constraints**: Only equations expressible in SymPy are supported
- **Unit tracking**: Units are metadata only; no automatic dimensional analysis
- **Numerical stability**: Simulations not validated for long-duration runs
- **Peer review**: math-trace supplements but does not replace scientific review
- **Scalability**: Papers with 100+ equations may have slow compile times

---

## Roadmap to v1.0.0

### v0.9.0-rc1 → v0.9.0
- External reproducibility review sign-off
- CHANGELOG and CITATION.cff finalized

### v1.0.0
- Lean formalization on ≥3 templates (Lean 4 theorems)
- Zenodo DOI minting for archival
- API stability declaration (no breaking changes)

### Post-v1.0.0 (Backlog)
- Palomar registry integration (optional)
- Interactive visualizations (Streamlit/Jupyter)
- Multi-paper comparison
- PDF export with LaTeX alternatives
- CI/CD automation enhancements

---

## Version History

### [0.1.0] - Initial commit
- Core infrastructure: SymPy → LaTeX → Typst pipeline
- Membrane dynamics example (stochastic P systems)
- Basic formula extraction and traceability

---

**For questions or feedback**, open a [GitHub issue](https://github.com/baseline0/math-trace/issues).
