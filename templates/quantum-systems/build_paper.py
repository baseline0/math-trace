"""
Build pipeline: model.py → formulas.typ → main.typ → PDF

Uses shared template_builder utilities for quantum systems formulas.
Placeholder figure generation (to be implemented with simulation).
"""

import sys
from pathlib import Path

try:
    from math_trace.template_builder import run_build_pipeline
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
    from math_trace.template_builder import run_build_pipeline


def run_model_export() -> bool:
    """Export formulas from src/model.py."""
    import subprocess
    result = subprocess.run([sys.executable, 'src/model.py'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ src/model.py failed:\n{result.stderr}")
        return False
    return True


def generate_figures() -> bool:
    """Generate quantum systems visualization.

    Placeholder: implement with numerical solution of Schrödinger equation.
    """
    print("📊 Figure generation: stub (not implemented)")
    return True


def main() -> bool:
    """Full build pipeline."""
    # Export formulas from model first
    if not run_model_export():
        return False

    return run_build_pipeline(
        equations_json='quantum_systems_equations.json',
        typst_file='main.typ',
        figure_generator=None,  # TODO: implement simulation figures
        domain_name='quantum systems'
    )


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
