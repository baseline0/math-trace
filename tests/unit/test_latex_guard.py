"""Guard: math-trace publishes with Typst, not LaTeX (docs/adr/ADR-301-typst-over-latex.md).

Two checks, each run over every file git tracks (the index, `git ls-files --cached`). Untracked and ignored
files, such as the Lake build tree under lean/.lake, are repository build output, not source, and are never read.

Two checks:

- no file ending in `.tex` outside LATEX_ALLOWLIST;
- no LaTeX compiler invocation (pdflatex, xelatex, lualatex, latexmk) in a non-Markdown
  file outside LATEX_ALLOWLIST.

Not flagged, on purpose: Markdown (ADRs and guides name LaTeX to explain the decision),
LaTeX math strings such as SymPy `.latex` output and equations.json (notation, not tooling),
and `\\documentclass` fixture bytes (not a build). The match is textual, so a comment that
names a compiler is flagged too; that is the coarse, intended behaviour.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from math_trace.constants import REPO_ROOT

# Each entry is a repo-relative path that may contain LaTeX, with the reason it may.
# An entry without a reason does not belong here; a stale entry fails the test below.
# Remove the publishers.py and formula.py entries when LatexPublisher is removed (ADR-301 fallback).
LATEX_ALLOWLIST: frozenset[str] = frozenset(
    {
        # This guard names the compiler commands and the .tex suffix it detects.
        "tests/unit/test_latex_guard.py",
        # LatexPublisher, the pdflatex fallback to Typst (ADR-301). Kept on purpose.
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


def _tracked_files(root: Path = REPO_ROOT) -> list[Path]:
    """Every file git tracks under root, from the index. A tracked path that was deleted from disk is skipped."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "-z"], capture_output=True, text=True, check=True
    )
    paths = [root / name for name in result.stdout.split("\0") if name]
    return [path for path in paths if path.is_file()]


def _rel(path: Path, root: Path = REPO_ROOT) -> str:
    return path.relative_to(root).as_posix()


def _build_command_offenders(files: list[Path], root: Path = REPO_ROOT) -> list[str]:
    """`path:line (tool)` for every non-Markdown, non-allowlisted, text file that names a LaTeX build tool."""
    offenders: list[str] = []
    for path in files:
        rel = _rel(path, root)
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
    return offenders


def test_no_tex_files_outside_allowlist() -> None:
    offenders = sorted(
        _rel(p) for p in _tracked_files() if p.suffix.lower() == ".tex" and _rel(p) not in LATEX_ALLOWLIST
    )
    assert not offenders, f"LaTeX source files found (ADR-301 chose Typst): {offenders}"


def test_no_latex_build_commands_outside_allowlist() -> None:
    offenders = _build_command_offenders(_tracked_files())
    assert not offenders, f"LaTeX build commands found (ADR-301 chose Typst): {offenders}"


def test_allowlist_entries_exist_and_are_not_stale() -> None:
    present = {_rel(p) for p in _tracked_files()}
    missing = sorted(entry for entry in LATEX_ALLOWLIST if entry not in present)
    assert not missing, f"LATEX_ALLOWLIST names files that do not exist: {missing}"


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True)


def _repo_with_untracked_build_tree(tmp_path: Path) -> Path:
    """A fresh repository whose Lake build tree (untracked, as .lake is ignored) names a build tool."""
    _git(tmp_path, "init", "-q")
    build_tree = tmp_path / ".lake" / "packages" / "mathlib" / ".docker"
    build_tree.mkdir(parents=True)
    (build_tree / "Dockerfile").write_text("RUN latexmk -pdf main.tex\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("tracked\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    return tmp_path


def test_guard_ignores_untracked_build_artifacts(tmp_path: Path) -> None:
    root = _repo_with_untracked_build_tree(tmp_path)
    assert _build_command_offenders(_tracked_files(root), root) == []


def test_guard_flags_a_tracked_latex_build_command(tmp_path: Path) -> None:
    root = _repo_with_untracked_build_tree(tmp_path)
    (root / "docs").mkdir()
    (root / "docs" / "build.sh").write_text("latexmk -pdf main.tex\n", encoding="utf-8")
    _git(root, "add", "docs/build.sh")
    assert _build_command_offenders(_tracked_files(root), root) == ["docs/build.sh:1 (latexmk)"]
