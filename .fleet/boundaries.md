# math-trace Boundaries

## Role
Formula-to-code traceability framework for research papers: automated conversion of mathematical formulas into validated simulation code.

## Scope
- **What we own:** Template library, formula parsing, code generation, validation framework, template catalog
- **What we don't own:** Specific domain implementations (delegated to individual templates)
- **What we provide:** Reusable templates, formula-to-code mapping, validation infrastructure

## Key Boundaries

### 1. Template Autonomy
- Each template in `templates/` is self-contained and independently maintainable
- Templates follow standardized structure but are free to implement domain-specific logic
- Templates must pass validation before being indexed in template catalog
- fleet-ops agents can refactor within templates (via rope-mcp) without manual review

### 2. Dependency Boundaries
- **Depends on:** fleet-base (for observability), agent-tooling (for MCP interfaces)
- **Does NOT depend on:** Specific MCPs directly (uses fleet-ops for coordination)
- **Used by:** Research teams for rapid formula-to-code conversion

### 3. Public vs Internal
- **Public exports:** README.md, templates/, examples/, docs/
- **Internal only:** .fleet/, audit logs, template index, governance
- All changes to public exports require validation and pass CI/CD before release

### 4. Fleet Integration
- Fleet agents (rope-mcp, vscode-workspace-mcp) can refactor template code
- All MCP operations logged in .fleet/audit.log for compliance
- Template changes trigger automatic validation via fleet-ops

## Hard Invariants

### Template Safety
- **I-TEMPLATE-001:** No template can modify files outside its own directory
  - Enforced by: File path validation in template runner
  - Verified by: Integration tests on all template operations

### Validation Gating
- **I-VALIDATE-001:** All templates must pass validation before public release
  - Enforced by: .fleet/config.yaml auto_validate + CI/CD
  - Verified by: `just test` includes template validation

### Audit Trail
- **I-AUDIT-001:** All fleet agent operations logged with timestamp and decision
  - Enforced by: fleet-base AuditLogger
  - Verified by: .fleet/audit.log contains all operations

## Lifecycle
- **Status:** Mature
- **Layer:** Layer 2 (application/utilities)
- **Maintainer:** Mark Alexiuk
- **Last Updated:** 2026-09-21
