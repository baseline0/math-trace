"""FastAPI server for interactive slide development & formula debugging.

Provides web UI for:
- Live formula editing (JSON)
- Configuration editing (YAML)
- Real-time slide preview (Revealjs + HTMX)
- Export (HTML with live formula evaluation)
"""

from __future__ import annotations

import html
import json
import logging
import tempfile
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .arxiv_extractor import extract_arxiv_id, load_extracted_paper, save_extracted_paper
from .formula import Formula
from .formula_browser import app as formula_browser_app
from .logging import get_logger
from .presentation_generator import PresentationConfig
from .presentation_server import PresentationServer
from .responses import ApiResponse

logger = get_logger(__name__)

app = FastAPI(
    title="math-trace Slide Editor",
    description="Interactive slide development with live formula preview",
    version="0.1.0",
)


# ============================================================================
# API Routes
# ============================================================================


@app.post("/api/preview")
async def preview_slide(
    formulas: dict,
    config: Optional[dict] = None,
    theme: str = "white",
):
    """Live preview of slides with current formulas + config.

    Args:
        formulas: Dictionary of formula definitions (name → latex)
        config: Presentation config (title, author, etc.)
        theme: Revealjs theme (white, black, league, sky, beige, etc.)

    Returns:
        JSON with rendered HTML
    """
    try:
        if not formulas:
            return {"status": "error", "message": "No formulas provided"}

        # Create presentation server
        title = config.get("title", "Untitled Presentation") if config else "Untitled Presentation"
        server = PresentationServer(title=title, theme=theme)

        # Convert formulas dict to Formula objects and add as slides
        for formula_name, formula_data in formulas.items():
            if isinstance(formula_data, dict):
                formula = Formula(
                    name=formula_data.get("name", formula_name),
                    latex=formula_data.get("latex", ""),
                    description=formula_data.get("description", ""),
                    source_line=formula_data.get("source_line", 0),
                )
                parameters = formula_data.get("parameters", {})
                server.add_formula_slide(
                    title=formula.name,
                    formulas={formula_name: formula},
                    parameters=parameters,
                    description=formula.description,
                )

        # Return rendered HTML as JSON
        html = server._render_presentation()
        return {"status": "success", "html": html}

    except KeyError as e:
        return {"status": "error", "message": f"Missing field: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Preview failed: {str(e)}"}


@app.post("/api/export")
async def export_slides(
    formulas: dict,
    config: Optional[dict] = None,
    format: str = "markdown",
):
    """Export presentation in specified format.

    Args:
        formulas: Dictionary of formulas
        config: Presentation config
        format: Output format ("markdown", "html", "pdf")

    Returns:
        File download or error
    """
    try:
        if not formulas:
            raise HTTPException(400, "No formulas provided")

        if config is None:
            config = {"title": "Untitled Presentation", "author": "Unknown"}

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            try:
                # Restructure config to match PresentationConfig schema
                pres_fields = {"title", "format", "backend", "slides", "metadata", "paper_url", "paper_doi"}
                metadata = {}

                # Extract non-PresentationConfig fields into metadata
                for key in list(config.keys()):
                    if key not in pres_fields:
                        metadata[key] = config.pop(key)

                # Set defaults for required fields
                if "title" not in config:
                    config["title"] = "Untitled"
                if "format" not in config:
                    config["format"] = "talk"
                if "slides" not in config:
                    config["slides"] = []
                if metadata:
                    config["metadata"] = metadata

                # Use PresentationServer to export HTML
                title = config.get("title", "Untitled Presentation")
                server = PresentationServer(title=title, theme="white")

                # Convert formulas to Formula objects
                for formula_name, formula_data in formulas.items():
                    if isinstance(formula_data, dict):
                        formula = Formula(
                            name=formula_data.get("name", formula_name),
                            latex=formula_data.get("latex", ""),
                            description=formula_data.get("description", ""),
                            source_line=formula_data.get("source_line", 0),
                        )
                        parameters = formula_data.get("parameters", {})
                        server.add_formula_slide(
                            title=formula.name,
                            formulas={formula_name: formula},
                            parameters=parameters,
                            description=formula.description,
                        )

                html_content = server._render_presentation()
                return {
                    "status": "success",
                    "html": html_content,
                    "filename": "presentation.html"
                }
            except TypeError as e:
                raise HTTPException(422, f"Config error: {str(e)}")

    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


