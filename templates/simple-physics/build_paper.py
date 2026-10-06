"""
Build pipeline: model.py → formulas.typ → simulation.png → main.typ → PDF

Uses shared template_builder utilities to:
1. Export SymPy formulas to JSON
2. Convert LaTeX formulas to Typst snippets
3. Run simulation
4. Generate matplotlib figures
5. Compile Typst document
"""

import subprocess
import sys
from pathlib import Path

try:
    from math_trace.template_builder import FigureGenerator, FormulaPipeline, run_build_pipeline
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from math_trace.template_builder import FigureGenerator, run_build_pipeline


def generate_figures() -> bool:
    """Run simulation and generate figure."""
    print("📊 Running simulation and generating figures...")

    try:
        import matplotlib
        from simulate import simulate_harmonic_oscillator

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

    # Run simulation
    t, x = simulate_harmonic_oscillator(amplitude=2.0, omega=0.5, steps=200, dt=0.1, seed=42)

    # Generate figure
    fig = plt.figure(figsize=(8, 5))
    plt.plot(t, x, linewidth=2, color="#2ca02c")
    plt.xlabel("Time (s)", fontsize=12)
    plt.ylabel("Position (m)", fontsize=12)
    plt.title("Harmonic Oscillator Trajectory", fontsize=14)
    plt.grid(alpha=0.3, linestyle="--")

    fig_gen = FigureGenerator()
    fig_gen.save_figure(fig, "oscillator.png")
    return True


def run_model_export() -> bool:
    """Export formulas from src/model.py."""
    result = subprocess.run([sys.executable, "src/model.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ src/model.py failed:\n{result.stderr}")
        return False
    return True


def main() -> bool:
    """Full build pipeline."""
    # Export formulas from model first
    if not run_model_export():
        return False

    return run_build_pipeline(
        equations_json="physics_equations.json",
        typst_file="main.typ",
        figure_generator=generate_figures,
        domain_name="physics",
    )


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
