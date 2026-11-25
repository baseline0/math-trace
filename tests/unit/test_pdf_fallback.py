"""PDF-only equation fallback tests.

The math-trace repo uses Typst for builds (ADR-301), so this suite does not
invoke any LaTeX build command. It verifies the fallback wrapper adds
provenance to whatever FormulaExtractor (pdfplumber) returns, using a stub.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

from math_trace.constants import REPO_ROOT as ROOT

if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from math_trace.pdf_fallback import extract_pdf_equations
from math_trace.services.extractor import ExtractedEquation


def test_records_have_provenance(tmp_path: Path) -> None:
    fake = [
        ExtractedEquation(
            name="eq_1",
            latex="S = T / T",
            description="Speedup ratio.",
            page=3,
            context="We define the speedup ...",
        )
    ]
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    with patch("math_trace.pdf_fallback.FormulaExtractor.extract_with_descriptions", return_value=fake):
        records = extract_pdf_equations(pdf, "TEST-2026-01")
    assert len(records) == 1
    rec = records[0]
    assert rec["paper_id"] == "TEST-2026-01"
    assert rec["origin"] == "pdf-fallback"
    assert rec["review"] == "needs_review"
    assert rec["locator"] == "page 3"
    assert rec["latex"] == "S = T / T"
    assert rec["context"]


def test_empty_pdf_yields_no_records(tmp_path: Path) -> None:
    pdf = tmp_path / "empty.pdf"
    pdf.write_bytes(b"%PDF-1.4\n")
    with patch("math_trace.pdf_fallback.FormulaExtractor.extract_with_descriptions", return_value=[]):
        assert extract_pdf_equations(pdf, "TEST-2026-02") == []
