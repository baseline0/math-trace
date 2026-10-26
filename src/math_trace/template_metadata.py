"""Guard for the template metadata pattern.

Every template's src/model.py defines export_equation_metadata(), and its equations.json is the output of that function.
This module checks, for each template, that:

1. src/model.py defines export_equation_metadata() at module level;
2. equations.json exists beside the template's model;
3. the JSON on disk equals what the function returns now, so a hand edit or a stale regeneration fails;
4. each recorded line points at the code it names: a dict entry's ``line`` is the def or class line of its
   ``code_ref``, and a Formula entry's ``source_line`` is a line where a ``Formula(...)`` call starts.
   See math_trace.code_refs.

Templates that do not yet follow the pattern are listed in EXEMPT_TEMPLATES with the reason. An exemption that is
no longer needed fails too, so the list cannot go stale.

Run by the pre-commit hook `template-equation-metadata`, or directly:
    uv run python -m math_trace.template_metadata
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from math_trace.code_refs import CodeRefError, formula_call_lines, resolve_code_ref
from math_trace.constants import REPO_ROOT

MODEL_FILE = Path("src") / "model.py"
EQUATIONS_FILE = "equations.json"
METADATA_FUNCTION = "export_equation_metadata"

# Templates that do not yet follow the pattern, with the reason. Empty now: every template defines
# export_equation_metadata() and writes equations.json. Add an entry only with a reason and a plan.
EXEMPT_TEMPLATES: dict[str, str] = {}


@dataclass(frozen=True)
class Problem:
    """One way a template departs from the pattern."""

    template: str
    message: str

    def render(self) -> str:
        return f"{self.template}: {self.message}"


def declares_metadata_function(model: Path) -> bool:
    """True when the module defines export_equation_metadata at top level. Reads the source; does not import it."""
    tree = ast.parse(model.read_text(), filename=str(model))
    return any(isinstance(node, ast.FunctionDef) and node.name == METADATA_FUNCTION for node in tree.body)


def load_metadata(model: Path) -> dict[str, Any]:
    """Import the model under a private name and return what export_equation_metadata() produces now."""
    module_name = f"_template_model_{model.parent.parent.name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, model)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {model}")
    module: ModuleType = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        metadata = getattr(module, METADATA_FUNCTION)()
    finally:
        sys.modules.pop(module_name, None)
    return json.loads(json.dumps(metadata))


def check_template(template_dir: Path) -> list[Problem]:
    """Problems for one template directory. Empty when it follows the pattern or has no model."""
    name = template_dir.name
    model = template_dir / MODEL_FILE
    if not model.exists():
        return []

    declares = declares_metadata_function(model)
    if name in EXEMPT_TEMPLATES:
        if declares:
            return [Problem(name, f"now defines {METADATA_FUNCTION}; remove it from EXEMPT_TEMPLATES")]
        return []
    if not declares:
        return [Problem(name, f"{MODEL_FILE} does not define {METADATA_FUNCTION}()")]

    equations = template_dir / EQUATIONS_FILE
    if not equations.exists():
        return [Problem(name, f"{EQUATIONS_FILE} is missing; run `python {MODEL_FILE}` in the template")]

    on_disk = json.loads(equations.read_text())
    generated = load_metadata(model)
    problems: list[Problem] = []
    if on_disk != generated:
        problems.append(
            Problem(
                name,
                f"{EQUATIONS_FILE} differs from {METADATA_FUNCTION}(); "
                f"regenerate with `python {MODEL_FILE}` in the template",
            )
        )
    problems.extend(line_problems(template_dir, on_disk))
    return problems


def line_problems(template_dir: Path, entries: dict[str, Any]) -> list[Problem]:
    """Recorded lines that do not point at the code they name. Reads the source; does not import it."""
    name = template_dir.name
    model = template_dir / MODEL_FILE
    call_lines = formula_call_lines(model.read_text())
    problems: list[Problem] = []
    for key, entry in entries.items():
        if "code_ref" in entry:
            try:
                expected = resolve_code_ref(template_dir, entry["code_ref"])
            except CodeRefError as error:
                problems.append(Problem(name, f"{key}: {error}"))
                continue
            if entry["line"] != expected:
                problems.append(
                    Problem(
                        name,
                        f"{key}: line {entry['line']} but {entry['code_ref']} is defined at line {expected}",
                    )
                )
        elif entry.get("source_line") not in call_lines:
            problems.append(
                Problem(name, f"{key}: source_line {entry.get('source_line')} is not where a Formula( call starts")
            )
    return problems


def check_all(templates_root: Path) -> list[Problem]:
    """Problems across every template directory under templates_root, in name order."""
    problems: list[Problem] = []
    for template_dir in sorted(p for p in templates_root.iterdir() if p.is_dir()):
        problems.extend(check_template(template_dir))
    return problems


def main() -> int:
    """Check every template in the repository. Returns 0 when all follow the pattern, 1 otherwise."""
    problems = check_all(REPO_ROOT / "templates")
    if not problems:
        print("✅ every template follows the equation-metadata pattern")
        return 0
    for problem in problems:
        print(f"❌ {problem.render()}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
