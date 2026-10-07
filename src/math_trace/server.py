"""FastAPI server for formula extraction and verification.

Provides web UI for:
- Paste arXiv URL to extract formulas
- View extracted formulas in JSON
- Navigate formulas with arrow keys
- Preview formula rendering
"""

from __future__ import annotations

import html
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .arxiv_extractor import (
    download_and_extract_equations,
    extract_arxiv_id,
    load_extracted_paper,
    save_extracted_paper,
)
from .logging import get_logger
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


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@app.post("/api/fetch-paper")
async def fetch_paper(url: str):
    """Fetch arXiv paper and extract formulas.

    Args:
        url: arXiv URL or paper ID (e.g., "2609.21904" or "https://arxiv.org/abs/2609.21904")

    Returns:
        {"status": "success", "paper_id": "...", "count": 42}
    """
    try:
        # Extract paper ID from URL or use directly
        paper_id = extract_arxiv_id(url)
        logger.info(f"Fetching paper {paper_id}")

        # Download and extract equations
        _tar_path, equations = download_and_extract_equations(paper_id)
        logger.info(f"Extracted {len(equations)} equations from {paper_id}")

        # Save to cache
        save_extracted_paper(paper_id)

        return {
            "status": "success",
            "paper_id": paper_id,
            "count": len(equations),
        }
    except Exception as e:
        logger.error(f"Error fetching paper: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/api/formulas")
