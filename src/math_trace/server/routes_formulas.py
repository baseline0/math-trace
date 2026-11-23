"""Formula browsing endpoints and cached-formula API routes."""

from __future__ import annotations

import html
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from math_trace.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


def _load_extracted_paper(*args, **kwargs):
    from math_trace.server import load_extracted_paper

    return load_extracted_paper(*args, **kwargs)


@router.get("/api/formulas")
async def get_formulas(paper_id: str):
    """Get extracted formulas for a paper.

    Args:
        paper_id: arXiv paper ID

    Returns:
        {"status": "success", "formulas": [{"id": "eq1", "name": "...", "latex": "..."}]}
    """
    try:
        data = _load_extracted_paper(paper_id)
        if not data:
            raise HTTPException(status_code=404, detail=f"No formulas found for {paper_id}")

        formulas = []
        for i, eq in enumerate(data.get("equations", [])):
            formulas.append(
                {
                    "id": f"eq{i}",
                    "name": eq.get("context", "Formula")[:50],
                    "latex": eq.get("latex", ""),
                    "description": eq.get("context", ""),
                    "source_line": i,
                    "source_file": "arxiv",
                }
            )

        return {
            "status": "success",
            "formulas": formulas,
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Formulas not found for {paper_id}") from e
    except Exception as e:
        logger.error(f"Error loading formulas: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/api/preview/{paper_id}/{formula_id}")
async def get_preview(paper_id: str, formula_id: str):
    """Get MathJax preview for a formula."""
    try:
        data = _load_extracted_paper(paper_id)
        if not data:
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

        idx = int(formula_id[2:]) if formula_id.startswith("eq") else int(formula_id)
        equations = data.get("equations", [])

        if idx >= len(equations):
            raise HTTPException(status_code=404, detail=f"Formula {formula_id} not found")

        eq = equations[idx]
        return {
            "status": "success",
            "latex": eq.get("latex", ""),
        }
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found") from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid formula ID") from e
    except Exception as e:
        logger.error(f"Error getting preview: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/api/formulas/arxiv-papers")
