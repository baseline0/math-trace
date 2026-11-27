"""Report model, hashing, provenance, and verdict logic for reference checks.

## Specification Map

| Rule or Invariant | Authority | Enforcement |
|---|---|---|
| Verdict fails loudly: missing required files, nonzero build step, nonzero contract tests, no outputs, nondeterministic outputs, expected-file problem, expected-hash mismatch are each named | reviewer-path contract | `verdict`; `tests/unit/test_reference_check.py::test_a_report_where_every_check_holds_passes`, `test_each_failed_check_is_named_in_the_report`, `test_a_changed_output_is_named_in_the_reason`, `test_a_changed_uv_lock_hash_is_named_in_the_reason`, `test_expected_problem_is_reported_as_failure` |
| Python version change is named alone (no output-drift noise); uv.lock change is named; both can be reported together | reviewer-path expected-hashes contract | `expected_reasons`; `tests/unit/test_reference_check.py::test_python_version_mismatch_is_reported_with_reason`, `test_a_python_change_is_named_and_not_reported_as_output_drift`, `test_python_and_uv_lock_changes_are_both_reported` |
| Dirty tree is recorded in provenance/report but is not a verdict failure | reviewer-path contract | `provenance`, `Report.dirty`, `verdict`; `tests/unit/test_reference_check.py::test_dirty_report_does_not_fail_verdict` |
| Required files are checked relative to reference directory; only absent files are listed | reviewer-path contract | `missing_required`; `tests/unit/test_reference_check.py::test_missing_required_lists_only_the_absent_files` |
| Output hashes are sha256 over files matching output globs, keyed by posix-relative path, sorted | reviewer-path determinism contract | `hash_files`, `file_sha256`; `tests/unit/test_reference_check.py::test_hashes_are_sorted_and_change_when_content_changes` |
| Expected-hashes file must exist/read as JSON with python/uv_lock_sha256/outputs; missing/unreadable is reported | reviewer-path expected-hashes contract | `read_expected`, `load_expected`; `tests/unit/test_reference_check.py::test_expected_problem_is_reported_as_failure`, `test_read_expected_reports_missing_and_unreadable` |
| `expected_payload` records python, uv_lock_sha256, and first-run outputs for a passing run | reviewer-path record contract | `expected_payload`; `tests/unit/test_reference_check.py::test_expected_payload_records_first_run_outputs` |
| Provenance outside git repo is explicitly unknown/clean; git location vars are stripped from child env | reviewer-path provenance contract | `provenance`, `_clean_env`; `tests/unit/test_reference_check.py::test_provenance_outside_a_git_repository_is_explicitly_unknown` |
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import platform
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from .registry import Reference


@dataclass(frozen=True)
class StepResult:
    argv: tuple[str, ...]
    returncode: int
    seconds: float


@dataclass(frozen=True)
class ExpectedHashes:
    """Recorded hashes a build is compared with: the Python version, the uv.lock hash, and each output's hash."""

    python: str
    uv_lock_sha256: str
    outputs: dict[str, str]


@dataclass
class Report:
    reference: str
    source_revision: str
    tag: str | None
    dirty: bool
    python: str
    missing_required: list[str] = field(default_factory=list)
    inputs: dict[str, str] = field(default_factory=dict)
    outputs_run_1: dict[str, str] = field(default_factory=dict)
    outputs_run_2: dict[str, str] = field(default_factory=dict)
    steps: list[StepResult] = field(default_factory=list)
    tests_returncode: int | None = None
    deterministic: bool = False
    failures: list[str] = field(default_factory=list)
    uv_lock_sha256: str = ""
    expected: ExpectedHashes | None = None
    expected_problem: str | None = None  # the registered expected file is absent or unreadable

    @property
    def result(self) -> str:
        return "pass" if not self.failures else "fail"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_files(directory: Path, patterns: tuple[str, ...]) -> dict[str, str]:
    """SHA-256 of every file matching the patterns, keyed by its path relative to `directory`, sorted."""
    found: dict[str, str] = {}
    for pattern in patterns:
        for match in glob.glob(str(directory / pattern), recursive=True):
            path = Path(match)
            if path.is_file():
                found[path.relative_to(directory).as_posix()] = file_sha256(path)
    return dict(sorted(found.items()))


def missing_required(reference: Reference, repo: Path) -> list[str]:
    base = repo / reference.directory
    return [name for name in reference.required if not (base / name).is_file()]


def verdict(report: Report) -> list[str]:
    """Why the report fails, one reason per failed check. Empty means it passes."""
    reasons: list[str] = []
    if report.missing_required:
        reasons.append(f"required files missing: {', '.join(report.missing_required)}")
    for step in report.steps:
        if step.returncode != 0:
            reasons.append(f"build step exited {step.returncode}: {' '.join(step.argv)}")
    if report.tests_returncode != 0:
        reasons.append(f"contract tests exited {report.tests_returncode}")
    if not report.outputs_run_1:
        reasons.append("the build produced no outputs")
    if not report.deterministic:
        reasons.append("two builds from the same checkout produced different outputs")
    if report.expected_problem:
        reasons.append(report.expected_problem)
    if report.expected is not None:
        reasons.extend(expected_reasons(report, report.expected))
    return reasons


