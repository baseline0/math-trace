"""
math-trace: Formula-to-code traceability for publication-quality mathematical documents.

Write publication-quality papers where every equation links back to code.

Quick start:

    from math_trace import SymPyToTypst
    import sympy as sp

    # Define your formula
    x = sp.Symbol('x', real=True)
    formula = x**2 + 2*x + 1

    # Convert to Typst
    converter = SymPyToTypst()
    typst_code = converter.convert(formula)
    print(typst_code)  # Ready for your paper

For more examples, see:
- examples/membrane-dynamics/ for a complete working example
- docs/getting-started-external.md for a quick start guide
- tests/ for usage patterns
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Mark Alexiuk"
__license__ = "MIT"

from .generators import SymPyToTypst, TypstEnvironmentBuilder
from .presentation_generator import (
    PresentationBackend,
    PresentationConfig,
    PresentationGenerator,
)
from .services import (
    ExtractedEquation,
    FormulaExtractor,
    PaperDownloader,
    PaperMetadata,
    PresentationBuilder,
)

# Backward compatibility alias
Formula = ExtractedEquation

__all__ = [
    # Generators
    "SymPyToTypst",
    "TypstEnvironmentBuilder",
    # Presentation
    "PresentationGenerator",
    "PresentationBackend",
    "PresentationConfig",
    # Services
    "PaperDownloader",
    "FormulaExtractor",
    "PresentationBuilder",
    "PaperMetadata",
    "Formula",
]
