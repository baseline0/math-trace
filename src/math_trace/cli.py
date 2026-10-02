"""Command-line interface for math-trace.

Orchestrates paper ingestion, formula extraction, and presentation generation.
Built with Typer for type-safe, self-documenting CLI.

Usage:
    math-trace ingest-paper https://arxiv.org/abs/2609.21904
    math-trace extract-formulas paper.pdf
    math-trace build-presentation formulas.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import yaml

from math_trace.presentation_generator import PresentationGenerator
from math_trace.services import (
    FormulaExtractor,
    PaperDownloader,
    PaperMetadata,
    PresentationBuilder,
)

app = typer.Typer(
    name="math-trace",
    help="Formula-to-code traceability for publication-quality mathematical documents.",
)


@app.command()
def ingest_paper(
    url: str = typer.Argument(..., help="Paper URL (arXiv, PubMed, or direct PDF link)"),
    output_dir: Path = typer.Option(
        Path("generated"),
        "--output",
        "-o",
        help="Output directory for extracted formulas and presentation",
    ),
    use_claude: bool = typer.Option(
        False,
        "--claude",
        help="Use Claude API to generate formula descriptions (costs $$)",
    ),
) -> None:
    """Download paper, extract formulas, and generate presentation.

    Example:
        math-trace ingest-paper https://arxiv.org/abs/2609.21904
    """
    typer.echo(f"📄 Downloading paper from {url}...")
    try:
        pdf_path = PaperDownloader.download(url)
        typer.echo(f"✅ Downloaded to {pdf_path}")
    except Exception as e:
        typer.echo(f"❌ Download failed: {e}", err=True)
        raise typer.Exit(1)

    typer.echo("🔍 Extracting formulas...")
    try:
        formulas = FormulaExtractor.extract_with_descriptions(pdf_path, use_claude)
        typer.echo(f"✅ Found {len(formulas)} formulas")
    except Exception as e:
        typer.echo(f"❌ Extraction failed: {e}", err=True)
        raise typer.Exit(1)

    # Build presentation config
    typer.echo("🎬 Building presentation...")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save formulas JSON
    formulas_dict = {
        f.name: {
            "latex": f.latex,
            "description": f.description,
            "source_line": f.page,
        }
        for f in formulas
    }
    formulas_json_path = output_dir / "formulas.json"
    formulas_json_path.write_text(json.dumps(formulas_dict, indent=2))
    typer.echo(f"✅ Formulas saved to {formulas_json_path}")

    # Generate presentation config
    paper_metadata = PaperMetadata(
        title="Extracted Formulas",
        url=url,
        pages=len(set(f.page for f in formulas)),
        formulas=formulas,
    )
    config = PresentationBuilder.build_config(paper_metadata, url)
    config_path = output_dir / "presentation_config.yaml"
    config_path.write_text(yaml.dump(config, default_flow_style=False))
    typer.echo(f"✅ Config saved to {config_path}")

    # Generate Marp presentation
    typer.echo("🎨 Generating Marp presentation...")
    try:
        generator = PresentationGenerator(formulas_json_path, config_path)
        slides_path = generator.build("marp", output_dir)
        typer.echo(f"✅ Presentation generated: {slides_path}")
    except Exception as e:
        typer.echo(f"❌ Presentation generation failed: {e}", err=True)
        raise typer.Exit(1)

    typer.echo("\n📊 Next steps:")
    typer.echo(f"  • View: marp {slides_path}")
    typer.echo(f"  • Export PDF: marp {slides_path} --pdf")


@app.command()
def extract_formulas(
    pdf_path: Path = typer.Argument(..., help="Path to PDF file"),
    output_file: Path = typer.Option(
        Path("formulas.json"),
        "--output",
        "-o",
        help="Output JSON file",
    ),
) -> None:
    """Extract formulas from a PDF file.

    Example:
        math-trace extract-formulas paper.pdf
    """
    if not pdf_path.exists():
        typer.echo(f"❌ File not found: {pdf_path}", err=True)
        raise typer.Exit(1)

    typer.echo(f"🔍 Extracting formulas from {pdf_path}...")
    try:
        formulas = FormulaExtractor.extract(pdf_path)
        typer.echo(f"✅ Found {len(formulas)} formulas")
    except Exception as e:
        typer.echo(f"❌ Extraction failed: {e}", err=True)
        raise typer.Exit(1)

    # Save to JSON
    formulas_dict = {
        f.name: {
            "latex": f.latex,
            "description": f.description,
            "page": f.page,
            "context": f.context,
        }
        for f in formulas
    }
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(formulas_dict, indent=2))
    typer.echo(f"✅ Saved to {output_file}")


@app.command()
def build_presentation(
    formulas_json: Path = typer.Argument(..., help="Path to formulas.json"),
    config_yaml: Path = typer.Argument(..., help="Path to presentation_config.yaml"),
    backend: str = typer.Option(
        "marp",
        "--backend",
        "-b",
        help="Presentation backend (marp, reveal, beamer)",
    ),
    output_dir: Path = typer.Option(
        Path("generated"),
        "--output",
        "-o",
        help="Output directory",
    ),
) -> None:
    """Build presentation from formulas and config.

    Example:
        math-trace build-presentation formulas.json presentation_config.yaml
    """
    if not formulas_json.exists():
        typer.echo(f"❌ Formulas file not found: {formulas_json}", err=True)
        raise typer.Exit(1)
    if not config_yaml.exists():
        typer.echo(f"❌ Config file not found: {config_yaml}", err=True)
        raise typer.Exit(1)

    typer.echo(f"🎬 Building {backend} presentation...")
    try:
        generator = PresentationGenerator(formulas_json, config_yaml)
        result = generator.build(backend, output_dir)
        typer.echo(f"✅ Generated: {result}")
    except Exception as e:
        typer.echo(f"❌ Generation failed: {e}", err=True)
        raise typer.Exit(1)


def main() -> None:
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
