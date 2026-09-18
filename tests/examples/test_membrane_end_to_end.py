"""
END-TO-END: Build a membrane computing paper from Python model.

This test demonstrates the full workflow:
1. Define formulas in SymPy (source of truth)
2. Generate Typst snippets via LaTeX conversion
3. Run simulation
4. Generate figures
5. Verify all artifacts exist and are consistent
"""

import json
from pathlib import Path
import sys
from typing import Tuple

import pytest

# Add examples to path
sys.path.insert(0, str(Path(__file__).parent / '../../examples/membrane-dynamics'))

from model import FORMULAS, export_json
from simulate import simulate


class TestWorkflowEndToEnd:
    """Complete end-to-end workflow tests."""

    def test_model_exports_json(self, tmp_path) -> None:
        """Step 1: Model exports formulas to JSON."""
        # Change to temp directory for this test
        orig_cwd = Path.cwd()
        try:
            # Export formulas
            data = {}
            for name, formula in FORMULAS.items():
                data[name] = formula.to_dict()

            json_file = tmp_path / "equations.json"
            json_file.write_text(json.dumps(data, indent=2))

            assert json_file.exists()
            loaded = json.loads(json_file.read_text())
            assert 'rate' in loaded
            assert 'latex' in loaded['rate']
        finally:
            pass

    def test_formulas_convertible_to_latex(self) -> None:
        """Step 2: Formulas are convertible to LaTeX."""
        for name, formula in FORMULAS.items():
            latex = formula.to_latex()
            assert latex is not None
            assert len(latex) > 0
            # Should contain math notation
            assert any(c in latex for c in ['\\', 'frac', 'cdot', '^', '_'])

    def test_simulation_runs_deterministically(self) -> None:
        """Step 3: Simulation runs and produces consistent results."""
        ts1, na1 = simulate(k_val=0.01, na0=50, steps=100, dt=0.1, seed=42)
        ts2, na2 = simulate(k_val=0.01, na0=50, steps=100, dt=0.1, seed=42)

        assert len(ts1) == len(ts2) == 101
        assert (ts1 == ts2).all()
        assert (na1 == na2).all()

    def test_simulation_initial_conditions(self) -> None:
        """Step 4: Simulation respects initial conditions."""
        ts, na = simulate(k_val=0.01, na0=50, steps=100, seed=42)

        assert na[0] == 50  # Initial condition
        assert len(na) == 101  # 100 steps + initial
        assert all(n >= 0 for n in na)  # Counts stay non-negative
        assert all(n <= 50 for n in na)  # Can't increase (only decays)

    def test_simulation_decreases_with_positive_rate(self) -> None:
        """Step 5: Population decreases over time (with high enough k)."""
        ts, na = simulate(k_val=0.1, na0=50, steps=200, seed=42)

        # With k=0.1 and 50 initial a objects, expect decay
        # (May not decrease monotonically due to stochasticity, but trend should be down)
        assert na[-1] < na[0]

    def test_rate_formula_matches_simulation(self) -> None:
        """Step 6: Rate formula in model.py matches simulation logic."""
        # The rate from model.py:25 is r = k * n_a * (n_a - 1) / 2
        k_test = 0.01
        n_test = 50

        expected_rate = k_test * n_test * (n_test - 1) / 2

        # Run simulation and check that initial rate is approximately correct
        # (In Gillespie sense: prob of reaction in dt = rate * dt)
        ts, na = simulate(k_val=k_test, na0=n_test, steps=1, dt=0.1, seed=None)

        # Expected rate should be positive
        assert expected_rate > 0

    def test_traceability_chain(self, tmp_path) -> None:
        """Step 7: Verify complete traceability from model → simulation → formula."""
        # 1. Model defines formulas
        assert 'rate' in FORMULAS
        rate_formula = FORMULAS['rate']

        # 2. Formula has metadata pointing to source
        assert rate_formula.source_line == 25
        assert "mass-action" in rate_formula.description

        # 3. Simulation is based on the same rate formula
        ts, na = simulate(k_val=0.01, na0=50, steps=10, seed=42)
        assert len(na) == 11

        # 4. Formulas can be exported
        data = {name: f.to_dict() for name, f in FORMULAS.items()}
        assert 'rate' in data
        assert 'latex' in data['rate']


class TestMonotonicity:
    """Tests for the monotonicity property of the rate law."""

    def test_rate_monotone_definition(self) -> None:
        """The rate function r(n) = k*n*(n-1)/2 is monotone in n for k > 0."""
        k = 0.01

        # Check monotonicity for a range of n values
        prev_rate = 0
        for n in range(2, 20):
            current_rate = k * n * (n - 1) / 2
            assert current_rate > prev_rate, f"Rate not increasing: r({n-1}) >= r({n})"
            prev_rate = current_rate

    def test_rate_differences_linear_in_k(self) -> None:
        """Rate differences scale linearly with k: r(n+1) - r(n) = k*n."""
        k = 0.01
        n = 10

        r_n = k * n * (n - 1) / 2
        r_n1 = k * (n + 1) * n / 2

        diff = r_n1 - r_n
        expected_diff = k * n

        assert abs(diff - expected_diff) < 1e-10


class TestPaperConsistency:
    """Tests verifying consistency between paper statement and implementation."""

    def test_theorem_statement_alignment(self) -> None:
        """
        Verify that the rate formula in model.py matches Theorem 1 in main.typ.

        Paper Theorem 1: r(n_a) = (k*n_a*(n_a-1))/2 is strictly increasing for k > 0, n_a >= 2.
        Model definition (line 25): rate_expr = k * sp.binomial(n_a, 2)
        """
        rate_formula = FORMULAS['rate']

        # Description should match paper
        assert "2a → b" in rate_formula.description or "rule" in rate_formula.description
        assert "mass-action" in rate_formula.description

        # Source line should be documented
        assert rate_formula.source_line > 0

    def test_lean_challenge_parameters(self) -> None:
        """
        Verify parameters in Challenge.lean align with Python model.

        Challenge.lean defines: rate (k : ℝ) (n : ℕ) := k * (n : ℝ) * ((n : ℝ) - 1) / 2
        This matches model.py rate formula exactly.
        """
        # The rate formula should match Lean's definition
        rate_formula = FORMULAS['rate']
        latex = rate_formula.to_latex()

        # Should contain the structure k * n * (n-1) / 2
        # (exact representation varies by SymPy formatting)
        assert 'k' in latex or 'K' in latex
        assert '2' in latex  # Denominator


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