async def browse_arxiv_papers(limit: int = 20):
    """List cached arXiv papers as HTML fragment for HTMX."""
    from math_trace.formula_browser import arxiv_papers

    try:
        papers = arxiv_papers(limit=limit)
    except Exception as e:
        logger.error(f"Error listing papers: {e}")
        return HTMLResponse('<p style="color: #999;">Unable to load papers. Please try again.</p>')

    if not papers:
        return HTMLResponse(
            '<p style="color: #999;">No cached papers found. Use POST /api/arxiv/extract to download one.</p>'
        )

    html_parts = ['<div style="display: flex; flex-direction: column; gap: 6px;">']
    for paper in papers:
        safe_paper_id = html.escape(str(paper["paper_id"]), quote=True)
        safe_title = html.escape(str(paper["title"][:50]))

        html_parts.append(f"""
        <div style="padding: 8px; background: #f5f5f5; border-radius: 4px; cursor: pointer;"
             hx-get="/api/formulas/arxiv/{safe_paper_id}/equations"
             hx-target="#formula-browser-equations"
             hx-swap="innerHTML">
            <div style="font-weight: 500; font-size: 12px;">{safe_title}</div>
            <div style="font-size: 11px; color: #666;">{safe_paper_id} • {paper["total_equations"]} eq • {paper["converted_equations"]} ✅</div>
        </div>
        """)
    html_parts.append("</div>")

    response = HTMLResponse("".join(html_parts))
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@router.get("/api/formulas/local-models")
async def browse_local_models(pattern: str = "*/src/model.py", root: str = "."):
    """Find local Python model files with FORMULAS dict (HTML for HTMX)."""
    from math_trace.formula_browser import local_models

    try:
        models = local_models(pattern=pattern, root=root)
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return HTMLResponse('<p style="color: #999;">Unable to load models. Please try again.</p>')

    if not models:
        return HTMLResponse(
            '<p style="color: #999;">No model.py files found matching pattern. Try exploring examples/*/src/model.py</p>'
        )

    html_parts = ['<div style="display: flex; flex-direction: column; gap: 6px;">']
    for model in models:
        safe_path = html.escape(str(model["path"]), quote=True)
        safe_path_display = html.escape(str(model["path"]))

        html_parts.append(f"""
        <div style="padding: 8px; background: #f5f5f5; border-radius: 4px; cursor: pointer;"
             hx-get="/api/formulas/local/{safe_path}/equations"
             hx-target="#formula-browser-equations"
             hx-swap="innerHTML">
            <div style="font-weight: 500; font-size: 12px;">🐍 {safe_path_display}</div>
            <div style="font-size: 11px; color: #666;">{model["formula_count"]} formulas</div>
        </div>
        """)
    html_parts.append("</div>")

    response = HTMLResponse("".join(html_parts))
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@router.get("/api/formulas/arxiv/{paper_id}/equations")
async def get_arxiv_equations(paper_id: str):
    """Get equations from cached arXiv paper (HTML for HTMX)."""
    from math_trace.formula_browser import arxiv_equations

    try:
        result = arxiv_equations(paper_id)
        equations = result["equations"]

        safe_title = html.escape(str(result.get("title", "Unknown"))[:40])
        safe_authors = html.escape(str(result.get("authors", "Unknown"))[:50])

        html_parts = [
            f'<div style="padding: 8px;"><strong>{safe_title}</strong><br>',
            f'<span style="font-size: 11px; color: #666;">{safe_authors}</span>',
            '<div style="margin-top: 8px; display: flex; flex-direction: column; gap: 4px;">',
        ]

        for eq in equations[:10]:  # Show first 10
            status_icon = "✅" if eq.get("sympy_expr") else "⏳"
            latex_preview = html.escape(eq["latex"][:40].replace("{", "").replace("}", ""))
            eq_name = html.escape(str(eq.get("name", eq.get("index", "unknown"))), quote=True)
            latex_json = json.dumps(eq["latex"]).replace('"', "&quot;")

            html_parts.append(f"""
            <button style="text-align: left; padding: 6px; background: white; border: 1px solid #ddd; border-radius: 3px; cursor: pointer; font-size: 11px;"
                    onclick="window.insertFormula('{eq_name}', {latex_json})">
                {status_icon} {latex_preview}...
            </button>
            """)

        if len(equations) > 10:
            html_parts.append(f'<p style="font-size: 11px; color: #999;">... and {len(equations) - 10} more</p>')

        html_parts.append("</div></div>")

        response = HTMLResponse("".join(html_parts))
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    except Exception as e:
        logger.error(f"Error getting equations for {paper_id}: {e}")
        return HTMLResponse('<p style="color: #d32f2f;">Unable to load equations. Please try again.</p>')


@router.get("/api/formulas/local/{path:path}/equations")
async def get_local_model_formulas(path: str):
    """Extract formulas from local model.py file (HTML for HTMX)."""
    from math_trace.formula_browser import local_model_formulas

    try:
        result = local_model_formulas(path)
        if result.get("error"):
            logger.warning(f"Error loading formulas from {path}: {result['error']}")
            return HTMLResponse('<p style="color: #d32f2f;">Unable to load formulas from this file.</p>')

        formulas = result["formulas"]
        safe_path = html.escape(str(path))

        html_parts = [
            f'<div style="padding: 8px;"><strong>{safe_path}</strong>',
            '<div style="margin-top: 8px; display: flex; flex-direction: column; gap: 4px;">',
        ]

        for formula in formulas:
            latex_preview = html.escape(formula["latex"][:40] if formula["latex"] else "[error]")
            formula_name = html.escape(formula["name"], quote=True)
            latex_json = json.dumps(formula["latex"]).replace('"', "&quot;")

            html_parts.append(f"""
            <button style="text-align: left; padding: 6px; background: white; border: 1px solid #ddd; border-radius: 3px; cursor: pointer; font-size: 11px;"
                    onclick="window.insertFormula('{formula_name}', {latex_json})">
                {html.escape(formula["name"])}: {latex_preview}...
            </button>
            """)

        html_parts.append("</div></div>")

        response = HTMLResponse("".join(html_parts))
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    except Exception as e:
        logger.error(f"Error loading formulas from {path}: {e}")
        return HTMLResponse('<p style="color: #d32f2f;">Unable to load formulas from this file.</p>')
