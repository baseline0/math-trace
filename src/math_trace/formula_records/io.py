"""JSONL IO for formula records.

## Specification Map

| Rule or Invariant | Authority | Enforcement |
|---|---|---|
| JSONL output is deterministic: one sorted-key JSON object per line, UTF-8, trailing newline | IO contract | `records_to_jsonl`, `write_records_jsonl`; `tests/unit/test_formula_records.py::test_build_records_from_tex_and_roundtrip` |
| `write_records_jsonl` creates parent directories | IO contract | `write_records_jsonl`; `tests/unit/test_formula_records.py::test_build_records_from_tex_and_roundtrip` |
| `read_records_jsonl` ignores blank lines and parses each line via `FormulaRecord.from_dict` | IO contract | `read_records_jsonl`; `tests/unit/test_formula_records.py::test_read_records_jsonl_ignores_blank_lines` |
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from .models import FormulaRecord


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
