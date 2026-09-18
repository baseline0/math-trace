#!/usr/bin/env python3
"""
Typst syntax and consistency checking for math-trace.

This script is the canonical linter for .typ files. It runs both in CI and locally,
ensuring consistent error detection and messaging.

Usage:
  python scripts/check_typst.py                    # Check all .typ files
  python scripts/check_typst.py path/to/file.typ  # Check specific file
  MATH_TRACE_TYPST_STRICT=1 python scripts/check_typst.py  # Run experimental checks

Exit codes:
  0 = All checks passed
  1 = Errors found (hard gates)
  2 = Warnings found (experimental checks only)
"""

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import re
import os

# ============================================================================
# Issue model: unified representation of all linting findings
# ============================================================================

@dataclass
class Issue:
    """A linting issue found in a .typ file."""
    path: str
    line: Optional[int] = None
    level: str = "error"  # "error" or "warning"
    message: str = ""
    suggestion: Optional[str] = None
    doc_section: Optional[str] = None  # e.g. "§1" or "Block comment collision"

    def format_for_ci(self) -> str:
        """Format as GitHub Actions annotation (::error file=...)."""
        parts = [f"::error" if self.level == "error" else f"::warning"]
        if self.line:
            parts.append(f"file={self.path},line={self.line}")
        else:
            parts.append(f"file={self.path}")

        msg = self.message
        if self.suggestion:
            msg += f" | Suggestion: {self.suggestion}"
        if self.doc_section:
            msg += f" | See: docs/TYPST-GOTCHAS.md {self.doc_section}"

        parts.append(f" {msg}")
        return "".join(parts)

    def format_for_terminal(self) -> str:
        """Format for human reading in terminal."""
        level_marker = "❌" if self.level == "error" else "⚠️"
        loc = f"{self.path}"
        if self.line:
            loc += f":{self.line}"

        lines = [f"{level_marker} {self.level.upper()}: {loc}"]
        lines.append(f"   {self.message}")
        if self.suggestion:
            lines.append(f"   Suggestion: {self.suggestion}")
        if self.doc_section:
            lines.append(f"   Docs: docs/TYPST-GOTCHAS.md {self.doc_section}")
        return "\n".join(lines)


# ============================================================================
# Core checks (always run)
# ============================================================================

def check_typst_compile(paths: list[Path]) -> list[Issue]:
    """
    Run typst compile with diagnostics on all paths.

    Why: This is the authoritative syntax check. Any file that doesn't compile
    is broken and must be fixed before merge.

    See: docs/TYPST-GOTCHAS.md
    """
    issues = []

    for path in paths:
        # For each .typ file, try to compile it
        # We compile to a temp location without actually generating PDF
        cmd = ["typst", "compile", str(path), "/tmp/check_output.pdf", "--diagnostic"]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            # Parse error output to extract line numbers if possible
            stderr = result.stderr + result.stdout

            # Try to extract line number from Typst error
            line_match = re.search(r':(\d+):', stderr)
            line_num = int(line_match.group(1)) if line_match else None

            # Extract first line of error message
            error_lines = [l for l in stderr.split('\n') if l.strip()]
            error_msg = error_lines[0] if error_lines else "Compilation failed"

            issues.append(Issue(
                path=str(path),
                line=line_num,
                level="error",
                message=error_msg,
                doc_section="Typst compilation"
            ))

    return issues


def check_includes_exist(paths: list[Path]) -> list[Issue]:
    """
    Verify that all #include references point to existing files.

    Why: Missing includes cause confusing "file not found" errors at compile time.
    Catching them early gives better diagnostics.

    See: docs/TYPST-GOTCHAS.md §4 (Missing #include files)
    """
    issues = []

    for path in paths:
        content = path.read_text(encoding='utf-8', errors='ignore')

        # Find all #include statements
        include_pattern = r'#include\s+"([^"]+)"'
        for match in re.finditer(include_pattern, content):
            include_path = match.group(1)

            # Resolve relative to the .typ file's directory
            base_dir = path.parent
            resolved = base_dir / include_path

            if not resolved.exists():
                # Find line number
                line_num = content[:match.start()].count('\n') + 1

                issues.append(Issue(
                    path=str(path),
                    line=line_num,
                    level="error",
                    message=f"#include file not found: {include_path}",
                    suggestion=f"Create {include_path} or fix the path",
                    doc_section="§4 (Missing #include files)"
                ))

    return issues


