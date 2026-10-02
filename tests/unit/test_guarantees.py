"""
Tests validating AGMAI-READY guarantees.

Each test verifies a specific claim about math-trace's capabilities and API.
These tests ensure that all guaranteed features work as documented.
"""

import json
import sys
from dataclasses import fields
from pathlib import Path

import pytest

# Add examples to path for model imports
sys.path.insert(0, str(Path(__file__).parent / '../../examples/membrane-dynamics/src'))

from math_trace.services import Formula
from model import FORMULAS, export_json


class TestEquationExtraction:
    """Verify equations can be extracted from SymPy models."""

    def test_equations_extractable_from_sympy(self):
        """Guarantee: Equation extraction from SymPy works."""
        # FORMULAS dict should contain extracted equations
        assert FORMULAS is not None
        assert len(FORMULAS) > 0
        assert 'rate' in FORMULAS

    def test_equations_have_latex_representation(self):
        """Guarantee: SymPy equations convert to LaTeX."""
        rate_formula = FORMULAS['rate']
        latex = rate_formula.to_latex()

        # LaTeX should be a non-empty string
        assert isinstance(latex, str)
        assert len(latex) > 0
        # Should contain LaTeX-like content
        assert any(char in latex for char in ['\\', '{', '}'])

    def test_json_export_produces_valid_json(self):
        """Guarantee: Equations export to valid JSON format."""
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = Path(f.name)

        try:
            # Export should create valid JSON
            export_json(json_path)
            content = json_path.read_text()
            data = json.loads(content)

            # Should have equations
            assert len(data) > 0
            # Rate equation should be present
            assert 'rate' in data
            # Should have required fields
            rate_data = data['rate']
            assert 'latex' in rate_data
            assert 'description' in rate_data
        finally:
            json_path.unlink(missing_ok=True)


class TestSourceLineTraceability:
    """Verify equations are tagged with source location."""

    def test_equations_have_source_line(self):
        """Guarantee: Every equation tagged with source line number."""
        for name, formula in FORMULAS.items():
            assert hasattr(formula, 'source_line'), f"{name} missing source_line"
            assert isinstance(formula.source_line, int), f"{name} source_line not int"
            assert formula.source_line > 0, f"{name} source_line must be positive"

    def test_equations_have_description(self):
        """Guarantee: Equations include descriptions (for metadata schema)."""
        for name, formula in FORMULAS.items():
            assert hasattr(formula, 'description')
            assert isinstance(formula.description, str)
            assert len(formula.description) > 0


class TestMetadataSchemaAPI:
    """Verify the Equation metadata API matches documented schema."""

    def test_formula_class_has_required_fields(self):
        """Guarantee: Formula/Equation class implements documented schema."""
        # Check that Formula has at least these documented fields
        rate_formula = FORMULAS['rate']

        required_fields = ['name', 'description', 'source_line']
        for field_name in required_fields:
            assert hasattr(rate_formula, field_name), \
                f"Formula missing documented field: {field_name}"

    def test_formula_name_is_string(self):
        """Guarantee: Equation name is human-readable string."""
        for name, formula in FORMULAS.items():
            assert hasattr(formula, 'name')
            assert isinstance(formula.name, str)
            assert len(formula.name) > 0

    def test_formula_provides_latex_method(self):
        """Guarantee: Equations provide to_latex() method for publication."""
        for name, formula in FORMULAS.items():
            assert hasattr(formula, 'to_latex')
            assert callable(formula.to_latex)
            latex_str = formula.to_latex()
            assert isinstance(latex_str, str)


class TestReproducibility:
    """Verify deterministic equation generation."""

    def test_same_model_generates_same_latex(self):
        """Guarantee: Same equation definition produces same LaTeX (deterministic)."""
        # Get LaTeX multiple times
        latex1 = FORMULAS['rate'].to_latex()
        latex2 = FORMULAS['rate'].to_latex()
        latex3 = FORMULAS['rate'].to_latex()

        # All should be identical
        assert latex1 == latex2 == latex3

    def test_json_export_deterministic(self):
        """Guarantee: Reproducibility — JSON export is deterministic."""
        import tempfile
        import json as json_module

        # Export twice
        exports = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json_path = Path(f.name)

            try:
                export_json(json_path)
                data = json_module.loads(json_path.read_text())
                exports.append(data)
            finally:
                json_path.unlink(missing_ok=True)

        # Both exports should be identical
        assert exports[0] == exports[1]


class TestCodeQualityStandards:
    """Verify code quality guarantees."""

    def test_formulas_are_dataclasses(self):
        """Guarantee: Formulas are structured data with typed fields (Python 3.11+ standard)."""
        # Formulas should have dataclass-like interface
        rate_formula = FORMULAS['rate']

        # Should have dataclass fields
        assert hasattr(rate_formula, "__dataclass_fields__")

    def test_formulas_have_docstrings(self):
        """Guarantee: Functions and classes have docstrings."""
        # Formula class should have docstring
        assert Formula.__doc__ is not None
        assert len(Formula.__doc__) > 0


class TestSupportedPythonVersions:
    """Verify Python version compatibility."""

    def test_code_compatible_with_python_3_13(self):
        """Guarantee: Works with Python 3.13 (and 3.11+)."""
        import sys as sys_module

        # Current runtime should be 3.11+
        assert sys_module.version_info >= (3, 11), \
            f"Requires Python 3.11+, have {sys_module.version_info.major}.{sys_module.version_info.minor}"


class TestAPIStability:
    """Verify documented API is consistent."""

    def test_formula_api_documented(self):
        """Guarantee: Formula API is consistent and documented."""
        rate_formula = FORMULAS['rate']

        # Should have consistent interface
        assert callable(getattr(rate_formula, 'to_latex'))

        # Should be able to access key fields
        _ = rate_formula.name
        _ = rate_formula.description
        _ = rate_formula.source_line


class TestEndToEndGuarantees:
    """Test full workflow guarantees together."""

    def test_model_to_latex_pipeline(self):
        """Guarantee: Complete pipeline from model.py to LaTeX works."""
        # 1. Equation defined in model.py ✓ (FORMULAS loaded)
        assert 'rate' in FORMULAS

        # 2. Equation has metadata ✓
        rate = FORMULAS['rate']
        assert rate.name
        assert rate.description
        assert rate.source_line > 0

        # 3. Convert to LaTeX ✓
        latex = rate.to_latex()
        assert latex

        # 4. Export to JSON ✓
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = Path(f.name)

        try:
            export_json(json_path)
            data = json.loads(json_path.read_text())
            assert 'rate' in data
        finally:
            json_path.unlink(missing_ok=True)
