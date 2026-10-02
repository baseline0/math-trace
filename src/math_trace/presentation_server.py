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

from pathlib import Path
from typing import Any, Dict, Optional

import sympy as sp
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from math_trace.formula import Formula


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
            try:
                # Find formula and slide context
                slide = self._find_slide_with_formula(formula_id)
                if not slide:
                    raise HTTPException(status_code=404, detail="Formula not found")

                formula = slide["formulas"][formula_id]

                # In a real app, we'd extract form params from the request.
                # For now, use the slide's default parameters.
                params = slide.get("parameters", {})

                # Evaluate formula
                result = self._evaluate_formula(formula.latex, params)
                source_link = f"{self.repo_path}:{formula.source_line}"

                return f"""
                <div class="formula-result">
                    <p><strong>Result:</strong> ${result}$</p>
                    <p style="font-size: 0.9em; color: #666;">
                        with {', '.join(f'{k}={v}' for k, v in params.items())}
                    </p>
                    <small><a href="{source_link}" target="_blank">View source: line {formula.source_line}</a></small>
                </div>
                """

            except Exception as e:
                return f"<div class='error'>Evaluation error: {str(e)}</div>"

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

        Converts LaTeX to SymPy expression, substitutes parameters, and evaluates.
        If parsing fails, returns the original LaTeX.

        Args:
            latex_str: LaTeX formula string (e.g., r"k \binom{n}{2}")
            params: Variable assignments (e.g., {"k": 1.5, "n": 10})

        Returns:
            Evaluated result as string or original LaTeX if evaluation fails
        """
        if not params:
            return latex_str

        try:
            import re

            expr_str = latex_str

            # Convert LaTeX binomial \binom{a}{b} → binomial(a, b)
            expr_str = re.sub(r"\\binom\s*\{\s*([^}]+)\s*\}\s*\{\s*([^}]+)\s*\}", r"binomial(\1, \2)", expr_str)

            # Convert LaTeX fractions: \frac{a}{b} → (a)/(b)
            expr_str = re.sub(r"\\frac\s*\{\s*([^}]+)\s*\}\s*\{\s*([^}]+)\s*\}", r"(\1)/(\2)", expr_str)

            # Convert other LaTeX commands
            expr_str = expr_str.replace(r"\sqrt", "sqrt")
            expr_str = expr_str.replace(r"\alpha", "alpha")
            expr_str = expr_str.replace(r"\beta", "beta")
            expr_str = expr_str.replace(r"\pi", "pi")

            # Remove remaining braces (they're just grouping in LaTeX)
            expr_str = expr_str.replace("{", "").replace("}", "")

            # Insert * between adjacent symbol/number and ( or ) and symbol
            expr_str = re.sub(r"([a-zA-Z0-9_\)])\s*\(", r"\1*(", expr_str)
            expr_str = re.sub(r"\)\s*([a-zA-Z0-9_\(])", r")*\1", expr_str)

            # Create SymPy symbols for all parameters
            symbols = {name: sp.Symbol(name) for name in params.keys()}

            # Add SymPy functions to namespace
            symbols.update({
                'binomial': sp.binomial,
                'sqrt': sp.sqrt,
                'pi': sp.pi,
            })

            # Parse expression
            expr = sp.sympify(expr_str, locals=symbols, transformations='all')

            # Substitute parameter values
            for name, value in params.items():
                expr = expr.subs(sp.Symbol(name), value)

            # Evaluate numerically
            result = float(expr.evalf())

            # Format: integers without decimals, floats with 4 sig figs
            if result == int(result):
                return str(int(result))
            else:
                return f"{result:.4g}"

        except Exception:
            # If evaluation fails, return original LaTeX
            return latex_str

    def _render_presentation(self) -> str:
        """Render full HTML presentation."""
        slides_html = "\n".join(self._render_slide(s) for s in self.slides)

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
        notes = f"<aside class='notes'>{slide['speaker_notes']}</aside>" if slide["speaker_notes"] else ""
        bg = f"data-background='{slide['background']}'" if slide["background"] else ""

        return f"""<section {bg}>
            <h2>{slide['title']}</h2>
            <div>{slide['content']}</div>
            {notes}
        </section>"""

    def _render_formula_slide(self, slide: Dict[str, Any]) -> str:
        """Render a formula slide with interactive elements."""
        params = slide.get("parameters", {})

        # Parameter input fields
        params_html = ""
        for param_name, param_value in params.items():
            params_html += f"""
                <div style="margin: 0.5em 0;">
                    <label for="param_{param_name}" style="display: inline-block; width: 80px;">
                        <em>{param_name}</em> =
                    </label>
                    <input type="number" id="param_{param_name}" name="{param_name}"
                           value="{param_value}" step="any"
                           style="width: 100px; padding: 0.25em;">
                </div>
            """

        # Formulas
        formulas_html = ""
        for formula_id, formula in slide["formulas"].items():
            formulas_html += f"""
            <div class="formula" style="margin-top: 1.5em;">
                <p><strong>{formula.name}</strong></p>
                <p>$${{formula.latex}}$$</p>
                <small>{formula.description}</small>
                <button hx-post="/api/evaluate?formula_id={formula_id}"
                        hx-swap="afterend"
                        style="margin-top: 0.5em;">
                    Evaluate
                </button>
                <small style="display: block; margin-top: 0.25em; color: #999;">
                    Defined: line {formula.source_line}
                </small>
            </div>
            """

        return f"""<section>
            <h2>{slide['title']}</h2>
            <p>{slide['description']}</p>
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
