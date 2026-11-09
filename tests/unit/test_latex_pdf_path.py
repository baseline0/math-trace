"""The LaTeX publisher reads the PDF its compiler writes: /tmp/<stem>.pdf."""

from pathlib import Path

from math_trace.publishers import _latex_pdf_path


def test_pdf_path_is_stem_dot_pdf_in_tmp() -> None:
    assert _latex_pdf_path(Path("/work/main.tex")) == Path("/tmp/main.pdf")


def test_pdf_path_keeps_only_the_stem() -> None:
    assert _latex_pdf_path(Path("paper.v2.tex")) == Path("/tmp/paper.v2.pdf")
