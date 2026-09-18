"""
Tests for formula generation from Python model.

Verifies that SymPy formulas are correctly exported and can be converted
to Typst/LaTeX formats.
"""

import json
from pathlib import Path
import sys

import pytest

# Add examples to path
sys.path.insert(0, str(Path(__file__).parent / '../examples/membrane-dynamics'))

from model import FORMULAS, export_json


def test_formulas_defined():
    """Verify that the model defines the required formulas."""
    assert 'rate' in FORMULAS
    assert FORMULAS['rate'].name == 'rate'


def test_rate_formula_correct():
    """Verify the rate formula matches the expected form."""
    rate_formula = FORMULAS['rate']
    latex = rate_formula.to_latex()

    # LaTeX should contain k and n_a
    assert 'k' in latex or 'K' in latex
    assert 'n_{a}' in latex or 'n_a' in latex or 'n' in latex


def test_export_json(tmp_path):
    """Verify JSON export contains all expected fields."""
    # Export to temp file
    json_path = tmp_path / "equations.json"

    data = {}
    for name, formula in FORMULAS.items():
        data[name] = formula.to_dict()

    json_path.write_text(json.dumps(data, indent=2))

    # Reload and verify
    loaded = json.loads(json_path.read_text())

    assert 'rate' in loaded
    rate_data = loaded['rate']

    # Check required fields
    assert 'latex' in rate_data
    assert 'sympy' in rate_data
    assert 'description' in rate_data
    assert 'source_line' in rate_data

    # Verify content
    assert len(rate_data['latex']) > 0
    assert 'k' in rate_data['sympy'] or 'K' in rate_data['sympy']


def test_formula_metadata():
    """Verify formula metadata (description, source line) is present."""
    rate = FORMULAS['rate']

    assert rate.description is not None
    assert len(rate.description) > 0
    assert rate.source_line > 0
    assert "mass-action" in rate.description.lower()


def test_to_latex():
    """Verify LaTeX conversion works."""
    for name, formula in FORMULAS.items():
        latex = formula.to_latex()

        assert isinstance(latex, str)
        assert len(latex) > 0
        # LaTeX should contain math symbols or common patterns
        assert any(c in latex for c in ['\\', '^', '_', 'frac', 'cdot'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
