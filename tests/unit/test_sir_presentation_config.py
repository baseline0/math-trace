"""The SIR presentation config must name only formulas that exist in the equations file.

A missing key shows as a warning on the slide, so this check fails in CI instead.
"""

import json

import yaml

from math_trace.constants import REPO_ROOT

EXAMPLE = REPO_ROOT / "examples" / "epidemiology-sir"


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
