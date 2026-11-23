"""Read-only Lean hardness probe endpoints."""

from __future__ import annotations

import dataclasses

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from math_trace.hardness_reports import HardnessReport, load_hardness, resolve_probe_root

from .ui import HARDNESS_HTML

router = APIRouter()


def hardness_report_or_404(root: str | None = None) -> HardnessReport:
    resolved = resolve_probe_root(root)
    try:
        return load_hardness(resolved)
    except (FileNotFoundError, ValueError, OSError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/api/hardness/summary")
async def hardness_summary(root: str | None = None):
    """Read-only summary of lean-hardness-probe telemetry."""

    report = hardness_report_or_404(root)
    return {
        "status": "success",
        **report.to_dict(),
    }


@router.get("/api/hardness/cases/{case_id}")
async def hardness_case(case_id: str, root: str | None = None):
    """Read one case and its attempt records."""

    report = hardness_report_or_404(root)
    for case in report.cases:
        if case.case_id == case_id:
            return {"status": "success", "case": dataclasses.asdict(case)}
    raise HTTPException(status_code=404, detail=f"unknown hardness case: {case_id}")


@router.get("/api/hardness/attempts")
async def hardness_attempts(root: str | None = None):
    """Read all attempt records, optionally filtered by case."""

    report = hardness_report_or_404(root)
    attempts = [dataclasses.asdict(attempt) for case in report.cases for attempt in case.attempt_records]
    return {"status": "success", "attempts": attempts}


@router.get("/api/hardness/attempts/{case_id}")
async def hardness_case_attempts(case_id: str, root: str | None = None):
    """Read attempt records for one case."""

    report = hardness_report_or_404(root)
    for case in report.cases:
        if case.case_id == case_id:
            return {
                "status": "success",
                "caseId": case_id,
                "attempts": [dataclasses.asdict(attempt) for attempt in case.attempt_records],
            }
    raise HTTPException(status_code=404, detail=f"unknown hardness case: {case_id}")


@router.get("/hardness", response_class=HTMLResponse)
async def hardness_dashboard(root: str | None = None):
    """Serve the read-only lean-hardness-probe validation dashboard."""

    hardness_report_or_404(root)
    return HARDNESS_HTML
