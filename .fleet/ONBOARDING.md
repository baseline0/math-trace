# Onboarding math-trace to Fleet

**How to register math-trace with fleet-ops infrastructure.**

This is a one-time setup. After this, fleet agents can automatically maintain and expand the repo.

## Prerequisites

- `fleet-base` repo cloned at `/home/mark/projects/fleet-base`
- Fleet-ops infrastructure running
- Mark Alexiuk access (creator)

## Step 1: Add to fleet-manifest.yaml

```bash
cd /home/mark/projects/fleet-ops

# Use fleet-base's onboarding script
python ../fleet-base/scripts/onboard_repo.py \
  --repo-name "math-trace" \
  --repo-path "/home/mark/projects/math-trace" \
  --repo-type "public-template-repo" \
  --repo-role "template-provider" \
  --fleet-config ".fleet/config.yaml" \
  --boundaries ".fleet/BOUNDARIES.md"
```

This:
1. Registers math-trace in `fleet-manifest.yaml`
2. Links to `.fleet/config.yaml` for governance rules
3. Links to `.fleet/BOUNDARIES.md` for decision authority
4. Sets role as "template-provider" (can add new templates)

## Step 2: Verify Registration

```bash
cd /home/mark/projects/math-trace

# Check that audit works
just audit-repo math-trace
```

Expected output:
```
✅ math-trace registered in fleet
✅ .fleet/config.yaml found
✅ .fleet/BOUNDARIES.md found
✅ Role: template-provider
✅ Governance: auto_fix enabled for environment, config, discovery
```

## Step 3: Configure MCP Access (Optional)

If you want fleet agents to use MCP for refactoring:

```bash
# Register rope-mcp for math-trace
python ../fleet-base/scripts/register_mcp.py \
  --mcp-name "rope-mcp" \
  --repo "math-trace" \
  --tasks "extract_formula_helpers,unify_build_scripts"

# Register vscode-workspace-mcp for batch operations
python ../fleet-base/scripts/register_mcp.py \
  --mcp-name "vscode-workspace-mcp" \
  --repo "math-trace" \
  --tasks "batch_refactor_templates,batch_validate_formulas"
```

## Step 4: Set Up Audit Logging

Create `.fleet/audit.log` (empty to start):

```bash
cd /home/mark/projects/math-trace
touch .fleet/audit.log

# Test that audit logging works
echo '{"event": "test", "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' >> .fleet/audit.log

# Verify
cat .fleet/audit.log
```

## Step 5: Test Fleet Operations

```bash
# Run a simple fleet check
cd /home/mark/projects/fleet-ops
just audit-repo math-trace

# Should produce output showing:
# - Dependency status
# - Template validation status
# - Configuration check
```

## Step 6: Enable Automated Maintenance

Once verified, enable scheduled maintenance:

```bash
# In fleet-ops config, add math-trace to maintenance schedule
just fleet-config-add-schedule \
  --repo math-trace \
  --schedule "weekly:monday@09:00" \
  --task "validate-all-templates"
```

This:
- Runs `just test-templates` every Monday at 9 AM
- Logs results to `.fleet/audit.log`
- Notifies mark-alexiuk if any tests fail

## Step 7: First Automated Run

Wait for the next scheduled run (or trigger manually):

```bash
# Manual trigger for testing
cd /home/mark/projects/fleet-ops
just fleet-fix --repo math-trace --mode dry-run
```

Review the proposed changes, then:

```bash
just fleet-fix --repo math-trace --mode staged
# Review commits, then push:
git push origin main
```

## Post-Onboarding

### Daily
- Fleet agents validate templates automatically
- GitHub Actions CI/CD runs on every commit

### Weekly
- Fleet agents check dependencies
- Validation report generated and logged

### Monthly
- Full audit of math-trace configuration
- Dependency security scan
- Report generated to fleet dashboard

### Quarterly
- Review template coverage
- Plan new template additions
- Assess maintenance costs

## Important: Keep .fleet/ Local

**Do NOT commit .fleet/ to GitHub!**

```bash
# Verify .gitignore excludes .fleet/
grep "^.fleet/" .gitignore
# Should show: .fleet/

# Before any push, verify:
git status  # Should NOT list .fleet/ files
```

The `.fleet/` directory contains internal fleet infrastructure that external users should never see.

## Troubleshooting Onboarding

### "fleet-base/scripts/onboard_repo.py not found"

```bash
# Check fleet-base is cloned
ls -la /home/mark/projects/fleet-base/scripts/onboard_repo.py

# If not found, clone it
cd /home/mark/projects
git clone https://github.com/baseline0/fleet-base.git
```

### "math-trace not in fleet-manifest.yaml"

```bash
# Check manifest
cd /home/mark/projects/fleet-ops
grep "math-trace" fleet-manifest.yaml

# If missing, run onboard_repo.py again
# Or manually add entry:
cat >> fleet-manifest.yaml << 'EOF'
math-trace:
  path: /home/mark/projects/math-trace
  role: template-provider
  config: .fleet/config.yaml
EOF
```

### "Audit logging not working"

```bash
# Check .fleet/audit.log exists
ls -la /home/mark/projects/math-trace/.fleet/audit.log

# If missing, create it
touch /home/mark/projects/math-trace/.fleet/audit.log

# Test logging
echo '{"test": true}' >> .fleet/audit.log

# Verify
cat .fleet/audit.log
```

## Next Steps

Once onboarded:

1. **Add more templates** — Fleet agents can help scaffold new domains
2. **Enable MCP refactoring** — Rope-mcp can DRY up formula code
3. **Monitor costs** — Check fleet dashboard for MCP usage
4. **Review audit logs** — Monthly reports show what fleet agents did

---

**Questions?** See:
- `.fleet/BOUNDARIES.md` — Governance rules
- `.fleet/MAINTENANCE.md` — Operational procedures
- `fleet-base` documentation — Fleet infrastructure details
