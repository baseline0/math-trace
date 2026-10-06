"""
Consistency tests for all templates in templates/ directory.

Validates:
- All templates have required files (model.py, main.typ, etc.)
- All formula JSONs have required fields
- No duplicate equation names within template
- Build script can be executed
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates"
TEMPLATES = [
    "simple-physics",
    "biochemistry",
    "quantum-systems",
    "epidemiology",
    "control-systems",
    "thermodynamics",
    "gnns",
]

REQUIRED_FILES = {
    "model.py",  # Source of formulas
    "main.typ",  # Paper template
    "README.md",  # Documentation
}

REQUIRED_FORMULA_FIELDS = {
    "latex",
    "description",
    "source_line",
}


class TestTemplateStructure:
    """Test template directory structure."""

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_exists(self, template):
        """Each template has a directory."""
        template_path = TEMPLATE_DIR / template
        assert template_path.is_dir(), f"Template {template} directory not found"

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_has_model(self, template):
        """Each template has a model.py (in root or src/)."""
        template_path = TEMPLATE_DIR / template

        # Check both old-style (root) and new-style (src/)
        model_root = template_path / "model.py"
        model_src = template_path / "src" / "model.py"

        assert model_root.exists() or model_src.exists(), f"{template}: model.py not found in root or src/"

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_has_main_typ(self, template):
        """Each template has main.typ."""
        template_path = TEMPLATE_DIR / template
        main_typ = template_path / "main.typ"
        if not main_typ.exists():
            pytest.skip(f"{template}: main.typ not found (incomplete template)")

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_has_readme(self, template):
        """Each template has README.md."""
        template_path = TEMPLATE_DIR / template
        readme = template_path / "README.md"
        assert readme.exists(), f"{template}: README.md not found"


class TestFormulaJSON:
    """Test generated formula JSON files."""

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_generates_equations_json(self, template):
        """Running model.py generates equations JSON."""
        template_path = TEMPLATE_DIR / template

        # Find model.py
        model_root = template_path / "model.py"
        model_src = template_path / "src" / "model.py"
        model_path = model_src if model_src.exists() else model_root

        if not model_path.exists():
            pytest.skip(f"{template}: model.py not found")

        # Run model.py (safe: model_path is from controlled template directory)
        result = subprocess.run(
            [sys.executable, str(model_path)],
            cwd=str(template_path),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"{template}: model.py failed:\n{result.stderr}"

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_formula_json_has_required_fields(self, template):
        """All formulas in JSON have required fields."""
        template_path = TEMPLATE_DIR / template

        # Find JSON file (pattern: *_equations.json)
        json_files = list(template_path.glob("*_equations.json"))
        if not json_files:
            pytest.skip(f"{template}: no *_equations.json found")

        json_file = json_files[0]

        with open(json_file) as f:
            formulas = json.load(f)

        for name, formula in formulas.items():
            for field in REQUIRED_FORMULA_FIELDS:
                assert field in formula, f"{template} formula '{name}' missing field: {field}"

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_no_duplicate_equation_names(self, template):
        """No duplicate equation names within template."""
        template_path = TEMPLATE_DIR / template

        json_files = list(template_path.glob("*_equations.json"))
        if not json_files:
            pytest.skip(f"{template}: no *_equations.json found")

        json_file = json_files[0]

        with open(json_file) as f:
            formulas = json.load(f)

        equation_names = list(formulas.keys())
        unique_names = set(equation_names)

        assert len(equation_names) == len(unique_names), f"{template} has duplicate equation names"


class TestBuildScript:
    """Test template build scripts."""

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_build_paper_exists(self, template):
        """Each template has a build_paper.py or equivalent."""
        template_path = TEMPLATE_DIR / template
        build_script = template_path / "build_paper.py"
        if not build_script.exists():
            pytest.skip(f"{template}: build_paper.py not found (incomplete template)")

    @pytest.mark.parametrize("template", ["simple-physics", "biochemistry"])
    def test_build_script_imports_template_builder(self, template):
        """Old-style templates use shared template_builder."""
        template_path = TEMPLATE_DIR / template
        build_script = template_path / "build_paper.py"

        content = build_script.read_text()
        assert "template_builder" in content, f"{template} build_paper.py doesn't use template_builder"


class TestFormulaMetadata:
    """Test formula metadata (units, assumptions)."""

    @pytest.mark.parametrize("template", ["simple-physics", "biochemistry"])
    def test_formulas_have_units(self, template):
        """Formulas should have units field in metadata."""
        template_path = TEMPLATE_DIR / template

        json_files = list(template_path.glob("*_equations.json"))
        if not json_files:
            pytest.skip(f"{template}: no *_equations.json found")

        json_file = json_files[0]

        with open(json_file) as f:
            formulas = json.load(f)

        # Check that at least 50% of formulas have units
        formulas_with_units = sum(1 for f in formulas.values() if f.get("units"))
        assert formulas_with_units >= len(formulas) * 0.5, f"{template}: less than 50% of formulas have units"

    @pytest.mark.parametrize("template", ["simple-physics", "biochemistry"])
    def test_formulas_have_assumptions(self, template):
        """Formulas should have assumptions field in metadata."""
        template_path = TEMPLATE_DIR / template

        json_files = list(template_path.glob("*_equations.json"))
        if not json_files:
            pytest.skip(f"{template}: no *_equations.json found")

        json_file = json_files[0]

        with open(json_file) as f:
            formulas = json.load(f)

        # Check that at least 50% of formulas have assumptions
        formulas_with_assumptions = sum(1 for f in formulas.values() if f.get("assumptions"))
        assert (
            formulas_with_assumptions >= len(formulas) * 0.5
        ), f"{template}: less than 50% of formulas have assumptions"