# ============================================================================
# Web UI
# ============================================================================


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>math-trace: Interactive Slide Editor</title>
    <script src="https://unpkg.com/htmx.org@1.9.10" integrity="sha384-D1Kt99CQMDuVetoXAqLObVeqkrf3xrjsKMBLQhArt8z0KH0u0p4kjJLnp6E/QTtz" crossorigin="anonymous"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            background: #1e1e1e;
            color: white;
            padding: 16px 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        header h1 {
            font-size: 20px;
            font-weight: 600;
        }

        header p {
            font-size: 12px;
            color: #aaa;
            margin-top: 4px;
        }

        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
            flex: 1;
            overflow: hidden;
        }

        .editor-panel {
            background: white;
            border-right: 1px solid #ddd;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .preview-panel {
            background: #f9f9f9;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .editor-section {
            flex: 1;
            padding: 16px;
            overflow-y: auto;
            border-bottom: 1px solid #ddd;
        }

        .editor-section:last-child {
            border-bottom: none;
        }

        .editor-section h2 {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        textarea {
            width: 100%;
            height: calc(100% - 30px);
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            resize: none;
        }

        textarea:focus {
            outline: none;
            border-color: #0066cc;
            box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.1);
        }

        .controls {
            padding: 12px 16px;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 8px;
            background: white;
        }

        button {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }

        button.primary {
            background: #0066cc;
            color: white;
        }

        button.primary:hover {
            background: #0052a3;
        }

        button.secondary {
            background: #f0f0f0;
            color: #333;
            border: 1px solid #ddd;
        }

        button.secondary:hover {
            background: #e6e6e6;
        }

        button:active {
            transform: scale(0.98);
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .preview-header {
            padding: 12px 16px;
            border-bottom: 1px solid #ddd;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: white;
        }

        .preview-header h2 {
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .preview-header button {
            padding: 6px 12px;
            font-size: 12px;
        }

        .preview-content {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: white;
            margin: 8px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }

        .preview-content iframe {
            width: 100%;
            height: 100%;
            border: none;
        }

        .error {
            color: #d32f2f;
            background: #ffebee;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 8px;
        }

        .success {
            color: #388e3c;
            background: #e8f5e9;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 8px;
        }

        .loading {
            color: #1976d2;
            background: #e3f2fd;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 12px;
            margin-bottom: 8px;
        }

        .status-message {
            min-height: 20px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <header>
        <h1>📊 math-trace Slide Editor</h1>
        <p>Interactive formula → slide development with live preview</p>
    </header>

    <div class="container">
        <!-- Left: Browser + Editors -->
        <div class="editor-panel">
            <div class="editor-section" style="flex: 0 0 auto; padding: 12px; border-bottom: 1px solid #ddd;">
                <h2 style="margin: 0 0 8px 0; font-size: 13px;">📚 Formula Browser</h2>
                <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                    <button class="secondary"
                            hx-get="/api/formulas/arxiv-papers"
                            hx-target="#formula-browser-list"
                            hx-swap="innerHTML"
                            style="padding: 6px 12px; font-size: 12px;">
                        📄 Cached Papers
                    </button>
                    <button class="secondary"
                            hx-get="/api/formulas/local-models"
                            hx-target="#formula-browser-list"
                            hx-swap="innerHTML"
                            style="padding: 6px 12px; font-size: 12px;">
                        🐍 Local Models
                    </button>
                </div>
                <div id="formula-browser-list" style="margin-top: 8px; max-height: 200px; overflow-y: auto; font-size: 12px; border: 1px solid #eee; border-radius: 4px; padding: 8px;">
                    <p style="color: #999; margin: 0;">Click a button above to browse formulas</p>
                </div>
            </div>

            <div class="editor-section">
                <h2>📐 Formulas (JSON)</h2>
                <textarea id="formulas" spellcheck="false">{
  "rate": {
    "latex": "k \\\\binom{n_a}{2}",
    "description": "Rate law for 2a → b"
  }
}</textarea>
            </div>

            <div class="editor-section">
                <h2>⚙️ Config (YAML)</h2>
                <textarea id="config" spellcheck="false">title: My Presentation
author: Your Name
theme: default
</textarea>
            </div>

            <div class="controls">
                <button class="primary" onclick="previewSlide()" id="preview-btn">
                    👁️ Preview
                </button>
                <button class="secondary" onclick="exportSlides()">
                    📥 Export
                </button>
                <button class="secondary" onclick="resetEditors()">
                    🔄 Reset
                </button>
            </div>
        </div>

        <!-- Right: Preview -->
        <div class="preview-panel">
            <div class="preview-header">
                <h2>👀 Live Preview</h2>
                <span style="font-size: 12px; color: #999;">Revealjs + HTMX</span>
            </div>
            <div class="preview-content">
                <div class="status-message" id="status"></div>
                <div id="preview" style="min-height: 300px;"></div>
            </div>
        </div>
    </div>

    <script>
        // Insert formula from browser into editor
        window.insertFormula = function(name, latex) {
            const currentText = document.getElementById('formulas').value.trim();
            let formulas = {};

            try {
                formulas = JSON.parse(currentText);
            } catch (e) {
                formulas = {};
            }

            // Add or update formula
            formulas[name] = {
                latex: latex,
                description: ''
            };

            // Update editor
            document.getElementById('formulas').value = JSON.stringify(formulas, null, 2);
            localStorage.setItem('formulas', document.getElementById('formulas').value);

            // Auto-preview
            previewSlide();
        };

        // Load from localStorage
        window.addEventListener('load', () => {
            const saved_formulas = localStorage.getItem('formulas');
            const saved_config = localStorage.getItem('config');
            if (saved_formulas) document.getElementById('formulas').value = saved_formulas;
            if (saved_config) document.getElementById('config').value = saved_config;
        });

        // Save to localStorage on edit
        document.getElementById('formulas').addEventListener('change', () => {
            localStorage.setItem('formulas', document.getElementById('formulas').value);
        });
        document.getElementById('config').addEventListener('change', () => {
            localStorage.setItem('config', document.getElementById('config').value);
        });

        async function previewSlide() {
            const status = document.getElementById('status');
            const preview = document.getElementById('preview');
            const btn = document.getElementById('preview-btn');

            try {
                const formulas_str = document.getElementById('formulas').value;
                const config_str = document.getElementById('config').value;

                // Parse JSON/YAML
                const formulas = JSON.parse(formulas_str);
                let config;
                try {
                    config = typeof YAML !== 'undefined' ? YAML.parse(config_str) : {title: "Config Error", author: "Error"};
                    if (!config) {
                        status.innerHTML = '<div class="error">❌ YAML library not loaded. Install js-yaml or use JSON format for config.</div>';
                        btn.disabled = false;
                        return;
                    }
                } catch (yaml_err) {
                    status.innerHTML = '<div class="error">❌ Config parse error: ' + yaml_err.message + '</div>';
                    btn.disabled = false;
                    return;
                }

                status.innerHTML = '<div class="loading">⏳ Rendering preview...</div>';
                btn.disabled = true;

                // Call API
                const response = await fetch('/api/preview', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ formulas, config, theme: 'white' })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    if (data.html) {
                        preview.innerHTML = data.html;
                        status.innerHTML = '<div class="success">✅ Preview rendered successfully</div>';
                    } else if (data.markdown) {
                        preview.innerHTML = '<pre style="font-size: 11px; overflow: auto;">' +
                                           escapeHtml(data.markdown) + '</pre>';
                        status.innerHTML = '<div class="success">✅ Markdown generated</div>';
                    }
                } else {
                    status.innerHTML = '<div class="error">❌ ' + data.message + '</div>';
                }
            } catch (e) {
                status.innerHTML = '<div class="error">❌ Error: ' + e.message + '</div>';
            } finally {
                btn.disabled = false;
            }
        }

        async function exportSlides() {
            const status = document.getElementById('status');
            try {
                const formulas_str = document.getElementById('formulas').value;
                const config_str = document.getElementById('config').value;

                const formulas = JSON.parse(formulas_str);
                let config;
                try {
                    config = typeof YAML !== 'undefined' ? YAML.parse(config_str) : {title: "Untitled", author: "Unknown"};
                    if (!config) {
                        status.innerHTML = '<div class="error">❌ Config parse failed: YAML library not available</div>';
                        return;
                    }
                } catch (yaml_err) {
                    status.innerHTML = '<div class="error">❌ Config parse error: ' + yaml_err.message + '</div>';
                    return;
                }

                status.innerHTML = '<div class="loading">⏳ Exporting...</div>';

                const response = await fetch('/api/export', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ formulas, config, format: 'markdown' })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'slides.md';
                    a.click();
                    status.innerHTML = '<div class="success">✅ Downloaded slides.md</div>';
                } else {
                    status.innerHTML = '<div class="error">❌ Export failed</div>';
                }
            } catch (e) {
                status.innerHTML = '<div class="error">❌ Error: ' + e.message + '</div>';
            }
        }

        function resetEditors() {
            localStorage.removeItem('formulas');
            localStorage.removeItem('config');
            location.reload();
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Load YAML library (non-blocking)
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/js-yaml@4.1.0/dist/js-yaml.min.js';
        script.async = true;
        document.head.appendChild(script);

        // Initial preview on load (with fallback if YAML fails to load)
        script.onload = () => {
            previewSlide();
        };

        script.onerror = () => {
            console.warn('YAML library failed to load; using JSON fallback');
            previewSlide();
        };
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve interactive slide editor dashboard."""
    return DASHBOARD_HTML


@app.get("/health", response_class=HTMLResponse)
async def root():
    """Redirect root to dashboard."""
    return DASHBOARD_HTML


# ============================================================================
# arXiv Integration Endpoints
# ============================================================================


@app.post("/api/arxiv/extract")
async def arxiv_extract(paper_url_or_id: str):
    """Extract equations from arXiv paper.

    Takes arXiv URL or ID (e.g., "2301.13848" or "https://arxiv.org/abs/2301.13848")
    Downloads source, extracts equations, saves to cache.

    Returns: ApiResponse with extracted paper data or error message.
    """
    try:
        # Validate and normalize ID
        paper_id = extract_arxiv_id(paper_url_or_id)

        # Extract and save
        paper_dir = save_extracted_paper(paper_id)

        # Load and return
        paper_data = load_extracted_paper(paper_id)

        return ApiResponse.success(
            data={
                "paper_id": paper_id,
                "title": paper_data["title"],
                "authors": paper_data["authors"],
                "total_equations": paper_data["total_equations"],
                "equations": paper_data["equations"],
                "cache_path": str(paper_dir),
            },
            message=f"Extracted {paper_data['total_equations']} equations. Ready for conversion.",
            code=200,
        ).to_dict()

    except ValueError as e:
        logger.error(f"Invalid arXiv ID: {e}")
        return ApiResponse.error(
            error="Invalid arXiv ID format",
            message=str(e),
            code=400,
        ).to_dict()
    except FileNotFoundError as e:
        logger.error(f"Paper not found: {e}")
        return ApiResponse.error(
            error="Paper not found in cache",
            message=str(e),
            code=404,
        ).to_dict()
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return ApiResponse.error(
            error="Extraction failed",
            message=str(e),
            code=500,
        ).to_dict()


@app.get("/api/arxiv/papers/{paper_id}")
async def arxiv_get_paper(paper_id: str):
    """Get cached extracted paper.

    Returns: ApiResponse with paper data or error message.
    """
    try:
        paper_data = load_extracted_paper(paper_id)
        return ApiResponse.success(
            data={
                "paper_id": paper_id,
                "title": paper_data["title"],
                "authors": paper_data["authors"],
                "extraction_timestamp": paper_data.get("extraction_timestamp"),
                "total_equations": len(paper_data["equations"]),
                "equations": paper_data["equations"],
            },
            code=200,
        ).to_dict()

    except FileNotFoundError:
        logger.warning(f"Paper not cached: {paper_id}")
        return ApiResponse.error(
            error="Paper not cached",
            message=f"No cached data for {paper_id}",
            code=404,
        ).to_dict()

    except Exception as e:
        logger.error(f"Error loading paper {paper_id}: {e}")
        return ApiResponse.error(
            error="Error loading paper",
            message=str(e),
            code=500,
        ).to_dict()


# ============================================================================
# Formula Browser Endpoints (HTMX Integration)
# ============================================================================


@app.get("/api/formulas/arxiv-papers")
async def browse_arxiv_papers(limit: int = 20):
    """List cached arXiv papers as HTML fragment for HTMX."""
    from .formula_browser import arxiv_papers

    try:
        papers = arxiv_papers(limit=limit)
    except Exception as e:
        logger.error(f"Error listing papers: {e}")
        return HTMLResponse(
            '<p style="color: #999;">Unable to load papers. Please try again.</p>'
        )

    if not papers:
        return HTMLResponse(
            '<p style="color: #999;">No cached papers found. Use POST /api/arxiv/extract to download one.</p>'
        )

    html_parts = ['<div style="display: flex; flex-direction: column; gap: 6px;">']
    for paper in papers:
        safe_paper_id = html.escape(str(paper['paper_id']), quote=True)
        safe_title = html.escape(str(paper['title'][:50]))
        safe_authors = html.escape(str(paper.get('authors', 'Unknown')))

        html_parts.append(f'''
        <div style="padding: 8px; background: #f5f5f5; border-radius: 4px; cursor: pointer;"
             hx-get="/api/formulas/arxiv/{safe_paper_id}/equations"
             hx-target="#formula-browser-equations"
             hx-swap="innerHTML">
            <div style="font-weight: 500; font-size: 12px;">{safe_title}</div>
            <div style="font-size: 11px; color: #666;">{safe_paper_id} • {paper['total_equations']} eq • {paper['converted_equations']} ✅</div>
        </div>
        ''')
    html_parts.append('</div>')

    response = HTMLResponse(''.join(html_parts))
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/api/formulas/local-models")
async def browse_local_models(pattern: str = "*/src/model.py", root: str = "."):
    """Find local Python model files with FORMULAS dict (HTML for HTMX)."""
    from .formula_browser import local_models

    try:
        models = local_models(pattern=pattern, root=root)
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return HTMLResponse(
            '<p style="color: #999;">Unable to load models. Please try again.</p>'
        )

    if not models:
        return HTMLResponse(
            '<p style="color: #999;">No model.py files found matching pattern. Try exploring examples/*/src/model.py</p>'
        )

    html_parts = ['<div style="display: flex; flex-direction: column; gap: 6px;">']
    for model in models:
        safe_path = html.escape(str(model['path']), quote=True)
        safe_path_display = html.escape(str(model['path']))

        html_parts.append(f'''
        <div style="padding: 8px; background: #f5f5f5; border-radius: 4px; cursor: pointer;"
             hx-get="/api/formulas/local/{safe_path}/equations"
             hx-target="#formula-browser-equations"
             hx-swap="innerHTML">
            <div style="font-weight: 500; font-size: 12px;">🐍 {safe_path_display}</div>
            <div style="font-size: 11px; color: #666;">{model['formula_count']} formulas</div>
        </div>
        ''')
    html_parts.append('</div>')

    response = HTMLResponse(''.join(html_parts))
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/api/formulas/arxiv/{paper_id}/equations")
async def get_arxiv_equations(paper_id: str):
    """Get equations from cached arXiv paper (HTML for HTMX)."""
    from .formula_browser import arxiv_equations

    try:
        result = arxiv_equations(paper_id)
        equations = result['equations']

        safe_title = html.escape(str(result.get("title", "Unknown"))[:40])
        safe_authors = html.escape(str(result.get("authors", "Unknown"))[:50])

        html_parts = [
            f'<div style="padding: 8px;"><strong>{safe_title}</strong><br>',
            f'<span style="font-size: 11px; color: #666;">{safe_authors}</span>',
            '<div style="margin-top: 8px; display: flex; flex-direction: column; gap: 4px;">'
        ]

        for eq in equations[:10]:  # Show first 10
            status_icon = "✅" if eq.get('sympy_expr') else "⏳"
            latex_preview = html.escape(eq['latex'][:40].replace('{', '').replace('}', ''))
            eq_name = html.escape(str(eq.get('name', eq.get('index', 'unknown'))), quote=True)
            latex_json = json.dumps(eq['latex']).replace('"', '&quot;')

            html_parts.append(f'''
            <button style="text-align: left; padding: 6px; background: white; border: 1px solid #ddd; border-radius: 3px; cursor: pointer; font-size: 11px;"
                    onclick="window.insertFormula('{eq_name}', {latex_json})">
                {status_icon} {latex_preview}...
            </button>
            ''')

        if len(equations) > 10:
            html_parts.append(f'<p style="font-size: 11px; color: #999;">... and {len(equations)-10} more</p>')

        html_parts.append('</div></div>')

        response = HTMLResponse(''.join(html_parts))
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    except Exception as e:
        logger.error(f"Error getting equations for {paper_id}: {e}")
        return HTMLResponse(
            '<p style="color: #d32f2f;">Unable to load equations. Please try again.</p>'
        )


@app.get("/api/formulas/local/{path:path}/equations")
async def get_local_model_formulas(path: str):
    """Extract formulas from local model.py file (HTML for HTMX)."""
    from .formula_browser import local_model_formulas

    try:
        result = local_model_formulas(path)
        if result.get('error'):
            logger.warning(f"Error loading formulas from {path}: {result['error']}")
            return HTMLResponse(
                '<p style="color: #d32f2f;">Unable to load formulas from this file.</p>'
            )

        formulas = result['formulas']
        safe_path = html.escape(str(path))

        html_parts = [
            f'<div style="padding: 8px;"><strong>{safe_path}</strong>',
            '<div style="margin-top: 8px; display: flex; flex-direction: column; gap: 4px;">'
        ]

        for formula in formulas:
            latex_preview = html.escape(
                formula['latex'][:40] if formula['latex'] else '[error]'
            )
            formula_name = html.escape(formula['name'], quote=True)
            latex_json = json.dumps(formula['latex']).replace('"', '&quot;')

            html_parts.append(f'''
            <button style="text-align: left; padding: 6px; background: white; border: 1px solid #ddd; border-radius: 3px; cursor: pointer; font-size: 11px;"
                    onclick="window.insertFormula('{formula_name}', {latex_json})">
                {html.escape(formula['name'])}: {latex_preview}...
            </button>
            ''')

        html_parts.append('</div></div>')

        response = HTMLResponse(''.join(html_parts))
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    except Exception as e:
        logger.error(f"Error loading formulas from {path}: {e}")
        return HTMLResponse(
            '<p style="color: #d32f2f;">Unable to load formulas from this file.</p>'
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
