"""
Build presentations from the SIR model.

Supports multiple output formats:
- Marp (Markdown slides) → HTML/PDF via Marp CLI
- Reveal.js (HTML slides) → Live presentations
- Beamer (LaTeX/PDF) → Traditional academic format

Usage:
  python build_presentation.py              # Build with default backend (Marp)
  python build_presentation.py --backend marp  # Explicit backend
  python build_presentation.py --all        # Build all available backends

Design Intent:
- The Typer command only parses arguments, maps errors to exit codes, and prints.
- Input checks, build orchestration, and output formatting are pure functions.
- The presentation generator is loaded lazily, so the pure logic imports without it.
"""

import sys
from collections.abc import Mapping, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Protocol

import typer

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

app = typer.Typer(help="Build presentations from SIR model")


class Backend(StrEnum):
    """Presentation backends the generator supports."""

    MARP = "marp"
    REVEAL = "reveal"
    BEAMER = "beamer"


class PresentationBuilder(Protocol):
    """The subset of PresentationGenerator used by this script."""

    def build(self, backend: str, output_dir: Path) -> Path: ...

    def build_all(self, output_dir: Path) -> Mapping[str, Path]: ...


def default_paths(script_dir: Path) -> tuple[Path, Path, Path]:
    """Return (model_path, config_path, output_dir) defaults relative to the example folder."""
    return (
        script_dir / "generated" / "sir_equations.json",
        script_dir / "presentation_config.yaml",
        script_dir / "generated",
    )


def input_errors(model_path: Path, config_path: Path) -> list[str]:
    """Return one message per missing input file. An empty list means the inputs are present."""
    errors: list[str] = []
    if not model_path.exists():
        errors.append(f"❌ {model_path} not found. Run build_paper.py first.")
    if not config_path.exists():
        errors.append(f"❌ {config_path} not found. Create presentation configuration.")
    return errors


def build_outputs(
    generator: PresentationBuilder,
    backend: Backend,
    build_all: bool,
    output_dir: Path,
) -> list[tuple[str, Path]]:
    """Build one backend, or every backend when build_all is set. Returns (backend, path) pairs."""
    if build_all:
        return [(name, Path(path)) for name, path in generator.build_all(output_dir).items()]
    return [(backend.value, generator.build(backend.value, output_dir))]


def start_line(backend: Backend, build_all: bool) -> str:
    """Format the line printed before a build starts."""
    if build_all:
        return "🎬 Building presentations in all formats..."
    return f"🎬 Building {backend.value} presentation..."


def result_lines(results: Sequence[tuple[str, Path]], build_all: bool) -> list[str]:
    """Format the per-output lines printed after a build."""
    if build_all:
        return [f"  ✅ {name:10} → {path}" for name, path in results]
    return [f"  ✅ Generated: {results[0][1]}"]


def next_steps_lines(output_dir: Path, backend: Backend, build_all: bool) -> list[str]:
    """Format the next-steps hints. Marp hints appear for the marp backend or for --all."""
    lines = ["\n📊 Next steps:"]
    if backend == Backend.MARP or build_all:
        lines.append(f"  • View Marp: marp {output_dir}/slides.md")
        lines.append(f"  • Export to PDF: marp {output_dir}/slides.md --pdf")
    return lines


def _load_generator(model_path: Path, config_path: Path) -> PresentationBuilder:
    """Import and construct the generator. The import is lazy so pure logic loads without it."""
    from math_trace.presentation_generator import PresentationGenerator

    return PresentationGenerator(model_path, config_path)


@app.command()
def main(
    backend: Backend = typer.Option(Backend.MARP, help="Presentation backend (default: marp)"),
    build_all: bool = typer.Option(False, "--all", help="Build all available backends"),
    output: Path | None = typer.Option(None, help="Output directory (default: generated/)"),
) -> None:
    """Build presentations from SIR model."""
    script_dir = Path(__file__).parent
    model_path, config_path, default_output = default_paths(script_dir)

    errors = input_errors(model_path, config_path)
    if errors:
        for message in errors:
            typer.echo(message)
        raise typer.Exit(1)

    output_dir = output or default_output
    typer.echo(start_line(backend, build_all))
    generator = _load_generator(model_path, config_path)

    results = build_outputs(generator, backend, build_all, output_dir)
    for line in result_lines(results, build_all):
        typer.echo(line)
    for line in next_steps_lines(output_dir, backend, build_all):
        typer.echo(line)


if __name__ == "__main__":
    app()
