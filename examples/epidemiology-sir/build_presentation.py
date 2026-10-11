"""
Build the SIR presentation as a single Revealjs HTML file.

Reads generated/sir_equations.json and presentation_config.yaml, and writes
generated/presentation.html (or --output). The HTML loads reveal.js and MathJax from
CDNs at pinned versions, so viewing it needs network access.

Usage:
  python build_presentation.py                          # writes generated/presentation.html
  python build_presentation.py --output /tmp/deck.html  # write elsewhere

Design Intent:
- The Typer command only parses arguments, maps errors to exit codes, and prints.
- Input checks, figure relocation, and output formatting are pure functions.
- The slide and HTML logic lives in math_trace.revealjs_generator.
"""

import sys
from collections.abc import Sequence
from pathlib import Path

import typer

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from math_trace.revealjs_generator import (
    Slide,
    build_slides,
    load_presentation_inputs,
    relocate_figures,
    render_html,
    write_presentation,
)

app = typer.Typer(help="Build the SIR presentation as a Revealjs HTML file")

OUTPUT_NAME = "presentation.html"


def default_paths(script_dir: Path) -> tuple[Path, Path, Path]:
    """Return (model_path, config_path, output_path) defaults relative to the example folder."""
    return (
        script_dir / "generated" / "sir_equations.json",
        script_dir / "presentation_config.yaml",
        script_dir / "generated" / OUTPUT_NAME,
    )


def input_errors(model_path: Path, config_path: Path) -> list[str]:
    """Return one message per missing input file. An empty list means the inputs are present."""
    errors: list[str] = []
    if not model_path.exists():
        errors.append(f"❌ {model_path} not found. Run build_paper.py first.")
    if not config_path.exists():
        errors.append(f"❌ {config_path} not found. Create presentation configuration.")
    return errors


def warning_lines(slides: Sequence[Slide]) -> list[str]:
    """Format one line per slide warning (for example, a formula name missing from the model)."""
    return [f"  ⚠️  Slide '{slide.title}': {message}" for slide in slides for message in slide.warnings]


def result_lines(output: Path) -> list[str]:
    """Format the line printed after the file is written."""
    return [f"  ✅ Generated: {output}"]


def next_steps_lines(output: Path) -> list[str]:
    """Format the next-steps hints."""
    return [
        "\n📊 Next steps:",
        f"  • Open in a browser: {output}",
        "  • The page loads reveal.js and MathJax from cdn.jsdelivr.net, so it needs network access.",
        "  • Press S in the deck to open speaker notes.",
    ]


@app.command()
def main(
    output: Path | None = typer.Option(None, help=f"Output HTML file (default: generated/{OUTPUT_NAME})"),
) -> None:
    """Build the SIR presentation as a single Revealjs HTML file."""
    script_dir = Path(__file__).parent
    model_path, config_path, default_output = default_paths(script_dir)

    errors = input_errors(model_path, config_path)
    if errors:
        for message in errors:
            typer.echo(message)
        raise typer.Exit(1)

    output_path = output or default_output
    typer.echo("🎬 Building Revealjs presentation...")

    inputs = load_presentation_inputs(model_path, config_path)
    slides = relocate_figures(build_slides(inputs), script_dir, output_path.parent)
    html_text = render_html(slides, title=str(inputs.config.get("title", "Presentation")))
    written = write_presentation(html_text, output_path)

    for line in warning_lines(slides):
        typer.echo(line)
    for line in result_lines(written):
        typer.echo(line)
    for line in next_steps_lines(written):
        typer.echo(line)


if __name__ == "__main__":
    app()
