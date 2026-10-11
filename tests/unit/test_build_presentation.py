"""Tests for the SIR presentation builder: pure helpers and the Typer wiring."""

import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

import pytest
from typer.testing import CliRunner

from math_trace.constants import REPO_ROOT

SCRIPT = REPO_ROOT / "examples" / "epidemiology-sir" / "build_presentation.py"


def _load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_presentation_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bp = _load_script()
runner = CliRunner()


class FakeGenerator:
    """Records calls and returns predictable output paths."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, Path]] = []

    def build(self, backend: str, output_dir: Path) -> Path:
        self.calls.append((backend, output_dir))
        return output_dir / f"{backend}.out"

    def build_all(self, output_dir: Path) -> dict[str, Path]:
        self.calls.append(("all", output_dir))
        return {name: output_dir / f"{name}.out" for name in ("marp", "reveal")}


def test_default_paths_are_relative_to_the_example_folder(tmp_path: Path) -> None:
    model, config, out = bp.default_paths(tmp_path)

    assert model == tmp_path / "generated" / "sir_equations.json"
    assert config == tmp_path / "presentation_config.yaml"
    assert out == tmp_path / "generated"


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


def test_build_outputs_single_backend_calls_build_once(tmp_path: Path) -> None:
    gen = FakeGenerator()

    results = bp.build_outputs(gen, bp.Backend.REVEAL, False, tmp_path)

    assert results == [("reveal", tmp_path / "reveal.out")]
    assert gen.calls == [("reveal", tmp_path)]


def test_build_outputs_all_uses_build_all(tmp_path: Path) -> None:
    gen = FakeGenerator()

    results = bp.build_outputs(gen, bp.Backend.MARP, True, tmp_path)

    assert results == [("marp", tmp_path / "marp.out"), ("reveal", tmp_path / "reveal.out")]
    assert gen.calls == [("all", tmp_path)]


def test_start_line_names_the_backend_or_all_formats() -> None:
    assert bp.start_line(bp.Backend.BEAMER, False) == "🎬 Building beamer presentation..."
    assert bp.start_line(bp.Backend.MARP, True) == "🎬 Building presentations in all formats..."


def test_result_lines_single_and_all(tmp_path: Path) -> None:
    single = [("marp", tmp_path / "x.html")]
    many = [("marp", tmp_path / "a"), ("beamer", tmp_path / "b")]

    assert bp.result_lines(single, False) == [f"  ✅ Generated: {tmp_path / 'x.html'}"]
    assert bp.result_lines(many, True) == [
        f"  ✅ marp       → {tmp_path / 'a'}",
        f"  ✅ beamer     → {tmp_path / 'b'}",
    ]


@pytest.mark.parametrize(
    ("backend", "build_all", "expects_marp_hints"),
    [
        (bp.Backend.MARP, False, True),
        (bp.Backend.REVEAL, False, False),
        (bp.Backend.REVEAL, True, True),
    ],
)
def test_next_steps_show_marp_hints_only_for_marp_or_all(
    tmp_path: Path, backend: bp.Backend, build_all: bool, expects_marp_hints: bool
) -> None:
    lines = bp.next_steps_lines(tmp_path, backend, build_all)

    assert lines[0] == "\n📊 Next steps:"
    assert (len(lines) == 3) is expects_marp_hints


def test_cli_missing_inputs_exit_1_with_messages(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bp, "default_paths", lambda _: (tmp_path / "m.json", tmp_path / "c.yaml", tmp_path))

    result = runner.invoke(bp.app, [])

    assert result.exit_code == 1
    assert "not found. Run build_paper.py first." in result.output
    assert "Create presentation configuration." in result.output


def test_cli_builds_marp_by_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "m.json").write_text("{}")
    (tmp_path / "c.yaml").write_text("")
    gen = FakeGenerator()
    monkeypatch.setattr(bp, "default_paths", lambda _: (tmp_path / "m.json", tmp_path / "c.yaml", tmp_path))
    monkeypatch.setattr(bp, "_load_generator", lambda *_: gen)

    result = runner.invoke(bp.app, [])

    assert result.exit_code == 0
    assert gen.calls == [("marp", tmp_path)]
    assert "🎬 Building marp presentation..." in result.output
    assert "View Marp:" in result.output


def test_cli_all_with_output_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "m.json").write_text("{}")
    (tmp_path / "c.yaml").write_text("")
    out = tmp_path / "custom"
    gen = FakeGenerator()
    monkeypatch.setattr(bp, "default_paths", lambda _: (tmp_path / "m.json", tmp_path / "c.yaml", tmp_path))
    monkeypatch.setattr(bp, "_load_generator", lambda *_: gen)

    result = runner.invoke(bp.app, ["--all", "--output", str(out)])

    assert result.exit_code == 0
    assert gen.calls == [("all", out)]
    assert "✅ marp       →" in result.output


def test_load_generator_reports_the_removing_commit_when_module_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(sys.modules, "math_trace.presentation_generator", None)

    with pytest.raises(
        bp.GeneratorUnavailableError, match=re.escape("math_trace.presentation_generator is missing")
    ) as info:
        bp._load_generator(tmp_path / "m.json", tmp_path / "c.yaml")

    assert "d8c5fb9" in str(info.value)


def test_cli_missing_generator_exits_1_with_clear_message(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "m.json").write_text("{}")
    (tmp_path / "c.yaml").write_text("")
    monkeypatch.setattr(bp, "default_paths", lambda _: (tmp_path / "m.json", tmp_path / "c.yaml", tmp_path))
    monkeypatch.setitem(sys.modules, "math_trace.presentation_generator", None)

    result = runner.invoke(bp.app, [])

    assert result.exit_code == 1
    assert "math_trace.presentation_generator is missing" in result.output
    assert "d8c5fb9" in result.output
    assert "Traceback" not in result.output


def test_cli_rejects_unknown_backend() -> None:
    result = runner.invoke(bp.app, ["--backend", "pptx"])

    assert result.exit_code == 2
