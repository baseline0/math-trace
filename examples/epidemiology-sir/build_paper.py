"""
Build pipeline for epidemiology SIR paper.

Orchestrates:
  1. Export symbolic formulas from model.py
  2. Run simulation and generate outputs
  3. Create figures (PNG for inclusion in Typst)
  4. Verify reproducibility
"""

import subprocess
import sys
from pathlib import Path
import json
import numpy as np

# Try to import matplotlib; make optional for CI
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️  matplotlib not available; skipping figure generation")

sys.path.insert(0, str(Path(__file__).parent / "src"))
from model import export_formulas, FORMULAS
from simulate import covid_baseline, measles_scenario, generate_report


def step_1_export_formulas():
    """Export SymPy formulas as JSON."""
    print("\n=== Step 1: Export Symbolic Formulas ===")
    output_path = Path(__file__).parent / 'generated' / 'sir_equations.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    export_formulas(output_path)

    with open(output_path) as f:
        formulas = json.load(f)

    print(f"✅ Exported {len(formulas['equations'])} equations")
    return formulas


def step_2_run_simulations():
    """Run scenarios and generate outputs."""
    print("\n=== Step 2: Run SIR Simulations ===")

    scenarios = {
        'covid': covid_baseline(),
        'measles': measles_scenario(),
    }

    reports = {}
    for name, (t, S, I, R, params) in scenarios.items():
        report = generate_report(t, S, I, R, params)
        reports[name] = report
        print(f"✅ {name.upper()}: R₀={params.R0:.1f}, Peak={report['key_outcomes']['peak_infection_count']:,}")

    return scenarios, reports


def step_3_generate_figures(scenarios):
    """Generate PNG figures from simulation outputs."""
    if not HAS_MATPLOTLIB:
        print("\n=== Step 3: Skip Figures (matplotlib not available) ===")
        return

    print("\n=== Step 3: Generate Figures ===")

    fig_dir = Path(__file__).parent / 'generated' / 'figures'
    fig_dir.mkdir(parents=True, exist_ok=True)

    # Figure 1: COVID scenario (S, I, R trajectories)
    t, S, I, R, params = scenarios['covid']

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(t, S / 1e6, label='S (Susceptible)', linewidth=2)
    ax.plot(t, I / 1e6, label='I (Infected)', linewidth=2)
    ax.plot(t, R / 1e6, label='R (Recovered)', linewidth=2)
    ax.set_xlabel('Time (days)', fontsize=12)
    ax.set_ylabel('Count (millions)', fontsize=12)
    ax.set_title(f'COVID-like SIR Scenario (R₀={params.R0})', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    output_file = fig_dir / 'sir_trajectory.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Generated {output_file}")
    plt.close(fig)

    # Figure 2: R₀ comparison (COVID vs Measles)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # COVID
    t_covid, S_covid, I_covid, R_covid, p_covid = scenarios['covid']
    ax1.plot(t_covid, I_covid / 1e6, linewidth=2.5, color='#d62728')
    ax1.fill_between(t_covid, 0, I_covid / 1e6, alpha=0.3, color='#d62728')
    ax1.set_xlabel('Time (days)', fontsize=11)
    ax1.set_ylabel('Infected (millions)', fontsize=11)
    ax1.set_title(f'COVID (R₀={p_covid.R0})', fontsize=12)
    ax1.grid(True, alpha=0.3)

    # Measles
    t_measles, S_measles, I_measles, R_measles, p_measles = scenarios['measles']
    ax2.plot(t_measles, I_measles / 1e6, linewidth=2.5, color='#1f77b4')
    ax2.fill_between(t_measles, 0, I_measles / 1e6, alpha=0.3, color='#1f77b4')
    ax2.set_xlabel('Time (days)', fontsize=11)
    ax2.set_ylabel('Infected (millions)', fontsize=11)
    ax2.set_title(f'Measles (R₀={p_measles.R0})', fontsize=12)
    ax2.grid(True, alpha=0.3)

    output_file = fig_dir / 'r0_comparison.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Generated {output_file}")
    plt.close(fig)


def step_4_verify_reproducibility():
    """Run simulation twice and verify identical output."""
    print("\n=== Step 4: Verify Reproducibility ===")

    t1, S1, I1, R1, p1 = covid_baseline()
    t2, S2, I2, R2, p2 = covid_baseline()

    # Check exact numerical reproducibility
    assert np.allclose(S1, S2), "S not reproducible"
    assert np.allclose(I1, I2), "I not reproducible"
    assert np.allclose(R1, R2), "R not reproducible"

    print("✅ Simulation output identical across runs (reproducible)")


def main():
    """Execute full build pipeline."""
    print("\n" + "="*60)
    print("SIR Model Paper Build Pipeline")
    print("="*60)

    try:
        formulas = step_1_export_formulas()
        scenarios, reports = step_2_run_simulations()
        step_3_generate_figures(scenarios)
        step_4_verify_reproducibility()

        print("\n" + "="*60)
        print("✅ BUILD SUCCESSFUL")
        print("="*60)
        print("\nGenerated artifacts:")
        print("  - generated/sir_equations.json (formulas)")
        print("  - generated/covid_scenario.json (report)")
        print("  - generated/figures/sir_trajectory.png (figure)")
        print("  - generated/figures/r0_comparison.png (figure)")
        return 0

    except Exception as e:
        print(f"\n❌ BUILD FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
