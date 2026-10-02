"""Tests for paper ingestion services."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from math_trace.services import (
    ExtractedEquation,
    FormulaExtractor,
    PaperDownloader,
    PaperMetadata,
    PresentationBuilder,
)

# Alias for tests
Formula = ExtractedEquation


class TestPaperDownloader:
    """Tests for PaperDownloader service."""

    def test_parse_arxiv_url_from_abs(self):
        """Parse arXiv /abs/ URL to PDF URL."""
        url = "https://arxiv.org/abs/2609.21904"
        pdf_url = PaperDownloader._parse_arxiv_url(url)
        assert pdf_url == "https://arxiv.org/pdf/2609.21904.pdf"

    def test_parse_arxiv_url_from_pdf(self):
        """Parse arXiv /pdf/ URL (already correct)."""
        url = "https://arxiv.org/pdf/2609.21904.pdf"
        pdf_url = PaperDownloader._parse_arxiv_url(url)
        assert pdf_url == "https://arxiv.org/pdf/2609.21904.pdf"

    def test_parse_arxiv_url_invalid(self):
        """Return None for non-arXiv URLs."""
        url = "https://example.com/paper.pdf"
        pdf_url = PaperDownloader._parse_arxiv_url(url)
        assert pdf_url is None


class TestFormulaExtractor:
    """Tests for FormulaExtractor service."""

    def test_extract_empty_pdf(self):
        """Handle PDF with no formulas."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = Path(f.name)

        try:
            with patch("pdfplumber.open") as mock_open:
                mock_pdf = MagicMock()
                mock_page = MagicMock()
                mock_page.extract_text.return_value = "Just text, no formulas."
                mock_pdf.pages = [mock_page]
                mock_open.return_value.__enter__.return_value = mock_pdf

                formulas = FormulaExtractor.extract(pdf_path)
                assert len(formulas) == 0
        finally:
            pdf_path.unlink()

    def test_extract_finds_display_math(self):
        """Extract display math formula."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = Path(f.name)

        try:
            with patch("pdfplumber.open") as mock_open:
                text = "The rate equation: $$ \\frac{dI}{dt} = \\beta S I $$"
                mock_pdf = MagicMock()
                mock_page = MagicMock()
                mock_page.extract_text.return_value = text
                mock_pdf.pages = [mock_page]
                mock_open.return_value.__enter__.return_value = mock_pdf

                formulas = FormulaExtractor.extract(pdf_path)
                assert len(formulas) > 0
                assert formulas[0].page == 1
        finally:
            pdf_path.unlink()


class TestPresentationBuilder:
    """Tests for PresentationBuilder service."""

    def test_build_config_single_formula(self):
        """Build presentation config from one formula."""
        formula = Formula(
            name="eq_1",
            latex="\\frac{dI}{dt} = \\beta S I",
            description="Rate equation",
            page=1,
            context="The rate of change...",
        )
        paper_metadata = PaperMetadata(
            title="SIR Model",
            url="https://arxiv.org/abs/2609.21904",
            pages=10,
            formulas=[formula],
        )

        config = PresentationBuilder.build_config(
            paper_metadata,
            "https://arxiv.org/abs/2609.21904",
        )

        assert "SIR Model" in config["title"]
        assert config["format"] == "talk"
        assert config["backend"] == "marp"
        assert len(config["slides"]) == 2  # Title + 1 formula

    def test_build_formulas_json(self):
        """Build formulas.json structure."""
        formulas = [
            Formula(
                name="eq_1",
                latex="\\beta S I",
                description="Transmission",
                page=1,
                context="context here",
            ),
            Formula(
                name="eq_2",
                latex="\\gamma I",
                description="Recovery",
                page=2,
                context="more context",
            ),
        ]

        formulas_dict = PresentationBuilder.build_formulas_json(formulas)

        assert "eq_1" in formulas_dict
        assert "eq_2" in formulas_dict
        assert formulas_dict["eq_1"]["latex"] == "\\beta S I"
        assert formulas_dict["eq_2"]["description"] == "Recovery"


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_ingest_workflow(self):
        """Test complete paper → formulas → config workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create mock formulas
            formulas = [
                Formula(
                    name="dS_dt",
                    latex="-\\beta S I",
                    description="Susceptible",
                    page=1,
                    context="S decreases",
                ),
                Formula(
                    name="dI_dt",
                    latex="\\beta S I - \\gamma I",
                    description="Infected",
                    page=1,
                    context="I changes",
                ),
            ]

            # Build config
            paper_metadata = PaperMetadata(
                title="Test SIR Model",
                url="https://arxiv.org/abs/test",
                pages=5,
                formulas=formulas,
            )
            config = PresentationBuilder.build_config(
                paper_metadata,
                "https://arxiv.org/abs/test",
            )

            # Save config
            config_path = tmpdir / "config.yaml"
            import yaml

            config_path.write_text(yaml.dump(config))

            # Save formulas
            formulas_dict = PresentationBuilder.build_formulas_json(formulas)
            formulas_path = tmpdir / "formulas.json"
            formulas_path.write_text(json.dumps(formulas_dict))

            # Verify outputs
            assert config_path.exists()
            assert formulas_path.exists()

            # Verify structure
            saved_config = yaml.safe_load(config_path.read_text())
            assert "Test SIR Model" in saved_config["title"]
            assert len(saved_config["slides"]) == 3  # Title + 2 formulas

            saved_formulas = json.loads(formulas_path.read_text())
            assert len(saved_formulas) == 2
