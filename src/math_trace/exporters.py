"""Formula export layer: Convert formulas to publishing formats.

## Architecture: Pluggable Export Backends

This module defines the abstraction for exporting formulas from their native
representation (currently SymPy) to interchange formats (LaTeX, MathML, etc.).

## Design Principle: Swap-friendly Converters

If Typst's math syntax changes, we can implement a new converter without
touching formula definitions or the publishing layer.

## Current Implementation

- No LaTeX-to-Typst converter lives here. The production converter is `SymPyToTypst` in `generators.py`.

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

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .formula import Formula


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


class LatexExporter:
    """Base class for LaTeX-based exports.

    Generates LaTeX from formulas, agnostic to the formula source.
    Works with any Formula representation that provides to_dict().
    """

    def export(self, formulas: dict[str, Formula]) -> str:
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
