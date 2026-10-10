"""Integration tests for complete arXiv formula extraction workflow.

Tests the full flow: fetch paper → extract formulas → load → preview.
"""

import sys

import pytest
from fastapi.testclient import TestClient

from math_trace.constants import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "src"))
from math_trace.server import app

client = TestClient(app)


class TestFetchPaperEndpoint:
    """Tests for POST /api/fetch-paper endpoint."""

    def test_fetch_paper_with_arxiv_id(self):
        """Fetch succeeds with valid arXiv ID."""
        response = client.post("/api/fetch-paper?url=2401.12345")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["paper_id"] == "2401.12345"
        assert data["count"] > 0

    def test_fetch_paper_with_full_url(self):
        """Fetch succeeds with full arXiv URL."""
        response = client.post("/api/fetch-paper?url=https://arxiv.org/abs/2401.12345")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["paper_id"] == "2401.12345"

    def test_fetch_paper_with_arxiv_url_variant(self):
        """Fetch succeeds with arxiv.org/pdf variant."""
        response = client.post("/api/fetch-paper?url=https://arxiv.org/pdf/2401.12345.pdf")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_fetch_paper_invalid_id_returns_error(self):
        """Fetch with invalid ID returns 400 error."""
        response = client.post("/api/fetch-paper?url=invalid-id-xyz")
        assert response.status_code == 400

    def test_fetch_paper_missing_url_returns_error(self):
        """Fetch without URL parameter returns error."""
        response = client.post("/api/fetch-paper")
        assert response.status_code >= 400

    def test_fetch_paper_returns_formula_count(self):
        """Fetch response includes count of extracted formulas."""
        response = client.post("/api/fetch-paper?url=2401.12345")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["count"], int)
        assert data["count"] > 0


class TestGetFormulasEndpoint:
    """Tests for GET /api/formulas endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Fetch a paper before each test."""
        client.post("/api/fetch-paper?url=2401.12345")

    def test_get_formulas_returns_array(self):
        """Formulas endpoint returns array of formulas."""
        response = client.get("/api/formulas?paper_id=2401.12345")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["formulas"], list)
        assert len(data["formulas"]) > 0

    def test_formula_has_required_fields(self):
        """Each formula includes required fields."""
        response = client.get("/api/formulas?paper_id=2401.12345")
        data = response.json()
        assert len(data["formulas"]) > 0

        formula = data["formulas"][0]
        assert "id" in formula
        assert "name" in formula
        assert "latex" in formula
        assert "description" in formula
        assert "source_line" in formula
        assert "source_file" in formula

    def test_formula_latex_is_valid_string(self):
        """Formula latex field contains valid LaTeX."""
        response = client.get("/api/formulas?paper_id=2401.12345")
        data = response.json()

        for formula in data["formulas"]:
            assert isinstance(formula["latex"], str)
            assert len(formula["latex"]) > 0
            # Should contain LaTeX markers or math operators
            assert any(char in formula["latex"] for char in ["\\", "^", "_", "{", "}"])

    def test_formula_id_format(self):
        """Formula IDs follow expected format (eq0, eq1, etc)."""
        response = client.get("/api/formulas?paper_id=2401.12345")
        data = response.json()

        for i, formula in enumerate(data["formulas"]):
            assert formula["id"] == f"eq{i}"

    def test_get_formulas_missing_paper_returns_404(self):
        """Formulas for nonexistent paper returns 404."""
        response = client.get("/api/formulas?paper_id=nonexistent")
        assert response.status_code == 404

    def test_get_formulas_missing_paper_id_param_returns_error(self):
        """Formulas without paper_id parameter returns error."""
        response = client.get("/api/formulas")
        assert response.status_code >= 400


class TestPreviewEndpoint:
    """Tests for GET /api/preview/{paper_id}/{formula_id} endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Fetch a paper before each test."""
        resp = client.post("/api/fetch-paper?url=2401.12345")
        assert resp.status_code == 200

    def test_preview_returns_latex(self):
        """Preview endpoint returns LaTeX for formula."""
        response = client.get("/api/preview/2401.12345/eq0")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "latex" in data
        assert isinstance(data["latex"], str)
        assert len(data["latex"]) > 0

    def test_preview_with_different_formula_ids(self):
        """Preview works for different formula IDs."""
        for idx in range(3):
            response = client.get(f"/api/preview/2401.12345/eq{idx}")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert len(data["latex"]) > 0

    def test_preview_with_numeric_id(self):
        """Preview accepts numeric formula ID."""
        response = client.get("/api/preview/2401.12345/0")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_preview_invalid_formula_id_returns_404(self):
        """Preview with invalid formula ID returns 404."""
        response = client.get("/api/preview/2401.12345/eq999")
        assert response.status_code == 404

    def test_preview_nonexistent_paper_returns_404(self):
        """Preview for nonexistent paper returns 404."""
        response = client.get("/api/preview/nonexistent/eq0")
        assert response.status_code == 404

    def test_preview_invalid_id_format_returns_error(self):
        """Preview with malformed ID returns error."""
        response = client.get("/api/preview/2401.12345/invalid")
        assert response.status_code >= 400


