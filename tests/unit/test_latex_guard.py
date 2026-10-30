"""Guard: math-trace publishes with Typst, not LaTeX (docs/adr/ADR-001-typst-over-latex.md).

Two checks, each run over every text file in the working tree:

- no file ending in `.tex` outside LATEX_ALLOWLIST;
- no LaTeX compiler invocation (pdflatex, xelatex, lualatex, latexmk) in a non-Markdown
  file outside LATEX_ALLOWLIST.

Not flagged, on purpose: Markdown (ADRs and guides name LaTeX to explain the decision),
LaTeX math strings such as SymPy `.latex` output and equations.json (notation, not tooling),
and `\\documentclass` fixture bytes (not a build). The match is textual, so a comment that
names a compiler is flagged too; that is the coarse, intended behaviour.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

from math_trace.constants import REPO_ROOT

pytestmark = pytest.mark.unit

# Each entry is a repo-relative path that may contain LaTeX, with the reason it may.
# An entry without a reason does not belong here; a stale entry fails the test below.
# Remove the publishers.py and formula.py entries when LatexPublisher is removed (ADR-001 fallback).
LATEX_ALLOWLIST: frozenset[str] = frozenset(
    {
        # This guard names the compiler commands and the .tex suffix it detects.
        "tests/unit/test_latex_guard.py",
        # LatexPublisher, the pdflatex fallback to Typst (ADR-001). Kept on purpose.
        "src/math_trace/publishers.py",
        # Comment at line 33 says a pdflatex fallback is available; prose, not a build call.
        "src/math_trace/formula.py",
    }
)

SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "dist",
    "build",
}
BUILD_TOOL = re.compile(r"\b(pdflatex|xelatex|lualatex|latexmk)\b")


def _working_tree_files() -> list[Path]:
    """Every regular file under REPO_ROOT, pruning SKIP_DIRS and any `.venv*` directory."""
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".venv")]
        for name in filenames:
            found.append(Path(dirpath, name))
    return found


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def test_no_tex_files_outside_allowlist() -> None:
    offenders = sorted(
        _rel(p) for p in _working_tree_files() if p.suffix.lower() == ".tex" and _rel(p) not in LATEX_ALLOWLIST
    )
    assert not offenders, f"LaTeX source files found (ADR-001 chose Typst): {offenders}"


def test_no_latex_build_commands_outside_allowlist() -> None:
    offenders: list[str] = []
    for path in _working_tree_files():
        rel = _rel(path)
        if path.suffix.lower() == ".md" or rel in LATEX_ALLOWLIST:
            continue
        data = path.read_bytes()
        if b"\0" in data:  # binary file
            continue
        text = data.decode("utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            match = BUILD_TOOL.search(line)
            if match:
                offenders.append(f"{rel}:{lineno} ({match.group(1)})")
    assert not offenders, f"LaTeX build commands found (ADR-001 chose Typst): {offenders}"


def test_allowlist_entries_exist_and_are_not_stale() -> None:
    present = {_rel(p) for p in _working_tree_files()}
    missing = sorted(entry for entry in LATEX_ALLOWLIST if entry not in present)
    assert not missing, f"LATEX_ALLOWLIST names files that do not exist: {missing}"
