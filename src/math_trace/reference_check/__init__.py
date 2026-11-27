"""Reviewer path: rebuild one reference from its checkout, check it, and write a report.

Public API is preserved for tests and downstream imports:
- `REFERENCES`, `Reference`, `Report`, `StepResult`, `ExpectedHashes`
- `check`, `verdict`, `expected_reasons`, `missing_required`, `hash_files`, `file_sha256`
- `provenance`, `lock_sha256`, `load_expected`, `expected_payload`
- Typer `app` and `run`

## Specification Map

| Rule or Invariant | Authority | Enforcement |
|---|---|---|
| Registered reference names are the only accepted CLI targets; unknown name exits 2 and names known refs | reviewer-path CLI contract | `run`; `tests/unit/test_reference_check.py::test_an_unknown_reference_is_refused_with_the_known_names` |
| `--record-expected true` requires reference to declare an expected-hashes file; otherwise exit 2 | reviewer-path CLI contract | `run`; `tests/unit/test_reference_check.py::test_record_expected_true_without_expected_file_is_refused` |
| CLI writes report JSON, prints result, exits 1 on any failure; on record-success writes expected-hashes payload | reviewer-path CLI contract | `run`; `tests/unit/test_reference_check.py::test_cli_writes_report_and_exits_1_on_failure`, `test_cli_records_expected_hashes_on_passing_run` |
| `check` orchestrates provenance, required-file check, build twice, determinism, contract tests, expected-hash comparison | reviewer-path contract | `report.check`; `tests/unit/test_reference_check.py` verdict/expected-reasons cases |
"""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path

import typer

from .registry import REFERENCES, Reference
from .report import (
    ExpectedHashes,
    Report,
    StepResult,
    expected_payload,
    expected_reasons,
    file_sha256,
    hash_files,
    load_expected,
    lock_sha256,
    missing_required,
    provenance,
    read_expected,
    verdict,
)
from .report import (
    check as _check,
)

app = typer.Typer(help="Rebuild a reference from its checkout and report what was checked.", add_completion=False)


class Toggle(StrEnum):
    """Explicit boolean value for a command option: `--name true` or `--name false`."""

    TRUE = "true"
    FALSE = "false"


def check(name: str, repo: Path, *, use_expected: bool = True) -> Report:
    """Run the full reviewer path for one registered reference."""
    return _check(name, repo, REFERENCES, use_expected=use_expected)


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
    from dataclasses import asdict

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

__all__ = [
    "ExpectedHashes",
    "REFERENCES",
    "Reference",
    "Report",
    "StepResult",
    "Toggle",
    "app",
    "check",
    "expected_payload",
    "expected_reasons",
    "file_sha256",
    "hash_files",
    "load_expected",
    "lock_sha256",
    "missing_required",
    "provenance",
    "read_expected",
    "run",
    "verdict",
]
