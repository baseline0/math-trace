#!/bin/bash
# Validate that precommit configurations are consistent across the fleet
#
# Usage:
#   bash scripts/validate-precommit-consistency.sh [--fix]
#
# Options:
#   --fix   Apply fixes to non-compliant repos (not implemented yet)
#
# Exit codes:
#   0 = All repos compliant
#   1 = Some repos non-compliant
#   2 = Error (missing tool, etc.)

set -e

FLEET_ROOT="${FLEET_ROOT:-/home/mark/projects}"
FIX_MODE="${1:---check}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track results
COMPLIANT_COUNT=0
NON_COMPLIANT_COUNT=0
REPOS_CHECKED=0

# Fleet repos to check
FLEET_REPOS=(
  "math-trace"
  "fleet-ops"
  "fleet-base"
  "fleet-agents"
  "fleet-spec"
  "fleet-toolbox"
  "fleet-coordination"
)

echo "🔍 Validating pre-commit configurations across fleet..."
echo ""

# Check if uv is available (for running pre-commit)
if ! command -v uv &> /dev/null; then
  echo -e "${RED}❌ uv not found. Install from: https://docs.astral.sh/uv/installation${NC}"
  exit 2
fi

# Validation rules
check_repo() {
  local repo_path="$1"
  local repo_name=$(basename "$repo_path")
  local config_file="$repo_path/.pre-commit-config.yaml"

  if [ ! -f "$config_file" ]; then
    echo -e "${YELLOW}⊘ $repo_name: No .pre-commit-config.yaml${NC}"
    return 1
  fi

  REPOS_CHECKED=$((REPOS_CHECKED + 1))
  local issues=0

  # Check 1: default_install_hook_types declared
  if ! grep -q "default_install_hook_types" "$config_file"; then
    echo -e "${RED}  ✗ Missing default_install_hook_types${NC}"
    issues=$((issues + 1))
  else
    echo -e "${GREEN}  ✓ Has default_install_hook_types${NC}"
  fi

  # Check 2: pre-commit and pre-push both declared
  if grep -q "default_install_hook_types:" "$config_file"; then
    if ! grep -A2 "default_install_hook_types:" "$config_file" | grep -q "pre-commit"; then
      echo -e "${RED}  ✗ Missing pre-commit in default_install_hook_types${NC}"
      issues=$((issues + 1))
    fi
    if ! grep -A2 "default_install_hook_types:" "$config_file" | grep -q "pre-push"; then
      echo -e "${RED}  ✗ Missing pre-push in default_install_hook_types${NC}"
      issues=$((issues + 1))
    fi
  fi

  # Check 3: All hooks have names with priority tags
  local hooks_without_names=$(grep -c "^\s*- id:" "$config_file" | head -1)
  local hooks_with_names=$(grep -c "^\s*name:.*\[P[0-3]\]" "$config_file" | head -1)

  if [ "$hooks_without_names" -gt 0 ] && [ "$hooks_with_names" -lt "$hooks_without_names" ]; then
    echo -e "${YELLOW}  ⚠ Some hooks missing [P0-P3] priority tags${NC}"
    issues=$((issues + 1))
  fi

  # Check 4: Unit tests in pre-push stage (if they exist)
  if grep -q "id: just-test-unit\|id: pytest" "$config_file"; then
    if grep -A10 "id: just-test-unit\|id: pytest" "$config_file" | grep -q "stages:.*pre-push"; then
      echo -e "${GREEN}  ✓ Tests in pre-push stage${NC}"
    else
      echo -e "${RED}  ✗ Tests not in pre-push stage${NC}"
      issues=$((issues + 1))
    fi
  fi

  # Check 5: Validate syntax
  if ! uv run --python 3.13 pre-commit validate-config "$config_file" > /dev/null 2>&1; then
    echo -e "${RED}  ✗ Configuration syntax invalid${NC}"
    issues=$((issues + 1))
  else
    echo -e "${GREEN}  ✓ Configuration syntax valid${NC}"
  fi

  if [ $issues -eq 0 ]; then
    echo -e "${GREEN}✅ $repo_name: COMPLIANT${NC}"
    COMPLIANT_COUNT=$((COMPLIANT_COUNT + 1))
    return 0
  else
    echo -e "${RED}❌ $repo_name: $issues issue(s)${NC}"
    NON_COMPLIANT_COUNT=$((NON_COMPLIANT_COUNT + 1))
    return 1
  fi
}

# Check all fleet repos
for repo_name in "${FLEET_REPOS[@]}"; do
  repo_path="$FLEET_ROOT/$repo_name"

  if [ ! -d "$repo_path" ]; then
    echo -e "${BLUE}→ $repo_name${NC}"
    echo -e "${YELLOW}  (not found in $FLEET_ROOT)${NC}"
    continue
  fi

  echo -e "${BLUE}→ $repo_name${NC}"
  check_repo "$repo_path"
  echo ""
done

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}Summary:${NC}"
echo -e "  Repos checked:    $REPOS_CHECKED"
echo -e "  ${GREEN}Compliant:${NC}        $COMPLIANT_COUNT"
echo -e "  ${RED}Non-compliant:${NC}    $NON_COMPLIANT_COUNT"

if [ $NON_COMPLIANT_COUNT -eq 0 ]; then
  echo -e "${GREEN}✅ All repos compliant!${NC}"
  exit 0
else
  echo -e "${RED}❌ Some repos need attention${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Review non-compliant repos above"
  echo "  2. Update their .pre-commit-config.yaml"
  echo "  3. Follow the math-trace config as reference"
  exit 1
fi
