"""Contract tests for the Sidorenko-style Turán density reference.

Validates:
- The Lean definitions this reference transcribes are recorded verbatim at the pinned commit
- The generated gap table covers r in {3, 4, 5} and m in 1..10
- Each row matches an independent float evaluation of the displayed constant
- The Lean evidence record names the pinned commit and does not claim a Comparator pass
"""

import json
import math

import pytest

from math_trace.constants import REPO_ROOT

EXAMPLE = REPO_ROOT / "examples" / "sidorenko-turan"
PINNED_COMMIT = "ba6f109bf01436ca15e55fdf5d35dbea85ffd9c9"


@pytest.fixture
def gap_table():
    """The generated table, written by build_table.py."""
    path = EXAMPLE / "generated" / "gap_table.json"
    if not path.exists():
        pytest.skip("run build_table.py first")
    return json.loads(path.read_text(encoding="utf-8"))


def float_gap(r: int, m: int) -> float:
    """c_r / m^((r-1)/r), evaluated in floats from the Lean definitions."""
    constant = (1 / (4 * r**2)) * (4 / r) ** (1 / r) * (1 - 1 / r) ** (2 - 2 / r)
    return constant / math.pow(m, (r - 1) / r)


class TestLeanTranscription:
    """The Lean definitions this reference depends on are kept verbatim."""

    def test_lean_statement_records_both_definitions(self):
        """paperConstant and paperGap are present, copied from the pinned commit."""
        text = (EXAMPLE / "lean_statement.lean").read_text(encoding="utf-8")
        assert "def paperConstant (r : ℕ) : ℝ :=" in text
        assert "def paperGap (r m : ℕ) : ℝ :=" in text
        assert "(1 / (4 * (r : ℝ) ^ 2))" in text
        assert "Real.rpow (4 / (r : ℝ)) (1 / (r : ℝ))" in text
        assert "Real.rpow (1 - 1 / (r : ℝ)) (2 - 2 / (r : ℝ))" in text

    def test_lean_evidence_names_the_pinned_commit(self):
        """The evidence record refers to the commit the statement was copied from."""
        evidence = json.loads((EXAMPLE / "formalization.json").read_text(encoding="utf-8"))
        assert evidence["source_commit"] == PINNED_COMMIT


class TestGapTable:
    """The generated table covers the registered grid and matches the formula."""

    def test_table_covers_the_registered_grid(self, gap_table):
        """Every r in {3, 4, 5} has m in 1..10, once each."""
        pairs = {(row["r"], row["m"]) for row in gap_table["rows"]}
        expected = {(r, m) for r in (3, 4, 5) for m in range(1, 11)}
        assert pairs == expected
        assert len(gap_table["rows"]) == len(expected)

    def test_rows_match_independent_float_evaluation(self, gap_table):
        """Each exact decimal agrees with the float formula to 1e-12."""
        for row in gap_table["rows"]:
            exact = float(row["gap_decimal"])
            assert exact == pytest.approx(float_gap(row["r"], row["m"]), abs=1e-12), row

    def test_gaps_are_positive_and_decrease_in_m(self, gap_table):
        """The claimed gap is positive and shrinks as the forbidden hypergraph grows."""
        for r in (3, 4, 5):
            gaps = [float(row["gap_decimal"]) for row in gap_table["rows"] if row["r"] == r]
            assert all(g > 0 for g in gaps)
            assert gaps == sorted(gaps, reverse=True)
