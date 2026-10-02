"""Formula export layer: Convert formulas to publishing formats.

## Architecture: Pluggable Export Backends

This module defines the abstraction for exporting formulas from their native
representation (currently SymPy) to interchange formats (LaTeX, MathML, etc.).

## Design Principle: Swap-friendly Converters

If Typst's math syntax changes, we can implement a new converter without
touching formula definitions or the publishing layer.

## Current Implementation

- **LatexToTypstConverter:** Regex-based conversion from LaTeX to Typst
  - Handles common math markup transformations
  - Could be replaced with a proper LaTeX parser if needed

## To Swap Converters (e.g., LaTeX → MathML)

1. Implement a new Converter class with convert(content: str) -> str
2. Update the export pipeline in build_paper.py to use the new converter
3. All formula sources continue to work (they export to the interchange format)

Example:
    class LatexToMathMLConverter:
        def convert(self, latex_str: str) -> str:
            # Parse LaTeX and generate MathML
            return mathml_str

See Also:
    - formula.py: Formula abstraction (pluggable source)
    - publishers.py: Publisher abstraction (pluggable output)
    - examples/*/build_paper.py: Orchestration
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod


class Converter(ABC):
    """Base class for format converters.

    Converts formula representations from one format to another.
    Subclasses implement specific conversion rules.
    """

    @abstractmethod
    def convert(self, content: str) -> str:
        """Convert content from source format to target format.

        Args:
            content: Source format string

        Returns:
            Converted content in target format
        """
        pass


class LatexToTypstConverter(Converter):
    """Converts LaTeX math syntax to Typst markup.

    MIGRATION PATH: If Typst's math syntax changes significantly, replace this
    converter with an updated version. All formula definitions continue to work.

    Current implementation uses regex-based replacements for common patterns.
    Future implementation could use a proper LaTeX parser for robustness.

    Examples:
        \\frac{a}{b} → a / b
        x^2 → x^2 (Typst uses same syntax)
        \\alpha → α (Unicode substitution)
    """

    def convert(self, latex: str) -> str:
        """Convert LaTeX to Typst markup.

        Args:
            latex: LaTeX math string

        Returns:
            Typst-compatible math string
        """
        result = latex

        # Common substitutions
        substitutions = {
            r"\\frac{([^}]*)}{([^}]*)}" : r"\1 / \2",
            r"\\sqrt{([^}]*)}" : r"sqrt(\1)",
            r"\\alpha": "α",
            r"\\beta": "β",
            r"\\gamma": "γ",
            r"\\delta": "δ",
            r"\\epsilon": "ε",
            r"\\lambda": "λ",
            r"\\mu": "μ",
            r"\\pi": "π",
            r"\\sigma": "σ",
        }

        for latex_pattern, typst_replacement in substitutions.items():
            result = re.sub(latex_pattern, typst_replacement, result)

        return result


class LatexExporter:
    """Base class for LaTeX-based exports.

    Generates LaTeX from formulas, agnostic to the formula source.
    Works with any Formula representation that provides to_dict().
    """

    def export(self, formulas: dict[str, "Formula"]) -> str:  # noqa: F821
        """Export formulas to LaTeX.

        Args:
            formulas: Dict mapping formula names to Formula objects

        Returns:
            LaTeX document content
        """
        lines = []
        for name, formula in formulas.items():
            lines.append(f"% {name}")
            lines.append(f"${formula.latex}$")
            lines.append("")
        return "\n".join(lines)
