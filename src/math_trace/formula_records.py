"""Normalized, stable records for mathematical formulas mined from papers or sources.

Design Intent:
- A record captures raw TeX/LaTeX, its source location and context, and a best-effort
  canonical symbolic identity (SymPy srepr/hash) when the expression can be parsed.
- Normalization is best-effort: many publication formulas contain macros, alignments,
  text, or constructs latex2sympy2 cannot parse. Such cases are recorded with
  ``normalized``/``canonical_srepr``/``expr_hash`` unset and a ``parse_error`` instead
  of failing the whole extraction.
- Records are JSON-serializable and stable (sorted keys, explicit fields) so downstream
  tools (tool-lit-review, tool-rag) can diff and index them.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import sympy as sp

from .equation_identity import canonical_srepr, expr_hash

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


@dataclass(frozen=True)
class FormulaSource:
    """Where a formula came from."""

    paper_id: str | None = None
    arxiv_id: str | None = None
    path: str | None = None
    file: str | None = None
    line: int | None = None
    env: str | None = None
    url: str | None = None
    licence: str | None = None
    source_sha256: str | None = None


@dataclass(frozen=True)
class FormulaRecord:
    """One formula with raw TeX, context, and optional normalized symbolic identity."""

    record_id: str
    latex: str
    source: FormulaSource
    context: str = ""
    concept_tags: tuple[str, ...] = ()
    normalized: bool = False
    canonical_srepr: str | None = None
    expr_hash: str | None = None
    sympy_str: str | None = None
    parse_error: str | None = None
    schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["concept_tags"] = list(self.concept_tags)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FormulaRecord:
        source_data = data.get("source") or {}
        allowed = {k: v for k, v in source_data.items() if k in FormulaSource.__annotations__}
        return cls(
            record_id=str(data["record_id"]),
            latex=str(data.get("latex", "")),
            source=FormulaSource(**allowed),
            context=str(data.get("context", "")),
            concept_tags=tuple(data.get("concept_tags") or ()),
            normalized=bool(data.get("normalized", False)),
            canonical_srepr=data.get("canonical_srepr"),
            expr_hash=data.get("expr_hash"),
            sympy_str=data.get("sympy_str"),
            parse_error=data.get("parse_error"),
            schema_version=int(data.get("schema_version", 1)),
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


_INFO_THEORY_PATTERNS: dict[str, tuple[str, ...]] = {
    "entropy": (r"\bH\s*[\(\[]", r"\\mathbb\{H\}", r"\\mathrm\{H\}", r"entropy"),
    "mutual_information": (r"\bI\s*[\(\[]", r"mutual.?information"),
    "kl_divergence": (r"\bD\s*[\(\[]", r"D_\{?KL\}?", r"\\mathrm\{KL\}", r"divergence"),
    "conditional_entropy": (r"H\s*\([^)]*\|", r"conditional.?entropy"),
    "chain_rule": (r"H\s*\([^,]+,\s*[^)]+\)", r"chain.?rule"),
    "data_processing": (r"\bDPI\b", r"data.?processing"),
    "pinsker": (r"Pinsker", r"total.?variation", r"\\|[^|]+\\|_1"),
    "fano": (r"Fano", r"P_e"),
    "markov": (r"Markov", r"\\to"),
    "jensen": (r"Jensen", r"concav", r"convex"),
    "log_sum_inequality": (r"log.?sum", r"\\log\s*\\frac"),
}


def infer_concept_tags(latex: str, context: str = "") -> tuple[str, ...]:
    """Heuristic concept tags for information-theoretic formulas (best-effort)."""
    hay = f"{latex}\n{context}"
    tags = [name for name, pats in _INFO_THEORY_PATTERNS.items() if any(re.search(p, hay, re.IGNORECASE) for p in pats)]
    return tuple(sorted(set(tags)))


def build_formula_record(
    latex: str,
    *,
    paper_id: str | None = None,
    arxiv_id: str | None = None,
    path: str | None = None,
    file: str | None = None,
    line: int | None = None,
    env: str | None = None,
    context: str = "",
    url: str | None = None,
    licence: str | None = None,
    source_sha256: str | None = None,
    concept_tags: Iterable[str] | None = None,
    record_id: str | None = None,
) -> FormulaRecord:
    """Build a normalized FormulaRecord from raw LaTeX and source metadata."""
    normalized, cs, h, sstr, err = normalize_latex(latex)
    tags = tuple(sorted(set(concept_tags))) if concept_tags is not None else infer_concept_tags(latex, context)
    rid = record_id or stable_record_id(paper_id or arxiv_id, file or path, str(line), _bare_body(latex))
    source = FormulaSource(
        paper_id=paper_id,
        arxiv_id=arxiv_id,
        path=path,
        file=file,
        line=line,
        env=env,
        url=url,
        licence=licence,
        source_sha256=source_sha256,
    )
    return FormulaRecord(
        record_id=rid,
        latex=latex,
        source=source,
        context=context,
        concept_tags=tags,
        normalized=normalized,
        canonical_srepr=cs,
        expr_hash=h,
        sympy_str=sstr,
        parse_error=err,
    )


def extract_display_formulas(tex: str) -> list[tuple[int, str, str, int, int]]:
    """Return (line, env, latex, start, end) for each display formula in TeX text."""
    results: list[tuple[int, str, str, int, int]] = []
    for m in _DISPLAY_BLOCK.finditer(tex):
        start, end = m.span("block")
        line = tex.count("\n", 0, start) + 1
        env = m.group("name") or ("bracket" if tex[start:].startswith(r"\[") else "dollar")
        results.append((line, env, m.group("block"), start, end))
    return results


def build_records_from_tex(
    tex: str,
    *,
    paper_id: str | None = None,
    arxiv_id: str | None = None,
    file: str | None = None,
    path: str | None = None,
    url: str | None = None,
    licence: str | None = None,
    source_sha256: str | None = None,
    context_chars: int = 240,
) -> list[FormulaRecord]:
    """Extract display formulas from TeX and build normalized records."""
    records: list[FormulaRecord] = []
    for line, env, latex, start, end in extract_display_formulas(tex):
        ctx_start = max(0, start - context_chars)
        ctx_end = min(len(tex), end + context_chars)
        context = re.sub(r"\s+", " ", tex[ctx_start:ctx_end]).strip()
        records.append(
            build_formula_record(
                latex,
                paper_id=paper_id,
                arxiv_id=arxiv_id,
                path=path,
                file=file,
                line=line,
                env=env,
                context=context,
                url=url,
                licence=licence,
                source_sha256=source_sha256,
            )
        )
    return records


def records_to_jsonl(records: Iterable[FormulaRecord]) -> str:
    return "".join(json.dumps(r.to_dict(), sort_keys=True, ensure_ascii=False) + "\n" for r in records)


def write_records_jsonl(records: Iterable[FormulaRecord], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(records_to_jsonl(records), encoding="utf-8")
    return output


def read_records_jsonl(path: Path) -> list[FormulaRecord]:
    records: list[FormulaRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        records.append(FormulaRecord.from_dict(json.loads(line)))
    return records
