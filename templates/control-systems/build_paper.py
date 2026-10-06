import sys
from pathlib import Path

try:
    from math_trace.template_builder import run_build_pipeline
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from math_trace.template_builder import run_build_pipeline


def main() -> bool:
    return run_build_pipeline(
        equations_json="control_equations.json",
        typst_file="main.typ",
        figure_generator=None,
        domain_name="control-systems",
    )


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
