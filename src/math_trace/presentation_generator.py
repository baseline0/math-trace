"""Pluggable presentation generator for formula-to-code traceability.

Converts math-trace models (SymPy formulas + narrative) to multiple presentation formats:
- Marp (Markdown slides)
- Reveal.js (HTML slides)
- Beamer (PDF slides via LaTeX)
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import sympy as sp
import yaml

from math_trace.generators import SymPyToTypst


@dataclass
class PresentationConfig:
    """Presentation structure and metadata."""

    title: str
    format: str  # "talk", "course-notes", "formula-reference"
    backend: str  # "marp", "reveal", "beamer"
    slides: list[dict[str, Any]]
    metadata: dict[str, Any] | None = None
    paper_url: str | None = None
    paper_doi: str | None = None


class PresentationBackend(ABC):
    """Abstract base class for presentation backends."""

    def __init__(self, converter: SymPyToTypst | None = None) -> None:
        """Initialize backend.

        Args:
            converter: Optional SymPyToTypst converter for formula rendering
        """
        self.converter = converter or SymPyToTypst()

    @abstractmethod
    def render(
        self,
        config: PresentationConfig,
        formulas: dict[str, Any],
        output_dir: Path,
    ) -> Path:
        """Render presentation to output format.

        Args:
            config: Presentation configuration
            formulas: Dictionary of formula metadata {name: {expr, description, source_line}}
            output_dir: Directory to write output files

        Returns:
            Path to main output file (PDF, HTML, or Markdown)
        """
        pass

    def _get_formula_typst(self, name: str, formulas: dict[str, Any]) -> str:
        """Get Typst representation of a formula.

        Args:
            name: Formula name (key in formulas dict)
            formulas: Formula dictionary (nested or flat)

        Returns:
            Typst-formatted formula string
        """
        if name not in formulas:
            return f"(Formula '{name}' not found)"

        formula_info = formulas[name]

        # Handle nested dict format with "latex" key
        if isinstance(formula_info, dict):
            # Try different possible keys for LaTeX representation
            latex_str = (
                formula_info.get("latex")
                or formula_info.get("expr")
                or str(formula_info)
            )
        else:
            latex_str = str(formula_info)

        if not latex_str:
            return f"(No formula for '{name}')"

        return self.converter._latex_to_typst(latex_str)

    def _format_citation(self, config: PresentationConfig) -> str:
        """Format paper citation as markdown/text.

        Args:
            config: Presentation configuration

        Returns:
            Citation string
        """
        cite_parts = []
        if config.paper_url:
            cite_parts.append(f"[{config.paper_url}]({config.paper_url})")
        if config.paper_doi:
            doi_url = f"https://doi.org/{config.paper_doi}"
            cite_parts.append(f"DOI: [{config.paper_doi}]({doi_url})")
        return " | ".join(cite_parts) if cite_parts else ""


class MarpBackend(PresentationBackend):
    """Generate Marp (Markdown) presentations."""

    def render(
        self,
        config: PresentationConfig,
        formulas: dict[str, Any],
        output_dir: Path,
    ) -> Path:
        """Render Marp markdown presentation.

        Args:
            config: Presentation configuration
            formulas: Formula dictionary
            output_dir: Output directory

        Returns:
            Path to generated slides.md
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "slides.md"

        lines = []

        # Marp frontmatter
        lines.append("---")
        lines.append("marp: true")
        lines.append("theme: default")
        lines.append("paginate: true")
        lines.append('title: "' + config.title + '"')
        lines.append("---")
        lines.append("")

        # Title slide
        lines.append(f"# {config.title}")
        lines.append("")
        if config.metadata and config.metadata.get("author"):
            lines.append(f"**{config.metadata['author']}**")
            lines.append("")
        if config.metadata and config.metadata.get("date"):
            lines.append(f"*{config.metadata['date']}*")
            lines.append("")
        if config.paper_url or config.paper_doi:
            lines.append("")
            lines.append(self._format_citation(config))

        # Slides
        for i, slide in enumerate(config.slides):
            lines.append("")
            lines.append("---")
            lines.append("")

            # Slide title
            if "title" in slide:
                lines.append(f"# {slide['title']}")
                lines.append("")

            # Slide content
            if "text" in slide:
                lines.append(slide["text"])
                lines.append("")

            # Formulas
            if "formulas" in slide:
                for formula_name in slide["formulas"]:
                    formula_text = self._get_formula_typst(formula_name, formulas)
                    if "description" in formulas.get(formula_name, {}):
                        desc = formulas[formula_name]["description"]
                        lines.append(f"**{desc}**")
                        lines.append("")
                    lines.append(f"$$\\text{{{formula_name}}} = {formula_text}$$")
                    lines.append("")

            # Figure
            if "figure" in slide:
                fig_path = slide["figure"]
                lines.append(f'![w:600]({fig_path})')
                lines.append("")

            # Speaker notes
            if "notes" in slide:
                lines.append("")
                lines.append("<!-- ")
                lines.append(f"**Notes:** {slide['notes']}")
                lines.append(" -->")

        # Write output
        output_file.write_text("\n".join(lines))
        return output_file