async def get_formulas(paper_id: str):
    """Get extracted formulas for a paper.

    Args:
        paper_id: arXiv paper ID

    Returns:
        {"status": "success", "formulas": [{"id": "eq1", "name": "...", "latex": "..."}]}
    """
    try:
        data = load_extracted_paper(paper_id)
        if not data:
            raise HTTPException(status_code=404, detail=f"No formulas found for {paper_id}")

        # Convert to frontend format
        formulas = []
        for i, eq in enumerate(data.get("equations", [])):
            formulas.append(
                {
                    "id": f"eq{i}",
                    "name": eq.get("context", "Formula")[:50],
                    "latex": eq.get("latex", ""),
                    "description": eq.get("context", ""),
                    "source_line": i,
                    "source_file": "arxiv",
                }
            )

        return {
            "status": "success",
            "formulas": formulas,
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Formulas not found for {paper_id}") from e
    except Exception as e:
        logger.error(f"Error loading formulas: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/preview/{paper_id}/{formula_id}")
async def get_preview(paper_id: str, formula_id: str):
    """Get MathJax preview for a formula.

    Args:
        paper_id: arXiv paper ID
        formula_id: formula ID (e.g., "eq0")

    Returns:
        {"status": "success", "latex": "x^2 + y^2"}
    """
    try:
        data = load_extracted_paper(paper_id)
        if not data:
            raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")

        # Parse formula ID
        idx = int(formula_id[2:]) if formula_id.startswith("eq") else int(formula_id)
        equations = data.get("equations", [])

        if idx >= len(equations):
            raise HTTPException(status_code=404, detail=f"Formula {formula_id} not found")

        eq = equations[idx]
        return {
            "status": "success",
            "latex": eq.get("latex", ""),
        }
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found") from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid formula ID") from e
    except Exception as e:
        logger.error(f"Error getting preview: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ============================================================================
# Web UI
# ============================================================================


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>math-trace: Formula Extractor</title>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        header {
            background: #1e1e1e;
            color: white;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        header h1 {
            font-size: 24px;
            margin-bottom: 15px;
        }

        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }

        #arxiv-url {
            flex: 1;
            padding: 10px;
            border: 1px solid #555;
            border-radius: 4px;
            background: #2a2a2a;
            color: white;
            font-size: 14px;
        }

        #arxiv-url::placeholder {
            color: #888;
        }

        button {
            padding: 10px 20px;
            background: #2196f3;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
        }

        button:hover {
            background: #1976d2;
        }

        button:disabled {
            background: #666;
            cursor: not-allowed;
        }

        .status-bar {
            padding: 10px 20px;
            background: #2a2a2a;
            color: #aaa;
            font-size: 13px;
            border-top: 1px solid #444;
        }

        .container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }

        .left-panel, .right-panel {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            border-right: 1px solid #ddd;
        }

        .right-panel {
            border-right: none;
            background: white;
        }

        .panel-header {
            font-weight: 600;
            margin-bottom: 15px;
            font-size: 16px;
            color: #333;
        }

        pre {
            background: #f0f0f0;
            padding: 12px;
            border-radius: 4px;
            font-size: 13px;
            overflow-x: auto;
            max-height: 400px;
            overflow-y: auto;
        }

        .formula-preview {
            padding: 20px;
            background: white;
            border-radius: 4px;
            min-height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }

        .formula-math {
            font-size: 24px;
            margin: 20px 0;
        }

        .formula-info {
            font-size: 12px;
            color: #666;
            margin-top: 20px;
            text-align: center;
        }

        .formula-nav {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 20px;
            align-items: center;
        }

        .formula-nav button {
            padding: 8px 15px;
            font-size: 14px;
        }

        .formula-counter {
            font-size: 14px;
            color: #666;
            min-width: 80px;
            text-align: center;
        }

        .loading {
            text-align: center;
            color: #999;
            padding: 40px;
        }

        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 15px;
        }

        .success {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <header>
        <h1>📄 Math-Trace Formula Extractor</h1>
        <div class="input-group">
            <input
                type="text"
                id="arxiv-url"
                placeholder="https://arxiv.org/abs/2609.21904"
            />
            <button id="fetch-btn" onclick="fetchPaper()">🔽 Fetch Paper</button>
        </div>
        <div id="message"></div>
    </header>

    <div class="status-bar">
        <span id="status">Ready to extract | Paper: <strong id="paper-name">None loaded</strong></span>
    </div>

    <div class="container">
        <div class="left-panel">
            <div class="panel-header">📋 Formula JSON</div>
            <pre id="json-display">{
  "formulas": []
}</pre>
        </div>

        <div class="right-panel">
            <div class="panel-header">👁️ Preview</div>
            <div id="preview-container">
                <div class="loading">
                    No formulas loaded yet.<br>
                    Paste an arXiv URL above to start.
                </div>
            </div>

            <div class="formula-nav" id="nav-container" style="display: none;">
                <button onclick="prevFormula()">← Prev</button>
                <div class="formula-counter">
                    <span id="formula-index">0</span> / <span id="formula-total">0</span>
                </div>
                <button onclick="nextFormula()">Next →</button>
            </div>
        </div>
    </div>

    <script>
        let currentFormulas = [];
        let currentIndex = 0;

        async function fetchPaper() {
            const url = document.getElementById('arxiv-url').value.trim();
            if (!url) {
                showMessage('Please enter an arXiv URL', 'error');
                return;
            }

            document.getElementById('fetch-btn').disabled = true;
            showMessage('Extracting formulas...', 'loading');

            try {
                // Fetch paper and extract formulas
                const fetchResp = await fetch('/api/fetch-paper?url=' + encodeURIComponent(url), {
                    method: 'POST'
                });
                if (!fetchResp.ok) {
                    const err = await fetchResp.json();
                    throw new Error(err.detail || 'Failed to fetch paper');
                }
                const fetchData = await fetchResp.json();
                const paperId = fetchData.paper_id;
                document.getElementById('paper-name').innerText = paperId;

                // Load formulas
                const formResp = await fetch('/api/formulas?paper_id=' + encodeURIComponent(paperId));
                if (!formResp.ok) {
                    throw new Error('Failed to load formulas');
                }
                const formData = await formResp.json();
                currentFormulas = formData.formulas;
                currentIndex = 0;

                showMessage(`✓ Extracted ${currentFormulas.length} formulas`, 'success');
                setTimeout(() => { document.getElementById('message').innerHTML = ''; }, 2000);
                updatePreview();
            } catch (error) {
                showMessage(`Error: ${error.message}`, 'error');
                currentFormulas = [];
                updatePreview();
            } finally {
                document.getElementById('fetch-btn').disabled = false;
            }
        }

        function showMessage(msg, type) {
            const el = document.getElementById('message');
            el.innerHTML = `<div class="${type}">${msg}</div>`;
            if (type === 'loading') {
                setTimeout(() => { el.innerHTML = ''; }, 3000);
            }
        }

        function updatePreview() {
            const container = document.getElementById('preview-container');
            const navContainer = document.getElementById('nav-container');

            if (currentFormulas.length === 0) {
                container.innerHTML = `
                    <div class="loading">
                        No formulas loaded yet.<br>
                        Paste an arXiv URL above to start.
                    </div>
                `;
                navContainer.style.display = 'none';
                document.getElementById('json-display').innerText =
                    JSON.stringify({ formulas: [] }, null, 2);
                return;
            }

            const formula = currentFormulas[currentIndex];
            container.innerHTML = `
                <div class="formula-preview">
                    <div><strong>${formula.name || 'Formula'}</strong></div>
                    <div class="formula-math">\\[${formula.latex}\\]</div>
                    <div class="formula-info">
                        ${formula.description || ''}<br>
                        Line ${formula.source_line} in ${formula.source_file || 'source'}
                    </div>
                </div>
            `;

            // Update JSON display
            document.getElementById('json-display').innerText =
                JSON.stringify({ formulas: currentFormulas }, null, 2);

            // Update navigation
            navContainer.style.display = 'flex';
            document.getElementById('formula-index').innerText = currentIndex + 1;
            document.getElementById('formula-total').innerText = currentFormulas.length;

            // Re-render math
            if (window.MathJax) {
                MathJax.typesetPromise().catch(e => console.log(e));
            }
        }

        function prevFormula() {
            if (currentFormulas.length === 0) return;
            currentIndex = (currentIndex - 1 + currentFormulas.length) % currentFormulas.length;
            updatePreview();
        }

        function nextFormula() {
            if (currentFormulas.length === 0) return;
            currentIndex = (currentIndex + 1) % currentFormulas.length;
            updatePreview();
        }

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (currentFormulas.length === 0) return;
            if (e.key === 'ArrowLeft') prevFormula();
            if (e.key === 'ArrowRight') nextFormula();
        });

        // Enter to fetch
        document.getElementById('arxiv-url').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') fetchPaper();
        });
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
        return HTMLResponse('<p style="color: #999;">Unable to load papers. Please try again.</p>')

    if not papers:
        return HTMLResponse(
            '<p style="color: #999;">No cached papers found. Use POST /api/arxiv/extract to download one.</p>'
        )

    html_parts = ['<div style="display: flex; flex-direction: column; gap: 6px;">']
    for paper in papers:
        safe_paper_id = html.escape(str(paper["paper_id"]), quote=True)
        safe_title = html.escape(str(paper["title"][:50]))

        html_parts.append(f"""
        <div style="padding: 8px; background: #f5f5f5; border-radius: 4px; cursor: pointer;"
             hx-get="/api/formulas/arxiv/{safe_paper_id}/equations"
             hx-target="#formula-browser-equations"
             hx-swap="innerHTML">
            <div style="font-weight: 500; font-size: 12px;">{safe_title}</div>
            <div style="font-size: 11px; color: #666;">{safe_paper_id} • {paper["total_equations"]} eq • {paper["converted_equations"]} ✅</div>
        </div>
        """)
    html_parts.append("</div>")

    response = HTMLResponse("".join(html_parts))
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
        return HTMLResponse('<p style="color: #999;">Unable to load models. Please try again.</p>')

    if not models:
        return HTMLResponse(
            '<p style="color: #999;">No model.py files found matching pattern. Try exploring examples/*/src/model.py</p>'
        )

    html_parts = ['<div style="display: flex; flex-direction: column; gap: 6px;">']
    for model in models:
        safe_path = html.escape(str(model["path"]), quote=True)
        safe_path_display = html.escape(str(model["path"]))

        html_parts.append(f"""
        <div style="padding: 8px; background: #f5f5f5; border-radius: 4px; cursor: pointer;"
             hx-get="/api/formulas/local/{safe_path}/equations"
             hx-target="#formula-browser-equations"
             hx-swap="innerHTML">
            <div style="font-weight: 500; font-size: 12px;">🐍 {safe_path_display}</div>
            <div style="font-size: 11px; color: #666;">{model["formula_count"]} formulas</div>
        </div>
        """)
    html_parts.append("</div>")

    response = HTMLResponse("".join(html_parts))
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/api/formulas/arxiv/{paper_id}/equations")
async def get_arxiv_equations(paper_id: str):
    """Get equations from cached arXiv paper (HTML for HTMX)."""
    from .formula_browser import arxiv_equations

    try:
        result = arxiv_equations(paper_id)
        equations = result["equations"]

        safe_title = html.escape(str(result.get("title", "Unknown"))[:40])
        safe_authors = html.escape(str(result.get("authors", "Unknown"))[:50])

        html_parts = [
            f'<div style="padding: 8px;"><strong>{safe_title}</strong><br>',
            f'<span style="font-size: 11px; color: #666;">{safe_authors}</span>',
            '<div style="margin-top: 8px; display: flex; flex-direction: column; gap: 4px;">',
        ]

        for eq in equations[:10]:  # Show first 10
            status_icon = "✅" if eq.get("sympy_expr") else "⏳"
            latex_preview = html.escape(eq["latex"][:40].replace("{", "").replace("}", ""))
            eq_name = html.escape(str(eq.get("name", eq.get("index", "unknown"))), quote=True)
            latex_json = json.dumps(eq["latex"]).replace('"', "&quot;")

            html_parts.append(f"""
            <button style="text-align: left; padding: 6px; background: white; border: 1px solid #ddd; border-radius: 3px; cursor: pointer; font-size: 11px;"
                    onclick="window.insertFormula('{eq_name}', {latex_json})">
                {status_icon} {latex_preview}...
            </button>
            """)

        if len(equations) > 10:
            html_parts.append(f'<p style="font-size: 11px; color: #999;">... and {len(equations) - 10} more</p>')

        html_parts.append("</div></div>")

        response = HTMLResponse("".join(html_parts))
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    except Exception as e:
        logger.error(f"Error getting equations for {paper_id}: {e}")
        return HTMLResponse('<p style="color: #d32f2f;">Unable to load equations. Please try again.</p>')


