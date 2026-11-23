"""Formula extraction service."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

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
