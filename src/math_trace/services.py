"""Pure Python services for paper ingestion and presentation generation.

Core services (testable, independent):
- PaperDownloader: Fetch PDFs from URLs (arXiv, PubMed, direct links)
- FormulaExtractor: Identify LaTeX formulas in PDF
- PresentationBuilder: Orchestrate formula extraction → presentation config
"""

from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional
from urllib.parse import urlparse
from urllib.request import urlopen

import pdfplumber


@dataclass
class ExtractedEquation:
    """Equation extracted from a PDF paper with metadata."""

    name: str
    latex: str
    description: str
    page: int
    context: str  # Surrounding text from paper


@dataclass
class PaperMetadata:
    """Paper information extracted from PDF."""

    title: str
    url: str
    pages: int
    formulas: list[ExtractedEquation]


class PaperDownloader:
    """Download papers from various sources."""

    @staticmethod
    def _parse_arxiv_url(url: str) -> str | None:
        """Convert arXiv page URL to PDF URL.

        Examples:
            https://arxiv.org/abs/2609.21904 → https://arxiv.org/pdf/2609.21904.pdf
            https://arxiv.org/pdf/2609.21904.pdf → https://arxiv.org/pdf/2609.21904.pdf
        """
        arxiv_pattern = r"arxiv\.org/(?:abs|pdf)/(\d+\.\d+)"
        match = re.search(arxiv_pattern, url)
        if match:
            arxiv_id = match.group(1)
            return f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        return None

    @staticmethod
    def _parse_pubmed_url(url: str) -> str | None:
        """Convert PubMed page URL to PDF URL (if available)."""
        # PubMed URLs typically don't have direct PDF links
        # Would need to scrape or use API
        return None

    @staticmethod
    def download(url: str, cache_dir: Path | None = None) -> Path:
        """Download paper PDF from URL.

        Supports:
        - arXiv URLs (abs or pdf)
        - PubMed URLs (experimental)
        - Direct PDF links

        Args:
            url: Paper URL or direct PDF link
            cache_dir: Directory to cache downloads (default: temp)

        Returns:
            Path to downloaded PDF

        Raises:
            ValueError: If URL format not recognized
            URLError: If download fails
        """
        if cache_dir is None:
            cache_dir = Path(tempfile.gettempdir()) / "math-trace-papers"
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Try to parse URL to get PDF link
        pdf_url = url
        if "arxiv.org" in url:
            pdf_url = PaperDownloader._parse_arxiv_url(url)
            if not pdf_url:
                raise ValueError(f"Cannot parse arXiv URL: {url}")

        # Generate cache filename from URL
        cache_name = urlparse(pdf_url).path.split("/")[-1]
        if not cache_name.endswith(".pdf"):
            cache_name = cache_name.replace("abs", "pdf") + ".pdf"
        cache_path = cache_dir / cache_name

        # Return cached if exists
        if cache_path.exists():
            return cache_path

        # Download
        with urlopen(pdf_url) as response:
            cache_path.write_bytes(response.read())

        return cache_path


class FormulaExtractor:
    """Extract LaTeX formulas from PDF."""

    # Common LaTeX math environment patterns
    MATH_PATTERNS: ClassVar[list[str]] = [
        r"\$\$(.+?)\$\$",  # Display math: $$ ... $$
        r"\$(.+?)\$",  # Inline math: $ ... $
        r"\\begin\{equation\*?\}(.+?)\\end\{equation\*?\}",  # equation env
        r"\\begin\{align\*?\}(.+?)\\end\{align\*?\}",  # align env
        r"\\begin\{gather\*?\}(.+?)\\end\{gather\*?\}",  # gather env
    ]

    @staticmethod
    def extract(pdf_path: Path) -> list[ExtractedEquation]:
        """Extract formulas from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of Formula objects with LaTeX, context, and page number
        """
        formulas = []
        formula_counter = 0

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if not text:
                    continue

                # Find all math environments
                for pattern in FormulaExtractor.MATH_PATTERNS:
                    for match in re.finditer(pattern, text, re.DOTALL):
                        latex = match.group(1).strip()

                        # Skip trivial or incomplete formulas
                        if len(latex) < 3 or latex.count("{") != latex.count("}"):
                            continue

                        formula_counter += 1

                        # Extract context (surrounding sentences)
                        start = max(0, match.start() - 200)
                        end = min(len(text), match.end() + 200)
                        context = text[start:end].strip()

                        formulas.append(
                            ExtractedEquation(
                                name=f"eq_{formula_counter}",
                                latex=latex,
                                description="",  # Will be filled by user or Claude
                                page=page_num,
                                context=context,
                            )
                        )

        return formulas

    @staticmethod
    def extract_with_descriptions(
        pdf_path: Path,
        use_claude: bool = False,
    ) -> list[ExtractedEquation]:
        """Extract formulas with auto-generated descriptions.

        Args:
            pdf_path: Path to PDF file
            use_claude: If True, use Claude API to generate descriptions (costs $$)

        Returns:
            List of Formula objects with descriptions
        """
        formulas = FormulaExtractor.extract(pdf_path)

        # Note: use_claude parameter reserved for future enhancement
        # (Claude API integration for auto-description generation)
        # Currently all paths use context-based descriptions

        # Use surrounding context as description
        for formula in formulas:
            # Extract first sentence from context as description
            sentences = formula.context.split(".")
            if sentences:
                formula.description = sentences[0].strip()[:100]

        return formulas


class PresentationBuilder:
    """Build presentation configuration from extracted formulas."""

    @staticmethod
    def build_config(
        paper_metadata: PaperMetadata,
        paper_url: str,
        paper_doi: str | None = None,
    ) -> dict:
        """Build presentation_config.yaml structure from formulas.

        Args:
            paper_metadata: Extracted paper metadata and formulas
            paper_url: Original paper URL (for citation)
            paper_doi: Optional DOI

        Returns:
            Dictionary matching presentation_config.yaml schema
        """
        slides = [
            {
                "title": paper_metadata.title,
                "text": f"**Source:** [{paper_url}]({paper_url})",
                "formulas": [],
            }
        ]

        # One slide per formula
        for i, formula in enumerate(paper_metadata.formulas, 1):
            slide = {
                "title": f"Formula {i}: {formula.description[:50]}",
                "text": f"**Page {formula.page}**\n\n{formula.context}",
                "formulas": [formula.name],
                "notes": f"Extracted from page {formula.page}",
            }
            slides.append(slide)

        config = {
            "title": f"{paper_metadata.title} (Formula Extraction)",
            "format": "talk",
            "backend": "marp",
            "metadata": {
                "author": "Auto-generated from paper",
                "date": "2026",
            },
            "paper_url": paper_url,
            "paper_doi": paper_doi,
            "slides": slides,
        }

        return config

    @staticmethod
    def build_formulas_json(formulas: list[ExtractedEquation]) -> dict:
        """Build formulas.json structure from extracted formulas.

        Args:
            formulas: List of Formula objects

        Returns:
            Dictionary matching formulas.json schema
        """
        formulas_dict = {}
        for formula in formulas:
            formulas_dict[formula.name] = {
                "latex": formula.latex,
                "description": formula.description or "Extracted formula",
                "source_line": formula.page,  # Use page as proxy for line
                "context": formula.context,
            }
        return formulas_dict


if __name__ == "__main__":
    # Quick test
    print("Services module loaded. Run tests with: pytest tests/")
