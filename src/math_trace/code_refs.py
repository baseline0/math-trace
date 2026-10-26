"""Resolve code references from equations.json to the line they name.

A template's equations.json points at code in one of two ways. A dict entry gives a ``code_ref`` such as
``model.py:PIDController`` or ``src/scenarios/x.py:damping_ratio()`` and a ``line``. A ``Formula(...)`` entry gives a
``source_line`` only. This module finds the line that each reference names, by parsing the source with ``ast``, so
the recorded numbers can be checked against the code instead of trusted.

A symbol resolves to the line of its ``def`` or ``class`` statement. A dotted symbol such as ``LinearSystem.is_stable()``
descends through nested classes and functions. The parser does not import the code, so the check runs on any template.
"""

from __future__ import annotations

import ast
from pathlib import Path


class CodeRefError(LookupError):
    """A code_ref names a file or symbol that does not exist."""


def symbol_line(source: str, symbol: str) -> int:
    """Line of the def or class statement that ``symbol`` names in ``source``.

    ``symbol`` may end in ``()`` and may be dotted, for example ``"LinearSystem.is_stable()"``.
    Raises CodeRefError when a part of the symbol is not found.
    """
    scope: list[ast.stmt] = ast.parse(source).body
    node: ast.stmt | None = None
    for part in symbol.removesuffix("()").split("."):
        node = next(
            (
                child
                for child in scope
                if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) and child.name == part
            ),
            None,
        )
        if node is None:
            raise CodeRefError(f"no def or class {symbol!r} (missing {part!r})")
        scope = node.body
    assert node is not None  # symbol is non-empty, so the loop ran at least once
    return node.lineno


def formula_call_lines(source: str) -> set[int]:
    """Lines where a ``Formula(...)`` call starts in ``source``."""
    return {
        node.lineno
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Formula"
    }


def resolve_code_ref(template_dir: Path, code_ref: str) -> int:
    """Line that ``code_ref`` names, read from the file it points at.

    The file is looked up beside the template's model (``src/<file>``) and then from the template folder (``<file>``).
    Raises CodeRefError when the reference is malformed, the file is missing, or the symbol is not defined.
    """
    file_part, sep, symbol = code_ref.partition(":")
    if not sep or not symbol:
        raise CodeRefError(f"code_ref {code_ref!r} must look like file.py:Symbol")
    candidates = [template_dir / "src" / file_part, template_dir / file_part]
    path = next((candidate for candidate in candidates if candidate.is_file()), None)
    if path is None:
        raise CodeRefError(f"code_ref {code_ref!r}: no such file under {template_dir.name}")
    return symbol_line(path.read_text(), symbol)
