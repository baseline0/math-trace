"""The SIR presentation config must name only formulas that exist in the equations file.

A missing key shows as a warning on the slide, so this check fails in CI instead.
"""

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from math_trace.constants import REPO_ROOT

EXAMPLE = REPO_ROOT / "examples" / "epidemiology-sir"


@pytest.fixture(autouse=True)
def generated_sir_equations() -> Path:
    """Write the gitignored equations file when a fresh checkout lacks it.

    The file is produced by the example's own `export_formulas`, so the test
    checks the same output that `build_paper.py` writes.
    """
    output = EXAMPLE / "generated" / "sir_equations.json"
    if not output.exists():
        spec = importlib.util.spec_from_file_location("sir_model", EXAMPLE / "src" / "model.py")
        assert spec is not None and spec.loader is not None
        model = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(model)
        output.parent.mkdir(parents=True, exist_ok=True)
        model.export_formulas(output)
    return output


def test_every_formula_in_the_sir_config_exists_in_the_equations() -> None:
    config = yaml.safe_load((EXAMPLE / "presentation_config.yaml").read_text(encoding="utf-8"))
    equations = json.loads((EXAMPLE / "generated" / "sir_equations.json").read_text(encoding="utf-8"))["equations"]

    missing = [
        (slide.get("title"), name)
        for slide in config.get("slides", [])
        for name in slide.get("formulas") or []
        if not isinstance(equations.get(name), dict) or "latex" not in equations[name]
    ]

    assert missing == []
