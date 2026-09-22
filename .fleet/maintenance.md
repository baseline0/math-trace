# Fleet Maintenance Procedures for math-trace

**Internal documentation for fleet agents maintaining math-trace.**

This file describes how to use fleet-ops to maintain, expand, and improve the math-trace public repository.

## Onboarding math-trace to Fleet

### Step 1: Register in fleet-manifest.yaml

```bash
python fleet-base/scripts/onboard_repo.py \
  --repo math-trace \
  --path /home/mark/projects/math-trace \
  --type public-template-repo \
  --role template-provider \
  --fleet-config /home/mark/projects/math-trace/.fleet/config.yaml
```

This adds math-trace to the fleet-manifest.yaml with:
- Role: `public-template-repo`
- Type: `template-provider`
- Config: points to `.fleet/config.yaml`

### Step 2: Verify Fleet Integration

```bash
cd /home/mark/projects/math-trace
just audit-repo math-trace
```

Should show:
- ✅ .fleet/config.yaml present
- ✅ .fleet/BOUNDARIES.md present
- ✅ .gitignore includes .fleet/
- ✅ Fleet governance rules loaded

## Daily Maintenance Tasks

### Morning: Validation Check

```bash
cd /home/mark/projects/math-trace

# 1. Validate all templates
just test-templates

# 2. Check dependencies
uv sync --frozen

# 3. Audit fleet config
just audit-repo math-trace
```

**If failures:** Log to `.fleet/audit.log`, notify mark-alexiuk.

### Weekly: Full Fleet Check

```bash
# Run fleet-wide audit
cd /home/mark/projects/fleet-ops
just audit-repo math-trace

# Fix infrastructure issues
just fleet-fix --mode staged  # Review before committing
```

**Fixable issues:**
- Dependency updates
- Justfile recipe improvements
- GitHub Actions workflow updates
- Test coverage additions

**Requires review:**
- Formula changes
- Simulation logic changes
- API changes

## Template Management Workflow

### Adding a New Template (e.g., genetics/)

#### 1. Create Template Directory

```bash
cd /home/mark/projects/math-trace
mkdir -p templates/genetics
```

#### 2. Use rope-mcp to Extract Helper Functions

```python
# Use rope-mcp to DRY up model.py patterns across templates
# Example: all templates have similar LaTeX → Typst conversion
# rope-mcp can extract this to a shared helper

coordinator.invoke_mcp(
    agent="template-agent",
    task_type="extract_formula_helpers",
    repo="math-trace",
    template="genetics"
)
```

#### 3. Generate Template Scaffold

```bash
# Copy from similar template
cp -r templates/simple-physics templates/genetics

# Update for new domain
cd templates/genetics
# Edit model.py, simulate.py, main.typ, README.md
```

#### 4. Validate

```bash
cd templates/genetics
python model.py  # Should output genetics_equations.json
python simulate.py
python build_paper.py  # Should generate formulas, figures
```

#### 5. Update Template Index

```bash
# Add to .fleet/templates.json
{
  "genetics": {
    "added": "2026-09-18",
    "formulas": 8,
    "status": "validated",
    "ci_pass_rate": 1.0
  }
}
```

#### 6. Commit

```bash
git add templates/genetics/ .fleet/templates.json
git commit -m "feat: Add genetics template with population genetics examples"
```

#### 7. Push & Release

```bash
git push origin main
# GitHub Actions automatically runs test-templates.yml

# After tests pass, can bump version and publish to PyPI
git tag v0.3.0
git push origin v0.3.0
```

### Updating Template Dependencies

**Scenario:** SymPy releases new version, new features available

```bash
# 1. Batch update all templates
cd /home/mark/projects/math-trace
uv add sympy@latest

# 2. Validate all templates
just test-templates

# 3. If failures, use rope-mcp to modernize code
coordinator.invoke_mcp(
    agent="refactor-agent",
    task_type="modernize_sympy_usage",
    repo="math-trace",
    new_version="1.13"
)

# 4. Commit & push
git add pyproject.toml uv.lock
git commit -m "chore: Update SymPy to 1.13, use new binomial() API"
git push origin main
```

## MCP-Assisted Maintenance

### Use rope-mcp for Refactoring

**Safe refactorings:**
- Extract common formula patterns from model.py
- Rename symbols across templates (n_a → n, etc.)
- Unify build_paper.py implementation

**Unsafe refactorings (requires manual review):**
- Change formula semantics
- Modify simulation algorithms
- Alter output formats

```bash
# Example: Extract formula helpers
coordinator.invoke_mcp(
    agent="rope-agent",
    task_type="extract_formula_helpers",
    repo="math-trace",
    pattern="sympy.binomial",  # Extract all binomial usage
    target_module="math_trace.formula_helpers"
)
```

### Use vscode-workspace-mcp for Batch Changes

**Multi-template operations:**

```bash
# Batch rename symbol across all templates
coordinator.invoke_mcp(
    agent="workspace-agent",
    task_type="batch_refactor_templates",
    repo="math-trace",
    pattern="templates/*/model.py",
    operation="rename_symbol",
    old_name="n_a",
    new_name="n"
)
```

