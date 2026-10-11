"""Build a single-file Revealjs HTML presentation from a model JSON and a presentation config.

Design:
- Pure core. ``build_slides``, ``relocate_figures``, ``markdown_to_html`` and ``render_html``
  take values and return values. ``load_presentation_inputs`` and ``write_presentation`` are
  the only functions that touch the filesystem.
- Slides are ``Slide`` dataclasses in a fixed order: one title slide built from the config
  metadata, then the config's ``slides`` in file order.
- Slide text is a small Markdown subset (headings, bullets, paragraphs, ``**bold**``,
  ``` `code` ```, and http(s) links). Text is HTML-escaped before any markup is added, so
  titles and text containing ``<`` or ``&`` stay literal.
- Equations come from the model JSON ``equations`` mapping (the ``latex`` field, shown as
  ``\\text{name} = latex``). MathJax 3 renders them from ``\\[ ... \\]`` delimiters.
  A formula name missing from the mapping does not fail the build: the slide gets a
  warning and the name is listed by ``Slide.warnings``.
- Figure paths in the config are relative to the example folder. ``relocate_figures``
  rewrites them relative to the output file, so the HTML can sit next to ``figures/``.
- CDN pins: reveal.js 5.2.0 (released 2025-03-19, past the two-week minimum; 6.x exists
  but was not chosen) and MathJax 3.2.2 (the last 3.x release; 4.x is not used).
  Both URLs were checked to resolve. The HTML needs network access to load them.
"""

from __future__ import annotations

import html
import json
import os
import re
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

import yaml

REVEAL_VERSION = "5.2.0"
MATHJAX_VERSION = "3.2.2"
REVEAL_BASE = f"https://cdn.jsdelivr.net/npm/reveal.js@{REVEAL_VERSION}/dist"
MATHJAX_SCRIPT = f"https://cdn.jsdelivr.net/npm/mathjax@{MATHJAX_VERSION}/es5/tex-mml-chtml.js"


@dataclass(frozen=True)
class PresentationInputs:
    """The two input documents, read as plain dicts."""

    model: dict[str, Any]
    config: dict[str, Any]


@dataclass(frozen=True)
class Equation:
    """One display equation: ``label = latex``, with an optional caption above it."""

    label: str
    latex: str
    caption: str = ""


@dataclass(frozen=True)
class Slide:
    """One slide. ``body`` is Markdown; ``equations`` and ``figure`` are rendered after it."""

    title: str
    body: str = ""
    equations: tuple[Equation, ...] = ()
    figure: str | None = None
    notes: str = ""
    warnings: tuple[str, ...] = field(default=())


def load_presentation_inputs(model_path: Path, config_path: Path) -> PresentationInputs:
    """Read the model JSON and the presentation YAML into plain dicts."""
    model = json.loads(model_path.read_text(encoding="utf-8"))
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(model, dict) or not isinstance(config, dict):
        raise ValueError("model and config must each be a mapping at the top level")
    return PresentationInputs(model=model, config=config)


def build_slides(inputs: PresentationInputs) -> list[Slide]:
    """Return the title slide followed by the config slides, in file order."""
    config = inputs.config
    equations = inputs.model.get("equations") or {}
    return [_title_slide(config), *(_config_slide(entry, equations) for entry in config.get("slides") or [])]


def relocate_figures(slides: list[Slide], example_dir: Path, output_dir: Path) -> list[Slide]:
    """Rewrite each figure path to be relative to ``output_dir``. Pure: no filesystem access."""
    relocated: list[Slide] = []
    for slide in slides:
        if slide.figure is None:
            relocated.append(slide)
            continue
        target = Path(slide.figure)
        if not target.is_absolute():
            target = example_dir / target
        relative = Path(os.path.relpath(target, output_dir)).as_posix()
        relocated.append(replace(slide, figure=relative))
    return relocated


def render_html(slides: list[Slide], title: str) -> str:
    """Return one self-contained HTML document with a Revealjs deck of ``slides``."""
    sections = "\n".join(_render_section(slide) for slide in slides)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<link rel="stylesheet" href="{REVEAL_BASE}/reveal.css">
