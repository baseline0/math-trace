"""PDF-only equation extraction fallback with provenance.

Uses math_trace.services.FormulaExtractor (pdfplumber) for papers where no
LaTeX source is available (older papers, non-arXiv venues). Emits records with
paper_id, page, locator, latex, and surrounding context so the formula can be
reviewed before entering the equation catalog. This complements — never
replaces — the LaTeX-first path in equations-history.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from math_trace.services.extractor import FormulaExtractor

app = typer.Typer(add_completion=False, help="Extract equation candidates from a PDF-only paper.")


def extract_pdf_equations(pdf_path: Path, paper_id: str) -> list[dict]:
    """Return provenance-rich formula records from a PDF."""
    formulas = FormulaExtractor.extract_with_descriptions(pdf_path)
    return [
        {
            "formula_id": f"PDF-{paper_id}-{f.name}",
            "paper_id": paper_id,
            "latex": f.latex,
            "description": f.description,
            "locator": f"page {f.page}",
            "page": f.page,
            "context": f.context,
            "origin": "pdf-fallback",
            "review": "needs_review",
        }
        for f in formulas
    ]


@app.command()
def extract(
    pdf_path: Annotated[Path, typer.Option("--pdf-path", help="Path to the PDF paper.")],
    paper_id: Annotated[str, typer.Option("--paper-id", help="Stable paper identifier for provenance.")],
    out_path: Annotated[Path, typer.Option("--out-path", help="Output JSON path.")],
) -> None:
    """Extract equation candidates with provenance from a PDF-only paper."""
    records = extract_pdf_equations(pdf_path, paper_id)
    payload = json.dumps(records, indent=2, ensure_ascii=False) + "\n"
    out_path.write_text(payload, encoding="utf-8")
    print(f"wrote {len(records)} candidates to {out_path}")


if __name__ == "__main__":
    app()
