"""
Build pipeline: model.py → formulas.typ → main.typ → PDF

Orchestrates the full publication workflow:
1. Export SymPy formulas to JSON
2. Convert LaTeX formulas to Typst snippets
3. Run quantum simulations
4. Generate matplotlib figures
5. Compile Typst document
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from math_trace.generators import SymPyToTypst


def generate_formulas() -> bool:
    """Convert SymPy formulas to Typst via LaTeX."""
    print("📐 Generating Typst formulas...")

    # 1. Run src/model.py to get JSON
    result = subprocess.run([sys.executable, "src/model.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ model.py failed:\n{result.stderr}")
        return False

    if not Path("quantum_systems_equations.json").exists():
        print("❌ model.py did not generate quantum_systems_equations.json")
        return False

    # 2. Convert LaTeX → Typst
    with open("quantum_systems_equations.json") as f:
        data = json.load(f)

    converter = SymPyToTypst()
    typst_lines = []
    for name, info in data.items():
        latex_str = info["latex"]
        typst_str = converter._latex_to_typst(latex_str)

        comment = f"// {info['description']} (from model.py:{info['source_line']})"
        definition = f"#let {name} = $ {typst_str} $"
        typst_lines.append(f"{comment}\n{definition}")

    output = Path("generated/formulas.typ")
    output.parent.mkdir(exist_ok=True)
    output.write_text("\n\n".join(typst_lines))
    print(f"✅ Generated {output}")
    return True


def generate_figures() -> bool:
    """Run simulations and generate figures."""
    print("📊 Running simulations and generating figures...")

    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        import matplotlib

        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt
        from simulate import simulate_harmonic_oscillator, simulate_particle_in_box
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

    # Create output directory
    Path("generated/figures").mkdir(parents=True, exist_ok=True)

    # Plot 1: Particle in a box and harmonic oscillator wavefunctions
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Particle in box
    x_box, psi_box = simulate_particle_in_box()
    ax1.plot(x_box, psi_box, linewidth=2, label="n=1 (ground state)")
    ax1.fill_between(x_box, 0, psi_box**2, alpha=0.3, label="Probability density")
    ax1.set_xlabel("Position x", fontsize=11)
    ax1.set_ylabel("Wavefunction ψ(x)", fontsize=11)
    ax1.set_title("Particle in a Box (L=1)", fontsize=12)
    ax1.legend()
    ax1.grid(alpha=0.3, linestyle="--")

    # Harmonic oscillator
    x_ho, psi_ho = simulate_harmonic_oscillator()
    ax2.plot(x_ho, psi_ho, linewidth=2, label="n=0 (ground state)")
    ax2.fill_between(x_ho, 0, psi_ho**2, alpha=0.3, label="Probability density")
    ax2.set_xlabel("Position x", fontsize=11)
    ax2.set_ylabel("Wavefunction ψ(x)", fontsize=11)
    ax2.set_title("Harmonic Oscillator (ω=1)", fontsize=12)
    ax2.legend()
    ax2.grid(alpha=0.3, linestyle="--")

    plt.tight_layout()
    plt.savefig("generated/figures/wavefunctions.png", dpi=300, bbox_inches="tight")
    print("✅ Generated wavefunctions.png")
    plt.close()

    # Plot 2: Energy level diagram
    _, ax = plt.subplots(figsize=(8, 6))

    # Particle in box energy levels
    n_levels = 5
    energies_box = np.arange(1, n_levels + 1) ** 2 * np.pi**2 / 2
    ax.hlines(energies_box, -0.2, 0.2, colors="blue", linewidth=2, label="Particle in Box")

    # Harmonic oscillator energy levels
    omega = 1.0
    energies_ho = (np.arange(n_levels) + 0.5) * omega
    ax.hlines(energies_ho, 0.8, 1.2, colors="red", linewidth=2, label="Harmonic Oscillator")

    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(0, 30)
    ax.set_ylabel("Energy E", fontsize=12)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Box", "Oscillator"])
    ax.set_title("Energy Level Comparison", fontsize=13)
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3, axis="y", linestyle="--")

    plt.tight_layout()
    plt.savefig("generated/figures/energy_levels.png", dpi=300, bbox_inches="tight")
    print("✅ Generated energy_levels.png")
    plt.close()
    return True


def build_pdf() -> bool:
    """Compile Typst document to PDF."""
    print("📝 Building Typst document...")

    if not Path("main.typ").exists():
        print("❌ main.typ not found")
        return False

    # Check if typst is available
    check_typst = subprocess.run(["which", "typst"], capture_output=True, text=True)

    if check_typst.returncode != 0:
        print("⚠️  Typst not found. To generate PDF:")
        print("   Run: just install-typst")
        print("   Or visit: https://github.com/typst/typst/releases")
        print("   (Typst file is ready at: main.typ)")
        return True  # Not a hard failure—formulas are ready

    result = subprocess.run(["typst", "compile", "main.typ"], capture_output=True, text=True)

    if result.returncode == 0:
        if Path("main.pdf").exists():
            print("✅ Generated main.pdf")
            return True
        else:
            print("❌ Typst compiled but main.pdf not found")
            return False
    else:
        print(f"❌ Typst compilation failed:\n{result.stderr}")
        return False


def main() -> bool:
    """Full build pipeline."""
    print("🚀 Building quantum systems paper...\n")

    steps = [
        ("Formulas", generate_formulas),
        ("Figures", generate_figures),
        ("PDF", build_pdf),
    ]

    pdf_generated = True
    for name, step in steps:
        if not step():
            if name == "PDF":
                pdf_generated = False
                # Don't fail on missing Typst—formulas are still useful
            else:
                print(f"\n❌ Failed at step: {name}")
                return False

    if pdf_generated and Path("main.pdf").exists():
        print("\n✅ Paper built successfully: main.pdf")
    else:
        print("\n✅ Formulas and figures ready!")
        if not pdf_generated:
            print("   (PDF generation requires Typst: run 'just install-typst')")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
