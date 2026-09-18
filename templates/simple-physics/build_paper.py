"""
Build pipeline: model.py → formulas.typ → simulation.png → main.typ → PDF

Orchestrates the full publication workflow:
1. Export SymPy formulas to JSON
2. Convert LaTeX formulas to Typst snippets
3. Run simulation
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

    if not Path('physics_equations.json').exists():
        print("❌ model.py did not generate physics_equations.json")
        return False

    # 2. Convert LaTeX → Typst (simple regex-based approach)
    with open('physics_equations.json') as f:
        data = json.load(f)

    typst_lines = []
    for name, info in data.items():
        latex_str = info['latex']
        # Simple LaTeX to Typst conversion
        typst_str = latex_str
        typst_str = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\\1)/(\\2)', typst_str)
        typst_str = re.sub(r'\\left\(', '(', typst_str)
        typst_str = re.sub(r'\\right\)', ')', typst_str)

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
        from simulate import simulate_harmonic_oscillator
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

    # Run simulation
    t, x = simulate_harmonic_oscillator(amplitude=2.0, omega=0.5, steps=200, dt=0.1, seed=42)

    # Generate figure
    plt.figure(figsize=(8, 5))
    plt.plot(t, x, linewidth=2, color='#2ca02c')
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Position (m)', fontsize=12)
    plt.title('Harmonic Oscillator Trajectory', fontsize=14)
    plt.grid(alpha=0.3, linestyle='--')
    plt.tight_layout()

    fig_path = Path('generated/figures/oscillator.png')
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
    print("🚀 Building physics paper...\n")

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
