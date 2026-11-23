"""Characterization tests for formula routes (API + browser fragments)."""

from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException

from math_trace.server import routes_formulas_api, routes_formulas_browser


def test_get_formulas_returns_mapped_equations(monkeypatch):
    monkeypatch.setattr(
        routes_formulas_api,
        "_load_extracted_paper",
        lambda paper_id: {
            "equations": [
                {"latex": "E=mc^2", "context": "Energy mass equivalence"},
                {"latex": "a^2+b^2=c^2", "context": "Pythagorean theorem"},
            ]
        },
    )

    body = asyncio.run(routes_formulas_api.get_formulas("2609.21904"))

    assert body["status"] == "success"
    assert body["formulas"][0] == {
        "id": "eq0",
        "name": "Energy mass equivalence",
        "latex": "E=mc^2",
        "description": "Energy mass equivalence",
        "source_line": 0,
        "source_file": "arxiv",
    }
    assert body["formulas"][1]["id"] == "eq1"


def test_get_formulas_missing_paper_raises_404(monkeypatch):
    monkeypatch.setattr(routes_formulas_api, "_load_extracted_paper", lambda paper_id: None)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(routes_formulas_api.get_formulas("missing"))

    # Characterization: current handler catches HTTPException in broad except
    # and remaps to a 500 with the original detail string.
    assert exc.value.status_code == 500
    assert "404" in str(exc.value.detail)
    assert "No formulas found for missing" in str(exc.value.detail)


def test_get_formulas_file_not_found_maps_to_404(monkeypatch):
    def _missing(_paper_id):
        raise FileNotFoundError("missing")

    monkeypatch.setattr(routes_formulas_api, "_load_extracted_paper", _missing)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(routes_formulas_api.get_formulas("missing"))

    assert exc.value.status_code == 404


def test_get_preview_returns_latex(monkeypatch):
    monkeypatch.setattr(
        routes_formulas_api,
        "_load_extracted_paper",
        lambda paper_id: {"equations": [{"latex": "x+y"}, {"latex": "a=b"}]},
    )

    body = asyncio.run(routes_formulas_api.get_preview("2609.21904", "eq1"))

    assert body == {"status": "success", "latex": "a=b"}


def test_get_preview_invalid_id_returns_400(monkeypatch):
    monkeypatch.setattr(
        routes_formulas_api,
        "_load_extracted_paper",
        lambda paper_id: {"equations": [{"latex": "x+y"}]},
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(routes_formulas_api.get_preview("2609.21904", "bad"))

    assert exc.value.status_code == 400


def test_get_preview_out_of_range_returns_404(monkeypatch):
    monkeypatch.setattr(
        routes_formulas_api,
        "_load_extracted_paper",
        lambda paper_id: {"equations": [{"latex": "x+y"}]},
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(routes_formulas_api.get_preview("2609.21904", "eq2"))

    assert exc.value.status_code == 404


def test_browse_arxiv_papers_renders_fragment(monkeypatch):
    monkeypatch.setattr(
        "math_trace.formula_browser.arxiv_papers",
        lambda limit=20: [
            {
                "paper_id": "2609.21904",
                "title": "A <Test> Paper",
                "total_equations": 3,
                "converted_equations": 2,
            }
        ],
    )

    resp = asyncio.run(routes_formulas_browser.browse_arxiv_papers())

    assert resp.status_code == 200
    assert "A &lt;Test&gt; Paper" in bytes(resp.body).decode()
    assert "/api/formulas/arxiv/2609.21904/equations" in bytes(resp.body).decode()


def test_browse_arxiv_papers_empty(monkeypatch):
    monkeypatch.setattr("math_trace.formula_browser.arxiv_papers", lambda limit=20: [])

    resp = asyncio.run(routes_formulas_browser.browse_arxiv_papers())

    assert "No cached papers found" in bytes(resp.body).decode()


def test_browse_local_models_renders_fragment(monkeypatch):
    monkeypatch.setattr(
        "math_trace.formula_browser.local_models",
        lambda pattern="*/src/model.py", root=".": [{"path": "examples/sir/src/model.py", "formula_count": 2}],
    )

    resp = asyncio.run(routes_formulas_browser.browse_local_models())

    body = bytes(resp.body).decode()
    assert "examples/sir/src/model.py" in body
    assert "2 formulas" in body


def test_get_arxiv_equations_renders_buttons(monkeypatch):
    monkeypatch.setattr(
        "math_trace.formula_browser.arxiv_equations",
        lambda paper_id: {
            "title": "Paper",
            "authors": "Author",
            "equations": [{"name": "eq1", "latex": "x+y", "sympy_expr": "x+y"}],
        },
    )

    resp = asyncio.run(routes_formulas_browser.get_arxiv_equations("2609.21904"))

    body = bytes(resp.body).decode()
    assert "window.insertFormula" in body
    assert "x+y" in body


def test_get_local_model_formulas_error_renders_message(monkeypatch):
    monkeypatch.setattr(
        "math_trace.formula_browser.local_model_formulas",
        lambda path: {"error": "bad file", "formulas": []},
    )

    resp = asyncio.run(routes_formulas_browser.get_local_model_formulas("bad.py"))

    assert "Unable to load formulas from this file." in bytes(resp.body).decode()


def test_get_local_model_formulas_renders_formulas(monkeypatch):
    monkeypatch.setattr(
        "math_trace.formula_browser.local_model_formulas",
        lambda path: {"error": None, "formulas": [{"name": "f1", "latex": "E=mc^2"}]},
    )

    resp = asyncio.run(routes_formulas_browser.get_local_model_formulas("model.py"))

    body = bytes(resp.body).decode()
    assert "f1" in body
    assert "E=mc^2" in body
