"""JSONL IO for formula records."""

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
