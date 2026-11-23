"""JSON API routes for cached/extracted formulas."""

from __future__ import annotations

from fastapi import HTTPException

from math_trace.logging import get_logger

logger = get_logger(__name__)


def _load_extracted_paper(*args, **kwargs):
    from math_trace.server import load_extracted_paper

    return load_extracted_paper(*args, **kwargs)


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
