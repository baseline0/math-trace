"""Regression tests: server error paths build ApiResponse.error without TypeError.

The server's error handlers once passed ``error=...`` as a keyword, which the
``ApiResponse.error(error_msg, message=None, code=400)`` signature does not
accept. These tests run the real handlers and assert the response body.
"""

import asyncio

import pytest

from math_trace import server


def test_arxiv_extract_invalid_id_returns_error_body() -> None:
    """An unparseable arXiv ID takes the ValueError path and returns the error body."""
    body = asyncio.run(server.arxiv_extract("not-an-arxiv-id"))

    assert body["status"] == "error"
    assert body["error"] == "Invalid arXiv ID format"
    assert "not-an-arxiv-id" in body["message"]


def test_arxiv_get_paper_not_cached_returns_error_body(monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing cache entry takes the FileNotFoundError path and returns the 404 body."""

    def _missing(paper_id: str, cache_dir=None) -> dict:
        raise FileNotFoundError(paper_id)

    monkeypatch.setattr(server, "load_extracted_paper", _missing)

    body = asyncio.run(server.arxiv_get_paper("2301.13848"))

    assert body == {
        "status": "error",
        "error": "Paper not cached",
        "message": "No cached data for 2301.13848",
    }


def test_arxiv_get_paper_unexpected_failure_returns_error_body(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unexpected failure takes the generic Exception path and returns the 500 body."""

    def _broken(paper_id: str, cache_dir=None) -> dict:
        raise RuntimeError("corrupt cache file")

    monkeypatch.setattr(server, "load_extracted_paper", _broken)

    body = asyncio.run(server.arxiv_get_paper("2301.13848"))

    assert body == {
        "status": "error",
        "error": "Error loading paper",
        "message": "corrupt cache file",
    }
