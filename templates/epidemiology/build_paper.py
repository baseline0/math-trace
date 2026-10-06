"""
Build pipeline: model.py → formulas.typ → simulation.png → main.typ → PDF

Uses shared template_builder utilities to:
1. Export SymPy formulas from model.py to JSON
2. Convert LaTeX formulas to Typst snippets
3. Run simulation scenarios
4. Generate matplotlib figures
5. Compile Typst document to PDF
"""

import sys
from pathlib import Path

try:
    from math_trace.template_builder import FigureGenerator, run_build_pipeline
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from math_trace.template_builder import FigureGenerator, run_build_pipeline


def generate_figures() -> bool:
    """Run simulations and generate comparative figure."""
    print("📊 Running disease simulations and generating figures...")

    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        import matplotlib
        from simulate import covid_baseline, intervention_scenario, measles_scenario

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

    # Run scenarios
    t_covid, S_covid, I_covid = covid_baseline()
    t_measles, S_measles, E_measles, I_measles = measles_scenario()
    t_int, S_int, I_int = intervention_scenario()

    # Generate comparison figure
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # COVID baseline
    axes[0].plot(t_covid, I_covid * 100, "b-", linewidth=2, label="I(t)")
    axes[0].plot(t_covid, S_covid * 100, "orange", linewidth=2, label="S(t)")
    axes[0].set_xlabel("Days", fontsize=11)
    axes[0].set_ylabel("Proportion (%)", fontsize=11)
    axes[0].set_title("COVID-19 Baseline (SIR)", fontsize=12, fontweight="bold")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Measles outbreak
    axes[1].plot(t_measles, I_measles * 100, "r-", linewidth=2, label="I(t)")
    axes[1].plot(t_measles, S_measles * 100, "orange", linewidth=2, label="S(t)")
    axes[1].set_xlabel("Days", fontsize=11)
    axes[1].set_ylabel("Proportion (%)", fontsize=11)
    axes[1].set_title("Measles Outbreak (SEIR)", fontsize=12, fontweight="bold")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    # Intervention impact
    axes[2].plot(t_int, I_int * 100, "purple", linewidth=2, label="Lockdown at day 50")
    t_covid_only, S_covid_only, I_covid_only = covid_baseline(days=200)
    axes[2].plot(t_covid_only, I_covid_only * 100, "b--", linewidth=1.5, alpha=0.6, label="No intervention")
    axes[2].axvline(x=50, color="red", linestyle=":", alpha=0.7, label="Intervention start")
    axes[2].set_xlabel("Days", fontsize=11)
    axes[2].set_ylabel("Infected (%)", fontsize=11)
    axes[2].set_title("Intervention Impact (SIR)", fontsize=12, fontweight="bold")
    axes[2].legend()
    axes[2].grid(alpha=0.3)

    plt.tight_layout()

    fig_gen = FigureGenerator()
    fig_gen.save_figure(fig, "epidemiology_scenarios.png")
    return True


def main() -> bool:
    """Full build pipeline."""
    return run_build_pipeline(
        equations_json="sir_equations.json",
        typst_file="main.typ",
        figure_generator=generate_figures,
        domain_name="epidemiology",
    )


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