**Always validate afterward:**
```bash
just test-templates
```

## Audit Trail Management

### View Recent Fleet Operations

```bash
# Show last 10 operations
tail -10 .fleet/audit.log

# Filter by event type
grep "agent_action" .fleet/audit.log | tail -5

# Filter by template
grep "genetics" .fleet/audit.log
```

### Generate Monthly Report

```python
# Script to generate fleet operations report
import json
from pathlib import Path
from datetime import datetime, timedelta

audit_log = Path(".fleet/audit.log")
today = datetime.now()
month_ago = today - timedelta(days=30)

with open(audit_log) as f:
    events = [json.loads(line) for line in f]

recent = [e for e in events if datetime.fromisoformat(e['timestamp']) > month_ago]

print(f"Fleet Operations (Last 30 Days):")
print(f"  Total events: {len(recent)}")
print(f"  Agent actions: {sum(1 for e in recent if e['event'] == 'agent_action')}")
print(f"  MCP invocations: {sum(1 for e in recent if e['event'] == 'mcp_invocation')}")
print(f"  Template additions: {sum(1 for e in recent if e['event'] == 'template_addition')}")
```

## Dependency Management

### Weekly: Check for Updates

```bash
cd /home/mark/projects/math-trace

# Check outdated dependencies
uv pip list --outdated

# Update patch versions (safe)
uv add sympy@latest matplotlib@latest numpy@latest

# Validate
just test

# Commit if tests pass
git add uv.lock
git commit -m "chore: Update dependencies (weekly maintenance)"
```

### Monthly: Security Audit

```bash
# Use fleet-base security scanning
python fleet-base/scripts/audit_dependencies.py --repo math-trace

# Check for known vulnerabilities
pip-audit

# Update if needed
uv sync --upgrade
```

## Release Process

### Bumping Version

```bash
# Increment version in pyproject.toml
# Example: 0.1.0 → 0.2.0 (new templates)

vim pyproject.toml  # Change version = "0.2.0"

git add pyproject.toml
git commit -m "chore: Bump version to 0.2.0"
```

### Creating Release Tag

```bash
git tag -a v0.2.0 -m "Release v0.2.0: Add genetics template"
git push origin v0.2.0
```

**GitHub Action triggers:** `.github/workflows/publish.yml` publishes to PyPI automatically.

### Verify PyPI Release

```bash
# After ~2 minutes, check PyPI
pip search math-trace  # (if search enabled)
pip install --upgrade math-trace
```

## Troubleshooting

### Template CI/CD Fails

```bash
# 1. Check what failed
cd templates/simple-physics
python model.py  # Does it run?
python simulate.py  # Does it run?
python build_paper.py  # Does it generate formulas/figures?

# 2. Check dependencies
uv sync

# 3. Look at GitHub Actions logs
# https://github.com/baseline0/math-trace/actions/workflows/test-templates.yml

# 4. Log issue to audit
echo '{"event": "ci_failure", "template": "simple-physics", ...}' >> .fleet/audit.log
```

### MCP Operation Fails

```bash
# 1. Check MCP availability
python -c "from fleet_ops import MCPCoordinator; MCPCoordinator().health_check()"

# 2. Check audit log for error details
grep "simple-physics" .fleet/audit.log | tail -1

# 3. Fallback to manual fix
# Manually refactor code, test, commit
git add .
git commit -m "fix: Manual refactor of template (MCP unavailable)"
```

### Dependency Conflict

```bash
# 1. Clear cache and resync
rm -rf .venv
uv sync

# 2. If still fails, pin conflicting package
# Edit pyproject.toml to pin version
# Example: "sympy>=1.12,<1.13"

uv sync
just test  # Verify

git add pyproject.toml uv.lock
git commit -m "fix: Pin sympy <1.13 due to API incompatibility"
```

## Fleet Agent Capabilities

### What Agents Can Do (Auto-Approved)

✅ **template-validator**
- Run CI/CD for templates
- Validate formulas.typ generation
- Check figures generate correctly
- Log results to .fleet/audit.log

✅ **dependency-updater**
- Bump Python patch versions
- Update uv.lock
- Run tests after update
- Commit if tests pass

✅ **template-discoverer**
- List new templates in .fleet/templates.json
- Update README.md templates section
- Generate template catalog

### What Agents Cannot Do (Manual Review Required)

❌ **formula-refactorer**
- Cannot use rope-mcp to change formula semantics
- Must get mark-alexiuk approval before proceeding

❌ **breaking-changes**
- Cannot modify template structure without human review
- Cannot change API of math_trace library

❌ **documentation-updater**
- Cannot change user-facing docs (README, CONTRIBUTING)
- mark-alexiuk must approve messaging changes

## Contact & Escalation

**Questions?** Check `.fleet/BOUNDARIES.md` for governance rules.

**Agent stuck?** Log to `.fleet/audit.log` with error details.

**Need human approval?** Create PR with `[REVIEW-REQUESTED]` tag.

**Emergency fix needed?** Contact mark-alexiuk directly.

---

**Version:** 1.0  
**Last Updated:** 2026-09-18  
**For:** Fleet agents maintaining math-trace
