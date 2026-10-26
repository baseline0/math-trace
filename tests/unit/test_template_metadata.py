"""Unit tests for the template equation-metadata guard, using throwaway template directories."""

import json
from pathlib import Path

import pytest

from math_trace import template_metadata as guard

MODEL_WITH_METADATA = """
def export_equation_metadata():
    return {"energy": {"latex": "E = mc^2", "line": 1}}
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
    template = make_template(templates, "demo", MODEL_WITH_METADATA, {"energy": {"latex": "E = mc^2", "line": 1}})

    assert guard.check_template(template) == []


def test_missing_metadata_function_is_reported(templates):
    template = make_template(templates, "demo", "def something_else():\n    return {}\n", {})

    problems = guard.check_template(template)

    assert [p.message for p in problems] == ["src/model.py does not define export_equation_metadata()"]


def test_missing_equations_file_is_reported(templates):
    template = make_template(templates, "demo", MODEL_WITH_METADATA, None)

    assert "equations.json is missing" in guard.check_template(template)[0].message


def test_hand_edited_equations_file_is_reported(templates):
    template = make_template(templates, "demo", MODEL_WITH_METADATA, {"energy": {"latex": "E = m c^2", "line": 1}})

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
    template = make_template(templates, "migrated", MODEL_WITH_METADATA, {"energy": {"latex": "E = mc^2", "line": 1}})

    problems = guard.check_template(template)

    assert "remove it from EXEMPT_TEMPLATES" in problems[0].message


def test_check_all_visits_every_template_in_name_order(templates):
    make_template(templates, "beta", "def other():\n    return {}\n", None)
    make_template(templates, "alpha", "def other():\n    return {}\n", None)

    assert [p.template for p in guard.check_all(templates)] == ["alpha", "beta"]
