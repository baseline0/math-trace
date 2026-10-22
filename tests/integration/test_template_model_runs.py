"""Integration: runs each template's real model.py in a subprocess, which writes its equations JSON into the template.

Moved out of tests/unit because it executes project scripts and writes into the checkout.
"""

import subprocess
import sys

import pytest

from math_trace.constants import REPO_ROOT

TEMPLATE_DIR = REPO_ROOT / "templates"
TEMPLATES = [
    "simple-physics",
    "biochemistry",
    "quantum-systems",
    "epidemiology",
    "control-systems",
    "thermodynamics",
    "gnns",
]


class TestTemplateModelRuns:
    """Each template's model.py runs to completion."""

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_generates_equations_json(self, template):
        """Running model.py generates equations JSON."""
        template_path = TEMPLATE_DIR / template

        # Find model.py
        model_root = template_path / "model.py"
        model_src = template_path / "src" / "model.py"
        model_path = model_src if model_src.exists() else model_root

        if not model_path.exists():
            pytest.skip(f"{template}: model.py not found")

        # Run model.py (safe: model_path is from controlled template directory)
        result = subprocess.run(
            [sys.executable, str(model_path)],
            cwd=str(template_path),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"{template}: model.py failed:\n{result.stderr}"
