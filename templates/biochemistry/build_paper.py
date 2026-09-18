"""
Build pipeline: model.py → formulas.typ → kinetics.png → main.typ → PDF

Orchestrates the full publication workflow:
1. Export SymPy formulas to JSON
2. Convert LaTeX formulas to Typst snippets
3. Run enzyme kinetics simulation
4. Generate matplotlib figures
5. Compile Typst document
"""

import json
import subprocess
import sys
from pathlib import Path
import re


def generate_formulas() -> bool:
    """Convert SymPy formulas to Typst via LaTeX."""
    print("📐 Generating Typst formulas...")

    # 1. Run model.py to get JSON
    result = subprocess.run([sys.executable, 'model.py'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ model.py failed:\n{result.stderr}")
        return False

    if not Path('biochemistry_equations.json').exists():
        print("❌ model.py did not generate biochemistry_equations.json")
        return False

    # 2. Convert LaTeX → Typst (simple regex-based approach)
    with open('biochemistry_equations.json') as f:
        data = json.load(f)

    typst_lines = []
    for name, info in data.items():
        latex_str = info['latex']
        # Simple LaTeX to Typst conversion
        typst_str = latex_str
        typst_str = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\\1)/(\\2)', typst_str)
        typst_str = re.sub(r'\\left\(', '(', typst_str)
        typst_str = re.sub(r'\\right\)', ')', typst_str)
        typst_str = re.sub(r'\\rightarrow', '->', typst_str)

        comment = f"// {info['description']} (from model.py:{info['source_line']})"
        definition = f"#let {name} = $ {typst_str} $"
        typst_lines.append(f"{comment}\n{definition}")

    output = Path('generated/formulas.typ')
    output.parent.mkdir(exist_ok=True)
    output.write_text('\n\n'.join(typst_lines))
    print(f"✅ Generated {output}")
    return True


def generate_figures() -> bool:
    """Run simulation and generate figure."""
    print("📊 Running simulation and generating figures...")

    try:
        from simulate import simulate_enzyme_kinetics, michaelis_menten
        import matplotlib
        matplotlib.use('Agg')
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
    ax1.plot(S_ideal, v_ideal, 'b-', linewidth=2, label='Ideal')
    ax1.scatter(S, v, alpha=0.6, s=30, color='orange', label='Measured')
    ax1.set_xlabel('[S] (mM)', fontsize=12)
    ax1.set_ylabel('v (umol/min)', fontsize=12)
    ax1.set_title('Michaelis-Menten Kinetics', fontsize=14)
    ax1.legend()
    ax1.grid(alpha=0.3)

    # Right: Double reciprocal (Lineweaver-Burk)
    ax2.plot(1/S_ideal, 1/v_ideal, 'b-', linewidth=2, label='Ideal')
    ax2.scatter(1/S, 1/v, alpha=0.6, s=30, color='orange', label='Measured')
    ax2.set_xlabel('1/[S] (mM^-1)', fontsize=12)
    ax2.set_ylabel('1/v (min/umol)', fontsize=12)
    ax2.set_title('Lineweaver-Burk Plot', fontsize=14)
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()

    fig_path = Path('generated/figures/kinetics.png')
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"✅ Generated {fig_path}")
    plt.close()
    return True


def build_pdf() -> bool:
    """Compile Typst document to PDF."""
    print("📝 Building Typst document...")

    if not Path('main.typ').exists():
        print("❌ main.typ not found")
        return False

    # Check if typst is available
    check_typst = subprocess.run(
        ['which', 'typst'],
        capture_output=True,
        text=True
    )

    if check_typst.returncode != 0:
        print("⚠️  Typst not found. To generate PDF:")
        print("   Run: cd ../.. && just install-typst")
        print("   Or visit: https://github.com/typst/typst/releases")
        print("   (Typst file is ready at: main.typ)")
        return True  # Not a hard failure—formulas are ready

    result = subprocess.run(
        ['typst', 'compile', 'main.typ'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        if Path('main.pdf').exists():
            print(f"✅ Generated main.pdf")
            return True
        else:
            print("❌ Typst compiled but main.pdf not found")
            return False
    else:
        print(f"❌ Typst compilation failed:\n{result.stderr}")
        return False


def main() -> bool:
    """Full build pipeline."""
    print("🚀 Building biochemistry paper...\n")

    steps = [
        ('Formulas', generate_formulas),
        ('Figures', generate_figures),
        ('PDF', build_pdf),
    ]

    pdf_generated = True
    for name, step in steps:
        if not step():
            if name == 'PDF':
                pdf_generated = False
                # Don't fail on missing Typst—formulas are still useful
            else:
                print(f"\n❌ Failed at step: {name}")
                return False

    if pdf_generated and Path('main.pdf').exists():
        print("\n✅ Paper built successfully: main.pdf")
    else:
        print("\n✅ Formulas and figures ready!")
        if not pdf_generated:
            print("   (PDF generation requires Typst: run 'cd ../.. && just install-typst')")
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
