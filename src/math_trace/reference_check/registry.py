"""Registered reference definitions for the reviewer path."""

from __future__ import annotations

from dataclasses import dataclass


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
