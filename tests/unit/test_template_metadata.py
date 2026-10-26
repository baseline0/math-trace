"""Unit tests for the template equation-metadata guard, using throwaway template directories."""

import json
from pathlib import Path

import pytest

from math_trace import template_metadata as guard

ENERGY = {"latex": "E = mc^2", "code_ref": "model.py:mass_energy", "line": 2}
MODEL_WITH_METADATA = """
def mass_energy():
    return 1


def export_equation_metadata():
    return {"energy": {"latex": "E = mc^2", "code_ref": "model.py:mass_energy", "line": 2}}
"""


def make_template(root: Path, name: str, model: str | None, equations: dict | None) -> Path:
    template = root / name
    (template / "src").mkdir(parents=True)
    if model is not None:
        (template / "src" / "model.py").write_text(model)
    if equations is not None:
        (template / "equations.json").write_text(json.dumps(equations))
    return template


@pytest.fixture
def templates(tmp_path):
    return tmp_path / "templates"


def test_matching_equations_pass(templates):
    template = make_template(templates, "demo", MODEL_WITH_METADATA, {"energy": ENERGY})

    assert guard.check_template(template) == []


def test_stale_line_for_code_ref_is_reported(templates):
    stale = {**ENERGY, "line": 5}
    template = make_template(templates, "demo", MODEL_WITH_METADATA, {"energy": stale})

    messages = [p.message for p in guard.check_template(template)]

    assert "energy: line 5 but model.py:mass_energy is defined at line 2" in messages


def test_code_ref_to_missing_symbol_is_reported(templates):
    missing = {**ENERGY, "code_ref": "model.py:no_such_function"}
    template = make_template(templates, "demo", MODEL_WITH_METADATA, {"energy": missing})

    messages = [p.message for p in guard.check_template(template)]

    assert any(m.startswith("energy: no def or class 'no_such_function'") for m in messages)


def test_formula_source_line_must_start_a_formula_call(templates):
    model = """
from math_trace.formula import Formula


def export_equation_metadata():
    return {"energy": {"latex": "E = mc^2", "source_line": 1}}
"""
    template = make_template(templates, "demo", model, {"energy": {"latex": "E = mc^2", "source_line": 1}})

    problems = guard.check_template(template)

    assert [p.message for p in problems] == ["energy: source_line 1 is not where a Formula( call starts"]


def test_missing_metadata_function_is_reported(templates):
    template = make_template(templates, "demo", "def something_else():\n    return {}\n", {})

    problems = guard.check_template(template)

    assert [p.message for p in problems] == ["src/model.py does not define export_equation_metadata()"]


def test_missing_equations_file_is_reported(templates):
    template = make_template(templates, "demo", MODEL_WITH_METADATA, None)

    assert "equations.json is missing" in guard.check_template(template)[0].message


def test_hand_edited_equations_file_is_reported(templates):
    template = make_template(templates, "demo", MODEL_WITH_METADATA, {"energy": {**ENERGY, "latex": "E = m c^2"}})

    assert "differs from export_equation_metadata()" in guard.check_template(template)[0].message


def test_template_without_model_is_skipped(templates):
    template = templates / "bare"
    template.mkdir(parents=True)

    assert guard.check_template(template) == []


def test_exempt_template_without_function_passes(templates, monkeypatch):
    monkeypatch.setitem(guard.EXEMPT_TEMPLATES, "legacy", "writes its own JSON name")
    template = make_template(templates, "legacy", "def other():\n    return {}\n", None)

    assert guard.check_template(template) == []


def test_exemption_that_is_no_longer_needed_is_reported(templates, monkeypatch):
    monkeypatch.setitem(guard.EXEMPT_TEMPLATES, "migrated", "writes its own JSON name")
    template = make_template(templates, "migrated", MODEL_WITH_METADATA, {"energy": ENERGY})

    problems = guard.check_template(template)

    assert "remove it from EXEMPT_TEMPLATES" in problems[0].message


def test_check_all_visits_every_template_in_name_order(templates):
    make_template(templates, "beta", "def other():\n    return {}\n", None)
    make_template(templates, "alpha", "def other():\n    return {}\n", None)

    assert [p.template for p in guard.check_all(templates)] == ["alpha", "beta"]
