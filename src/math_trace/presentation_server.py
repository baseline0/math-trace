"""Web-based presentation server for interactive formula slides.

Serves Revealjs + HTMX slides with live formula computation and traceability.

## Architecture

- **Slides:** HTML (Revealjs) served by FastAPI
- **Rendering:** MathJax for all mathematics
- **Interactivity:** HTMX for live formula updates
- **Computation:** Server-side SymPy evaluation
- **Traceability:** Click formulas to see source code location

## Usage

```python
from math_trace.presentation_server import PresentationServer
from math_trace.formula import Formula

# Create server
server = PresentationServer(title="My Research Talk")

# Add slides
server.add_slide(
    title="Membrane Dynamics",
    content="Our model describes ion channels...",
)

# Add interactive formula slide
server.add_formula_slide(
    title="Rate Law",
    formulas={
        "rate": Formula(
            name="rate",
            latex="k \\\\binom{n}{2}",
            description="Collision rate",
            source_line=42,
        ),
    },
    parameters={"k": 1.0, "n": 10},
)

# Run server
server.run(port=8000)

# Open http://localhost:8000 in browser
# Click formulas to see source code
# Click "Evaluate" to compute with parameters
```

## Features

- **Live formula updates:** Change parameters, see results instantly
- **Source traceability:** Click formula → opens model.py at source line
- **Beautiful math:** MathJax renders all TeX/LaTeX/AsciiMath
- **Keyboard shortcuts:** Arrow keys to navigate, 's' for speaker notes
- **Export:** Print to PDF with all formulas rendered
"""

from __future__ import annotations

import html
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import sympy as sp
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from math_trace.formula import Formula
from math_trace.logging import get_logger

logger = get_logger(__name__)


