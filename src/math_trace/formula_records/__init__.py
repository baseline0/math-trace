"""Normalized, stable records for mathematical formulas mined from papers or sources.

Public API preserved for downstream callers and tests.

## Specification Map

| Rule or Invariant | Authority | Enforcement |
|---|---|---|
| `FormulaRecord`/`FormulaSource` are frozen dataclasses; `to_dict()` round-trips through `from_dict()` for known fields | formula record data contract | `models.FormulaRecord.to_dict/from_dict`; `tests/unit/test_formula_records.py::test_build_records_from_tex_and_roundtrip`, `test_read_records_jsonl_ignores_blank_lines` |
| `from_dict` ignores unknown source keys and applies defaults for missing optional fields (forward-compatible read) | compatibility contract | `models.FormulaRecord.from_dict`; `tests/unit/test_formula_records.py::test_formula_record_from_dict_ignores_unknown_source_keys_and_defaults` |
| `stable_record_id` is deterministic SHA-256-based (`sha256:` + 16 hex chars) over identifying parts | record identity contract | `normalize.stable_record_id`; `tests/unit/test_formula_records.py::test_stable_record_id_deterministic` |
| `normalize_latex` is best-effort: never raises; returns `(ok, canonical_srepr, expr_hash, sympy_str, parse_error)`; empty body -> `empty` error | normalization contract | `normalize.normalize_latex`; `tests/unit/test_formula_records.py::test_normalize_best_effort`, `test_normalize_empty_and_unparsed` |
| Display-formula extraction returns `(line, env, latex, start, end)` for display math blocks | extraction contract | `normalize.extract_display_formulas`; `tests/unit/test_formula_records.py::test_extract_display_formulas` |
| Record builder preserves raw LaTeX/source metadata, infers concept tags when not supplied, and normalizes best-effort | builder contract | `builder.build_formula_record/build_records_from_tex`; `tests/unit/test_formula_records.py::test_build_record_preserves_raw_and_tags`, `test_build_records_from_tex_and_roundtrip` |
| JSONL IO writes sorted-key deterministic lines, skips blank lines on read, and creates parent dirs on write | IO contract | `io.records_to_jsonl/write_records_jsonl/read_records_jsonl`; `tests/unit/test_formula_records.py::test_build_records_from_tex_and_roundtrip`, `test_read_records_jsonl_ignores_blank_lines` |
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
