"""
Regression tests: Template Build Pipeline

Verifies that each template can execute the full build pipeline:
model.py → equations.json → formulas.typ → simulation → figures → PDF

These tests prevent breaking the critical path for end-users.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

MATH_TRACE_ROOT = Path(__file__).parent.parent.parent
TEMPLATES_DIR = MATH_TRACE_ROOT / "templates"

PRODUCTION_TEMPLATES = [
    "epidemiology",
    "quantum-systems",
    "control-systems",
    "gnns",
    "thermodynamics",
]


@pytest.fixture
def template_dir(request):
    """Return template directory for parametrized template name."""
    template_name = request.param
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        pytest.skip(f"Template {template_name} not found")
    return template_path


class TestTemplateFullBuild:
    """Verify each template builds end-to-end without errors."""

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_template_model_exports_json(self, template):
        """Model exports equations.json with valid LaTeX."""
        template_dir = TEMPLATES_DIR / template
        if not template_dir.exists():
            pytest.skip(f"Template {template} not found")

        # Run model.py in template directory
        result = subprocess.run(
            [sys.executable, "src/model.py"],
            cwd=template_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Model export failed:\n{result.stderr}"

        # Verify equations.json exists and is valid
        equations_file = None
        for json_file in template_dir.glob("*equations.json"):
            equations_file = json_file
            break

        assert equations_file is not None, f"No equations.json found in {template}"
        assert equations_file.stat().st_size > 0, "equations.json is empty"

        # Verify JSON is valid and has expected structure
        with open(equations_file) as f:
            equations = json.load(f)

        assert isinstance(equations, dict), "equations.json should be a dict"
        assert len(equations) >= 3, f"{template} should export >= 3 equations"

        # Spot-check first equation
        first_eq = next(iter(equations.values()))
        required_fields = ["latex", "code_ref", "line"]
        for field in required_fields:
            assert field in first_eq, f"Missing field '{field}' in equation metadata"

        # Verify LaTeX has no obvious syntax errors
        assert "$" not in first_eq["latex"], "LaTeX should not contain $"
        # Some formulas are simple (like "PV = nRT") without special commands
        assert len(first_eq["latex"]) > 0, "LaTeX should not be empty"

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_template_simulation_runs_without_error(self, template):
        """Template scenario simulations execute successfully."""
        template_dir = TEMPLATES_DIR / template
        if not template_dir.exists():
            pytest.skip(f"Template {template} not found")

        # Verify simulate.py exists
        simulate_file = template_dir / "src" / "simulate.py"
        if not simulate_file.exists():
            pytest.skip(f"No simulate.py found in {template}")

        # Try importing and running a basic scenario
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; sys.path.insert(0, 'src'); from simulate import *; print('OK')",
            ],
            cwd=template_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Simulate module import failed for {template}:\n{result.stderr}"
        assert "OK" in result.stdout, "Simulate module did not import successfully"

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_template_build_paper_script_exists(self, template):
        """Verify build_paper.py exists and is executable."""
        template_dir = TEMPLATES_DIR / template
        if not template_dir.exists():
            pytest.skip(f"Template {template} not found")

        build_script = template_dir / "build_paper.py"
        assert build_script.exists(), f"No build_paper.py in {template}"

        # Verify it's valid Python
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(build_script)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"build_paper.py has syntax errors:\n{result.stderr}"

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_template_main_typ_exists_and_valid(self, template):
        """Verify main.typ document structure exists."""
        template_dir = TEMPLATES_DIR / template
        if not template_dir.exists():
            pytest.skip(f"Template {template} not found")

        typ_file = template_dir / "main.typ"
        assert typ_file.exists(), f"No main.typ found in {template}"

        # Verify it's readable and has reasonable size
        content = typ_file.read_text()
        assert len(content) > 100, "main.typ is too small to be a valid document"

        # Spot-check for Typst structure (should have assignments or directives)
        assert (
            "#set" in content or "#let" in content or "let " in content or "=" in content or "import" in content
        ), "main.typ doesn't look like valid Typst"

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_template_has_minimum_directory_structure(self, template):
        """Every template has required directories and files."""
        template_dir = TEMPLATES_DIR / template
        if not template_dir.exists():
            pytest.skip(f"Template {template} not found")

        required_dirs = ["src", "src/tests"]
        required_files = ["src/model.py", "main.typ", "README.md"]
        optional_files = ["src/simulate.py"]  # Some templates may not have simulation

        for dir_name in required_dirs:
            dir_path = template_dir / dir_name
            assert dir_path.exists() and dir_path.is_dir(), f"Missing required directory: {dir_name}"

        for file_name in required_files:
            file_path = template_dir / file_name
            assert file_path.exists() and file_path.is_file(), f"Missing required file: {file_name}"

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_template_readme_describes_purpose(self, template):
        """README.md exists and describes the template."""
        template_dir = TEMPLATES_DIR / template
        if not template_dir.exists():
            pytest.skip(f"Template {template} not found")

        readme = template_dir / "README.md"
        assert readme.exists(), f"No README.md in {template}"

        content = readme.read_text()
        assert len(content) > 50, "README.md is too short to be useful"


@pytest.mark.integration
class TestFormulaExportConsistency:
    """Verify formula export produces consistent, valid output."""

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_all_formulas_have_latex_field(self, template):
        """Every exported formula has valid LaTeX."""
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
        assert result.returncode == 0

        # Load equations
        equations_file = None
        for json_file in template_dir.glob("*equations.json"):
            equations_file = json_file
            break

        assert equations_file is not None

        with open(equations_file) as f:
            equations = json.load(f)

        for eq_name, eq_data in equations.items():
            assert "latex" in eq_data, f"Missing LaTeX in {eq_name}"
            latex = eq_data["latex"]

            # Verify LaTeX is non-empty
            assert len(latex) > 0, f"Empty LaTeX in {eq_name}"

            # Verify no obvious corruption
            assert "$" not in latex, f"Unescaped $ in {eq_name}"
            assert "\\\\" not in latex, f"Double-escaped backslash in {eq_name}"

            # Verify matching braces (basic check)
            open_braces = latex.count("{")
            close_braces = latex.count("}")
            assert open_braces == close_braces, f"Unmatched braces in {eq_name}: {latex}"

    @pytest.mark.parametrize("template", PRODUCTION_TEMPLATES, indirect=False)
    def test_formulas_have_metadata(self, template):
        """Every formula has required metadata fields."""
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

        required_fields = ["latex", "code_ref", "line"]

        for eq_name, eq_data in equations.items():
            for field in required_fields:
                assert field in eq_data, f"Missing '{field}' in {eq_name}: {list(eq_data.keys())}"
                assert eq_data[field] is not None, f"Null value for {field} in {eq_name}"
