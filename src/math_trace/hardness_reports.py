"""Read-only adapters for lean-hardness-probe reports.

math-trace does not own the probe's generated telemetry.  This module only
reads the JSON/JSONL reports produced by ``lean-hardness-probe`` and presents
them for validation and publication workflows.
"""

from __future__ import annotations

import dataclasses
import json
import os
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .constants import REPO_ROOT

__all__ = [
    "HardnessAttempt",
    "HardnessCase",
    "HardnessReport",
    "load_hardness",
    "resolve_probe_root",
]


@dataclass(frozen=True)
class HardnessAttempt:
    case_id: str
    target_name: str
    script: str
    status: str
    exit_code: int | None
    friction: str
    elapsed_ms: float | None
    proof_steps: int | None
    tactic_hits: int | None
    backtracks: int | None
    branches: int | None
    goals: int | None
    goals_before: int | None
    goals_text: tuple[str, ...]
    goals_before_text: tuple[str, ...]
    error_message: str


@dataclass(frozen=True)
class HardnessCase:
    case_id: str
    lean_files: int
    stubs: int
    targets: tuple[str, ...]
    mean_elapsed_ms: float
    max_branches: int
    max_backtracks: int
    mean_proof_steps: float
    mean_tactic_hits: float
    frictions: dict[str, int]
    attempts: dict[str, int]
    attempt_frictions: dict[str, int]
    attempt_records: tuple[HardnessAttempt, ...]

    @property
    def attempt_count(self) -> int:
        return len(self.attempt_records)

    @property
    def friction_mix(self) -> str:
        return ", ".join(f"{kind}:{count}" for kind, count in sorted(self.frictions.items()))


@dataclass(frozen=True)
class HardnessReport:
    root: Path
    cases: tuple[HardnessCase, ...]
    total_stubs: int
    total_telemetry_records: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "probeRoot": str(self.root),
            "totalStubs": self.total_stubs,
            "totalTelemetryRecords": self.total_telemetry_records,
            "cases": [dataclasses.asdict(case) for case in self.cases],
        }


def resolve_probe_root(root: str | Path | None = None) -> Path:
    """Resolve the lean-hardness-probe repository root.

    An explicit argument wins, followed by ``LEAN_HARDNESS_PROBE_ROOT``.  The
    default is the sibling checkout used by this workspace.
    """

    if root is not None:
        candidate = Path(root).expanduser()
    else:
        env_root = os.environ.get("LEAN_HARDNESS_PROBE_ROOT")
        candidate = Path(env_root).expanduser() if env_root else REPO_ROOT.parent / "lean-hardness-probe"
    return candidate.resolve(strict=False)


def _optional_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _optional_float(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _string_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in value if item is not None)


def _count_mapping(value: Any) -> dict[str, int]:
    if not isinstance(value, Mapping):
        return {}
    result: dict[str, int] = {}
    for key, count in value.items():
        if isinstance(count, bool) or not isinstance(count, int):
            continue
        result[str(key)] = count
    return result


def _parse_attempt(record: Mapping[str, Any], fallback_case: str) -> HardnessAttempt:
    case_id = str(record.get("caseId") or fallback_case)
    exit_code = _optional_int(record.get("exitCode"))
    return HardnessAttempt(
        case_id=case_id,
        target_name=str(record.get("targetName") or ""),
        script=str(record.get("script") or ""),
        status=str(record.get("status") or "unknown"),
        exit_code=exit_code,
        friction=str(record.get("friction") or "unknown"),
        elapsed_ms=_optional_float(record.get("elapsedMs")),
        proof_steps=_optional_int(record.get("proofSteps")),
        tactic_hits=_optional_int(record.get("tacticHits")),
        backtracks=_optional_int(record.get("backtracks")),
        branches=_optional_int(record.get("branches")),
        goals=_optional_int(record.get("goals")),
        goals_before=_optional_int(record.get("goalsBefore")),
        goals_text=_string_tuple(record.get("goalsText")),
        goals_before_text=_string_tuple(record.get("goalsBeforeText")),
        error_message=str(record.get("errorMessage") or ""),
    )


def _load_attempts(root: Path) -> dict[str, list[HardnessAttempt]]:
    attempts_dir = root / "reports" / "attempts"
    by_case: dict[str, list[HardnessAttempt]] = defaultdict(list)
    if not attempts_dir.is_dir():
        return by_case
    for path in sorted(attempts_dir.glob("*.jsonl")):
        fallback_case = path.stem
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            if not raw_line.strip():
                continue
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, Mapping):
                continue
            attempt = _parse_attempt(record, fallback_case)
            by_case[attempt.case_id].append(attempt)
    return by_case


def _case_from_summary(case_id: str, raw: Mapping[str, Any], attempts: list[HardnessAttempt]) -> HardnessCase:
    targets_raw = raw.get("targets")
    targets = tuple(sorted(str(item) for item in targets_raw)) if isinstance(targets_raw, list) else ()
    return HardnessCase(
        case_id=case_id,
        lean_files=int(raw.get("leanFiles") or 0),
        stubs=int(raw.get("stubs") or 0),
        targets=targets,
        mean_elapsed_ms=float(raw.get("meanElapsedMs") or 0.0),
        max_branches=int(raw.get("maxBranches") or 0),
        max_backtracks=int(raw.get("maxBacktracks") or 0),
        mean_proof_steps=float(raw.get("meanProofSteps") or 0.0),
        mean_tactic_hits=float(raw.get("meanTacticHits") or 0.0),
        frictions=_count_mapping(raw.get("frictions")),
        attempts=_count_mapping(raw.get("attempts")),
        attempt_frictions=_count_mapping(raw.get("attemptFrictions")),
        attempt_records=tuple(attempts),
    )


def load_hardness(root: str | Path | None = None) -> HardnessReport:
    """Load a read-only hardness report from a probe repository root."""

    resolved_root = resolve_probe_root(root)
    summary_path = resolved_root / "reports" / "summary.json"
    if not summary_path.is_file():
        raise FileNotFoundError(f"hardness summary not found: {summary_path}")

    try:
        summary_data = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid hardness summary: {summary_path}") from exc
    if not isinstance(summary_data, Mapping):
        raise ValueError(f"hardness summary must be a JSON object: {summary_path}")

    attempts_by_case = _load_attempts(resolved_root)
    cases: list[HardnessCase] = []
    for case_id, raw in summary_data.items():
        if not isinstance(raw, Mapping):
            continue
        attempts = attempts_by_case.pop(str(case_id), [])
        cases.append(_case_from_summary(str(case_id), raw, attempts))

    # Preserve attempt-only cases so a stale summary cannot hide telemetry.
    for case_id, attempts in sorted(attempts_by_case.items()):
        cases.append(
            _case_from_summary(
                case_id,
                {},
                attempts,
            )
        )

    cases.sort(key=lambda case: case.case_id)
    total_stubs = sum(case.stubs for case in cases)
    total_records = sum(case.attempt_count for case in cases)
    return HardnessReport(
        root=resolved_root,
        cases=tuple(cases),
        total_stubs=total_stubs,
        total_telemetry_records=total_records,
    )
