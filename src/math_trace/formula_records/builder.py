"""Record construction from LaTeX/TeX sources."""

from __future__ import annotations

import re
from collections.abc import Iterable

from .models import FormulaRecord, FormulaSource
from .normalize import _bare_body, extract_display_formulas, normalize_latex, stable_record_id
from .tags import infer_concept_tags


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