@app.get("/api/formulas/local/{path:path}/equations")
async def get_local_model_formulas(path: str):
    """Extract formulas from local model.py file (HTML for HTMX)."""
    from .formula_browser import local_model_formulas

    try:
        result = local_model_formulas(path)
        if result.get("error"):
            logger.warning(f"Error loading formulas from {path}: {result['error']}")
            return HTMLResponse('<p style="color: #d32f2f;">Unable to load formulas from this file.</p>')

        formulas = result["formulas"]
        safe_path = html.escape(str(path))

        html_parts = [
            f'<div style="padding: 8px;"><strong>{safe_path}</strong>',
            '<div style="margin-top: 8px; display: flex; flex-direction: column; gap: 4px;">',
        ]

        for formula in formulas:
            latex_preview = html.escape(formula["latex"][:40] if formula["latex"] else "[error]")
            formula_name = html.escape(formula["name"], quote=True)
            latex_json = json.dumps(formula["latex"]).replace('"', "&quot;")

            html_parts.append(f"""
            <button style="text-align: left; padding: 6px; background: white; border: 1px solid #ddd; border-radius: 3px; cursor: pointer; font-size: 11px;"
                    onclick="window.insertFormula('{formula_name}', {latex_json})">
                {html.escape(formula["name"])}: {latex_preview}...
            </button>
            """)

        html_parts.append("</div></div>")

        response = HTMLResponse("".join(html_parts))
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    except Exception as e:
        logger.error(f"Error loading formulas from {path}: {e}")
        return HTMLResponse('<p style="color: #d32f2f;">Unable to load formulas from this file.</p>')


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