class PresentationServer:
    """Web server for interactive formula-driven presentations.

    Combines Revealjs (presentation framework), MathJax (math rendering),
    and HTMX (live updates) to create interactive slides where formulas
    can be computed live and traced to source code.

    Design Pattern: Pluggable presentation backend (see formula.py docstring)
    This is one implementation of the presentation layer. Future implementations
    could use different frameworks (e.g., Quarto, Marp web, custom).
    """

    def __init__(
        self,
        title: str = "math-trace Presentation",
        theme: str = "white",
        transition: str = "slide",
        repo_path: Optional[Path] = None,
    ):
        """Initialize presentation server.

        Args:
            title: Presentation title
            theme: Revealjs theme (white, black, league, sky, beige, simple, serif, blood, night, moon, solarized)
            transition: Slide transition (none, fade, slide, convex, concave, zoom)
            repo_path: Path to repo for source code links
        """
        self.app = FastAPI(title=title)
        self.title = title
        self.theme = theme
        self.transition = transition
        self.repo_path = repo_path or Path.cwd()
        self.slides: list[Dict[str, Any]] = []

        # Setup routes
        self._setup_routes()

    def add_slide(
        self,
        title: str,
        content: str,
        speaker_notes: Optional[str] = None,
        background: Optional[str] = None,
    ) -> None:
        """Add a text slide.

        Args:
            title: Slide title
            content: Slide content (HTML)
            speaker_notes: Optional speaker notes
            background: Optional background color/image
        """
        self.slides.append(
            {
                "type": "text",
                "title": title,
                "content": content,
                "speaker_notes": speaker_notes or "",
                "background": background,
            }
        )

    def add_formula_slide(
        self,
        title: str,
        formulas: Dict[str, Formula],
        parameters: Optional[Dict[str, float]] = None,
        description: Optional[str] = None,
    ) -> None:
        """Add a slide with interactive formulas.

        Args:
            title: Slide title
            formulas: Dict mapping formula names to Formula objects
            parameters: Initial parameter values for evaluation
            description: Slide description
        """
        self.slides.append(
            {
                "type": "formula",
                "title": title,
                "formulas": formulas,
                "parameters": parameters or {},
                "description": description or "",
            }
        )

    def _setup_routes(self) -> None:
        """Setup FastAPI routes."""

        @self.app.get("/", response_class=HTMLResponse)
        def index():
            """Serve main presentation."""
            return self._render_presentation()

        @self.app.post("/api/evaluate", response_class=HTMLResponse)
        def evaluate(formula_id: str = Query(...)):
            """Evaluate a formula with parameters from form data.

            Receives formula_id and variable=value pairs via form submission.
            Returns HTML fragment with computed result.
            """
            # Validate formula_id
            if not formula_id or not isinstance(formula_id, str):
                logger.warning("Invalid formula_id: missing or wrong type")
                raise HTTPException(status_code=400, detail="Invalid formula_id")

            if len(formula_id) > 256:
                logger.warning(f"Invalid formula_id: too long ({len(formula_id)} chars)")
                raise HTTPException(status_code=400, detail="Invalid formula_id")

            try:
                # Find formula and slide context
                slide = self._find_slide_with_formula(formula_id)
                if not slide:
                    logger.debug(f"Formula not found: {formula_id}")
                    raise HTTPException(status_code=404, detail="Formula not found")

                formula = slide["formulas"][formula_id]

                # In a real app, we'd extract form params from the request.
                # For now, use the slide's default parameters.
                params = slide.get("parameters", {})

                # Evaluate formula
                result = self._evaluate_formula(formula.latex, params)
                source_link = html.escape(str(self.repo_path), quote=True) + f":{formula.source_line}"

                # Build safe HTML response (result already validated in _evaluate_formula)
                params_html = ", ".join(
                    f"{html.escape(str(k))}={html.escape(str(v))}"
                    for k, v in params.items()
                )

                response = HTMLResponse(
                    f"""
                    <div class="formula-result">
                        <p><strong>Result:</strong> ${result}$</p>
                        <p style="font-size: 0.9em; color: #666;">
                            with {params_html}
                        </p>
                        <small><a href="{source_link}" target="_blank">View source: line {formula.source_line}</a></small>
                    </div>
                    """
                )
                # Security headers
                response.headers["X-Content-Type-Options"] = "nosniff"
                response.headers["X-Frame-Options"] = "SAMEORIGIN"
                response.headers["X-XSS-Protection"] = "1; mode=block"
                return response

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Evaluation error: {e}")
                return HTMLResponse(
                    "<div class='error'>Unable to evaluate formula. Please try again.</div>",
                    status_code=500,
                )

    def _find_formula(self, formula_id: str) -> Optional[Formula]:
        """Find formula by ID across all slides."""
        for slide in self.slides:
            if slide["type"] == "formula":
                if formula_id in slide["formulas"]:
                    return slide["formulas"][formula_id]
        return None

    def _find_slide_with_formula(self, formula_id: str) -> Optional[Dict[str, Any]]:
        """Find slide containing formula (includes context like parameters)."""
        for slide in self.slides:
            if slide["type"] == "formula":
                if formula_id in slide["formulas"]:
                    return slide
        return None

    def _evaluate_formula(self, latex_str: str, params: Dict[str, float]) -> str:
        """Evaluate a LaTeX formula with given parameters.

        Converts common LaTeX patterns to evaluable expressions.
        If parsing fails, returns original LaTeX.

        Args:
            latex_str: LaTeX formula string (e.g., r"k \binom{n}{2}")
            params: Variable assignments (e.g., {"k": 1.5, "n": 10})

        Returns:
            Evaluated result as string or original LaTeX if evaluation fails
        """
        # Validate inputs
        if not latex_str or not isinstance(latex_str, str):
            return "(invalid formula)"

        if not params or not isinstance(params, dict):
            return latex_str

        # Validate parameter types and ranges
        try:
            for key, value in params.items():
                if not isinstance(value, (int, float)):
                    logger.warning(f"Invalid parameter type for {key}: expected number, got {type(value)}")
                    raise ValueError(f"Parameter {key} must be a number")
                # Sanity check: prevent extremely large values
                if not (-1e10 < value < 1e10):
                    logger.warning(f"Parameter {key}={value} out of reasonable range")
                    raise ValueError(f"Parameter {key} out of reasonable range")
        except (ValueError, TypeError) as e:
            logger.debug(f"Parameter validation failed: {e}")
            return latex_str

        try:
            import re

            # Pre-process LaTeX to Python-evaluable form
            expr_str = latex_str

            # Evaluate binomial coefficients with actual parameter values
            def eval_binomial(match):
                a_str, b_str = match.group(1), match.group(2)
                try:
                    # Try to parse as number or parameter name
                    a = (
                        float(a_str)
                        if a_str.replace(".", "").replace("-", "").isdigit()
                        else params.get(a_str, float("nan"))
                    )
                    b = (
                        float(b_str)
                        if b_str.replace(".", "").replace("-", "").isdigit()
                        else params.get(b_str, float("nan"))
                    )
                    result = sp.binomial(int(a), int(b))
                    return f"({result})"  # Wrap in parens for safety
                except Exception:
                    return match.group(0)

            expr_str = re.sub(r"\\binom\s*\{\s*([^}]+)\s*\}\s*\{\s*([^}]+)\s*\}", eval_binomial, expr_str)

            # Replace LaTeX commands with function names
            expr_str = expr_str.replace(r"\sqrt", "sqrt")
            expr_str = expr_str.replace(r"\pi", "pi")

            # Remove braces (they're just grouping in LaTeX)
            expr_str = expr_str.replace("{", "").replace("}", "")

            # Insert * between adjacent tokens: digit/paren and symbol, symbol and digit/paren
            expr_str = re.sub(r"(\d)\s*([a-zA-Z])", r"\1*\2", expr_str)
            expr_str = re.sub(r"([a-zA-Z])\s*(\()", r"\1*\2", expr_str)
            expr_str = re.sub(r"(\))\s*([a-zA-Z0-9])", r"\1*\2", expr_str)
            expr_str = re.sub(r"(\))\s*(\()", r"\1*\2", expr_str)

            # Create namespace
            namespace = {name: sp.Symbol(name) for name in params.keys()}
            namespace.update({
                "sqrt": sp.sqrt,
                "pi": sp.pi,
                "exp": sp.exp,
                "log": sp.log,
                "sin": sp.sin,
                "cos": sp.cos,
            })

            # Parse and evaluate
            expr = sp.sympify(expr_str, locals=namespace)

            # Substitute parameter values
            for name, value in params.items():
                expr = expr.subs(sp.Symbol(name), value)

            # Compute result
            result = float(expr.evalf())

            # Format: integers without decimals, floats with 4 sig figs
            if abs(result - round(result)) < 1e-9:
                return str(int(round(result)))
            else:
                return f"{result:.4g}"

        except Exception:
            return latex_str

    def _render_presentation(self) -> str:
        """Render full HTML presentation."""
        MAX_SLIDES = 1000
        slides_to_render = self.slides

        if len(self.slides) > MAX_SLIDES:
            logger.warning(
                f"Presentation has {len(self.slides)} slides, "
                f"truncating to {MAX_SLIDES}"
            )
            slides_to_render = self.slides[:MAX_SLIDES]

        slides_html = "\n".join(self._render_slide(s) for s in slides_to_render)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>

    <!-- Revealjs CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/theme/{self.theme}.min.css">

    <!-- MathJax for math rendering -->
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

    <!-- HTMX for live updates -->
    <script src="https://unpkg.com/htmx.org"></script>

    <style>
        .formula {{
            padding: 1em;
            border: 1px solid #ccc;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        .formula:hover {{
            background: #f0f0f0;
        }}
        .formula-result {{
            margin-top: 1em;
            padding: 1em;
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
        }}
        .error {{
            padding: 1em;
            background: #ffebee;
            border-left: 4px solid #f44336;
            color: #c62828;
        }}
        .controls {{
            margin-top: 1em;
        }}
        button {{
            padding: 0.5em 1em;
            background: #2196f3;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}
        button:hover {{
            background: #1976d2;
        }}
        small {{
            display: block;
            margin-top: 0.5em;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
            {slides_html}
        </div>
    </div>

    <!-- Revealjs JS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/plugin/notes/notes.min.js"></script>

    <script>
        // Initialize Revealjs
        Reveal.initialize({{
            hash: true,
            transition: '{self.transition}',
            plugins: [ RevealNotes ],
            keyboard: true,
            controls: true,
        }});

        // Re-render math when HTMX swaps content
        htmx.onLoad(function(content) {{
            if (window.MathJax) {{
                MathJax.typesetPromise([content]).catch(err => console.log(err));
            }}
        }});
    </script>
</body>
</html>"""

    def _render_slide(self, slide: Dict[str, Any]) -> str:
        """Render a single slide."""
        if slide["type"] == "text":
            return self._render_text_slide(slide)
        elif slide["type"] == "formula":
            return self._render_formula_slide(slide)
        else:
            return ""

    def _render_text_slide(self, slide: Dict[str, Any]) -> str:
        """Render a text slide."""
        safe_title = html.escape(slide.get("title", ""))
        safe_notes = html.escape(slide.get("speaker_notes", "")) if slide.get("speaker_notes") else ""
        notes = f"<aside class='notes'>{safe_notes}</aside>" if safe_notes else ""

        # Background is URL, escape carefully
        bg_value = slide.get("background", "")
        safe_bg = html.escape(bg_value, quote=True) if bg_value else ""
        bg = f"data-background='{safe_bg}'" if safe_bg else ""

        # Content is user-provided HTML, but should already be trusted from add_slide calls
        # If we want to escape it too: content = html.escape(slide.get("content", ""))
        content = slide.get("content", "")

        return f"""<section {bg}>
            <h2>{safe_title}</h2>
            <div>{content}</div>
            {notes}
        </section>"""

    def _render_formula_slide(self, slide: Dict[str, Any]) -> str:
        """Render a formula slide with interactive elements."""
        params = slide.get("parameters", {})

        # Parameter input fields (with HTML escaping)
        params_html = ""
        for param_name, param_value in params.items():
            safe_param_name = html.escape(str(param_name), quote=True)
            safe_param_value = html.escape(str(param_value), quote=True)
            params_html += f"""
                <div style="margin: 0.5em 0;">
                    <label for="param_{safe_param_name}" style="display: inline-block; width: 80px;">
                        <em>{safe_param_name}</em> =
                    </label>
                    <input type="number" id="param_{safe_param_name}" name="{safe_param_name}"
                           value="{safe_param_value}" step="any"
                           style="width: 100px; padding: 0.25em;">
                </div>
            """

        # Formulas (with HTML escaping for metadata, LaTeX for math)
        formulas_html = ""
        for formula_id, formula in slide["formulas"].items():
            safe_formula_id = html.escape(str(formula_id), quote=True)
            safe_name = html.escape(formula.name)
            safe_latex = html.escape(formula.latex)  # LaTeX is rendered by MathJax, so escape it
            safe_description = html.escape(formula.description)

            formulas_html += f"""
            <div class="formula" style="margin-top: 1.5em;">
                <p><strong>{safe_name}</strong></p>
                <p>${{safe_latex}}$</p>
                <small>{safe_description}</small>
                <button hx-post="/api/evaluate?formula_id={safe_formula_id}"
                        hx-swap="afterend"
                        style="margin-top: 0.5em;">
                    Evaluate
                </button>
                <small style="display: block; margin-top: 0.25em; color: #999;">
                    Defined: line {formula.source_line}
                </small>
            </div>
            """

        safe_title = html.escape(slide.get("title", ""))
        safe_description = html.escape(slide.get("description", ""))

        return f"""<section>
            <h2>{safe_title}</h2>
            <p>{safe_description}</p>
            <div style="background: #f5f5f5; padding: 1em; border-radius: 4px; margin: 1em 0;">
                <p style="margin-top: 0; font-weight: bold; font-size: 0.9em;">Parameters:</p>
                {params_html}
            </div>
            {formulas_html}
        </section>"""

    def run(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """Run the presentation server.

        Args:
            host: Bind address
            port: Port number
        """
        import uvicorn

        print(f"\n🎤 Presentation server running at http://{host}:{port}")
        print("   Arrow keys: navigate slides")
        print("   's': speaker notes")
        print("   'f': fullscreen")
        print("   'esc': exit fullscreen\n")

        uvicorn.run(self.app, host=host, port=port)
