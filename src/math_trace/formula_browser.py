"""Browse and select formulas from cached papers and local models.

Typer CLI commands that are auto-generated as FastAPI endpoints.
Provides unified interface for formula discovery.
"""

import json
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(help="Browse and select formulas from various sources")


@app.command()
def arxiv_papers(limit: int = typer.Option(20, help="Max papers to return")) -> list[dict]:
    """List cached arXiv papers with equation counts.

    Returns: [{paper_id, title, authors, equation_count}, ...]
    """
    cache_dir = Path.home() / ".math-trace" / "arxiv-cache" / "papers"

    if not cache_dir.exists():
        return []

    papers = []
    for paper_dir in sorted(cache_dir.iterdir())[:limit]:
        if not paper_dir.is_dir():
            continue

        metadata_path = paper_dir / "metadata.json"
        if not metadata_path.exists():
            continue

        metadata = json.loads(metadata_path.read_text())
        equations_path = paper_dir / "equations.jsonl"

        # Count equations
        eq_count = 0
        converted_count = 0
        if equations_path.exists():
            for line in equations_path.read_text().strip().split('\n'):
                if line:
                    eq_count += 1
                    eq = json.loads(line)
                    if eq.get('conversion_status') == 'converted':
                        converted_count += 1

        papers.append({
            'paper_id': paper_dir.name,
            'title': metadata.get('title', 'Unknown'),
            'authors': metadata.get('authors', 'Unknown')[:50],
            'total_equations': eq_count,
            'converted_equations': converted_count,
        })

    return papers


@app.command()
def local_models(
    pattern: str = typer.Option(
        "*/src/model.py",
        help="Glob pattern for model files"
    ),
    root: str = typer.Option(
        ".",
        help="Root directory to search"
    ),
) -> list[dict]:
    """Find Python files with FORMULAS dict in local filesystem.

    Returns: [{path, formula_count, formulas: [{name, latex}, ...]}, ...]
    """
    root_path = Path(root).resolve()
    models = []

    for model_path in root_path.glob(pattern):
        try:
            content = model_path.read_text()

            # Look for FORMULAS dict
            if 'FORMULAS' not in content:
                continue

            # Try to extract formula names via regex (safe, doesn't execute)
            import re
            formula_names = re.findall(r"'(\w+)':\s*Formula\(", content)

            if not formula_names:
                # Try alternate format
                formula_names = re.findall(r'"(\w+)":\s*Formula\(', content)

            if formula_names:
                models.append({
                    'path': str(model_path.relative_to(root_path)),
                    'formula_count': len(formula_names),
                    'formulas': [{'name': name} for name in formula_names],
                })

        except Exception:
            continue

    return sorted(models, key=lambda m: m['path'])


@app.command()
def arxiv_equations(paper_id: str) -> dict:
    """Get equations from cached arXiv paper.

    Returns: {paper_id, title, equations: [{index, latex, context, sympy_expr, status}, ...]}
    """
    cache_dir = Path.home() / ".math-trace" / "arxiv-cache" / "papers"
    paper_dir = cache_dir / paper_id

    if not paper_dir.exists():
        typer.echo(f"Paper not found: {paper_id}", err=True)
        raise typer.Exit(1)

    metadata = json.loads((paper_dir / "metadata.json").read_text())

    equations = []
    equations_path = paper_dir / "equations.jsonl"
    if equations_path.exists():
        for line in equations_path.read_text().strip().split('\n'):
            if line:
                equations.append(json.loads(line))

    return {
        'paper_id': paper_id,
        'title': metadata.get('title'),
        'authors': metadata.get('authors'),
        'total_equations': len(equations),
        'equations': equations,
    }


@app.command()
def local_model_formulas(
    path: str = typer.Argument(..., help="Path to model.py file"),
) -> dict:
    """Extract formulas from local model.py file.

    Returns: {path, formulas: [{name, latex}, ...]}
    """
    model_path = Path(path).resolve()

    if not model_path.exists():
        typer.echo(f"File not found: {path}", err=True)
        raise typer.Exit(1)

    try:
        # Import the model dynamically
        import sys
        import importlib.util

        spec = importlib.util.spec_from_file_location("model", model_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["model"] = module
        spec.loader.exec_module(module)

        if not hasattr(module, 'FORMULAS'):
            return {
                'path': str(model_path),
                'error': 'No FORMULAS dict found',
                'formulas': [],
            }

        formulas = []
        for name, formula_obj in module.FORMULAS.items():
            try:
                latex = formula_obj.to_latex()
                formulas.append({
                    'name': name,
                    'latex': latex,
                    'description': getattr(formula_obj, 'description', ''),
                })
            except Exception as e:
                formulas.append({
                    'name': name,
                    'latex': f"[Error: {e}]",
                    'description': '',
                })

        return {
            'path': str(model_path),
            'formulas': formulas,
        }

    except Exception as e:
        return {
            'path': str(model_path),
            'error': str(e),
            'formulas': [],
        }


if __name__ == "__main__":
    app()
