"""Formula browsing and cached-formula API routes.

Compatibility facade: JSON API handlers live in routes_formulas_api, HTMX/HTML
fragment handlers live in routes_formulas_browser. Preserve import paths and
router behavior used by tests and server package exports.
"""

from __future__ import annotations

from fastapi import APIRouter

from .routes_formulas_api import get_formulas, get_preview
from .routes_formulas_browser import (
    browse_arxiv_papers,
    browse_local_models,
    get_arxiv_equations,
    get_local_model_formulas,
)

router = APIRouter()
router.add_api_route("/api/formulas", get_formulas, methods=["GET"])
router.add_api_route("/api/preview/{paper_id}/{formula_id}", get_preview, methods=["GET"])
router.add_api_route("/api/formulas/arxiv-papers", browse_arxiv_papers, methods=["GET"])
router.add_api_route("/api/formulas/local-models", browse_local_models, methods=["GET"])
router.add_api_route("/api/formulas/arxiv/{paper_id}/equations", get_arxiv_equations, methods=["GET"])
router.add_api_route("/api/formulas/local/{path:path}/equations", get_local_model_formulas, methods=["GET"])

__all__ = [
    "browse_arxiv_papers",
    "browse_local_models",
    "get_arxiv_equations",
    "get_formulas",
    "get_local_model_formulas",
    "get_preview",
    "router",
]
