# math-trace Fleet Boundaries

**Internal fleet governance for math-trace (not public).**

This document defines how fleet-ops agents maintain and expand math-trace as a public open-source project.

## Repository Role

**Type:** Public template repository + research framework  
**Fleet Status:** Public repo, private fleet integration  
**Maintained By:** mark-alexiuk (with fleet-ops automation)  
**Users:** External scientists + internal fleet agents

## Public vs Private

### Public (Visible to External Users)
- README.md, CONTRIBUTING.md, LICENSE
- examples/ (membrane-dynamics)
- templates/ (simple-physics, biochemistry, etc.)
- docs/ (getting-started, tutorials)
- src/math_trace/ (library code)
- .github/workflows/ (test-templates.yml, publish.yml)

**Principle:** External users see a professional, well-maintained open-source project.

### Private (Fleet Infrastructure Only)
- .fleet/ (this directory)
- .fleet/config.yaml (fleet governance)
- .fleet/BOUNDARIES.md (this file)
- .fleet/audit.log (MCP operations, maintenance logs)
- .fleet/templates.json (internal template tracking)

**Principle:** Fleet agents use this metadata to maintain the repo; external users never see it.

## Governance Model

### Fixable by Fleet Agents (No Review Required)
- **environment** — Python dependencies, uv.lock updates, Python version bumps
- **config** — pyproject.toml metadata, Justfile recipes, GitHub Actions
- **discovery** — New templates, new domain examples (after validation), test coverage

**Validation:** All fixable changes must pass `just test` + template CI/CD before commit.

**Audit:** All changes logged to `.fleet/audit.log` with timestamp, agent, action, result.

### Requires Human Review
- **code** — Formula conversions, simulation logic, SymPy expressions
- **breaking_changes** — API changes, template structure changes
- **public_messaging** — README updates, documentation changes affecting external users

**Process:** Agent proposes change → PR with `[REVIEW-REQUESTED]` tag → mark-alexiuk approves → agent merges.

## Template Management

### Adding New Templates

**Automated (Fleet Agent):**
1. Create `templates/new-domain/` with model.py, simulate.py, build_paper.py, main.typ, README.md
2. Run CI/CD: ensure model.py, simulate.py, build_paper.py all pass
3. Log to `.fleet/templates.json`: add entry with domain, formulas count, status
4. Commit with `[NEW-TEMPLATE]` tag

**Human Review:**
1. Mark-alexiuk reviews domain relevance, documentation quality
2. Checks README captures domain-specific customization
3. Approves or requests changes
4. Push to main branch

**Result:** New template available for external users to fork.

### Updating Existing Templates

**When:** Dependencies update, new SymPy features available, user feedback

**Automated:**
- Dependency updates (uv add/remove)
- Justfile recipe improvements
- Test coverage additions

**Manual Review:**
- Changes to model.py (formula definitions)
- Changes to simulate.py (simulation logic)
- Changes to main.typ narrative

## MCP Coordination

### rope-mcp: Refactoring Template Code

**Enabled for:**
- Extracting common formula helpers (DRY up model.py across templates)
- Unifying build scripts (keep build_paper.py consistent across domains)
- Renaming symbols for clarity

**Disabled for:**
- Changing formula semantics
- Refactoring simulation algorithms

### vscode-workspace-mcp: Multi-Template Operations

**Batch operations across all templates:**
- Update SymPy exports (when SymPy API changes)
- Synchronize Typst formatting across domains
- Bulk template generation

**Always requires validation:** `just test-templates` must pass.

## Dependency Management

### Python Dependencies (uv.lock)

**Who can update:** Fleet agents (auto)  
**Validation:** `uv sync`, `just test` must pass  
**Frequency:** Weekly (fleet-check), as needed for security

**Policy:**
- Pin minor versions in pyproject.toml (e.g., `sympy>=1.12`)
- Uv resolves exact versions in uv.lock
- Every dependency update logged to `.fleet/audit.log`

### Typst Version

**Current:** Latest stable from https://github.com/typst/typst/releases  
**Managed by:** `just install-typst` recipe (uses official installer)  
**Validation:** CI/CD runs on every commit to templates/

