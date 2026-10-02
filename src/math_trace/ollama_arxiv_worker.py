"""Ollama worker task for LaTeX → SymPy conversion.

Dispatched as a background job. Converts extracted equations to SymPy.
Designed for batch overnight processing or local Ollama inference.

Usage:
  python -m math_trace.ollama_arxiv_worker convert {paper_id}
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from latex2sympy2 import latex2sympy


def convert_equation_to_sympy(latex: str, context: str = "") -> dict:
    """Convert single LaTeX equation to SymPy.

    Returns: {sympy_expr, conversion_status, error (if any)}
    """
    try:
        # Clean up LaTeX for sympy
        latex_clean = latex.strip()
        latex_clean = re.sub(r'&=|&|\\\\|\\label\{[^}]*\}', '', latex_clean)

        # Attempt conversion
        sympy_expr = latex2sympy(latex_clean)

        return {
            'sympy_expr': str(sympy_expr),
            'conversion_status': 'converted',
            'error': None,
        }

    except Exception as e:
        return {
            'sympy_expr': None,
            'conversion_status': 'failed',
            'error': f"{type(e).__name__}: {str(e)[:80]}",
        }


def process_paper(paper_id: str, cache_dir: Path = None) -> dict:
    """Convert all equations in a paper from LaTeX to SymPy.

    Reads equations.jsonl, converts each, updates in place.
    Returns conversion summary.
    """
    if cache_dir is None:
        cache_dir = Path.home() / ".math-trace" / "arxiv-cache"

    paper_dir = cache_dir / "papers" / paper_id
    equations_path = paper_dir / "equations.jsonl"

    if not equations_path.exists():
        return {"status": "error", "message": f"Paper not found: {paper_id}"}

    # Read all equations
    equations = []
    for line in equations_path.read_text().strip().split('\n'):
        if line:
            equations.append(json.loads(line))

    print(f"Converting {len(equations)} equations for paper {paper_id}...")

    # Convert each
    converted = 0
    failed = 0

    for i, eq in enumerate(equations):
        result = convert_equation_to_sympy(eq['latex'], eq.get('context', ''))
        eq.update(result)

        if result['conversion_status'] == 'converted':
            converted += 1
            print(f"  [{i+1}/{len(equations)}] ✅ {eq['latex'][:50]}")
        else:
            failed += 1
            print(f"  [{i+1}/{len(equations)}] ❌ {eq['latex'][:50]}")

    # Save back
    with open(equations_path, 'w') as f:
        for eq in equations:
            f.write(json.dumps(eq) + '\n')

    # Update metadata with conversion summary
    metadata_path = paper_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text())
    metadata['conversion_summary'] = {
        'total': len(equations),
        'converted': converted,
        'failed': failed,
        'success_rate': converted / len(equations) if equations else 0,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2))

    return {
        "status": "success",
        "paper_id": paper_id,
        "total_equations": len(equations),
        "converted": converted,
        "failed": failed,
        "success_rate": converted / len(equations) if equations else 0,
        "message": f"Converted {converted}/{len(equations)} equations ({100*converted/len(equations):.0%})",
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m math_trace.ollama_arxiv_worker convert <paper_id>")
        sys.exit(1)

    command = sys.argv[1]
    paper_id = sys.argv[2]

    if command == "convert":
        result = process_paper(paper_id)
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
