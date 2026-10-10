"""Shared build pipeline utilities for formula-to-paper templates.

Provides reusable components for:
- Converting SymPy formulas (JSON) → Typst via LaTeX
- Checking Typst availability
- Building PDFs with graceful degradation
- Matplotlib figure generation with consistent styling
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any


class FormulaPipeline:
    """Convert SymPy formulas JSON → Typst via LaTeX."""

    def __init__(self, equations_json_path: str, output_dir: str = "generated"):
        """
        Initialize formula pipeline.

        Args:
            equations_json_path: Path to JSON file exported by model.py
            output_dir: Directory to write formulas.typ (default: "generated")
        """
        self.equations_json_path = Path(equations_json_path)
        self.output_dir = Path(output_dir)
        self.output_file = self.output_dir / "formulas.typ"

    def generate_formulas(self) -> bool:
        """Convert SymPy formulas to Typst via LaTeX.

        Returns:
            True if successful, False otherwise
        """
        print("📐 Generating Typst formulas...")

        if not self.equations_json_path.exists():
            print(f"❌ {self.equations_json_path} not found")
            return False

        try:
            from math_trace.generators import SymPyToTypst
        except ImportError:
            print("❌ math_trace not installed. Install with: pip install math-trace")
            return False

        # Load equations
        try:
            with open(self.equations_json_path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {self.equations_json_path}: {e}")
            return False

        # Convert LaTeX → Typst
        converter = SymPyToTypst()
        typst_lines = []

        for name, info in data.items():
            latex_str = info.get("latex", "")
            if not latex_str:
                print(f"⚠️  Skipping {name}: no LaTeX formula")
                continue

            typst_str = converter._latex_to_typst(latex_str)
            description = info.get("description", name)
            source_line = info.get("source_line", "?")

            comment = f"// {description} (from model.py:{source_line})"
            definition = f"#let {name} = $ {typst_str} $"
            typst_lines.append(f"{comment}\n{definition}")

        # Write output
        self.output_dir.mkdir(exist_ok=True)
        self.output_file.write_text("\n\n".join(typst_lines))
        print(f"✅ Generated {self.output_file}")
        return True


class FigureGenerator:
    """Matplotlib figure generation with consistent styling."""

    def __init__(self, output_dir: str = "generated/figures"):
        """Initialize figure generator.

        Args:
            output_dir: Directory to save figures (default: "generated/figures")
        """
        self.output_dir = Path(output_dir)

    def save_figure(self, fig: Any, name: str, dpi: int = 300, close: bool = True) -> Path:
        """Save matplotlib figure with consistent settings.

        Args:
            fig: matplotlib figure object
            name: Figure filename (e.g., "oscillator.png")
            dpi: Resolution (default: 300)
            close: Whether to close figure after saving (default: True)

        Returns:
            Path to saved figure
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        fig_path = self.output_dir / name

        fig.tight_layout()
        fig.savefig(fig_path, dpi=dpi, bbox_inches="tight")
        print(f"✅ Generated {fig_path}")

        if close:
            import matplotlib.pyplot as plt

            plt.close(fig)

        return fig_path


def check_typst_installed() -> bool:
    """Check if Typst is available on PATH.

    Returns:
        True if typst command exists, False otherwise
    """
    result = subprocess.run(["which", "typst"], capture_output=True, text=True)
    return result.returncode == 0


def build_pdf(typst_file: str = "main.typ") -> bool:
    """Compile Typst document to PDF.

    Args:
        typst_file: Path to .typ file (default: "main.typ")

    Returns:
        True if PDF generated, False otherwise.
        Returns True (non-fatal) if Typst not found.
    """
    print("📝 Building Typst document...")

    typst_path = Path(typst_file)
    if not typst_path.exists():
        print(f"❌ {typst_file} not found")
        return False

    if not check_typst_installed():
        print("⚠️  Typst not found. To generate PDF:")
        print("   Run: cd ../.. && just install-typst")
        print("   Or visit: https://github.com/typst/typst/releases")
        print(f"   (Typst file is ready at: {typst_file})")
        return True  # Not a hard failure—formulas are ready

    result = subprocess.run(["typst", "compile", str(typst_path)], capture_output=True, text=True)

    if result.returncode == 0:
        pdf_path = typst_path.with_suffix(".pdf")
        if pdf_path.exists():
            print(f"✅ Generated {pdf_path}")
            return True
        else:
            print(f"❌ Typst compiled but {pdf_path} not found")
            return False
    else:
        print(f"❌ Typst compilation failed:\n{result.stderr}")
        return False


def run_build_pipeline(
    equations_json: str,
    typst_file: str = "main.typ",
    figure_generator: Callable | None = None,
    domain_name: str = "paper",
) -> bool:
    """Execute full build pipeline: formulas → figures → PDF.

    Args:
        equations_json: Path to equations JSON file
        typst_file: Path to Typst document
        figure_generator: Optional callable that runs simulations and generates figures.
                         Should return True on success.
        domain_name: Domain name for logging (e.g., "physics", "biochemistry")

    Returns:
        True if all steps succeed (or gracefully degrade), False on hard failure
    """
    print(f"🚀 Building {domain_name} paper...\n")

    # Step 1: Generate formulas
    pipeline = FormulaPipeline(equations_json)
    if not pipeline.generate_formulas():
        print("\n❌ Failed at step: Formulas")
        return False

    # Step 2: Generate figures (optional)
    if figure_generator:
        print()
        if not figure_generator():
            print("\n❌ Failed at step: Figures")
            return False

    # Step 3: Build PDF
    print()
    pdf_generated = build_pdf(typst_file)

    # Summary
    pdf_path = Path(typst_file).with_suffix(".pdf")
    if pdf_generated and pdf_path.exists():
        print(f"\n✅ Paper built successfully: {pdf_path}")
        return True

    if not check_typst_installed():
        # Missing Typst is non-fatal: the formulas and figures are still usable.
        print("\n✅ Formulas and figures ready!")
        print("   (PDF generation requires Typst: run 'cd ../.. && just install-typst')")
        return True

    # Typst is installed but the document did not compile. That is a real failure.
    print("\n❌ Failed at step: PDF")
    return False