## Cost Tracking

### MCP Operations Tracked

- `extract_formula_helpers` — Rope refactoring
- `unify_build_scripts` — Script consolidation
- `batch_refactor_templates` — Multi-template changes

### Maintenance Categories

- `template-validation` — CI/CD runs, fleet-check
- `dependency-updates` — Weekly uv checks
- `ci-cd-maintenance` — GitHub Actions monitoring
- `documentation-sync` — README, TEMPLATE-USAGE updates

### Monthly Report

Fleet-ops generates cost report showing:
- MCP hours spent on math-trace
- Maintenance time per category
- Template validation pass rates

## Audit Trail

**Log Location:** `.fleet/audit.log`  
**Format:** JSON, one entry per line  
**Retention:** 1 year (rotated automatically)

**Logged Events:**
- agent_action: WHO did WHAT on REPO
- mcp_invocation: MCP method, status, duration
- policy_decision: Authorization decision, reason
- template_addition: New template added, validation result
- dependency_update: uv.lock changes, validation result

**Example:**
```json
{
  "timestamp": "2026-09-18T10:30:45Z",
  "event": "agent_action",
  "agent": "template-validator",
  "action": "validate_template",
  "repo": "math-trace",
  "template": "simple-physics",
  "status": "success",
  "details": "All steps passed: model.py, simulate.py, build_paper.py"
}
```

## Release & Publication

### Public Releases (GitHub)

**Trigger:** When template count increases OR major fixes completed  
**Process:**
1. Fleet agent bumps version in pyproject.toml
2. Creates git tag (e.g., v0.2.0)
3. GitHub Action publishes to PyPI
4. Release notes auto-generated from `.fleet/audit.log`

**External users:** See new version on PyPI and GitHub Releases

### PyPI Package

**Maintained By:** Fleet agents (auto-publish on release)  
**Contents:** src/math_trace/, templates/, examples/, docs/
**Excluded:** .fleet/, .gitignore, test logs

## Integration with Fleet Infrastructure

### Fleet Dashboard

**Metrics reported:**
- Template count (+ trend)
- Template pass rate (% passing CI/CD)
- Dependency versions (latest vs pinned)
- Maintenance hours (monthly)

### Palomar Registry

**Formal Proofs:** Optional Lean formalizations in templates/*/lean/  
**Auto-Register:** Disabled (manual review only)  
**Use Case:** Scientists can link their formalized theorems to Palomar

### onboard_repo.py

**How to onboard math-trace as a template repo:**
```bash
python fleet-base/scripts/onboard_repo.py \
  --repo math-trace \
  --type public-template-repo \
  --role template-provider \
  --fleet-config .fleet/config.yaml
```

## Decision Log

### Why .fleet/ is Hidden

- **Public clarity:** External users don't need to know about fleet infrastructure
- **Simplicity:** math-trace appears as a normal open-source repo
- **Flexibility:** Fleet integration details can evolve without public API changes
- **Security:** Audit logs and internal metrics not exposed

### Why enable auto_fix for Dependencies

- **Safety:** uv.lock is deterministic; updates always repeatable
- **Speed:** No need to wait for human review for routine maintenance
- **Auditing:** All changes logged to .fleet/audit.log
- **Validation:** CI/CD must pass before commit

### Why Manual Review for Code Changes

- **Correctness:** Formula changes affect research validity
- **Impact:** Simulation logic changes affect external users
- **Trust:** Scientists need confidence formulas are correct
- **Quality:** Code review ensures best practices

## Contact & Escalation

**Fleet Agent Questions:** Check .fleet/audit.log for recent decisions  
**Policy Exceptions:** Open GitHub issue with `[FLEET-POLICY]` tag  
**Urgent Maintenance:** Contact mark-alexiuk directly

## Version History

- **v1.0** (2026-09-18) — Initial fleet integration for math-trace
  - Public repo + private fleet infrastructure
  - Template management automation
  - MCP coordination for refactoring
  - Audit trail + cost tracking

---

**Not for external distribution.** This file is for internal fleet operations only.