class TestCompleteWorkflow:
    """Integration tests for complete extraction workflow."""

    def test_fetch_extract_load_navigate(self):
        """Complete workflow: fetch → extract → load → navigate."""
        # 1. Fetch paper and extract formulas
        fetch_resp = client.post("/api/fetch-paper?url=2401.12345")
        assert fetch_resp.status_code == 200
        fetch_data = fetch_resp.json()
        paper_id = fetch_data["paper_id"]
        formula_count = fetch_data["count"]
        assert formula_count > 0

        # 2. Load formulas
        load_resp = client.get(f"/api/formulas?paper_id={paper_id}")
        assert load_resp.status_code == 200
        load_data = load_resp.json()
        formulas = load_data["formulas"]
        assert len(formulas) == formula_count

        # 3. Navigate through formulas and preview
        for _i, formula in enumerate(formulas[:5]):  # Test first 5
            preview_resp = client.get(f"/api/preview/{paper_id}/{formula['id']}")
            assert preview_resp.status_code == 200
            preview_data = preview_resp.json()
            assert preview_data["status"] == "success"
            assert len(preview_data["latex"]) > 0

    def test_multiple_papers_can_coexist(self):
        """Multiple papers can be fetched and accessed independently."""
        # Fetch the same paper twice (tests caching)
        resp1 = client.post("/api/fetch-paper?url=2401.12345")
        resp2 = client.post("/api/fetch-paper?url=2401.12345")

        assert resp1.status_code == 200
        assert resp2.status_code == 200

        data1 = resp1.json()
        data2 = resp2.json()

        # Load both
        load1 = client.get(f"/api/formulas?paper_id={data1['paper_id']}")
        load2 = client.get(f"/api/formulas?paper_id={data2['paper_id']}")

        assert load1.status_code == 200
        assert load2.status_code == 200

        # They should have the same formulas (same paper)
        formulas1 = load1.json()["formulas"]
        formulas2 = load2.json()["formulas"]
        assert formulas1
        assert formulas2
        assert len(formulas1) == len(formulas2)

    def test_formula_data_consistency(self):
        """Formula data is consistent across endpoints."""
        # Fetch and load
        client.post("/api/fetch-paper?url=2401.12345")
        load_resp = client.get("/api/formulas?paper_id=2401.12345")
        formulas = load_resp.json()["formulas"]

        # For each formula, preview should match
        for formula in formulas[:3]:
            preview_resp = client.get(f"/api/preview/2401.12345/{formula['id']}")
            preview_latex = preview_resp.json()["latex"]

            # Preview LaTeX should match formula LaTeX
            assert preview_latex == formula["latex"]


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
    """Tests for dashboard HTML serving."""

    def test_dashboard_loads(self):
        """Dashboard HTML is served at root."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "math-trace" in response.text
        assert "Formula Extractor" in response.text

    def test_dashboard_has_arxiv_input(self):
        """Dashboard includes arXiv URL input field."""
        response = client.get("/")
        assert response.status_code == 200
        assert "arxiv-url" in response.text
        assert "https://arxiv.org/abs/" in response.text

    def test_dashboard_has_two_column_layout(self):
        """Dashboard includes two-column layout structure."""
        response = client.get("/")
        assert response.status_code == 200
        assert "left-panel" in response.text
        assert "right-panel" in response.text
        assert "Formula JSON" in response.text or "json-display" in response.text

    def test_dashboard_includes_mathjax(self):
        """Dashboard loads MathJax for rendering LaTeX."""
        response = client.get("/")
        assert response.status_code == 200
        assert "mathjax" in response.text.lower()

    def test_dashboard_includes_navigation(self):
        """Dashboard includes formula navigation controls."""
        response = client.get("/")
        assert response.status_code == 200
        assert "prevFormula" in response.text or "prev" in response.text.lower()
        assert "nextFormula" in response.text or "next" in response.text.lower()

    def test_dashboard_includes_fetch_button(self):
        """Dashboard includes fetch/download button."""
        response = client.get("/")
        assert response.status_code == 200
        assert "fetch" in response.text.lower() or "download" in response.text.lower()
