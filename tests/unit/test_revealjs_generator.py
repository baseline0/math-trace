"""Tests for the Revealjs generator: slide building, HTML rendering, escaping, and file output."""

from pathlib import Path
from typing import Any

from math_trace.revealjs_generator import (
    MATHJAX_VERSION,
    REVEAL_VERSION,
    Equation,
    PresentationInputs,
    Slide,
    build_slides,
    load_presentation_inputs,
    markdown_to_html,
    relocate_figures,
    render_html,
    write_presentation,
)


def _fixture_inputs(slides: list[dict[str, Any]] | None = None) -> PresentationInputs:
    model: dict[str, Any] = {
        "equations": {
            "dS_dt": {"latex": r"- \frac{I S \beta}{N}", "description": "Susceptible rate"},
            "R0": {"latex": r"\frac{\beta}{\gamma}", "description": "Reproduction number"},
        }
    }
    config: dict[str, Any] = {
        "title": "Fixture Deck",
        "metadata": {"author": "Test Author", "date": "2026", "affiliation": "Lab"},
        "paper_url": "https://example.org/paper",
        "paper_doi": "10.0000/fixture",
        "slides": slides
        if slides is not None
        else [
            {"title": "First", "text": "Intro line", "notes": "say hi"},
            {"title": "Second", "text": "- one\n- two", "formulas": ["dS_dt"], "figure": "generated/f.png"},
            {"title": "Third", "text": "Ratio", "formulas": ["R0", "missing_name"]},
        ],
    }
    return PresentationInputs(model=model, config=config)


def test_build_slides_puts_title_slide_first_then_config_order() -> None:
    slides = build_slides(_fixture_inputs())

    assert [s.title for s in slides] == ["Fixture Deck", "First", "Second", "Third"]
    assert "**Test Author**" in slides[0].body
    assert "https://example.org/paper" in slides[0].body


def test_build_slides_resolves_formulas_from_model_equations() -> None:
    slides = build_slides(_fixture_inputs())
    second = slides[2]

    assert [eq.label for eq in second.equations] == ["dS_dt"]
    assert second.equations[0].latex == r"- \frac{I S \beta}{N}"
    assert second.equations[0].caption == "Susceptible rate"
    assert second.figure == "generated/f.png"
    assert second.warnings == ()


def test_build_slides_keeps_unknown_formula_as_warning_not_error() -> None:
    third = build_slides(_fixture_inputs())[3]

    assert [eq.label for eq in third.equations] == ["R0"]
    assert third.warnings == ("formula 'missing_name' not found in model equations",)


def test_build_slides_carries_speaker_notes() -> None:
    first = build_slides(_fixture_inputs())[1]

    assert first.notes == "say hi"
    assert first.figure is None


def test_relocate_figures_makes_paths_relative_to_output_dir(tmp_path: Path) -> None:
    example = tmp_path / "example"
    output = example / "generated"
    slides = [Slide(title="F", figure="generated/figures/a.png"), Slide(title="N")]

    relocated = relocate_figures(slides, example, output)

    assert relocated[0].figure == "figures/a.png"
    assert relocated[1] == slides[1]
    assert slides[0].figure == "generated/figures/a.png"  # input is not mutated


def test_render_html_contains_reveal_markers_and_slide_titles() -> None:
    html_text = render_html(build_slides(_fixture_inputs()), title="Fixture Deck")

    assert f"reveal.js@{REVEAL_VERSION}/dist/reveal.js" in html_text
    assert f"reveal.js@{REVEAL_VERSION}/dist/reveal.css" in html_text
    assert "Reveal.initialize(" in html_text
    assert f"mathjax@{MATHJAX_VERSION}/" in html_text
    assert html_text.count("<section>") == 4
    for title in ("Fixture Deck", "First", "Second", "Third"):
        assert f"<h2>{title}</h2>" in html_text
    assert "<title>Fixture Deck</title>" in html_text


def test_render_html_renders_equations_for_mathjax_and_figures_as_img() -> None:
    slide = Slide(
        title="Eq",
        equations=(Equation(label="dS_dt", latex=r"- \frac{I S \beta}{N}", caption="Susceptible"),),
        figure="figures/a.png",
    )

    html_text = render_html([slide], title="T")

    assert r"\[ \mathrm{dS\_dt} = - \frac{I S \beta}{N} \]" in html_text
    assert "Susceptible" in html_text
    assert '<img src="figures/a.png" alt="Eq">' in html_text


def test_render_html_escapes_titles_and_text_with_angle_brackets_and_ampersands() -> None:
    slides = [
        Slide(title="A < B & C", body="x < y & <script>alert(1)</script>", notes="<b>n</b> & more"),
    ]

    html_text = render_html(slides, title="Deck <x>")

    assert "<h2>A &lt; B &amp; C</h2>" in html_text
    assert "<title>Deck &lt;x&gt;</title>" in html_text
    assert "<script>alert(1)</script>" not in html_text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_text
    assert "&lt;b&gt;n&lt;/b&gt; &amp; more" in html_text


def test_markdown_to_html_handles_bullets_bold_code_and_paragraphs() -> None:
    result = markdown_to_html("### Head\n\nLine **bold** and `x<y`\n- item *one*\n- item two\n\nTail")

    assert result == (
        "<h3>Head</h3>\n"
        "<p>Line <strong>bold</strong> and <code>x&lt;y</code></p>\n"
        "<ul><li>item *one*</li><li>item two</li></ul>\n"
        "<p>Tail</p>"
    )


def test_markdown_https_link_is_anchor_with_escaped_url() -> None:
    result = markdown_to_html("[ok](https://example.org/a?b=1&c=2)")

    assert result == '<p><a href="https://example.org/a?b=1&amp;c=2">ok</a></p>'


def test_markdown_non_http_link_is_not_turned_into_an_anchor() -> None:
    result = markdown_to_html("[bad](javascript:alert(1))")

    assert "<a " not in result
    assert "javascript:alert(1)" in result


def test_load_presentation_inputs_reads_yaml_and_json(tmp_path: Path) -> None:
    model_path = tmp_path / "m.json"
    config_path = tmp_path / "c.yaml"
    model_path.write_text('{"equations": {"R0": {"latex": "1"}}}', encoding="utf-8")
    config_path.write_text('title: "T"\nslides:\n  - title: "S1"\n', encoding="utf-8")

    inputs = load_presentation_inputs(model_path, config_path)

    assert inputs.model == {"equations": {"R0": {"latex": "1"}}}
    assert inputs.config == {"title": "T", "slides": [{"title": "S1"}]}


def test_write_presentation_writes_utf8_html_under_tmp_path(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "presentation.html"

    written = write_presentation("<!doctype html><p>R₀</p>", target)

    assert written == target
    assert target.read_text(encoding="utf-8") == "<!doctype html><p>R₀</p>"