<link rel="stylesheet" href="{REVEAL_BASE}/theme/white.css">
<style>
  .reveal img {{ max-height: 60vh; margin: 0 auto; }}
  .reveal .equation {{ font-size: 1.1em; margin: 0.4em 0 0.8em; }}
  .reveal .caption {{ font-size: 0.85em; margin: 0.6em 0 0; }}
  .reveal .warning {{ color: #b00020; font-size: 0.85em; }}
</style>
<script>
  window.MathJax = {{
    tex: {{ inlineMath: [["\\\\(", "\\\\)"]], displayMath: [["\\\\[", "\\\\]"]] }},
    startup: {{ typeset: true }}
  }};
</script>
<script defer src="{MATHJAX_SCRIPT}"></script>
</head>
<body>
<div class="reveal">
<div class="slides">
{sections}
</div>
</div>
<script src="{REVEAL_BASE}/reveal.js"></script>
<script>
  Reveal.initialize({{ hash: true, slideNumber: true, transition: "fade" }});
</script>
</body>
</html>
"""


def markdown_to_html(text: str) -> str:
    """Convert the supported Markdown subset to HTML. Escapes all text before adding markup."""
    out: list[str] = []
    paragraph: list[str] = []
    items: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            out.append("<p>" + "<br>".join(_inline(line) for line in paragraph) + "</p>")
            paragraph.clear()

    def flush_list() -> None:
        if items:
            out.append("<ul>" + "".join(f"<li>{_inline(item)}</li>" for item in items) + "</ul>")
            items.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush_paragraph()
            flush_list()
        elif line.startswith("- "):
            flush_paragraph()
            items.append(line[2:].strip())
        elif line.startswith("#"):
            flush_paragraph()
            flush_list()
            out.append(f"<h3>{_inline(line.lstrip('#').strip())}</h3>")
        else:
            flush_list()
            paragraph.append(line)
    flush_paragraph()
    flush_list()
    return "\n".join(out)


def write_presentation(html_text: str, path: Path) -> Path:
    """Write the HTML document to ``path``, creating parent folders. Returns the path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")
    return path


_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_CODE = re.compile(r"`([^`]+)`")


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _inline(text: str) -> str:
    """Escape, then apply bold, code and link markup. Only http(s) links become anchors."""
    escaped = _esc(text)
    escaped = _CODE.sub(r"<code>\1</code>", escaped)
    escaped = _BOLD.sub(r"<strong>\1</strong>", escaped)
    return _LINK.sub(r'<a href="\2">\1</a>', escaped)


def _title_slide(config: dict[str, Any]) -> Slide:
    metadata = config.get("metadata") or {}
    lines: list[str] = []
    if metadata.get("author"):
        lines.append(f"**{metadata['author']}**")
    date_affiliation = " · ".join(str(part) for part in (metadata.get("date"), metadata.get("affiliation")) if part)
    if date_affiliation:
        lines.append(date_affiliation)
    if config.get("paper_url"):
        lines.append(f"[{config['paper_url']}]({config['paper_url']})")
    if config.get("paper_doi"):
        lines.append(f"DOI: {config['paper_doi']}")
    return Slide(title=str(config.get("title", "")), body="\n\n".join(lines))


def _config_slide(entry: dict[str, Any], equations: dict[str, Any]) -> Slide:
    resolved: list[Equation] = []
    warnings: list[str] = []
    for name in entry.get("formulas") or []:
        spec = equations.get(name)
        if not isinstance(spec, dict) or "latex" not in spec:
            warnings.append(f"formula '{name}' not found in model equations")
            continue
        resolved.append(Equation(label=str(name), latex=str(spec["latex"]), caption=str(spec.get("description", ""))))
    figure = entry.get("figure")
    return Slide(
        title=str(entry.get("title", "")),
        body=str(entry.get("text") or ""),
        equations=tuple(resolved),
        figure=str(figure) if figure else None,
        notes=str(entry.get("notes") or ""),
        warnings=tuple(warnings),
    )


def _tex_label(label: str) -> str:
    """Typeset a model name as upright math. MathJax 3 does not honour ``\\_`` inside ``\\text``."""
    return "\\mathrm{" + label.replace("\\", "").replace("_", "\\_") + "}"


def _render_equation(eq: Equation) -> str:
    parts: list[str] = []
    if eq.caption:
        parts.append(f'<p class="caption"><strong>{_esc(eq.caption)}</strong></p>')
    # The LaTeX is HTML-escaped so that a stray < or & cannot break out of the element.
    parts.append(f'<div class="equation">\\[ {_tex_label(eq.label)} = {_esc(eq.latex)} \\]</div>')
    return "\n".join(parts)


def _render_section(slide: Slide) -> str:
    parts = [f"<h2>{_esc(slide.title)}</h2>"]
    if slide.body:
        parts.append(markdown_to_html(slide.body))
    parts.extend(_render_equation(eq) for eq in slide.equations)
    if slide.figure:
        parts.append(f'<img src="{_esc(slide.figure)}" alt="{_esc(slide.title)}">')
    parts.extend(f'<p class="warning">Warning: {_esc(w)}</p>' for w in slide.warnings)
    if slide.notes:
        parts.append(f'<aside class="notes">{_esc(slide.notes)}</aside>')
    return "<section>\n" + "\n".join(parts) + "\n</section>"
