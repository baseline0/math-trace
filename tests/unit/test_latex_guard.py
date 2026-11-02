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

import os
import re
import subprocess
from pathlib import Path

import pytest

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


GIT_LOCATION_VARS = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_NAMESPACE",
    "GIT_PREFIX",
)


def _git_env() -> dict[str, str]:
    """The environment for a git call, without the git location variables a git hook exports.

    git exports GIT_DIR and GIT_INDEX_FILE to pre-commit hooks. Inherited, they point `git -C <other repo>` at the
    hook's own repository and index, so the guard and its temporary-repository tests read and write the wrong one.
    Other GIT_* settings are kept.
    """
    return {key: value for key, value in os.environ.items() if key not in GIT_LOCATION_VARS}


def _tracked_files(root: Path = REPO_ROOT) -> list[Path]:
    """Every file git tracks under root, plus every untracked file git does not ignore.

    Ignored build trees (lean/.lake) are left out, as they are not source. Untracked, unignored files are included, so a
    new file with a build command is caught before it is committed, as the walk of the working tree caught it.
    """
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        capture_output=True,
        text=True,
        check=True,
        env=_git_env(),
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
    subprocess.run(["git", "-C", str(root), *args], capture_output=True, check=True, env=_git_env())


def _repo_with_untracked_build_tree(tmp_path: Path) -> Path:
    """A fresh repository whose Lake build tree (ignored, as lean/.gitignore ignores .lake/) names a build tool."""
    _git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text(".lake/\n", encoding="utf-8")
    build_tree = tmp_path / ".lake" / "packages" / "mathlib" / ".docker"
    build_tree.mkdir(parents=True)
    (build_tree / "Dockerfile").write_text("RUN latexmk -pdf main.tex\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("tracked\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md", ".gitignore")
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


def test_guard_is_not_fooled_by_the_hook_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run as a pre-commit hook does: GIT_DIR and GIT_INDEX_FILE point at some other repository. The guard must still
    read the temporary repository it was asked about."""
    root = _repo_with_untracked_build_tree(tmp_path)
    (root / "docs").mkdir()
    (root / "docs" / "build.sh").write_text("latexmk -pdf main.tex\n", encoding="utf-8")
    _git(root, "add", "docs/build.sh")
    other = tmp_path / "elsewhere"
    other.mkdir()
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(other / "index"))
    assert _build_command_offenders(_tracked_files(root), root) == ["docs/build.sh:1 (latexmk)"]


def _staged_names(root: Path) -> str:
    """The staged paths of root, read with the GIT_* variables scrubbed."""
    result = subprocess.run(
        ["git", "-C", str(root), "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=True,
        env=_git_env(),
    )
    return result.stdout


def _calling_and_scratch(tmp_path: Path, script: str) -> tuple[Path, Path]:
    """A `calling` repository with one staged file, and a `scratch` repository whose tracked build.sh holds script."""
    calling = tmp_path / "calling"
    scratch = tmp_path / "scratch"
    for repo in (calling, scratch):
        repo.mkdir()
        _git(repo, "init", "-q")
    (calling / "staged.txt").write_text("staged\n", encoding="utf-8")
    _git(calling, "add", "staged.txt")
    (scratch / "build.sh").write_text(script, encoding="utf-8")
    _git(scratch, "add", "build.sh")
    return calling, scratch


def _point_git_env_at(monkeypatch: pytest.MonkeyPatch, repo: Path) -> None:
    """Export GIT_DIR and GIT_INDEX_FILE for repo, as a pre-commit hook does."""
    monkeypatch.setenv("GIT_DIR", str(repo / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(repo / ".git" / "index"))


def test_guard_does_not_mutate_calling_repository_index(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run as a hook does, with GIT_DIR and GIT_INDEX_FILE pointing at the calling repository. The guard must report
    the scratch offender, and the calling repository's staged list must be unchanged afterwards."""
    calling, scratch = _calling_and_scratch(tmp_path, "latexmk -pdf main.tex\n")
    staged_before = _staged_names(calling)
    assert staged_before == "staged.txt\n"
    _point_git_env_at(monkeypatch, calling)

    assert _build_command_offenders(_tracked_files(scratch), scratch) == ["build.sh:1 (latexmk)"]

    assert _staged_names(calling) == staged_before


def test_clean_scratch_repository_reports_nothing_and_leaves_calling_index_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mirror of the test above: a clean scratch repository reports nothing, and the calling index is untouched."""
    calling, scratch = _calling_and_scratch(tmp_path, "echo hello\n")
    staged_before = _staged_names(calling)
    assert staged_before == "staged.txt\n"
    _point_git_env_at(monkeypatch, calling)

    assert _build_command_offenders(_tracked_files(scratch), scratch) == []

    assert _staged_names(calling) == staged_before


def test_git_env_keeps_unrelated_git_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Only the location variables are removed; identity, SSH and config settings reach git unchanged."""
    monkeypatch.setenv("GIT_DIR", "/elsewhere/.git")
    monkeypatch.setenv("GIT_SSH_COMMAND", "ssh -i /keys/ci")
    monkeypatch.setenv("GIT_AUTHOR_NAME", "CI Bot")
    env = _git_env()
    assert "GIT_DIR" not in env
    assert env["GIT_SSH_COMMAND"] == "ssh -i /keys/ci"
    assert env["GIT_AUTHOR_NAME"] == "CI Bot"


def test_guard_flags_an_untracked_unignored_build_command(tmp_path: Path) -> None:
    """A new file not yet added is still checked, so the guard keeps the coverage of the old working-tree walk."""
    root = _repo_with_untracked_build_tree(tmp_path)
    (root / "notes.sh").write_text("latexmk -pdf main.tex\n", encoding="utf-8")
    assert _build_command_offenders(_tracked_files(root), root) == ["notes.sh:1 (latexmk)"]
