"""Browse and select formulas from cached papers and local models.

Typer CLI commands that are auto-generated as FastAPI endpoints.
Provides unified interface for formula discovery.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

import typer

from .constants import CACHE_DIR
from .logging import get_logger

logger = get_logger(__name__)
app = typer.Typer(help="Browse and select formulas from various sources")


@app.command()
def arxiv_papers(limit: int = typer.Option(20, help="Max papers to return")) -> list[dict]:
    """List cached arXiv papers with equation counts.

    Returns: [{paper_id, title, authors, equation_count}, ...]
    """
    papers_dir = CACHE_DIR / "papers"

    if not papers_dir.exists():
        logger.debug(f"Papers cache directory not found: {papers_dir}")
        return []

    papers = []
    for paper_dir in sorted(papers_dir.iterdir())[:limit]:
        if not paper_dir.is_dir():
            continue

        metadata_path = paper_dir / "metadata.json"
        if not metadata_path.exists():
            logger.warning(f"Missing metadata for paper {paper_dir.name}")
            continue

        try:
            metadata = json.loads(metadata_path.read_text())

            # Validate metadata structure
            if not isinstance(metadata, dict):
                logger.warning(f"Invalid metadata format for {paper_dir.name}: expected dict")
                continue
            if "paper_id" not in metadata:
                logger.warning(f"Missing 'paper_id' in metadata for {paper_dir.name}")
                continue
        except (OSError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to read metadata for {paper_dir.name}: {e}")
            continue

        equations_path = paper_dir / "equations.jsonl"

        # Count equations (with limit to prevent DoS)
        MAX_EQUATIONS = 10000
        eq_count = 0
        converted_count = 0
        if equations_path.exists():
            try:
                for line in equations_path.read_text().strip().split("\n"):
                    if eq_count >= MAX_EQUATIONS:
                        logger.warning(f"Paper {paper_dir.name} has >{MAX_EQUATIONS} equations, truncating")
                        break

                    if line:
                        eq_count += 1
                        try:
                            eq = json.loads(line)
                            if eq.get("conversion_status") == "converted":
                                converted_count += 1
                        except json.JSONDecodeError as e:
                            logger.debug(f"Invalid JSON in equations file: {e}")
            except OSError as e:
                logger.error(f"Failed to read equations for {paper_dir.name}: {e}")

        # HTML escape metadata for safe output
        papers.append(
            {
                "paper_id": paper_dir.name,
                "title": html.escape(metadata.get("title", "Unknown")),
                "authors": html.escape(str(metadata.get("authors", "Unknown"))[:50]),
                "total_equations": eq_count,
                "converted_equations": converted_count,
            }
        )

    return papers


def local_models(pattern: str = "*/src/model.py", root: str = ".") -> list[dict]:
    """Find Python files with FORMULAS dict in local filesystem.

    Returns: [{path, formula_count, formulas: [{name, latex}, ...]}, ...]
    """
    # Validate glob pattern (whitelist safe patterns)
    SAFE_PATTERNS = ["*/src/model.py", "model.py", "**/model.py", "**/src/model.py"]
    if pattern not in SAFE_PATTERNS:
        logger.warning(f"Unsafe pattern '{pattern}', using default")
        pattern = SAFE_PATTERNS[0]

    root_path = Path(root).resolve()
    models = []

    try:
        model_paths = list(root_path.glob(pattern))

        # Limit results to prevent DoS
        MAX_MODELS = 1000
        if len(model_paths) > MAX_MODELS:
            logger.warning(f"Pattern returned {len(model_paths)} files, truncating to {MAX_MODELS}")
            model_paths = model_paths[:MAX_MODELS]
    except (ValueError, OSError) as e:
        logger.error(f"Invalid glob pattern '{pattern}': {e}")
        return []

    for model_path in model_paths:
        try:
            content = model_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            logger.debug(f"Failed to read {model_path}: {e}")
            continue

        # Look for FORMULAS dict
        if "FORMULAS" not in content:
            continue

        # Try to extract formula names via regex (safe, doesn't execute)
        formula_names = re.findall(r"'(\w+)':\s*Formula\(", content)

        if not formula_names:
            # Try alternate format
            formula_names = re.findall(r'"(\w+)":\s*Formula\(', content)

        # Limit formulas per file
        MAX_FORMULAS_PER_FILE = 500
        if len(formula_names) > MAX_FORMULAS_PER_FILE:
            logger.warning(f"File {model_path} has >{MAX_FORMULAS_PER_FILE} formulas, truncating")
            formula_names = formula_names[:MAX_FORMULAS_PER_FILE]

        if formula_names:
            models.append(
                {
                    "path": str(model_path.relative_to(root_path)),
                    "formula_count": len(formula_names),
                    "formulas": [{"name": name} for name in formula_names],
                }
            )

    return sorted(models, key=lambda m: m["path"])


@app.command()
def list_local_models(
    pattern: str = typer.Option("*/src/model.py", help="Glob pattern for model files"),
    root: str = typer.Option(".", help="Root directory to search"),
) -> list[dict]:
    """List Python files with FORMULAS dict (Typer CLI wrapper)."""
    return local_models(pattern=pattern, root=root)


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
        for line in equations_path.read_text().strip().split("\n"):
            if line:
                equations.append(json.loads(line))

    return {
        "paper_id": paper_id,
        "title": metadata.get("title"),
        "authors": metadata.get("authors"),
        "total_equations": len(equations),
        "equations": equations,
    }


@app.command()
def local_model_formulas(
    path: str = typer.Argument(..., help="Path to model.py file"),
) -> dict:
    """Extract formulas from local model.py file.

    Returns: {path, formulas: [{name, latex}, ...]}
    """
    import importlib.util
    import sys

    model_path = Path(path).resolve()

    if not model_path.exists():
        msg = f"File not found: {path}"
        logger.error(msg)
        typer.echo(msg, err=True)
        raise typer.Exit(1)

    try:
        # Import the model dynamically
        spec = importlib.util.spec_from_file_location("model", model_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module spec from {model_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules["model"] = module
        spec.loader.exec_module(module)

        if not hasattr(module, "FORMULAS"):
            logger.debug(f"No FORMULAS dict in {model_path}")
            return {
                "path": str(model_path),
                "error": "No FORMULAS dict found",
                "formulas": [],
            }

        formulas = []
        MAX_FORMULAS_PER_FILE = 500
        for name, formula_obj in module.FORMULAS.items():
            if len(formulas) >= MAX_FORMULAS_PER_FILE:
                logger.warning(f"File {model_path} has >{MAX_FORMULAS_PER_FILE} formulas, truncating")
                break

            try:
                latex = formula_obj.to_latex()

                # Validate LaTeX size
                MAX_LATEX_SIZE = 10000
                if len(latex) > MAX_LATEX_SIZE:
                    logger.warning(f"Formula '{name}' LaTeX too large ({len(latex)} chars), skipping")
                    continue

                formulas.append(
                    {
                        "name": name,
                        "latex": latex,
                        "description": getattr(formula_obj, "description", ""),
                    }
                )
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to extract LaTeX for formula '{name}': {e}")
                formulas.append(
                    {
                        "name": name,
                        "latex": "[Error: unable to extract LaTeX]",
                        "description": "",
                    }
                )

        return {
            "path": str(model_path),
            "formulas": formulas,
        }

    except (ImportError, OSError, SyntaxError) as e:
        logger.error(f"Failed to load module {model_path}: {e}")
        return {
            "path": str(model_path),
            "error": f"{type(e).__name__}: {e}",
            "formulas": [],
        }


if __name__ == "__main__":
    app()