def expected_reasons(report: Report, expected: ExpectedHashes) -> list[str]:
    """Why this build differs from the recorded hashes. A Python change is named alone, not reported as output drift."""
    reasons: list[str] = []
    if report.python != expected.python:
        reasons.append(
            f"python version changed: recorded {expected.python}, running {report.python}; "
            "the expected hashes depend on the Python and library versions, so re-record them on this Python"
        )
    else:
        for name in sorted(set(expected.outputs) | set(report.outputs_run_1)):
            if expected.outputs.get(name) != report.outputs_run_1.get(name):
                reasons.append(f"output differs from the recorded hash: {name}")
    if report.uv_lock_sha256 != expected.uv_lock_sha256:
        reasons.append(
            f"uv.lock changed: recorded sha256 {expected.uv_lock_sha256 or 'absent'}, "
            f"now {report.uv_lock_sha256 or 'absent'}; the dependency pins moved, so re-record the expected hashes"
        )
    return reasons


def lock_sha256(repo: Path) -> str:
    """SHA-256 of the repository's uv.lock, or "" when there is none."""
    path = repo / "uv.lock"
    return file_sha256(path) if path.is_file() else ""


def load_expected(path: Path) -> ExpectedHashes:
    data = json.loads(path.read_text(encoding="utf-8"))
    return ExpectedHashes(
        python=str(data["python"]),
        uv_lock_sha256=str(data["uv_lock_sha256"]),
        outputs={str(k): str(v) for k, v in data["outputs"].items()},
    )


def read_expected(path: Path, reference: Reference) -> tuple[ExpectedHashes | None, str | None]:
    """The recorded hashes, or the named reason they cannot be read. A registered file must exist."""
    shown = f"{reference.directory}/{reference.expected}"
    if not path.is_file():
        return None, f"expected hashes file missing: {shown}"
    try:
        return load_expected(path), None
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        return None, f"expected hashes file unreadable: {shown} ({error})"


def expected_payload(report: Report) -> dict[str, object]:
    """The expected-hashes file for a passing run: the Python version, the uv.lock hash, and the first run's outputs."""
    return {
        "python": report.python,
        "uv_lock_sha256": report.uv_lock_sha256,
        "outputs": report.outputs_run_1,
    }


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


def _clean_env() -> dict[str, str]:
    """The environment for child processes, without the git location variables a git hook exports."""
    return {key: value for key, value in os.environ.items() if key not in GIT_LOCATION_VARS}


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=False, env=_clean_env()
    )
    return done.stdout.strip() if done.returncode == 0 else ""


def provenance(repo: Path) -> tuple[str, str | None, bool]:
    """(source revision, exact tag or None, dirty)."""
    revision = _git(repo, "rev-parse", "HEAD") or "unknown"
    tag = _git(repo, "describe", "--tags", "--exact-match", "HEAD") or None
    dirty = bool(_git(repo, "status", "--porcelain"))
    return revision, tag, dirty


def run_step(argv: tuple[str, ...], cwd: Path) -> StepResult:
    started = time.monotonic()
    done = subprocess.run(list(argv), cwd=cwd, capture_output=True, text=True, check=False, env=_clean_env())
    return StepResult(argv=argv, returncode=done.returncode, seconds=round(time.monotonic() - started, 1))


def check(name: str, repo: Path, references: dict[str, Reference], *, use_expected: bool = True) -> Report:
    """Run the full reviewer path for one registered reference. `use_expected=False` skips the recorded-hash comparison."""
    reference = references[name]
    revision, tag, dirty = provenance(repo)
    report = Report(
        reference=name,
        source_revision=revision,
        tag=tag,
        dirty=dirty,
        python=platform.python_version(),
        uv_lock_sha256=lock_sha256(repo),
    )
    report.missing_required = missing_required(reference, repo)
    base = repo / reference.directory
    if use_expected and reference.expected is not None:
        report.expected, report.expected_problem = read_expected(base / reference.expected, reference)
    report.inputs = {name_: file_sha256(base / name_) for name_ in reference.required if (base / name_).is_file()}
    if not report.missing_required:
        report.steps = [run_step(argv, base) for argv in reference.build]
        report.outputs_run_1 = hash_files(base, reference.outputs)
        report.steps += [run_step(argv, base) for argv in reference.build]
        report.outputs_run_2 = hash_files(base, reference.outputs)
        report.deterministic = bool(report.outputs_run_1) and report.outputs_run_1 == report.outputs_run_2
        tests = subprocess.run(
            ["uv", "run", "pytest", "-q", "-p", "no:cacheprovider", *reference.contract_tests],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
            env=_clean_env(),
        )
        report.tests_returncode = tests.returncode
    report.failures = verdict(report)
    return report