class PresentationGenerator:
    """Main generator: orchestrates model loading and presentation rendering."""

    def __init__(self, model_path: Path, config_path: Path) -> None:
        """Initialize generator.

        Args:
            model_path: Path to model.py or model JSON
            config_path: Path to presentation_config.yaml
        """
        self.model_path = Path(model_path)
        self.config_path = Path(config_path)
        self.converter = SymPyToTypst()

        # Load configuration
        with open(self.config_path) as f:
            config_data = yaml.safe_load(f)
        self.config_data = config_data

    def _load_formulas(self) -> dict[str, Any]:
        """Load formulas from model.

        Supports both:
        - model.py with export_formulas() function
        - model_equations.json file (flat or nested under "equations" key)

        Returns:
            Dictionary of formulas {name: {latex, description, source_line, ...}}
        """
        if self.model_path.suffix == ".json":
            with open(self.model_path) as f:
                data = json.load(f)

            # Handle nested structure where equations are under "equations" key
            if isinstance(data, dict) and "equations" in data:
                return data["equations"]
            return data

        # Try to load from Python module
        import sys
        import importlib.util

        spec = importlib.util.spec_from_file_location("model", self.model_path)
        if spec and spec.loader:
            model_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(model_module)

            if hasattr(model_module, "export_formulas"):
                return model_module.export_formulas()

        raise ValueError(f"Cannot load formulas from {self.model_path}")

    def build(self, backend: str = "marp", output_dir: Path | None = None) -> Path:
        """Build presentation in specified backend format.

        Args:
            backend: Backend to use ("marp", "reveal", "beamer")
            output_dir: Output directory (defaults to model_path parent / "generated")

        Returns:
            Path to generated presentation file
        """
        if output_dir is None:
            output_dir = self.model_path.parent / "generated"

        # Load formulas
        formulas = self._load_formulas()

        # Create config object
        config = PresentationConfig(
            title=self.config_data.get("title", "Presentation"),
            format=self.config_data.get("format", "talk"),
            backend=backend,
            slides=self.config_data.get("slides", []),
            metadata=self.config_data.get("metadata"),
            paper_url=self.config_data.get("paper_url"),
            paper_doi=self.config_data.get("paper_doi"),
        )

        # Select backend
        if backend == "marp":
            backend_obj = MarpBackend(self.converter)
        else:
            raise ValueError(f"Backend '{backend}' not yet implemented")

        # Render
        return backend_obj.render(config, formulas, output_dir)

    def build_all(self, output_dir: Path | None = None) -> dict[str, Path]:
        """Build presentation in all available backends.

        Args:
            output_dir: Output directory

        Returns:
            Dictionary mapping backend names to output paths
        """
        results = {}
        for backend in ["marp"]:  # Add "reveal", "beamer" when implemented
            results[backend] = self.build(backend, output_dir)
        return results


if __name__ == "__main__":
    # Quick test
    import sys

    if len(sys.argv) < 3:
        print("Usage: python presentation_generator.py <model_path> <config_path> [backend]")
        print("  model_path: Path to model.py or model_equations.json")
        print("  config_path: Path to presentation_config.yaml")
        print("  backend: marp (default), reveal, beamer")
        sys.exit(1)

    model_path = Path(sys.argv[1])
    config_path = Path(sys.argv[2])
    backend = sys.argv[3] if len(sys.argv) > 3 else "marp"

    generator = PresentationGenerator(model_path, config_path)
    output = generator.build(backend)
    print(f"✅ Generated presentation: {output}")
