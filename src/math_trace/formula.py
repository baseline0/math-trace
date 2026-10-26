"""Standardized formula representation and abstraction layer.

## Architecture: Pluggable Formula Backends

The Formula abstraction is designed to survive dependency maintenance risks by
decoupling formula definition from export and publishing. This module defines
the contract that all formula representations must implement.

## Design Principle: Swap-friendly Abstractions

Currently math-trace uses SymPy for symbolic mathematics. However, if SymPy
becomes unmaintained, we can swap it for an alternative (e.g., MathBox) without
rewriting the entire codebase.

**The Pipeline:**
    Source Formula → Export to LaTeX → Typst Conversion → PDF Publishing → Lean (optional)

Each stage is independent. If any library becomes problematic, we can swap its
implementation while keeping the rest of the pipeline unchanged.

## Currently Implemented

- **Formula Definition Layer:** SymPy (Python symbolic math)
  - All formulas are SymPy expressions
  - Exported as LaTeX via sp.latex()

- **Export Layer:** Regex-based LaTeX→Typst conversion (see exporters.py)
  - Converts LaTeX syntax to Typst syntax
  - Plugin-based for future alternatives

- **Publishing Layer:** Typst compiler (see publishers.py)
  - Currently uses Typst for PDF generation
  - Fallback to pdflatex available

## To Swap Libraries (e.g., SymPy → MathBox)

1. Implement a new Formula subclass that matches this interface
2. Update examples/*/model.py to use the new class
3. Rest of pipeline unchanged (still exports LaTeX)

Example:
    class MathBoxFormula(Formula):
        def __init__(self, expr):
            self.expr = expr
            self.latex = expr.to_latex()  # Provide LaTeX for downstream

See Also:
    - generators.py: SymPyToTypst (swap if Typst syntax changes)
    - publishers.py: Publisher interface (swap if Typst becomes unmaintained)
    - examples/*/build_paper.py: Orchestration (unchanged when swapping)
"""

import sys
from dataclasses import asdict, dataclass
from types import FrameType

# Frames from this file and from the dataclass-generated __init__ (compiled from "<string>") are skipped when
# locating the code that built the formula.
_INTERNAL_FILENAMES = frozenset({__file__, "<string>"})


@dataclass
class Formula:
    """Standardized representation of a mathematical formula.

    All templates should export formulas using this dataclass.
    This ensures consistent structure, verification metadata, and test coverage.

    The Formula dataclass is a simple contract: it holds the formula's
    LaTeX representation and metadata. The actual computation engine
    (SymPy, MathBox, etc.) is abstracted away—downstream code only
    cares that to_dict() returns valid LaTeX.

    This design enables swapping formula sources without touching the
    export/publish pipeline (see module docstring for examples).
    """

    name: str
    """Unique identifier (e.g., 'schrodinger', 'michaelis_menten')"""

    latex: str
    """LaTeX representation (from sp.latex() or manual LaTeX string)"""

    description: str
    """Human-readable description of the formula"""

    source_line: int | None = None
    """Line in model.py where the Formula( call starts. Left out, it is captured from the calling code."""

    assumptions: str = ""
    """Mathematical assumptions (e.g., 'assumes n ≥ 0')"""

    units: str = ""
    """Physical units (e.g., 'm/s', 'dimensionless')"""

    verified: bool = False
    """Whether formula has been manually reviewed and tested"""

    def __post_init__(self) -> None:
        """Record the line that constructed this formula, so no line number is typed by hand."""
        if self.source_line is None:
            self.source_line = _caller_line()

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return asdict(self)


def _caller_line() -> int:
    """Line of the first frame outside this module and the generated __init__ (the code that wrote Formula(...))."""
    frame: FrameType | None = sys._getframe(1)
    while frame is not None and frame.f_code.co_filename in _INTERNAL_FILENAMES:
        frame = frame.f_back
    if frame is None:
        raise RuntimeError("Formula was built outside any calling code, so it has no source line")
    return frame.f_lineno


def formula_to_json_dict(formula: Formula) -> dict:
    """Convert Formula to JSON-compatible dictionary.

    Filters out verification metadata (kept for validation, not distribution).

    Returns:
        Dict with name, latex, description, source_line, assumptions, units
    """
    return {
        "latex": formula.latex,
        "description": formula.description,
        "source_line": formula.source_line,
        "assumptions": formula.assumptions,
        "units": formula.units,
    }
