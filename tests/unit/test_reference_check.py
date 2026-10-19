"""The reviewer path must fail loudly and say why. These tests cover each failure, and the pure verdict logic.

The full build is not run here (it takes seconds and writes into the example). The end-to-end run is the recipe
`just reference-check`, and its report is the evidence.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from math_trace import reference_check as rc

pytestmark = pytest.mark.unit


def _passing_report(**overrides: object) -> rc.Report:
    base: dict[str, object] = {
        "reference": "ref",
        "source_revision": "abc",
        "tag": None,
        "dirty": False,
        "python": "3.13",
        "outputs_run_1": {"out.json": "h"},
        "outputs_run_2": {"out.json": "h"},
        "steps": [rc.StepResult(argv=("uv", "run"), returncode=0, seconds=0.1)],
        "tests_returncode": 0,
        "deterministic": True,
    }
    base.update(overrides)
    return rc.Report(**base)  # type: ignore[arg-type]


def test_a_report_where_every_check_holds_passes() -> None:
    report = _passing_report()

    assert rc.verdict(report) == []
    assert report.result == "pass"


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"missing_required": ["src/model.py"]}, "required files missing: src/model.py"),
        ({"steps": [rc.StepResult(argv=("uv", "run", "x"), returncode=1, seconds=0.1)]}, "build step exited 1"),
        ({"tests_returncode": 1}, "contract tests exited 1"),
        ({"outputs_run_1": {}, "outputs_run_2": {}, "deterministic": False}, "produced no outputs"),
        ({"deterministic": False}, "two builds from the same checkout produced different outputs"),
    ],
)
def test_each_failed_check_is_named_in_the_report(overrides: dict[str, object], reason: str) -> None:
    report = _passing_report(**overrides)

    reasons = rc.verdict(report)

    assert any(reason in r for r in reasons), reasons
    report.failures = reasons
    assert report.result == "fail"


def test_missing_required_lists_only_the_absent_files(tmp_path: Path) -> None:
    (tmp_path / "ex").mkdir()
    (tmp_path / "ex" / "present.py").write_text("x = 1\n")
    reference = rc.Reference(
        directory="ex", build=(), required=("present.py", "absent.py"), outputs=(), contract_tests=()
    )

    assert rc.missing_required(reference, tmp_path) == ["absent.py"]


def test_hashes_are_sorted_and_change_when_content_changes(tmp_path: Path) -> None:
    (tmp_path / "b.txt").write_text("one")
    (tmp_path / "a.txt").write_text("two")
    first = rc.hash_files(tmp_path, ("*.txt",))

    (tmp_path / "b.txt").write_text("changed")
    second = rc.hash_files(tmp_path, ("*.txt",))

    assert list(first) == ["a.txt", "b.txt"]
    assert first["a.txt"] == second["a.txt"]
    assert first["b.txt"] != second["b.txt"]


def test_provenance_outside_a_git_repository_is_explicitly_unknown(tmp_path: Path) -> None:
    revision, tag, dirty = rc.provenance(tmp_path)

    assert (revision, tag, dirty) == ("unknown", None, False)


def test_an_unknown_reference_is_refused_with_the_known_names(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        rc.app,
        [
            "--reference",
            "no-such-reference",
            "--repo",
            str(tmp_path),
            "--report",
            str(tmp_path / "r.json"),
            "--record-expected",
            "false",
        ],
    )

    assert result.exit_code == 2
    assert "known: epidemiology-sir, sidorenko-turan" in result.output
    assert not (tmp_path / "r.json").exists()


def test_the_epidemiology_reference_is_registered_with_its_contract_tests() -> None:
    reference = rc.REFERENCES["epidemiology-sir"]

    assert reference.build and reference.contract_tests
    assert "generated/sir_equations.json" in reference.outputs


def test_the_sidorenko_turan_reference_is_registered_with_its_contract_tests() -> None:
    reference = rc.REFERENCES["sidorenko-turan"]

    assert reference.build and reference.contract_tests
    assert "generated/gap_table.json" in reference.outputs
    assert reference.expected == "expected-hashes.json"


def _expected(**overrides: object) -> rc.ExpectedHashes:
    base: dict[str, object] = {"python": "3.13", "uv_lock_sha256": "lock", "outputs": {"out.json": "h"}}
    base.update(overrides)
    return rc.ExpectedHashes(**base)  # type: ignore[arg-type]


def test_outputs_and_uv_lock_matching_the_recorded_hashes_pass() -> None:
    report = _passing_report(uv_lock_sha256="lock", expected=_expected())

    assert rc.verdict(report) == []


def test_a_changed_output_is_named_in_the_reason() -> None:
    report = _passing_report(
        uv_lock_sha256="lock",
        outputs_run_1={"out.json": "changed"},
        outputs_run_2={"out.json": "changed"},
        expected=_expected(),
    )

    assert rc.verdict(report) == ["output differs from the recorded hash: out.json"]


def test_a_changed_uv_lock_hash_is_named_in_the_reason() -> None:
    report = _passing_report(uv_lock_sha256="other", expected=_expected())

    reasons = rc.verdict(report)

    assert len(reasons) == 1
    assert reasons[0].startswith("uv.lock changed: recorded sha256 lock, now other")


def test_a_python_change_is_named_and_not_reported_as_output_drift() -> None:
    report = _passing_report(
        python="3.12",
        uv_lock_sha256="lock",
        outputs_run_1={"out.json": "changed"},
        outputs_run_2={"out.json": "changed"},
        expected=_expected(),
    )

    reasons = rc.verdict(report)

    assert len(reasons) == 1
    assert reasons[0].startswith("python version changed: recorded 3.13, running 3.12")


def test_epidemiology_sir_without_an_expected_file_is_unchanged() -> None:
    assert rc.REFERENCES["epidemiology-sir"].expected is None

    report = _passing_report(uv_lock_sha256="anything")

    assert rc.verdict(report) == []
