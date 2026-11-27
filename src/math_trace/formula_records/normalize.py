"""Normalization and display-formula extraction helpers.

## Specification Map

| Rule or Invariant | Authority | Enforcement |
|---|---|---|
| `normalize_latex` is best-effort and never raises; empty body returns `(False,None,None,None,"empty")` | normalization contract | `normalize_latex`; `tests/unit/test_formula_records.py::test_normalize_best_effort`, `test_normalize_empty_and_unparsed` |
| Successful normalization returns canonical srepr and `sha256:` expr hash | identity contract | `normalize_latex`, `math_trace.equation_identity`; `tests/unit/test_formula_records.py::test_normalize_best_effort` |
| `stable_record_id` is deterministic `sha256:` + 16 hex chars from identifying parts | record identity contract | `stable_record_id`; `tests/unit/test_formula_records.py::test_stable_record_id_deterministic` |
| `extract_display_formulas` returns `(line, env, latex, start, end)` for display blocks | extraction contract | `extract_display_formulas`; `tests/unit/test_formula_records.py::test_extract_display_formulas` |
"""

from __future__ import annotations

import hashlib
import re

import sympy as sp

from math_trace.equation_identity import canonical_srepr, expr_hash

# Display environments and wrappers treated as the equation body.
_DISPLAY_BEGIN = re.compile(r"\\begin\{(equation|align|gather|multline|eqnarray|displaymath|split|aligned)\*?\}")
_DISPLAY_END = re.compile(r"\\end\{(equation|align|gather|multline|eqnarray|displaymath|split|aligned)\*?\}")
_LABEL_RE = re.compile(r"\\label\{[^}]*\}")
_TAG_RE = re.compile(r"\\tag\{[^}]*\}")
_NUMBERING_RE = re.compile(r"\\nonumber|\\notag")

# Common macros/constructs that confuse latex2sympy2 but are safe to simplify for a
# canonical math attempt (best-effort; original latex is always preserved).
_TEXT_RE = re.compile(r"\\(?:text|mbox|operatorname|mathrm|mathit|mathbf)\{([^{}]*)\}")
_SPACING_RE = re.compile(r"\\[,;!:]|\\quad|\\qquad|\\,")
_DISPLAY_BLOCK = re.compile(
    r"(?P<block>\\begin\{(?P<name>equation|align|gather|multline|eqnarray|displaymath|split|aligned)\*?\}.*?\\end\{(?P=name)\*?\}|\\\[.*?\\\]|\$\$.*?\$\$)",
    re.DOTALL,
)


def _bare_body(latex: str) -> str:
    """Strip display wrappers, labels/tags/numbering, and collapse whitespace for parsing."""
    text = latex.strip()
    text = _DISPLAY_BEGIN.sub("", text)
    text = _DISPLAY_END.sub("", text)
    if text.startswith(r"\[") and text.endswith(r"\]"):
        text = text[2:-2]
    if text.startswith(r"\(") and text.endswith(r"\)"):
        text = text[2:-2]
    if text.startswith("$$") and text.endswith("$$") and len(text) >= 4:
        text = text[2:-2]
    if text.startswith("$") and text.endswith("$") and len(text) > 1:
        text = text[1:-1]
    text = _LABEL_RE.sub("", text)
    text = _TAG_RE.sub("", text)
    text = _NUMBERING_RE.sub("", text)
    text = _SPACING_RE.sub(" ", text)
    text = _TEXT_RE.sub(r" \1 ", text)
    text = text.replace("&", " ").replace(r"\\", " ")
    return re.sub(r"\s+", " ", text).strip()


def _try_latex2sympy(body: str) -> sp.Basic | None:
    """Best-effort parse via latex2sympy2; returns None on any failure."""
    try:
        from latex2sympy2 import latex2sympy
    except Exception:
        return None
    try:
        expr = latex2sympy(body)
    except Exception:
        return None
    if not isinstance(expr, sp.Basic):
        try:
            expr = sp.sympify(expr)
        except Exception:
            return None
    return expr


def normalize_latex(latex: str) -> tuple[bool, str | None, str | None, str | None, str | None]:
    """Return (normalized, canonical_srepr, expr_hash, sympy_str, parse_error) for LaTeX."""
    body = _bare_body(latex)
    if not body:
        return False, None, None, None, "empty"
    try:
        expr = _try_latex2sympy(body)
        if expr is None:
            raise ValueError("unparsed")
        cs = canonical_srepr(expr)
        return True, cs, expr_hash(expr), str(expr), None
    except Exception as exc:
        return False, None, None, None, f"{type(exc).__name__}: {exc}"


def stable_record_id(*parts: str | None) -> str:
    """Deterministic short id from source-identifying parts."""
    material = "\n".join("" if p is None else str(p) for p in parts)
    return "sha256:" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def extract_display_formulas(tex: str) -> list[tuple[int, str, str, int, int]]:
    """Return (line, env, latex, start, end) for each display formula in TeX text."""
    results: list[tuple[int, str, str, int, int]] = []
    for m in _DISPLAY_BLOCK.finditer(tex):
        start, end = m.span("block")
        line = tex.count("\n", 0, start) + 1
        env = m.group("name") or ("bracket" if tex[start:].startswith(r"\[") else "dollar")
        results.append((line, env, m.group("block"), start, end))
    return results
