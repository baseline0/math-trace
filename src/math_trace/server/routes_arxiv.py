"""arXiv extraction and cached-paper API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from math_trace.arxiv_extractor import download_and_extract_equations, extract_arxiv_id, save_extracted_paper
from math_trace.logging import get_logger
from math_trace.responses import ApiResponse

logger = get_logger(__name__)
router = APIRouter()


def _load_extracted_paper(*args, **kwargs):
    from math_trace.server import load_extracted_paper

    return load_extracted_paper(*args, **kwargs)


@router.post("/api/fetch-paper")
async def fetch_paper(url: str):
    """Fetch arXiv paper and extract formulas.

    Args:
        url: arXiv URL or paper ID (e.g., "2609.21904" or "https://arxiv.org/abs/2609.21904")

    Returns:
        {"status": "success", "paper_id": "...", "count": 42}
    """
    try:
        paper_id = extract_arxiv_id(url)
        logger.info(f"Fetching paper {paper_id}")

        _tar_path, equations = download_and_extract_equations(paper_id)
        logger.info(f"Extracted {len(equations)} equations from {paper_id}")

        save_extracted_paper(paper_id)

        return {
            "status": "success",
            "paper_id": paper_id,
            "count": len(equations),
        }
    except Exception as e:
        logger.error(f"Error fetching paper: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/api/arxiv/extract")
async def arxiv_extract(paper_url_or_id: str):
    """Extract equations from arXiv paper.

    Takes arXiv URL or ID (e.g., "2301.13848" or "https://arxiv.org/abs/2301.13848")
    Downloads source, extracts equations, saves to cache.

    Returns: ApiResponse with extracted paper data or error message.
    """
    try:
        paper_id = extract_arxiv_id(paper_url_or_id)
        paper_dir = save_extracted_paper(paper_id)
        paper_data = _load_extracted_paper(paper_id)

        return ApiResponse.success(
            data={
                "paper_id": paper_id,
                "title": paper_data["title"],
                "authors": paper_data["authors"],
                "total_equations": paper_data["total_equations"],
                "equations": paper_data["equations"],
                "cache_path": str(paper_dir),
            },
            message=f"Extracted {paper_data['total_equations']} equations. Ready for conversion.",
            code=200,
        ).to_dict()

    except ValueError as e:
        logger.error(f"Invalid arXiv ID: {e}")
        return ApiResponse.error(
            "Invalid arXiv ID format",
            message=str(e),
            code=400,
        ).to_dict()
    except FileNotFoundError as e:
        logger.error(f"Paper not found: {e}")
        return ApiResponse.error(
            "Paper not found in cache",
            message=str(e),
            code=404,
        ).to_dict()
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return ApiResponse.error(
            "Extraction failed",
            message=str(e),
            code=500,
        ).to_dict()


@router.get("/api/arxiv/papers/{paper_id}")
async def arxiv_get_paper(paper_id: str):
    """Get cached extracted paper.

    Returns: ApiResponse with paper data or error message.
    """
    try:
        paper_data = _load_extracted_paper(paper_id)
        return ApiResponse.success(
            data={
                "paper_id": paper_id,
                "title": paper_data["title"],
                "authors": paper_data["authors"],
                "extraction_timestamp": paper_data.get("extraction_timestamp"),
                "total_equations": len(paper_data["equations"]),
                "equations": paper_data["equations"],
            },
            code=200,
        ).to_dict()

    except FileNotFoundError:
        logger.warning(f"Paper not cached: {paper_id}")
        return ApiResponse.error(
            "Paper not cached",
            message=f"No cached data for {paper_id}",
            code=404,
        ).to_dict()

    except Exception as e:
        logger.error(f"Error loading paper {paper_id}: {e}")
        return ApiResponse.error(
            "Error loading paper",
            message=str(e),
            code=500,
        ).to_dict()
