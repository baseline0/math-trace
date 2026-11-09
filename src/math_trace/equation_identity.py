"""Stable identity for an equation: a symbolic name, a hash of its canonical expression, and where it lives in code.

The hash is taken over the SymPy expression, not over source text. Operand order, spacing, comments and docstrings do
not change it; a change to the mathematics does. A source location is recorded for provenance, but it is not part of
the identity, so moving a function does not invalidate a citation.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import sympy as sp


def canonical_srepr(expr: sp.Basic | str) -> str:
    """The canonical text of a SymPy expression. Built-in canonicalisation orders commutative operands."""
    sym = sp.sympify(expr) if isinstance(expr, str) else expr
    return sp.srepr(sym)


def expr_hash(expr: sp.Basic | str) -> str:
    """'sha256:<hex>' over the canonical text of the expression."""
    digest = hashlib.sha256(canonical_srepr(expr).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


@dataclass(frozen=True)
class EquationId:
    """The identity of one equation as cited by a paper."""

    name: str
    expr_hash: str
    source_file: str
    function: str | None
    line: int | None
    commit: str | None

    @classmethod
    def from_expr(
        cls,
        name: str,
        expr: sp.Basic | str,
        source_file: str,
        function: str | None = None,
        line: int | None = None,
        commit: str | None = None,
    ) -> EquationId:
        return cls(name, expr_hash(expr), source_file, function, line, commit)

    def matches(self, expr: sp.Basic | str) -> bool:
        """True when the expression still has the recorded hash, whatever its source text."""
        return expr_hash(expr) == self.expr_hash
