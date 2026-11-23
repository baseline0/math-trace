"""Datamodels for formula records."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


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
