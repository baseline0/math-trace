# Changelog

Generated from conventional commits. See git log for full history.

eef49d3 fix: Resolve all linting violations (RUF, F821, I001)
0babc33 fix: standardize ruff config and resolve all linting errors
f885516 fix: resolve all ruff linting errors in tests
d8c5fb9 refactor(phase1): remove deprecated presentation modules
59bbe47 fix: make /api/preview return JSON instead of raw HTML
824ff88 chore: purge all remaining Marp references from server
5b74ea8 fix: switch live UI preview from Marp to Revealjs + HTMX
d387a54 fix: resolve all ruff linting issues
94037fc refactor: separate auto-generated and hand-curated Justfile recipes
4be6cd8 fix: remove invalid auto-generated Just recipes from Justfile
e6f83d4 fix: update CI paths to match current template structure (src/ subdirs)
439e5ca fix: remove invalid ruff flake8-bandit skips config
476bf81 feat: wire up live formula evaluation in presentation server
76d14ba refactor: Phase 3 - utilities, docstrings, and TODO cleanup
76dda31 refactor: Phase 2 - standardize API responses and imports
493c63a fix: update test_services.py import for renamed Formula class
bd67aab refactor: Phase 1 code quality improvements
de1cfbe feat: add Revealjs + HTMX presentation system
eb53d22 fix: resolve e2e test failures
7abc820 fix: add httpx dependency for FastAPI TestClient support
54ad117 refactor: move ADR content into source code docstrings
fc64c13 fix: remove deprecated version attribute from compose.yaml
c569672 fix: include README.md in Docker build
83b40f6 feat: add end-to-end arXiv pipeline test
d39e6a5 feat: add Docker lifecycle commands to Justfile
d96a0e5 feat: add Docker Compose setup for easy deployment
b31e803 fix: make formula_browser functions callable directly (not just Typer CLI)
29a116b feat: add HTMX-powered formula browser UI
186982f docs: add arXiv extraction workflow guide
301e7b7 feat: add arXiv paper extraction pipeline
0937cb6 fix: handle UI config fields properly (author, theme, etc)
9dc9e14 fix: use correct PresentationGenerator API in preview/export endpoints
7a72aaf refactor: remove AGMAI partnership references
5e1dc54 fix(server): handle YAML library loading gracefully with JSON fallback
e6a1524 feat(templates): complete 5 core templates (epidemiology, control-systems, thermodynamics, gnns)
51bb4d6 fix: update test imports after moving model.py to src/ layout
7ccfcd6 refactor: improve project organization (docs, examples, root cleanup)
fe0f867 feat(server): FastAPI interactive slide editor with live preview
a51b7bf refactor(templates): unified build pipeline, standardized structure, and formula metadata
f1ffb5a docs: absorb AGMAI-READY into README and portfolio materials
d2d08cb refactor: reorganize tests with unit/integration split and conftest-based markers
cbfcfb3 docs: simplify README project structure tree
db3dc75 chore: apply code-as-docs policy, remove CLAUDE.md and .claude/ from tracking
069272d chore: align pre-commit and ruff with PyPI best practices
28f6276 fix: CI template check should only validate complete templates
73e7989 chore: add MIT license and PyPI release recipes
3d2b8d9 chore: fix linting, improve CI, and add badges
3fe74cd feat: add pluggable presentation generator (Marp backend)
1a29a84 chore: add code quality tooling and CI pipeline
afc2188 fix: improve LaTeX-to-Typst converter for template quality
90415ed refactor: move .fleet/ metadata to fleet-coordination registry
5a90d64 refactor: simplify TODO.md per convention — keep only active tasks
fcccc48 fix: add missing required files for quantum-systems template
5845fa3 feat(thermodynamics): add reference-contract validation tests for ideal gas & Carnot cycle
a4b988d refactor(thermodynamics): manifest tolerance and entropy scope corrections
319e79b fix(control-systems): correct settling-status semantics to require sustained band membership
41d07c0 feat(control-systems): finalize DC motor reference contract with finite-horizon semantics
9857523 docs: add mutation-capable implementation manifest for Control contract lane
7c54dd3 docs: add read-only capability preflight manifest for Control contract lane
e4d2e0e docs: add explicit non-authorization to semantic-minimum standard
92b8d14 docs: add equation-traceability semantic minimum standard
d9d2fe3 feat: quantum harmonic oscillator reference contract hardening
d5d161e fix: quantum manifest acceptance criteria updated with distinct failure modes
7eda556 chore: defer platform ideas until two reference contracts exist
429ec37 fix: correct Quantum implementation manifest scope to exclude paper infrastructure
86d04c3 docs: add mutation-capable implementation manifest for Quantum contract lane
40d6296 docs: add read-only capability preflight manifest for Quantum contract lane
2b02a2b docs: add read-only discovery manifest for Phase 4 reconciliation
447f72c docs: restructure Phase 4 per consultant feedback; simplify TODO.md
b9a8fa8 feat: add contract tests and reproducibility hardening for epidemiology reference
57f6ac7 feat(examples): add epidemiology SIR model reference artifact
3cdddde docs: Add Week 1 contract freeze for AGMAI engagement
a807e36 docs: add test status badge to README
caabf11 docs: Add Approved Backlog section (Phase 4-5 marked for execution)
fec62f1 docs: Integrate Phase 4-5 roadmap with detailed execution plan
eb5d857 docs: Update TODO.md - reflect 5 templates complete + Phase 4 continuation roadmap
3294a3f feat: Add 3 production templates - Control Systems, GNNs, Thermodynamics
f7d7587 feat: Add Epidemiology template - SIR/SEIR disease modeling
0c31e65 feat: Add Quantum Systems template - complete Phase 1 reference implementation
6848c73 chore: standardize .fleet/ to schema v1.0 (lowercase, yaml, versioned)
407ab65 feat: One-command installation automation with `just setup` + Python 3.13 standardization
e779420 docs: Add comprehensive Phase 4-6 roadmap with fleet governance integration
187d067 fix: standardize pyproject.toml to modern [dependency-groups] format
c97865b docs: Add feedback round 3 - hardening and edge cases for production readiness
46184c0 docs: Add feedback round 2 - design specifics for deterministic rendering, auditable artifacts, CI gates
6ab17e7 docs: Update market assessment with feedback round 1 - traceability, parameters, CI integration
cdccbb3 docs: Add honest market assessment for formula-driven Marp slides
416937a docs: Add release qualification checklist
347e468 docs: Add strategic planning documents
cb64d09 fix: Resolve Typst compilation and formula conversion issues for release
d9d5496 fix: Improve risky_bold_comment regex to ignore escaped slashes
19c6950 improve: Make Typst linting more robust and data-driven
f1767f5 refactor: Modularize and document Typst linting system
2e0ba7a fix: Escape /* inside bold text; add Typst syntax linting
add74fd feat: Stage C - Private fleet integration for internal maintenance
a94065c feat: Stage B - Fork-friendly templates for physics and biochemistry
d1cad44 fix: Clarify build output when Typst not installed; simplify paper recipe
7dd3cc5 fix: Make build graceful when Typst not installed
fd6e994 feat: Stage A - PyPI-ready setup
b765922 chore: Add pytest/pytest-asyncio as dev dependencies and include uv.lock
