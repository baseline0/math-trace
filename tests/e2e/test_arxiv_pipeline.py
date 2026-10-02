"""End-to-end arXiv extraction and processing pipeline test.

Tests the full workflow:
1. Download arXiv paper source
2. Extract equations
3. Convert to SymPy
4. Verify cache structure

Uses known fixed paper for reproducibility.
Run on demand: just e2e-test
"""

import json
from pathlib import Path
from typing import Dict, List

import pytest


# Known paper with predictable structure for testing
TEST_PAPER_ID = "2301.13848"
TEST_PAPER_TITLE = "Attention is All You Need"


class TestArxivExtraction:
    """Test arXiv source download and equation extraction."""

    def test_extract_known_paper(self):
        """Download and extract equations from known paper."""
        from math_trace.arxiv_extractor import extract_arxiv_id, download_and_extract_equations

        # Validate ID extraction
        paper_id = extract_arxiv_id(f"https://arxiv.org/abs/{TEST_PAPER_ID}")
        assert paper_id == TEST_PAPER_ID

        # Download and extract
        tex_content, equations = download_and_extract_equations(TEST_PAPER_ID, max_equations=50)

        # Verify we got content
        assert len(tex_content) > 1000, "Should have substantial TeX content"
        assert len(equations) > 0, "Should extract at least some equations"

        # Verify equation structure
        for eq in equations:
            assert eq.latex, "Each equation should have LaTeX"
            assert eq.context, "Each equation should have context"
            assert eq.conversion_status == "pending"

        print(f"✅ Extracted {len(equations)} equations from {TEST_PAPER_ID}")

    def test_equation_structure(self):
        """Verify extracted equations have required fields."""
        from math_trace.arxiv_extractor import download_and_extract_equations, Equation

        tex_content, equations = download_and_extract_equations(TEST_PAPER_ID, max_equations=10)

        assert equations, "Should extract equations"

        for eq in equations:
            assert isinstance(eq, Equation)
            assert eq.index >= 0
            assert len(eq.latex) > 0
            assert len(eq.context) > 0
            assert eq.sympy_expr is None  # Not converted yet
            assert eq.conversion_status == "pending"

    def test_equation_quality(self):
        """Verify extracted equations are meaningful (not just formatting)."""
        from math_trace.arxiv_extractor import download_and_extract_equations

        tex_content, equations = download_and_extract_equations(TEST_PAPER_ID, max_equations=20)

        # Filter for meaningful equations (LaTeX expressions, typically start with \ or contain =)
        meaningful_equations = [
            eq for eq in equations
            if len(eq.latex) > 5 and ('=' in eq.latex or '\\' in eq.latex)
        ]

        assert len(meaningful_equations) > 0, "Should have meaningful equations"
        print(f"✅ Found {len(meaningful_equations)} meaningful equations")


class TestArxivCaching:
    """Test caching of extracted papers."""

    def test_save_and_load_paper(self):
        """Save extracted paper to cache and reload it."""
        from math_trace.arxiv_extractor import save_extracted_paper, load_extracted_paper

        # Save
        paper_dir = save_extracted_paper(TEST_PAPER_ID)
        assert paper_dir.exists()

        # Verify files exist
        assert (paper_dir / "metadata.json").exists()
        assert (paper_dir / "equations.jsonl").exists()

        # Load
        paper_data = load_extracted_paper(TEST_PAPER_ID)

        # Verify structure
        assert paper_data["paper_id"] == TEST_PAPER_ID
        assert "title" in paper_data
        assert "equations" in paper_data
        assert len(paper_data["equations"]) > 0

        print(f"✅ Saved and loaded {len(paper_data['equations'])} equations")

    def test_cache_persistence(self):
        """Verify cached equations persist across loads."""
        from math_trace.arxiv_extractor import load_extracted_paper

        # Load paper (should be in cache from previous test)
        paper1 = load_extracted_paper(TEST_PAPER_ID)
        paper2 = load_extracted_paper(TEST_PAPER_ID)

        # Should be identical
        assert paper1["paper_id"] == paper2["paper_id"]
        assert len(paper1["equations"]) == len(paper2["equations"])
        assert paper1["equations"][0]["latex"] == paper2["equations"][0]["latex"]

        print(f"✅ Cache persistence verified")


