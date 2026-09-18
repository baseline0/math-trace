"""
math-trace: Formula-to-code traceability for publication-quality mathematical documents.

Provides tools for linking SymPy formulas to Typst papers, Lean formalizations,
and Palomar registry entries.
"""

__version__ = "0.1.0"

from .generators import SymPyToTypst

__all__ = ['SymPyToTypst']
