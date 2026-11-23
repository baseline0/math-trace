"""Presentation build/config service."""

from __future__ import annotations

from .extractor import ExtractedEquation, PaperMetadata


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
