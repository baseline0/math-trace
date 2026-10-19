"""Reviewer path: rebuild one reference from its checkout, check it, and write a report that says what was checked.

A reference is registered explicitly in REFERENCES: where it lives, the commands that build it, the files it must
contain, and the tests that hold its contract. The check:
1. confirms the required files exist;
2. runs the build twice, and hashes every output after each run;
3. runs the contract tests;
4. records provenance: the source revision, whether it is a tag, whether the tree is dirty, and the Python version;
5. when the reference registers an expected-hashes file, compares the outputs, the uv.lock hash, and the Python version
   with it. A Python change is named as a version change, not reported as output drift.

It passes only when all four hold. The report is JSON, and the exit status is 0 on a pass and 1 on a fail, so a
failure is readable in the report, not an opaque traceback.

Usage:
    uv run python -m math_trace.reference_check --reference epidemiology-sir --repo . --report report.json
"""

from __future__ import annotations

import glob
import hashlib
import json
import platform
import subprocess
import time
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path

import typer

app = typer.Typer(help="Rebuild a reference from its checkout and report what was checked.", add_completion=False)


@dataclass(frozen=True)
class Reference:
    """One registered reference. Paths are relative to the repo root; build commands run in `directory`."""

    directory: str
    build: tuple[tuple[str, ...], ...]
    required: tuple[str, ...]
    outputs: tuple[str, ...]  # glob patterns, relative to `directory`
    contract_tests: tuple[str, ...]  # relative to the repo root
    expected: str | None = None  # expected-hashes file, relative to `directory`; None means no recorded hashes


REFERENCES: dict[str, Reference] = {
    "epidemiology-sir": Reference(
        directory="examples/epidemiology-sir",
        build=(
            ("uv", "run", "python", "build_paper.py"),
            ("uv", "run", "python", "build_presentation.py", "--output", "generated/presentation.html"),
        ),
        required=(
            "build_paper.py",
            "build_presentation.py",
            "presentation_config.yaml",
            "src/model.py",
            "src/simulate.py",
        ),
        outputs=(
            "generated/sir_equations.json",
            "generated/covid_scenario.json",
            "generated/figures/*.png",
            "generated/presentation.html",
        ),
        contract_tests=(
            "tests/integration/test_epidemiology_sir_contract.py",
            "tests/unit/test_build_presentation.py",
            "tests/unit/test_sir_presentation_config.py",
        ),
    ),
    "sidorenko-turan": Reference(
        directory="examples/sidorenko-turan",
        build=(("uv", "run", "python", "build_table.py"),),
        required=(
            "build_table.py",
            "lean_statement.lean",
            "formalization.json",
        ),
        outputs=("generated/gap_table.json",),
        contract_tests=("tests/integration/test_sidorenko_turan_contract.py",),
        expected="expected-hashes.json",
    ),
}


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


def _read_expected(path: Path, reference: Reference) -> tuple[ExpectedHashes | None, str | None]:
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


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    return done.stdout.strip() if done.returncode == 0 else ""


def provenance(repo: Path) -> tuple[str, str | None, bool]:
    """(source revision, exact tag or None, dirty)."""
    revision = _git(repo, "rev-parse", "HEAD") or "unknown"
    tag = _git(repo, "describe", "--tags", "--exact-match", "HEAD") or None
    dirty = bool(_git(repo, "status", "--porcelain"))
    return revision, tag, dirty


def run_step(argv: tuple[str, ...], cwd: Path) -> StepResult:
    started = time.monotonic()
    done = subprocess.run(list(argv), cwd=cwd, capture_output=True, text=True, check=False)
    return StepResult(argv=argv, returncode=done.returncode, seconds=round(time.monotonic() - started, 1))


def check(name: str, repo: Path, *, use_expected: bool = True) -> Report:
    """Run the full reviewer path for one registered reference. `use_expected=False` skips the recorded-hash comparison."""
    reference = REFERENCES[name]
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
        report.expected, report.expected_problem = _read_expected(base / reference.expected, reference)
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
        )
        report.tests_returncode = tests.returncode
    report.failures = verdict(report)
    return report


class Toggle(StrEnum):
    """Explicit boolean value for a command option: `--name true` or `--name false`."""

    TRUE = "true"
    FALSE = "false"


@app.command()
def run(
    reference: str = typer.Option(..., "--reference", help="A registered reference name."),
    repo: Path = typer.Option(..., "--repo", help="The repository root."),
    report: Path = typer.Option(..., "--report", help="Where to write the JSON report."),
    record_expected: Toggle = typer.Option(
        ...,
        "--record-expected",
        help=(
            "true: after a passing build, write the reference's expected-hashes file and skip the "
            "recorded-hash comparison; false: compare against the recorded hashes."
        ),
    ),
) -> None:
    """Rebuild a registered reference twice, check it, write the report, and exit 1 on any failure."""
    if reference not in REFERENCES:
        typer.echo(f"unknown reference {reference!r}; known: {', '.join(sorted(REFERENCES))}", err=True)
        raise typer.Exit(2)
    record = record_expected is Toggle.TRUE
    if record and REFERENCES[reference].expected is None:
        typer.echo(f"{reference} has no expected-hashes file to record", err=True)
        raise typer.Exit(2)
    result = check(reference, repo, use_expected=not record)
    payload = asdict(result) | {"result": result.result}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    typer.echo(f"{reference}: {result.result} (report: {report})")
    for reason in result.failures:
        typer.echo(f"  - {reason}")
    if result.failures:
        raise typer.Exit(1)
    if record:
        target = repo / REFERENCES[reference].directory / str(REFERENCES[reference].expected)
        target.write_text(json.dumps(expected_payload(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        typer.echo(f"recorded expected hashes: {target}")


if __name__ == "__main__":
    app()
