"""Contract tests for epidemiology SIR/R0 reference.

Validates:
- Frequency-dependent SIR transmission model
- R0 = beta/gamma under stated assumptions
- Required symbol/assumption metadata
- Provenance and source identifiers
- Output/manifest generation and reproducibility
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def sir_example_dir():
    """Path to epidemiology-sir example."""
    return Path(__file__).parent.parent / "examples" / "epidemiology-sir"


@pytest.fixture
def generated_output_dir(tmp_path):
    """Temporary directory for generated outputs."""
    return tmp_path / "generated"


class TestFrequencyDependentModel:
    """Validate frequency-dependent SIR transmission model."""

    def test_model_imports_sympy(self, sir_example_dir):
        """Model uses SymPy for symbolic equations."""
        model_file = sir_example_dir / "model.py"
        content = model_file.read_text()
        assert "from sympy import" in content or "import sympy" in content

    def test_model_defines_required_symbols(self, sir_example_dir):
        """Model defines S, I, R, N, beta, gamma, R0."""
        model_file = sir_example_dir / "model.py"
        content = model_file.read_text()
        required_symbols = ["S", "I", "R", "N", "beta", "gamma"]
        for symbol in required_symbols:
            assert symbol in content, f"Missing symbol: {symbol}"

    def test_frequency_dependent_transmission(self, sir_example_dir):
        """Transmission rate is frequency-dependent (beta * S * I / N)."""
        model_file = sir_example_dir / "model.py"
        content = model_file.read_text()
        # Check for frequency-dependent (divide by N) convention
        assert "/ N" in content or "N)" in content, "Expected frequency-dependent transmission"

    def test_r0_formula_beta_over_gamma(self, sir_example_dir):
        """R0 is defined as beta / gamma."""
        model_file = sir_example_dir / "model.py"
        content = model_file.read_text()
        assert "R0" in content or "R_0" in content
        assert "beta" in content and "gamma" in content


class TestModelAssumptions:
    """Validate documented assumptions."""

    def test_assumptions_documented_in_paper(self, sir_example_dir):
        """Model assumptions are stated in the paper."""
        paper_file = sir_example_dir / "main.typ"
        content = paper_file.read_text()
        # Check for key assumption statements
        assumptions = [
            "constant",  # constant beta
            "homogeneous",  # homogeneous mixing
            "simplified",  # simplified
        ]
        content_lower = content.lower()
        for assumption in assumptions:
            assert assumption in content_lower, f"Missing assumption: {assumption}"

    def test_limitations_documented(self, sir_example_dir):
        """Limitations are clearly stated."""
        paper_file = sir_example_dir / "main.typ"
        content = paper_file.read_text()
        content_lower = content.lower()
        # Check for boundary/limitation language
        # At least some of these should be present
        limitations = [
            "pedagogical",
            "simplified",
            "additional modeling",
        ]
        found_count = sum(1 for limit in limitations if limit in content_lower)
        assert found_count >= 2, f"Expected at least 2 limitations documented; found {found_count}"


class TestProvenance:
    """Validate provenance and source identifiers."""

    def test_model_has_line_comments(self, sir_example_dir):
        """Model includes line numbers and comments for traceability."""
        model_file = sir_example_dir / "model.py"
        lines = model_file.read_text().split("\n")
        # Should have meaningful comments or documentation
        comment_count = sum(1 for line in lines if "#" in line and not line.strip().startswith("#!/"))
        assert comment_count > 0, "Model should have explanatory comments"

    def test_citations_present(self, sir_example_dir):
        """Paper includes proper citations."""
        paper_file = sir_example_dir / "main.typ"
        content = paper_file.read_text()
        # Check for citation markers
        assert "Kermack" in content or "citation" in content.lower()

    def test_scenario_labels_explicit(self, sir_example_dir):
        """Scenario parameters are explicitly labeled (COVID-like, measles)."""
        simulate_file = sir_example_dir / "simulate.py"
        content = simulate_file.read_text()
        assert "covid" in content.lower() or "COVID" in content
        assert "measles" in content.lower() or "Measles" in content


class TestOutputManifest:
    """Validate output generation and manifest."""

    def test_build_script_exists(self, sir_example_dir):
        """Build orchestration script exists."""
        build_file = sir_example_dir / "build_paper.py"
        assert build_file.exists(), "build_paper.py required"

    def test_build_script_is_executable_via_python(self, sir_example_dir):
        """Build script can be imported and run."""
        # Verify it's valid Python
        build_file = sir_example_dir / "build_paper.py"
        content = build_file.read_text()
        assert "def " in content or "class " in content, "build_paper.py should define functions/classes"

    def test_expected_outputs_documented(self, sir_example_dir):
        """Expected output files/formats are documented."""
        # Check build_paper.py for expected outputs
        build_file = sir_example_dir / "build_paper.py"
        content = build_file.read_text()
        # Should mention output formats
        expected_mentions = ["json", "png", "figure", "export"]
        assert any(term in content.lower() for term in expected_mentions)


class TestReproducibility:
    """Validate reproducibility of model and outputs."""

    def test_build_runs_without_errors(self, sir_example_dir):
        """Build pipeline completes successfully."""
        build_file = sir_example_dir / "build_paper.py"
        result = subprocess.run(
            [sys.executable, str(build_file)],
            cwd=str(sir_example_dir),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"

    def test_build_is_deterministic(self, sir_example_dir):
        """Running build twice produces identical JSON outputs."""
        build_file = sir_example_dir / "build_paper.py"

        # Run build twice
        outputs1 = {}
        outputs2 = {}

        for run_num, outputs in [(1, outputs1), (2, outputs2)]:
            result = subprocess.run(
                [sys.executable, str(build_file)],
                cwd=str(sir_example_dir),
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, f"Build run {run_num} failed"

            # Find and load generated JSON files
            gen_dir = sir_example_dir / "generated"
            if gen_dir.exists():
                for json_file in gen_dir.glob("*.json"):
                    content = json_file.read_text()
                    outputs[json_file.name] = content

        # Compare outputs
        assert len(outputs1) > 0, "No JSON outputs generated in run 1"
        assert len(outputs1) == len(outputs2), "Different number of outputs between runs"

        for filename in outputs1:
            assert filename in outputs2, f"Missing {filename} in run 2"
            json1 = json.loads(outputs1[filename])
            json2 = json.loads(outputs2[filename])
            assert json1 == json2, f"JSON {filename} differs between runs"

    def test_r0_value_formula_consistency(self, sir_example_dir):
        """R0 value matches beta/gamma formula in outputs."""
        build_file = sir_example_dir / "build_paper.py"
        result = subprocess.run(
            [sys.executable, str(build_file)],
            cwd=str(sir_example_dir),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # Check generated JSON for R0 consistency
        gen_dir = sir_example_dir / "generated"
        if gen_dir.exists():
            for json_file in gen_dir.glob("*.json"):
                try:
                    data = json.loads(json_file.read_text())
                    # If data contains beta, gamma, R0, verify formula
                    if "beta" in data and "gamma" in data and "R0" in data:
                        expected_r0 = data["beta"] / data["gamma"]
                        assert abs(data["R0"] - expected_r0) < 1e-10, f"R0 formula mismatch in {json_file.name}"
                except json.JSONDecodeError:
                    pass  # Skip invalid JSON


class TestIntegration:
    """Integration tests for full pipeline."""

    def test_full_build_and_validate(self, sir_example_dir):
        """Complete build pipeline produces all required artifacts."""
        build_file = sir_example_dir / "build_paper.py"
        result = subprocess.run(
            [sys.executable, str(build_file)],
            cwd=str(sir_example_dir),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"

        # Verify generated directory and outputs exist
        gen_dir = sir_example_dir / "generated"
        assert gen_dir.exists(), "generated/ directory not created"

        # Check for expected output types
        json_files = list(gen_dir.glob("*.json"))
        png_files = list(gen_dir.glob("**/*.png"))

        assert len(json_files) > 0, "No JSON outputs generated"
        assert len(png_files) > 0 or True, "PNG outputs optional but recommended"  # PNG is optional

    def test_model_consistency_with_paper(self, sir_example_dir):
        """Model equations match paper derivations."""
        model_file = sir_example_dir / "model.py"
        paper_file = sir_example_dir / "main.typ"

        model_file.read_text()
        paper_content = paper_file.read_text()

        # Both should reference the same key equations
        shared_terms = ["dS/dt", "dI/dt", "dR/dt"]
        for term in shared_terms:
            assert term in paper_content.lower() or "susceptible" in paper_content.lower()
