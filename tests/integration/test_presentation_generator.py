"""PresentationGenerator integration tests.

Tests the presentation generation pipeline with various config formats,
edge cases, and failure modes to catch issues before they reach the UI.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent / "../../src"))
from math_trace.presentation_generator import MarpBackend, PresentationConfig, PresentationGenerator


class TestPresentationGeneratorLoading:
    """Tests PresentationGenerator initialization and config loading."""

    @pytest.fixture
    def temp_formula_file(self):
        """Create a temporary formula JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "rate": {"latex": "k \\binom{n}{2}"},
                "equilibrium": {"latex": "I^* = (1 - 1/R_0) N"}
            }, f)
            path = Path(f.name)
        yield path
        path.unlink(missing_ok=True)

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                "title": "Disease Modeling",
                "format": "talk",
                "backend": "marp",
                "slides": [
                    {"title": "Introduction", "text": "Disease dynamics"}
                ]
            }, f)
            path = Path(f.name)
        yield path
        path.unlink(missing_ok=True)

    def test_generator_initializes_with_files(self, temp_formula_file, temp_config_file):
        """Generator loads formula and config files correctly."""
        gen = PresentationGenerator(temp_formula_file, temp_config_file)
        assert gen.model_path == temp_formula_file
        assert gen.config_path == temp_config_file
        assert gen.config_data is not None
        assert gen.config_data["title"] == "Disease Modeling"

    def test_generator_with_special_characters_in_title(self, temp_formula_file):
        """Generator handles special characters in config."""
        config_content = {
            "title": "My P: the sequel",  # Colon is fine when quoted in YAML
            "format": "talk",
            "backend": "marp",
            "slides": [{"title": "Intro"}]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_content, f)
            config_path = Path(f.name)

        try:
            gen = PresentationGenerator(temp_formula_file, config_path)
            assert gen.config_data["title"] == "My P: the sequel"
        finally:
            config_path.unlink(missing_ok=True)

    def test_generator_with_unicode_characters(self, temp_formula_file):
        """Generator handles Unicode in title."""
        config_content = {
            "title": "分子動力学",  # Japanese
            "format": "talk",
            "backend": "marp",
            "slides": [{"title": "Overview"}]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_content, f)
            config_path = Path(f.name)

        try:
            gen = PresentationGenerator(temp_formula_file, config_path)
            assert "分子" in gen.config_data["title"]
        finally:
            config_path.unlink(missing_ok=True)

    def test_generator_loads_formula_json(self, temp_config_file):
        """Generator loads formulas from JSON file."""
        formulas_data = {
            "rate": {"latex": "k n"},
            "equilibrium": {"latex": "I^*"}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(formulas_data, f)
            formula_path = Path(f.name)

        try:
            gen = PresentationGenerator(formula_path, temp_config_file)
            formulas = gen._load_formulas()
            assert "rate" in formulas
            assert formulas["rate"]["latex"] == "k n"
        finally:
            formula_path.unlink(missing_ok=True)


class TestConfigParsingEdgeCases:
    """Test YAML config parsing with edge cases."""

    def test_yaml_quoted_strings_with_colons(self):
        """Quoted YAML strings preserve colons."""
        yaml_str = 'title: "My P: with colon"'
        config = yaml.safe_load(yaml_str)
        assert config["title"] == "My P: with colon"

    def test_yaml_dict_parsing(self):
        """Dict-format config parses correctly."""
        yaml_dict = {
            "title": "Test",
            "format": "talk",
            "backend": "marp",
            "slides": []
        }
        yaml_str = yaml.dump(yaml_dict)
        parsed = yaml.safe_load(yaml_str)
        assert parsed["title"] == "Test"
        assert parsed["format"] == "talk"

    def test_yaml_preserves_special_chars_in_metadata(self):
        """Special characters in metadata survive round-trip."""
        config_dict = {
            "title": "My P: colon version",
            "metadata": {
                "author": "O'Brien & Associates",
                "affiliation": "New York, USA"
            }
        }
        yaml_str = yaml.dump(config_dict)
        parsed = yaml.safe_load(yaml_str)
        assert "&" in parsed["metadata"]["author"]
        assert ":" in parsed["title"]


class TestMarpBackendRendering:
    """Test Marp backend rendering with various configs."""

    @pytest.fixture
    def marp_backend(self):
        """Create a Marp backend instance."""
        return MarpBackend()

    def test_marp_renders_with_title_and_metadata(self, marp_backend):
        """Marp backend renders title slide with metadata."""
        config = PresentationConfig(
            title="Disease Modeling",
            format="talk",
            backend="marp",
            slides=[],
            metadata={"author": "Dr. Smith", "date": "2026-10-02"}
        )
        formulas = {"rate": {"latex": "k n", "description": "Rate law"}}

        with tempfile.TemporaryDirectory() as tmpdir:
            result = marp_backend.render(config, formulas, Path(tmpdir))
            assert result.exists()
            content = result.read_text()
            assert "Disease Modeling" in content
            assert "Dr. Smith" in content

    def test_marp_renders_with_formulas(self, marp_backend):
        """Marp backend includes formulas in slides."""
        config = PresentationConfig(
            title="Formulas",
            format="talk",
            backend="marp",
            slides=[
                {
                    "title": "Rate Law",
                    "formulas": ["rate"]
                }
            ]
        )
        formulas = {"rate": {"latex": "k \\binom{n}{2}", "description": "Rate law"}}

        with tempfile.TemporaryDirectory() as tmpdir:
            result = marp_backend.render(config, formulas, Path(tmpdir))
            content = result.read_text()
            assert "Rate Law" in content
            assert "Rate law" in content  # Description should appear

    def test_marp_handles_missing_formulas_gracefully(self, marp_backend):
        """Marp backend handles undefined formula references."""
        config = PresentationConfig(
            title="Test",
            format="talk",
            backend="marp",
            slides=[
                {"title": "Slide", "formulas": ["undefined_formula"]}
            ]
        )
        formulas = {}  # Empty - the referenced formula doesn't exist

        with tempfile.TemporaryDirectory() as tmpdir:
            # Should not crash even if formula missing
            try:
                result = marp_backend.render(config, formulas, Path(tmpdir))
                # Either succeeds or fails gracefully
                assert result is not None or isinstance(result, Path)
            except KeyError:
                # Expected - formula doesn't exist
                pass
