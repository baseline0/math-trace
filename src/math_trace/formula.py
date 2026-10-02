"""Standardized formula representation for math-trace templates.

Provides a dataclass contract for all formulas exported by model.py files.
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Formula:
    """Standardized representation of a mathematical formula.

    All templates should export formulas using this dataclass.
    This ensures consistent structure, verification metadata, and test coverage.
    """

    name: str
    """Unique identifier (e.g., 'schrodinger', 'michaelis_menten')"""

    latex: str
    """LaTeX representation (from sp.latex() or manual LaTeX string)"""

    description: str
    """Human-readable description of the formula"""

    source_line: int
    """Line number in model.py where this formula is defined"""

    assumptions: str = ""
    """Mathematical assumptions (e.g., 'assumes n ≥ 0')"""

    units: str = ""
    """Physical units (e.g., 'm/s', 'dimensionless')"""

    verified: bool = False
    """Whether formula has been manually reviewed and tested"""

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return asdict(self)


def formula_to_json_dict(formula: Formula) -> dict:
    """Convert Formula to JSON-compatible dictionary.

    Filters out verification metadata (kept for validation, not distribution).

    Returns:
        Dict with name, latex, description, source_line, assumptions, units
    """
    return {
        'latex': formula.latex,
        'description': formula.description,
        'source_line': formula.source_line,
        'assumptions': formula.assumptions,
        'units': formula.units,
    }
