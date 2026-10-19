"""Tests for the SIR presentation builder: pure helpers and the Typer wiring."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest
from typer.testing import CliRunner

from math_trace.constants import REPO_ROOT
from math_trace.revealjs_generator import Slide

SCRIPT = REPO_ROOT / "examples" / "epidemiology-sir" / "build_presentation.py"


def _load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_presentation_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bp = _load_script()
runner = CliRunner()

FIXTURE_MODEL = '{"equations": {"R0": {"latex": "\\\\frac{\\\\beta}{\\\\gamma}", "description": "R0"}}}'
FIXTURE_CONFIG = """\
title: "Fixture <Deck> & Co"
metadata:
  author: "Test Author"
paper_url: "https://example.org/paper"
slides:
  - title: "Intro"
    text: "Hello **world**"
  - title: "Ratio"
    text: "R0 below"
    formulas: ["R0", "R_0"]
    figure: "generated/figures/r0.png"
"""


def _write_fixture_inputs(folder: Path) -> tuple[Path, Path]:
    model = folder / "sir_equations.json"
    config = folder / "presentation_config.yaml"
    model.write_text(FIXTURE_MODEL, encoding="utf-8")
    config.write_text(FIXTURE_CONFIG, encoding="utf-8")
    return model, config


def test_default_paths_are_relative_to_the_example_folder(tmp_path: Path) -> None:
    model, config, output = bp.default_paths(tmp_path)

    assert model == tmp_path / "generated" / "sir_equations.json"
    assert config == tmp_path / "presentation_config.yaml"
    assert output == tmp_path / "generated" / "presentation.html"


def test_input_errors_empty_when_both_inputs_exist(tmp_path: Path) -> None:
    model = tmp_path / "m.json"
    config = tmp_path / "c.yaml"
    model.write_text("{}")
    config.write_text("")

    assert bp.input_errors(model, config) == []


def test_input_errors_reports_each_missing_file(tmp_path: Path) -> None:
    errors = bp.input_errors(tmp_path / "m.json", tmp_path / "c.yaml")

    assert errors == [
        f"❌ {tmp_path / 'm.json'} not found. Run build_paper.py first.",
        f"❌ {tmp_path / 'c.yaml'} not found. Create presentation configuration.",
    ]


def test_warning_lines_name_the_slide_and_message() -> None:
    slides = [
        Slide(title="Clean"),
        Slide(title="Ratio", warnings=("formula 'R_0' not found in model equations",)),
    ]

    assert bp.warning_lines(slides) == ["  ⚠️  Slide 'Ratio': formula 'R_0' not found in model equations"]


def test_warning_lines_empty_when_no_slide_warns() -> None:
    assert bp.warning_lines([Slide(title="Clean")]) == []


def test_result_lines_report_the_written_file(tmp_path: Path) -> None:
    assert bp.result_lines(tmp_path / "p.html") == [f"  ✅ Generated: {tmp_path / 'p.html'}"]


def test_next_steps_point_at_the_file_and_mention_network_access(tmp_path: Path) -> None:
    lines = bp.next_steps_lines(tmp_path / "p.html")

    assert lines[0] == "\n📊 Next steps:"
    assert f"  • Open in a browser: {tmp_path / 'p.html'}" in lines
    assert any("network access" in line for line in lines)


def test_cli_missing_inputs_exit_1_with_messages(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bp, "default_paths", lambda _: (tmp_path / "m.json", tmp_path / "c.yaml", tmp_path / "p.html"))

    result = runner.invoke(bp.app, ["--output", str(tmp_path / "deck.html")])

    assert result.exit_code == 1
    assert "not found. Run build_paper.py first." in result.output
    assert "Create presentation configuration." in result.output


def test_cli_end_to_end_writes_revealjs_html_to_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    model, config = _write_fixture_inputs(tmp_path)
    out = tmp_path / "out" / "deck.html"
    monkeypatch.setattr(bp, "default_paths", lambda _: (model, config, tmp_path / "unused.html"))

    result = runner.invoke(bp.app, ["--output", str(out)])

    assert result.exit_code == 0, result.output
    assert out.exists()
    html_text = out.read_text(encoding="utf-8")
    assert "reveal.js@" in html_text
    assert "Reveal.initialize(" in html_text
    assert "<h2>Intro</h2>" in html_text
    assert "<title>Fixture &lt;Deck&gt; &amp; Co</title>" in html_text
    assert "Hello <strong>world</strong>" in html_text
    assert "Warning: formula &#x27;R_0&#x27; not found" in html_text
    assert "Generated:" in result.output
    assert "Traceback" not in result.output


def test_cli_rejects_removed_backend_and_all_options() -> None:
    assert runner.invoke(bp.app, ["--backend", "marp"]).exit_code == 2
    assert runner.invoke(bp.app, ["--all"]).exit_code == 2
