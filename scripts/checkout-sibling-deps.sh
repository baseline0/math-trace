#!/bin/bash
# Checkout sibling dependencies defined in pyproject.toml
#
# This script reads editable path dependencies from [tool.uv.sources] in pyproject.toml
# and clones each sibling repository to ../dependency-name if not already present.
#
# Designed for use in GitHub Actions workflows and local development.
#
# Usage: scripts/checkout-sibling-deps.sh [--org <org>] [--token <token>]
#
# Arguments (optional):
#   --org ORG       GitHub organization (default: baseline0)
#   --token TOKEN   GitHub API token (default: $GITHUB_TOKEN)
#
# Environment variables:
#   GITHUB_TOKEN    Automatically provided by GitHub Actions
#   GITHUB_WORKSPACE Set by GitHub Actions; used to determine siblings directory
#
# Behavior:
#   - Idempotent: skips already-present, valid git repositories
#   - Fails loudly with actionable errors if any dependency cannot be cloned
#   - Works in CI and local development (auto-detects token availability)
#   - Validates that cloned repos are usable git repositories

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SIBLINGS_DIR="${GITHUB_WORKSPACE:-$(dirname "$PROJECT_ROOT")}"

# Defaults (can be overridden by arguments)
ORG="${ORG:-baseline0}"
TOKEN="${GITHUB_TOKEN:-}"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --org)
      ORG="$2"
      shift 2
      ;;
    --token)
      TOKEN="$2"
      shift 2
      ;;
    --help|-h)
      head -20 "$0" | tail -18
      exit 0
      ;;
    *)
      echo "::error::Unknown argument: $1"
      exit 1
      ;;
  esac
done

# ============================================================================
# Functions
# ============================================================================

# Extract sibling dependency names from pyproject.toml
# Returns one dependency name per line (e.g., "fleet-base\nfleet-toolbox")
extract_dependencies() {
  local pyproject="$1"

  if [[ ! -f "$pyproject" ]]; then
    echo "::error::pyproject.toml not found at $pyproject"
    return 1
  fi

  # Extract all lines from [tool.uv.sources] section that match editable path pattern.
  # Pattern: name = { path = "../something", editable = true }
  # We extract the dependency name and the path, then validate path is a sibling.

  local in_sources_section=0
  local dep_name=""
  local dep_path=""

  while IFS= read -r line; do
    # Enter the [tool.uv.sources] section
    if [[ "$line" =~ ^\[tool\.uv\.sources\] ]]; then
      in_sources_section=1
      continue
    fi

    # Exit [tool.uv.sources] when we hit another section
    if [[ "$line" =~ ^\[[a-z] ]] && [[ $in_sources_section -eq 1 ]]; then
      in_sources_section=0
      continue
    fi

    # Skip if not in the sources section or line is empty/comment
    if [[ $in_sources_section -eq 0 ]]; then
      continue
    fi
    if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "${line// }" ]]; then
      continue
    fi

    # Parse: name = { path = "../something", editable = true }
    # Extract the key (dependency name)
    if [[ "$line" =~ ^([a-zA-Z0-9_-]+)[[:space:]]*= ]]; then
      dep_name="${BASH_REMATCH[1]}"

      # Check if this line has both path = "../..." and editable = true
      if [[ "$line" =~ path[[:space:]]*=[[:space:]]*\"\.\.\/([^\"]+)\" ]]; then
        if [[ "$line" =~ editable[[:space:]]*=[[:space:]]*true ]]; then
          echo "$dep_name"
        fi
      fi
    fi
  done < "$pyproject"

  return 0
}

# Checkout a single sibling dependency
# Returns 0 on success, 1 on failure
checkout_sibling() {
  local dep_name="$1"
  local sibling_path="$SIBLINGS_DIR/$dep_name"

  # If directory already exists and is a valid git repo, skip
  if [[ -d "$sibling_path/.git" ]]; then
    echo "  ✓ $dep_name (already present at $sibling_path)"
    return 0
  fi

  # If directory exists but is NOT a git repo, error (likely corruption or misconfiguration)
  if [[ -d "$sibling_path" ]]; then
    echo "  ✗ $dep_name"
    echo "::error::$sibling_path exists but is not a valid git repository. Remove it and retry."
    return 1
  fi

  # Construct clone URL
  local clone_url="https://github.com/$ORG/$dep_name.git"
  local clone_opts=()

  # Use token if available (for authentication with private repos in CI)
  if [[ -n "$TOKEN" ]]; then
    clone_url="https://${TOKEN}@github.com/$ORG/$dep_name.git"
    # Mask token in output
    clone_opts+=("--quiet")
  fi

  echo -n "  ⋯ $dep_name... "

  # Clone the repository
  if ! git clone "${clone_opts[@]}" "$clone_url" "$sibling_path" 2>&1 | grep -v "Cloning"; then
    echo ""
    echo "::error::Failed to clone $dep_name from $clone_url"
    echo "::error::  Check that:"
    echo "::error::    1. Repository exists at github.com/$ORG/$dep_name"
    echo "::error::    2. Token (if used) has sufficient permissions"
    echo "::error::    3. Network connectivity is available"
    return 1
  fi

  # Validate the clone is a usable git repo
  if [[ ! -d "$sibling_path/.git" ]]; then
    echo "✗ (validation failed)"
    echo "::error::$sibling_path was cloned but is not a valid git repository"
    rm -rf "$sibling_path"
    return 1
  fi

  echo "✓"
  return 0
}

# ============================================================================
# Main
# ============================================================================

main() {
  echo "📦 Checking out sibling dependencies"
  echo ""
  echo "  Project:      $PROJECT_ROOT"
  echo "  Siblings dir: $SIBLINGS_DIR"
  echo "  GitHub org:   $ORG"
  echo "  Auth:         $([ -n "$TOKEN" ] && echo "via token" || echo "no token (public repos only)")"
  echo ""

  local pyproject="$PROJECT_ROOT/pyproject.toml"

  # Extract all sibling dependencies
  local dependencies
  if ! dependencies=$(extract_dependencies "$pyproject"); then
    return 1
  fi

  if [[ -z "$dependencies" ]]; then
    echo "  ℹ No sibling dependencies found in pyproject.toml"
    return 0
  fi

  echo "  Cloning dependencies:"
  local failed=0
  while IFS= read -r dep; do
    if [[ -n "$dep" ]]; then
      if ! checkout_sibling "$dep"; then
        failed=$((failed + 1))
      fi
    fi
  done <<< "$dependencies"

  echo ""
  if [[ $failed -gt 0 ]]; then
    echo "✗ Failed to checkout $failed sibling dependency/dependencies"
    return 1
  fi

  echo "✓ All sibling dependencies ready"
  return 0
}

main "$@"
