"""FastAPI server for interactive slide development & formula debugging.

Provides web UI for:
- Live formula editing (JSON)
- Configuration editing (YAML)
- Real-time slide preview (Marp → HTML)
- Export (slides.md, PDF via Marp)
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .presentation_generator import MarpBackend, PresentationConfig

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
    backend: str = "marp",
):
    """Live preview of slides with current formulas + config.

    Args:
        formulas: Dictionary of formula definitions (name → latex)
        config: Presentation config (title, author, theme, etc.)
        backend: Rendering backend ("marp", "reveal", "beamer")

    Returns:
        Rendered HTML or error message
    """
    try:
        if not formulas:
            return {"status": "error", "message": "No formulas provided"}

        # Use default config if not provided
        if config is None:
            config = {
                "title": "Untitled Presentation",
                "author": "Unknown",
                "theme": "default",
            }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Render presentation
            try:
                # Ensure config has required fields for PresentationConfig
                if "format" not in config:
                    config["format"] = "talk"
                if "backend" not in config:
                    config["backend"] = backend
                if "slides" not in config:
                    config["slides"] = []

                # Create presentation config
                pres_config = PresentationConfig(**config)

                # Render using Marp backend
                marp = MarpBackend()
                result_path = marp.render(pres_config, formulas, tmpdir_path)

                # Read and return result
                if result_path.exists():
                    markdown = result_path.read_text()
                    return {"status": "success", "markdown": markdown}
                else:
                    return {"status": "error", "message": "Rendering produced no output"}
            except TypeError as e:
                return {"status": "error", "message": f"Config error: {str(e)}"}
            except Exception as e:
                return {"status": "error", "message": f"Render failed: {str(e)}"}

    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON: {str(e)}"}
    except yaml.YAMLError as e:
        return {"status": "error", "message": f"Invalid YAML: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


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
                # Ensure config has required fields
                if "format" not in config:
                    config["format"] = "talk"
                if "backend" not in config:
                    config["backend"] = format or "marp"
                if "slides" not in config:
                    config["slides"] = []

                # Create presentation config
                pres_config = PresentationConfig(**config)

                # Render using Marp backend
                marp = MarpBackend()
                result_path = marp.render(pres_config, formulas, tmpdir_path)

                # Return file for download
                if result_path.exists():
                    return FileResponse(
                        result_path,
                        media_type="text/markdown",
                        filename="slides.md",
                    )
                else:
                    raise HTTPException(500, "Export generation failed")
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
        <!-- Left: Editors -->
        <div class="editor-panel">
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
                <span style="font-size: 12px; color: #999;">Marp backend</span>
            </div>
            <div class="preview-content">
                <div class="status-message" id="status"></div>
                <div id="preview" style="min-height: 300px;"></div>
            </div>
        </div>
    </div>

    <script>
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
                    body: JSON.stringify({ formulas, config, backend: 'marp' })
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
