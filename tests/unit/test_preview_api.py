"""Tests for live preview API to prevent regression.

Ensures:
- /api/preview returns JSON (not raw HTML)
- Response contains required fields: status, html
- HTML content is valid
- Error cases return proper error messages
"""

import json

import pytest
from fastapi.testclient import TestClient

from math_trace.server import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestPreviewAPI:
    """Test /api/preview endpoint."""

    def test_preview_returns_json_not_html(self, client):
        """Verify API returns JSON response, not raw HTML."""
        formulas = {
            "rate": {
                "name": "Rate Law",
                "latex": r"k \binom{n}{2}",
                "description": "Collision rate",
                "source_line": 42,
            }
        }
        config = {"title": "Test Presentation"}

        response = client.post(
            "/api/preview",
            json={"formulas": formulas, "config": config},
        )

        # Should return JSON, not HTML
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        # Parse JSON to verify it's valid
        data = response.json()
        assert isinstance(data, dict)

    def test_preview_response_structure(self, client):
        """Verify response has required fields."""
        formulas = {
            "eq": {
                "name": "Equation",
                "latex": "x^2 + y^2 = z^2",
                "description": "Pythagorean",
                "source_line": 1,
            }
        }

        response = client.post("/api/preview", json={"formulas": formulas})

        data = response.json()
        assert "status" in data, "Response missing 'status' field"
        assert "html" in data or "message" in data, "Response missing 'html' or 'message'"

        if data["status"] == "success":
            assert "html" in data, "Success response missing 'html'"
            assert isinstance(data["html"], str), "'html' should be a string"
            assert "<!DOCTYPE html>" in data["html"], "html should be valid HTML"
            assert "Revealjs" in data["html"], "html should use Revealjs"

    def test_preview_html_contains_revealjs_not_marp(self, client):
        """Regression test: ensure HTML uses Revealjs, not Marp."""
        formulas = {
            "test": {
                "name": "Test",
                "latex": "e=mc^2",
                "description": "Energy",
                "source_line": 1,
            }
        }

        response = client.post("/api/preview", json={"formulas": formulas})
        data = response.json()

        assert data["status"] == "success"
        html = data["html"]

        # Must use Revealjs
        assert "reveal.js" in html or "Reveal" in html, "HTML should use Revealjs"

        # Must NOT use Marp
        assert "marp: true" not in html, "HTML should not contain 'marp: true'"
        assert 'class="reveal"' in html, "HTML should have Revealjs reveal class"

    def test_preview_error_no_formulas(self, client):
        """Test error response when formulas missing."""
        response = client.post(
            "/api/preview",
            json={"formulas": {}, "config": {"title": "Empty"}},
        )

        data = response.json()
        assert data["status"] == "error"
        assert "message" in data
        assert "formulas" in data["message"].lower()

    def test_preview_returns_json_on_error(self, client):
        """Regression test: errors should return JSON, not HTML error page."""
        # Invalid formulas format (string instead of dict)
        response = client.post(
            "/api/preview",
            json={"formulas": "invalid"},
        )

        # FastAPI returns 422 for validation errors (correct behavior)
        assert response.status_code == 422
        assert response.headers["content-type"] == "application/json"

        data = response.json()
        assert "detail" in data  # FastAPI's validation error format