# ============================================================================
# Experimental checks (opt-in via MATH_TRACE_TYPST_STRICT)
# ============================================================================

def check_risky_bold_comment(paths: list[Path]) -> list[Issue]:
    """
    Detect likely '/*' inside bold text like *lean/*.

    Why: Typst parses '/*' as start of block comment, causing unclosed
    comment errors with confusing diagnostics.

    See: docs/TYPST-GOTCHAS.md §1 (Block comment collision)
    """
    issues = []

    for path in paths:
        content = path.read_text(encoding='utf-8', errors='ignore')

        # Pattern: *.../*... (bold text containing /*)
        # This is a heuristic; may have false positives in code blocks
        pattern = r'\*[^*]*\/\*'

        for match in re.finditer(pattern, content):
            line_num = content[:match.start()].count('\n') + 1

            issues.append(Issue(
                path=str(path),
                line=line_num,
                level="warning",
                message="Possible '/*' inside bold text (Typst interprets as block comment start)",
                suggestion="Use backslash: \\/* or use strong(\"...\") instead",
                doc_section="§1 (Block comment collision)"
            ))

    return issues


def check_comment_balance(paths: list[Path]) -> list[Issue]:
    """
    Ensure block comments are balanced (/* has matching */).

    Why: Unclosed comments often cause cryptic "unexpected end of file" errors.
    This heuristic catches the most obvious cases.

    See: docs/TYPST-GOTCHAS.md §1 (Block comment collision)
    """
    issues = []

    for path in paths:
        content = path.read_text(encoding='utf-8', errors='ignore')

        open_count = content.count('/*')
        close_count = content.count('*/')

        if open_count != close_count:
            issues.append(Issue(
                path=str(path),
                level="warning",
                message=f"Unbalanced block comments: {open_count} opening /*, {close_count} closing */",
                suggestion="Check for unclosed /* ... */ blocks",
                doc_section="§1 (Block comment collision)"
            ))

    return issues


# ============================================================================
# Main orchestration
# ============================================================================

def find_typ_files(paths: Optional[list[str]] = None) -> list[Path]:
    """
    Find all .typ files to check.

    If paths provided, check those; otherwise, find all .typ files in repo.
    """
    if paths:
        return [Path(p) for p in paths if p.endswith('.typ')]

    # Recursively find all .typ files, excluding .git and build dirs
    root = Path('.')
    excluded = {'.git', '__pycache__', 'build', 'dist', '.venv', 'venv'}

    typ_files = []
    for p in root.rglob('*.typ'):
        if not any(exc in p.parts for exc in excluded):
            typ_files.append(p)

    return sorted(typ_files)


def main():
    """Run all checks and report results."""

    # Parse arguments
    paths_to_check = sys.argv[1:] if len(sys.argv) > 1 else None
    typ_files = find_typ_files(paths_to_check)

    if not typ_files:
        print("No .typ files found.")
        return 0

    print(f"Checking {len(typ_files)} .typ file(s)...\n")

    # Run all checks
    all_issues = []

    # Core checks (always run)
    all_issues.extend(check_typst_compile(typ_files))
    all_issues.extend(check_includes_exist(typ_files))

    # Experimental checks (opt-in)
    if os.environ.get('MATH_TRACE_TYPST_STRICT'):
        all_issues.extend(check_risky_bold_comment(typ_files))
        all_issues.extend(check_comment_balance(typ_files))

    # Report results
    if not all_issues:
        print("✅ All Typst checks passed!")
        return 0

    # Separate errors and warnings
    errors = [i for i in all_issues if i.level == "error"]
    warnings = [i for i in all_issues if i.level == "warning"]

    # Print in terminal format
    for issue in errors:
        print(issue.format_for_terminal())
    for issue in warnings:
        print(issue.format_for_terminal())

    # Also emit GitHub Actions annotations if in CI
    if os.environ.get('GITHUB_ACTIONS'):
        for issue in all_issues:
            print(issue.format_for_ci())

    # Summary
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")

    # Exit code
    if errors:
        return 1
    elif warnings:
        return 2
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
