"""Unit tests for resolving code_ref symbols to the line of their def or class statement."""

from pathlib import Path

import pytest

from math_trace.code_refs import CodeRefError, formula_call_lines, resolve_code_ref, symbol_line

SOURCE = """\
class LinearSystem:
    def is_stable(self):
        return True


async def simulate():
    return 0


def steady_state_error():
    return 1


x = Formula(name="x")
"""


def test_class_resolves_to_its_class_line() -> None:
    assert symbol_line(SOURCE, "LinearSystem") == 1


def test_method_with_parentheses_resolves_through_its_class() -> None:
    assert symbol_line(SOURCE, "LinearSystem.is_stable()") == 2


def test_function_with_parentheses_resolves_to_its_def_line() -> None:
    assert symbol_line(SOURCE, "steady_state_error()") == 10


def test_async_function_resolves() -> None:
    assert symbol_line(SOURCE, "simulate") == 6


def test_missing_symbol_raises() -> None:
    with pytest.raises(CodeRefError, match="missing 'nope'"):
        symbol_line(SOURCE, "nope()")


def test_assignment_is_not_a_symbol() -> None:
    with pytest.raises(CodeRefError):
        symbol_line(SOURCE, "x")


def test_formula_call_lines_finds_each_constructor_call() -> None:
    source = "a = Formula(\n    name='a',\n)\nb = Other()\nc = Formula(name='c')\n"

    assert formula_call_lines(source) == {1, 5}


def test_resolve_code_ref_prefers_src_then_template_root(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "model.py").write_text("def f():\n    return 1\n")
    (tmp_path / "other.py").write_text("\n\ndef g():\n    return 2\n")

    assert resolve_code_ref(tmp_path, "model.py:f()") == 1
    assert resolve_code_ref(tmp_path, "other.py:g()") == 3


def test_resolve_code_ref_rejects_malformed_and_missing(tmp_path: Path) -> None:
    with pytest.raises(CodeRefError, match="must look like"):
        resolve_code_ref(tmp_path, "model.py")
    with pytest.raises(CodeRefError, match="no such file"):
        resolve_code_ref(tmp_path, "ghost.py:f()")
