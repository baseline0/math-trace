"""FastAPI server for formula extraction, browsing, and hardness dashboards.

This package splits routes by responsibility while preserving the public
`math_trace.server` module API used by tests and downstream code.
"""

from __future__ import annotations

import os

# Compatibility: tests monkeypatch `math_trace.server.load_extracted_paper`.
from math_trace.arxiv_extractor import load_extracted_paper

from .app import app, create_app
from .routes_arxiv import arxiv_extract, arxiv_get_paper, fetch_paper
from .routes_formulas import (
    browse_arxiv_papers,
    browse_local_models,
    get_arxiv_equations,
    get_formulas,
    get_local_model_formulas,
    get_preview,
)
from .routes_hardness import (
    hardness_attempts,
    hardness_case,
    hardness_case_attempts,
    hardness_dashboard,
    hardness_report_or_404,
    hardness_summary,
)
from .ui import DASHBOARD_HTML, HARDNESS_HTML

# Compatibility alias used by older tests/imports.
_hardness_report_or_404 = hardness_report_or_404

__all__ = [
    "DASHBOARD_HTML",
    "HARDNESS_HTML",
    "_hardness_report_or_404",
    "app",
    "arxiv_extract",
    "arxiv_get_paper",
    "browse_arxiv_papers",
    "browse_local_models",
    "create_app",
    "fetch_paper",
    "get_arxiv_equations",
    "get_formulas",
    "get_local_model_formulas",
    "get_preview",
    "hardness_attempts",
    "hardness_case",
    "hardness_case_attempts",
    "hardness_dashboard",
    "hardness_report_or_404",
    "hardness_summary",
    "load_extracted_paper",
]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=int(os.environ.get("FLEET_PORT", "8080")),
        reload=True,
    )
