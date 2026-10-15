"""Computable companion for the Sidorenko-style Turán density reference.

A theorem has no simulation, so this reference's "model" stage evaluates the claimed gap
1 - c_r / m^((r-1)/r) exactly, for r in {3, 4, 5} and m in 1..10, and writes the table to
generated/gap_table.json. The constant is transcribed from `paperConstant` and `paperGap` in the
Lean statement recorded in lean_statement.lean. Arithmetic is symbolic (sympy), and only the
decimal rendering is rounded, so the table is deterministic.

This checks the arithmetic of the displayed constant. It does not check that the Lean statement
matches the paper's claim; that is the Comparator check recorded in formalization.json.
"""

import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "generated" / "gap_table.json"
RANKS = (3, 4, 5)
EDGE_COUNTS = tuple(range(1, 11))
DIGITS = 30


def paper_constant(r: int) -> sp.Expr:
    """c_r = (1 / (4 r^2)) (4/r)^(1/r) (1 - 1/r)^(2 - 2/r), as in Lean's paperConstant."""
    r_ = sp.Integer(r)
    return (
        sp.Rational(1, 4)
        / r_**2
        * (sp.Integer(4) / r_) ** (sp.Integer(1) / r_)
        * (1 - sp.Integer(1) / r_) ** (2 - sp.Integer(2) / r_)
    )


def paper_gap(r: int, m: int) -> sp.Expr:
    """The claimed gap c_r / m^((r-1)/r), as in Lean's paperGap."""
    return paper_constant(r) / sp.Integer(m) ** (sp.Rational(r - 1, r))


def build_rows() -> list[dict[str, object]]:
    """One row per (r, m): the exact gap expression and its decimal value."""
    rows: list[dict[str, object]] = []
    for r in RANKS:
        for m in EDGE_COUNTS:
            gap = paper_gap(r, m)
            rows.append(
                {
                    "r": r,
                    "m": m,
                    "gap_exact": sp.srepr(gap),
                    "gap_decimal": str(sp.N(gap, DIGITS)),
                    "turan_density_upper_bound": str(sp.N(1 - gap, DIGITS)),
                }
            )
    return rows


def main() -> None:
    """Write the gap table as sorted, indented JSON."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    table = {
        "source": "lean_statement.lean (paperConstant, paperGap; commit ba6f109)",
        "statement": "turanDensity F <= 1 - paperGap r m for r >= 3, m >= 1",
        "digits": DIGITS,
        "rows": build_rows(),
    }
    OUTPUT.write_text(json.dumps(table, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(HERE)} ({len(table['rows'])} rows)")


if __name__ == "__main__":
    main()
