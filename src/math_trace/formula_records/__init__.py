"""Normalized, stable records for mathematical formulas mined from papers or sources.

Public API preserved for downstream callers and tests.
"""

from .builder import build_formula_record, build_records_from_tex
from .io import read_records_jsonl, records_to_jsonl, write_records_jsonl
from .models import FormulaRecord, FormulaSource
from .normalize import extract_display_formulas, normalize_latex, stable_record_id
from .tags import infer_concept_tags

__all__ = [
    "FormulaRecord",
    "FormulaSource",
    "build_formula_record",
    "build_records_from_tex",
    "extract_display_formulas",
    "infer_concept_tags",
    "normalize_latex",
    "read_records_jsonl",
    "records_to_jsonl",
    "stable_record_id",
    "write_records_jsonl",
]
