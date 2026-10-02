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
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from math_trace.presentation_generator import PresentationGenerator


def main() -> int:
    """Build presentations."""
    import argparse

    parser = argparse.ArgumentParser(description="Build presentations from SIR model")
    parser.add_argument(
        "--backend",
        choices=["marp", "reveal", "beamer"],
        default="marp",
        help="Presentation backend (default: marp)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build all available backends",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory (default: generated/)",
    )

    args = parser.parse_args()

    # Paths
    model_path = Path(__file__).parent / "generated" / "sir_equations.json"
    config_path = Path(__file__).parent / "presentation_config.yaml"

    if not model_path.exists():
        print(f"❌ {model_path} not found. Run build_paper.py first.")
        return 1

    if not config_path.exists():
        print(f"❌ {config_path} not found. Create presentation configuration.")
        return 1

    # Build presentations
    generator = PresentationGenerator(model_path, config_path)

    output_dir = args.output or (Path(__file__).parent / "generated")

    if args.all:
        print("🎬 Building presentations in all formats...")
        results = generator.build_all(output_dir)
        for backend, path in results.items():
            print(f"  ✅ {backend:10} → {path}")
    else:
        print(f"🎬 Building {args.backend} presentation...")
        result = generator.build(args.backend, output_dir)
        print(f"  ✅ Generated: {result}")

    print("\n📊 Next steps:")
    if args.backend == "marp" or args.all:
        print(f"  • View Marp: marp {output_dir}/slides.md")
        print(f"  • Export to PDF: marp {output_dir}/slides.md --pdf")

    return 0


if __name__ == "__main__":
    sys.exit(main())