class TestSymPyConversion:
    """Test LaTeX to SymPy conversion."""

    @pytest.mark.skip(reason="antlr4 (v4.7.2) incompatible with Python 3.13; upgrade when available")
    def test_direct_conversion(self):
        """Test direct latex2sympy2 conversion on extracted equations."""
        from math_trace.arxiv_extractor import load_extracted_paper
        from math_trace.ollama_arxiv_worker import convert_equation_to_sympy

        paper_data = load_extracted_paper(TEST_PAPER_ID)
        equations = paper_data["equations"][:10]  # Test first 10

        conversion_results = {
            "successful": [],
            "failed": []
        }

        for eq in equations:
            result = convert_equation_to_sympy(eq["latex"], eq.get("context", ""))

            if result["conversion_status"] == "converted":
                conversion_results["successful"].append({
                    "latex": eq["latex"][:50],
                    "sympy": result["sympy_expr"][:50]
                })
            else:
                conversion_results["failed"].append({
                    "latex": eq["latex"][:50],
                    "error": result["error"][:50]
                })

        # Report results
        success_rate = len(conversion_results["successful"]) / len(equations) * 100
        print(f"✅ Conversion rate: {success_rate:.0f}% ({len(conversion_results['successful'])}/{len(equations)})")

        # Should have at least some successful conversions
        assert len(conversion_results["successful"]) > 0, "Should convert at least some equations"


class TestAPIEndpoints:
    """Test API endpoints for arXiv integration."""

    @pytest.fixture
    def client(self):
        """Create FastAPI test client."""
        from fastapi.testclient import TestClient
        from math_trace.server import app

        return TestClient(app)

    def test_extract_endpoint(self, client):
        """Test /api/arxiv/extract endpoint."""
        response = client.post(
            f"/api/arxiv/extract?paper_url_or_id={TEST_PAPER_ID}"
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "success"
        data = response_data["data"]
        assert data["paper_id"] == TEST_PAPER_ID
        assert data["total_equations"] > 0

        print(f"✅ Extract endpoint returned {data['total_equations']} equations")

    def test_get_paper_endpoint(self, client):
        """Test /api/arxiv/papers/{id} endpoint."""
        response = client.get(f"/api/arxiv/papers/{TEST_PAPER_ID}")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "success"
        data = response_data["data"]
        assert data["paper_id"] == TEST_PAPER_ID
        assert len(data["equations"]) > 0

        print(f"✅ Get paper endpoint returned {len(data['equations'])} equations")

    def test_formula_browser_endpoints(self, client):
        """Test formula browser endpoints."""
        # Test arxiv papers listing
        response = client.get("/api/formulas/arxiv-papers")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

        # Test local models listing
        response = client.get("/api/formulas/local-models")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

        print(f"✅ Formula browser endpoints working")


class TestEndToEndWorkflow:
    """Integration test: full workflow from paper to equations."""

    @pytest.mark.skip(reason="antlr4 (v4.7.2) incompatible with Python 3.13; upgrade when available")
    def test_complete_pipeline(self):
        """Test complete workflow: extract → cache → load → convert."""
        from math_trace.arxiv_extractor import (
            save_extracted_paper,
            load_extracted_paper
        )
        from math_trace.ollama_arxiv_worker import process_paper

        # Step 1: Extract and cache
        print(f"\n[1/4] Extracting {TEST_PAPER_ID}...")
        paper_dir = save_extracted_paper(TEST_PAPER_ID)
        assert paper_dir.exists()

        # Step 2: Verify cache
        print(f"[2/4] Verifying cache...")
        paper_data = load_extracted_paper(TEST_PAPER_ID)
        assert paper_data["paper_id"] == TEST_PAPER_ID
        initial_eq_count = len(paper_data["equations"])
        assert initial_eq_count > 0

        # Step 3: Convert equations
        print(f"[3/4] Converting {initial_eq_count} equations...")
        result = process_paper(TEST_PAPER_ID)
        assert result["status"] == "success"

        # Step 4: Verify conversion
        print(f"[4/4] Verifying conversion results...")
        paper_data_after = load_extracted_paper(TEST_PAPER_ID)
        converted_count = sum(
            1 for eq in paper_data_after["equations"]
            if eq.get("conversion_status") == "converted"
        )

        conversion_rate = converted_count / initial_eq_count * 100
        print(f"\n✅ End-to-end test complete!")
        print(f"   Papers: {TEST_PAPER_ID}")
        print(f"   Equations extracted: {initial_eq_count}")
        print(f"   Equations converted: {converted_count} ({conversion_rate:.0f}%)")
        print(f"   Cache location: {paper_dir}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
