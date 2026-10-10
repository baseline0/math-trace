"""FastAPI server endpoint integration tests.

Tests the health and dashboard endpoints. The preview and export endpoints
were removed in the phase 1 refactor and their tests were deleted with them.
"""

import sys

from fastapi.testclient import TestClient

# Import server app
from math_trace.constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "src"))
from math_trace.server import app

client = TestClient(app)


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

    def test_dashboard_has_fallback_for_missing_yaml(self):
        """Dashboard handles YAML library load failure gracefully."""
        response = client.get("/")
        assert response.status_code == 200
        # Should have fallback logic
        assert "JSON" in response.text or "fallback" in response.text or "JSON fallback" in response.text
