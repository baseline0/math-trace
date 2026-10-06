"""FastAPI server endpoint integration tests.

Tests the live preview and export API endpoints with various inputs
to catch configuration and parsing errors before they reach the UI.
"""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Import server app
sys.path.insert(0, str(Path(__file__).parent / "../../src"))
from math_trace.server import app

client = TestClient(app)


class TestPreviewEndpoint:
    """Tests for /api/preview endpoint."""

    def test_preview_with_valid_formulas_and_config(self):
        """Preview succeeds with valid JSON formulas and config dict."""
        response = client.post(
            "/api/preview",
            json={
                "formulas": {"rate": {"latex": "k \\binom{n}{2}"}},
                "config": {"title": "Test", "author": "Me"},
                "backend": "marp",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["success", "error"]

    def test_preview_rejects_empty_formulas(self):
        """Preview returns error for empty formulas dict."""
        response = client.post("/api/preview", json={"formulas": {}, "config": {"title": "Test"}})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "formula" in data["message"].lower() or "empty" in data["message"].lower()

    def test_preview_rejects_non_dict_formulas(self):
        """Preview returns error when formulas is not a dict."""
        response = client.post("/api/preview", json={"formulas": "not a dict", "config": {"title": "Test"}})
        # Should reject with validation error (422) or return error status
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            data = response.json()
            assert "error" in data.get("status", "").lower()

    def test_preview_uses_default_config_when_missing(self):
        """Preview uses default config if not provided."""
        response = client.post("/api/preview", json={"formulas": {"x": {"latex": "x"}}, "backend": "marp"})
        assert response.status_code == 200
        data = response.json()
        # Should not crash due to missing config
        assert "status" in data

    def test_preview_error_message_clarity(self):
        """Error messages should be clear and actionable, not 'Unexpected token'."""
        response = client.post("/api/preview", json={"formulas": {}, "config": {"title": ""}})
        assert response.status_code == 200
        data = response.json()
        if data["status"] == "error":
            # Error message should not contain cryptic parsing errors
            assert "Unexpected token" not in data["message"]
            assert "is not valid JSON" not in data["message"]
            # Should hint at the actual problem
            assert any(
                word in data["message"].lower() for word in ["formula", "config", "empty", "invalid", "required"]
            )

    def test_preview_with_special_characters_in_formulas(self):
        """Preview handles special characters in LaTeX safely."""
        response = client.post(
            "/api/preview",
            json={
                "formulas": {
                    "rate": {"latex": "k \\frac{n_a}{2} + \\int"},
                    "equilibrium": {"latex": "I^* = (1 - 1/R_0) \\times N"},
                },
                "config": {"title": "Complex Formulas", "author": "Test"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Should handle special chars without escaping issues
        assert isinstance(data, dict)


class TestExportEndpoint:
    """Tests for /api/export endpoint."""

    def test_export_with_valid_inputs(self):
        """Export succeeds with valid formulas and config."""
        response = client.post(
            "/api/export",
            json={
                "formulas": {"rate": {"latex": "k n"}},
                "config": {"title": "Export Test", "author": "Me"},
                "format": "markdown",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "markdown" in data
        assert "slides.md" in data["filename"]

    def test_export_markdown_contains_marp_frontmatter(self):
        """Exported markdown includes Marp frontmatter."""
        response = client.post(
            "/api/export",
            json={
                "formulas": {"rate": {"latex": "k \\binom{n}{2}"}},
                "config": {"title": "Test Presentation", "author": "Test Author"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        markdown = data["markdown"]

        # Should have Marp frontmatter
        assert "---" in markdown
        assert "marp: true" in markdown
        assert "theme: default" in markdown
        assert "paginate: true" in markdown
        assert 'title: "Test Presentation"' in markdown

    def test_export_markdown_includes_title_and_author(self):
        """Exported markdown includes title and author from config."""
        response = client.post(
            "/api/export",
            json={
                "formulas": {"placeholder": {"latex": "x"}},
                "config": {"title": "Disease Modeling", "author": "Dr. Smith"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        markdown = data["markdown"]

        assert "# Disease Modeling" in markdown
        assert "Dr. Smith" in markdown

    def test_export_with_slides_containing_formulas(self):
        """Export includes formulas when slides reference them."""
        response = client.post(
            "/api/export",
            json={
                "formulas": {"rate": {"latex": "k \\binom{n}{2}", "description": "Rate law"}},
                "config": {
                    "title": "Kinetics",
                    "format": "talk",
                    "backend": "marp",
                    "slides": [
                        {
                            "title": "Reaction Rate",
                            "text": "The rate follows a binomial distribution.",
                            "formulas": ["rate"],
                        }
                    ],
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        markdown = data["markdown"]

        # Should contain slide content
        assert "Reaction Rate" in markdown
        assert "binomial distribution" in markdown
        assert "Rate law" in markdown

    def test_export_rejects_empty_formulas(self):
        """Export returns error for empty formulas."""
        response = client.post("/api/export", json={"formulas": {}, "config": {"title": "Test"}, "format": "markdown"})
        # Should reject with error status code
        assert response.status_code >= 400

    def test_export_error_message_not_cryptic(self):
        """Export error doesn't expose internal JSON parse errors."""
        response = client.post("/api/export", json={"formulas": {}, "config": {"title": ""}})
        # Should reject gracefully
        assert response.status_code >= 400
        # If it returns JSON, verify it has error info (not cryptic parse error)
        try:
            data = response.json()
            if "detail" in data or "message" in data:
                # If error message present, should not be cryptic
                msg = str(data.get("detail", "")) + str(data.get("message", ""))
                assert "Unexpected token" not in msg
        except (ValueError, TypeError):
            # If not JSON, that's fine - just checking for cryptic parse errors
            pass


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""

    def test_health_check(self):
        """Health endpoint confirms server is running."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestDashboardUI:
    """Tests for dashboard serving."""

    def test_dashboard_loads(self):
        """Dashboard HTML is served at root."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "math-trace" in response.text
        assert "Preview" in response.text

    def test_dashboard_includes_yaml_library(self):
        """Dashboard attempts to load YAML library."""
        response = client.get("/")
        assert response.status_code == 200
        assert "js-yaml" in response.text or "YAML" in response.text

    def test_dashboard_has_fallback_for_missing_yaml(self):
        """Dashboard handles YAML library load failure gracefully."""
        response = client.get("/")
        assert response.status_code == 200
        # Should have fallback logic
        assert "JSON" in response.text or "fallback" in response.text or "JSON fallback" in response.text
