"""
Build pipeline: model.py → formulas.typ → kinetics.png → main.typ → PDF

Uses shared template_builder utilities to:
1. Export SymPy formulas to JSON
2. Convert LaTeX formulas to Typst snippets
3. Run enzyme kinetics simulation
4. Generate matplotlib figures
5. Compile Typst document
"""

import sys
from pathlib import Path

try:
    from math_trace.template_builder import FigureGenerator, run_build_pipeline
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from math_trace.template_builder import FigureGenerator, run_build_pipeline


def generate_figures() -> bool:
    """Run simulation and generate figure."""
    print("📊 Running simulation and generating figures...")

    try:
        import matplotlib
        from simulate import michaelis_menten, simulate_enzyme_kinetics

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

    # Run simulation
    S, v = simulate_enzyme_kinetics(Vmax=100.0, Km=5.0, steps=100, S_max=50.0, seed=42)

    # Generate figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Michaelis-Menten curve with data
    S_ideal = np.linspace(0.01, 50, 200)
    v_ideal = michaelis_menten(S_ideal, 100.0, 5.0)
    ax1.plot(S_ideal, v_ideal, "b-", linewidth=2, label="Ideal")
    ax1.scatter(S, v, alpha=0.6, s=30, color="orange", label="Measured")
    ax1.set_xlabel("[S] (mM)", fontsize=12)
    ax1.set_ylabel("v (umol/min)", fontsize=12)
    ax1.set_title("Michaelis-Menten Kinetics", fontsize=14)
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Right: Double reciprocal (Lineweaver-Burk)
    ax2.plot(1 / S_ideal, 1 / v_ideal, "b-", linewidth=2, label="Ideal")
    ax2.scatter(1 / S, 1 / v, alpha=0.6, s=30, color="orange", label="Measured")
    ax2.set_xlabel("1/[S] (mM^-1)", fontsize=12)
    ax2.set_ylabel("1/v (min/umol)", fontsize=12)
    ax2.set_title("Lineweaver-Burk Plot", fontsize=14)
    ax2.legend()
    ax2.grid(alpha=0.3)

    fig_gen = FigureGenerator()
    fig_gen.save_figure(fig, "kinetics.png")
    return True


def run_model_export() -> bool:
    """Export formulas from src/model.py."""
    import subprocess

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
        equations_json="biochemistry_equations.json",
        typst_file="main.typ",
        figure_generator=generate_figures,
        domain_name="biochemistry",
    )


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
