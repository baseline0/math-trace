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

__version__ = "0.1.0"
__author__ = "Mark Alexiuk"
__license__ = "MIT"

from .generators import SymPyToTypst, TypstEnvironmentBuilder

__all__ = [
    "SymPyToTypst",
    "TypstEnvironmentBuilder",
]
