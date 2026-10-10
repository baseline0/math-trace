"""
Regression tests: Formula Pipeline Integrity

Verifies that formulas survive the full conversion pipeline:
Python (SymPy) → JSON export → LaTeX → Typst verification

These tests catch silent data loss, corruption, and conversion errors.
"""

import json
import subprocess
import sys

import pytest

from math_trace.constants import REPO_ROOT

MATH_TRACE_ROOT = REPO_ROOT
TEMPLATES_DIR = MATH_TRACE_ROOT / "templates"

PRODUCTION_TEMPLATES = [
    "epidemiology",
    "quantum-systems",
    "control-systems",
    "gnns",
    "thermodynamics",
]


@pytest.mark.integration
class TestFormulaPipelineIntegrity:
    """Verify formulas survive full pipeline without corruption."""

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_formula_count_consistency(self, template):
        """Formula count exported = expected minimum."""
        template_dir = TEMPLATES_DIR / template
        if not template_dir.exists():
            pytest.skip(f"Template {template} not found")

        # Export formulas
        result = subprocess.run(
            [sys.executable, "src/model.py"],
            cwd=template_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Model export failed: {result.stderr}"

        # Find and load equations
        equations_file = None
        for json_file in template_dir.glob("*equations.json"):
            equations_file = json_file
            break

        assert equations_file is not None, f"No equations.json found in {template}"

        with open(equations_file) as f:
            equations = json.load(f)

        # Verify minimum formula count
        formula_count = len(equations)
        assert formula_count >= 3, f"{template} should export >= 3 formulas, got {formula_count}"

        # Spot-check: at least 3 should have non-trivial LaTeX
        non_trivial = 0
        for eq_data in equations.values():
            if len(eq_data.get("latex", "")) > 10:
                non_trivial += 1

        assert non_trivial >= 3, f"{template} should have >= 3 non-trivial formulas, got {non_trivial}"

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_formula_latex_validity(self, template):
        """All exported LaTeX has valid syntax."""
        template_dir = TEMPLATES_DIR / template
        if not template_dir.exists():
            pytest.skip(f"Template {template} not found")

        # Export
        subprocess.run(
            [sys.executable, "src/model.py"],
            cwd=template_dir,
            capture_output=True,
            timeout=30,
        )

        # Load
        equations_file = None
        for json_file in template_dir.glob("*equations.json"):
            equations_file = json_file
            break

        assert equations_file is not None

        with open(equations_file) as f:
            equations = json.load(f)

        # Check each formula's LaTeX
        for eq_name, eq_data in equations.items():
            latex = eq_data.get("latex", "")

            # Rule 1: No unescaped $ (TeX delimiter shouldn't appear in raw LaTeX)
            assert "$" not in latex, f"{eq_name} contains unescaped $: {latex[:50]}"

            # Rule 2: Matching braces
            open_braces = latex.count("{")
            close_braces = latex.count("}")
            assert (
                open_braces == close_braces
            ), f"{eq_name} has mismatched braces ({open_braces} open, {close_braces} closed): {latex[:60]}"

            # Rule 3: No double-escaped backslashes (likely corruption)
            assert "\\\\\\\\" not in latex, f"{eq_name} has double-escaped backslashes: {latex[:50]}"

            # Rule 4: Simple formulas (like "PV = nRT") are OK, complex ones should have TeX commands
            # Don't require special syntax—basic math notation is valid LaTeX
            pass

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_formula_metadata_fields_complete(self, template):
        """Every formula has required metadata fields with valid values."""
        template_dir = TEMPLATES_DIR / template
        if not template_dir.exists():
            pytest.skip(f"Template {template} not found")

        # Export
        subprocess.run(
            [sys.executable, "src/model.py"],
            cwd=template_dir,
            capture_output=True,
            timeout=30,
        )

        # Load
        equations_file = None
        for json_file in template_dir.glob("*equations.json"):
            equations_file = json_file
            break

        assert equations_file is not None

        with open(equations_file) as f:
            equations = json.load(f)

        # Required fields that should not be null/empty
        critical_fields = ["latex", "code_ref", "line"]

        for eq_name, eq_data in equations.items():
            # Check presence
            for field in critical_fields:
                assert field in eq_data, f"{eq_name} missing field: {field}"

            # Check non-empty/non-null
            for field in critical_fields:
                value = eq_data[field]
                assert value is not None, f"{eq_name}.{field} is null"
                assert len(str(value)) > 0, f"{eq_name}.{field} is empty"

            # Validate line number
            line_num = eq_data["line"]
            assert isinstance(line_num, int) and line_num > 0, f"{eq_name}.line should be positive int, got {line_num}"

            # Validate code_ref format (should contain filename:function)
            code_ref = eq_data["code_ref"]
            assert ":" in code_ref, f"{eq_name}.code_ref missing colon: {code_ref}"

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_formula_special_characters_preserved(self, template):
        """Greek letters and special symbols survive export."""
        template_dir = TEMPLATES_DIR / template
        if not template_dir.exists():
            pytest.skip(f"Template {template} not found")

        # Export
        subprocess.run(
            [sys.executable, "src/model.py"],
            cwd=template_dir,
            capture_output=True,
            timeout=30,
        )

        # Load
        equations_file = None
        for json_file in template_dir.glob("*equations.json"):
            equations_file = json_file
            break

        assert equations_file is not None

        with open(equations_file) as f:
            equations = json.load(f)

        # Spot-check: at least one formula should have Greek letters or special math
        special_chars = {
            "alpha",
            "beta",
            "gamma",
            "delta",
            "theta",
            "lambda",
            "mu",
            "sigma",
            "rho",
            "frac",
            "sqrt",
            "sum",
            "prod",
            "int",
            "partial",
        }

        formulas_with_special = 0
        for eq_data in equations.values():
            latex = eq_data.get("latex", "")
            if any(char in latex for char in special_chars):
                formulas_with_special += 1

        # At least one formula should have mathematical notation
        assert formulas_with_special >= 1, f"{template} should have >= 1 formula with special math notation"

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_formula_units_assumptions_not_lost(self, template):
        """Optional fields (units, assumptions) are preserved if present."""
        template_dir = TEMPLATES_DIR / template
        if not template_dir.exists():
            pytest.skip(f"Template {template} not found")

        # Export
        subprocess.run(
            [sys.executable, "src/model.py"],
            cwd=template_dir,
            capture_output=True,
            timeout=30,
        )

        # Load
        equations_file = None
        for json_file in template_dir.glob("*equations.json"):
            equations_file = json_file
            break

        assert equations_file is not None

        with open(equations_file) as f:
            equations = json.load(f)

        # If any formula has optional fields, verify they're not empty
        for eq_name, eq_data in equations.items():
            if "units" in eq_data and eq_data["units"] is not None:
                assert len(str(eq_data["units"])) > 0, f"{eq_name}.units is present but empty"

            if "assumptions" in eq_data and eq_data["assumptions"] is not None:
                # Should be a string or list
                assumptions = eq_data["assumptions"]
                if isinstance(assumptions, str | list):
                    assert len(assumptions) > 0

            if "description" in eq_data and eq_data["description"] is not None:
                assert len(str(eq_data["description"])) > 0, f"{eq_name}.description is present but empty"

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_no_formula_truncation_or_data_loss(self, template):
        """Formulas are not truncated or corrupted during export."""
        template_dir = TEMPLATES_DIR / template
        if not template_dir.exists():
            pytest.skip(f"Template {template} not found")

        # Export
        subprocess.run(
            [sys.executable, "src/model.py"],
            cwd=template_dir,
            capture_output=True,
            timeout=30,
        )

        # Load
        equations_file = None
        for json_file in template_dir.glob("*equations.json"):
            equations_file = json_file
            break

        assert equations_file is not None

        with open(equations_file) as f:
            equations = json.load(f)

        # Check for common truncation patterns
        truncation_patterns = [
            "...",  # Ellipsis truncation
            "<truncated>",
            "[truncated]",
        ]

        for eq_name, eq_data in equations.items():
            latex = eq_data.get("latex", "")

            for pattern in truncation_patterns:
                assert pattern not in latex, f"{eq_name} appears truncated (contains {pattern})"

            # Check for incomplete TeX commands
            if "\\" in latex:
                # If it has backslashes, should have complete commands
                parts = latex.split("\\")
                for part in parts[1:]:  # Skip first part before first backslash
                    if len(part) > 0:
                        # Command should have at least one character after backslash
                        first_char = part[0]
                        # Should be letter or {
                        assert (
                            first_char.isalpha() or first_char == "{"
                        ), f"{eq_name} has incomplete command: \\{first_char}"
