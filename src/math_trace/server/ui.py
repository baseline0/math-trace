"""HTML dashboards served by the math-trace FastAPI server."""

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

HARDNESS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>math-trace: Lean hardness probe</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background: #f5f5f5; color: #222; }
        header { background: #1e1e1e; color: white; padding: 20px; }
        header h1 { margin: 0 0 6px; font-size: 24px; }
        header p { margin: 0; color: #bbb; font-size: 13px; }
        main { padding: 20px; max-width: 1200px; margin: 0 auto; }
        .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 20px; }
        .card { background: white; border-radius: 6px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
        .card .value { font-size: 28px; font-weight: 700; }
        .card .label { color: #666; font-size: 12px; text-transform: uppercase; }
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 6px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
        th, td { padding: 8px 10px; border-bottom: 1px solid #eee; font-size: 13px; text-align: left; vertical-align: top; }
        th { background: #fafafa; }
        .error { color: #c62828; }
        .status-ok { color: #2e7d32; }
        .status-error { color: #c62828; }
        .muted { color: #666; font-size: 12px; }
        .bar { height: 8px; background: #e0e0e0; border-radius: 4px; overflow: hidden; }
        .bar > span { display: block; height: 100%; background: #2196f3; }
        pre { white-space: pre-wrap; word-break: break-word; font-size: 12px; }
    </style>
</head>
<body>
    <header>
        <h1>Lean hardness probe dashboard</h1>
        <p>Read-only validation view over <code>reports/summary.json</code> and <code>reports/attempts/*.jsonl</code>.</p>
    </header>
    <main>
        <div id="status" class="muted">Loading…</div>
        <div class="cards" id="cards"></div>
        <h2>Cases</h2>
        <table>
            <thead>
                <tr>
                    <th>Case</th>
                    <th>Stubs</th>
                    <th>Telemetry</th>
                    <th>Max backtracks</th>
                    <th>Mean steps</th>
                    <th>Frictions</th>
                </tr>
            </thead>
            <tbody id="cases"></tbody>
        </table>
        <h2>Attempts</h2>
        <table>
            <thead>
                <tr>
                    <th>Case</th>
                    <th>Target</th>
                    <th>Status</th>
                    <th>Friction</th>
                    <th>Steps</th>
                    <th>Backtracks</th>
                    <th>Error</th>
                </tr>
            </thead>
            <tbody id="attempts"></tbody>
        </table>
    </main>
    <script>
        function esc(value) {
            return String(value ?? "").replace(/[&<>"']/g, ch => ({
                "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
            }[ch]));
        }
        async function load() {
            const response = await fetch("/api/hardness/summary");
            if (!response.ok) {
                document.getElementById("status").textContent = "Could not load hardness report.";
                return;
            }
            const data = await response.json();
            document.getElementById("status").textContent =
                `Probe root: ${data.probeRoot} | ${data.totalStubs} stubs | ${data.totalTelemetryRecords} telemetry records`;
            const cards = document.getElementById("cards");
            cards.innerHTML = `
                <div class="card"><div class="value">${data.totalStubs}</div><div class="label">Stubs</div></div>
                <div class="card"><div class="value">${data.totalTelemetryRecords}</div><div class="label">Telemetry records</div></div>
                <div class="card"><div class="value">${data.cases.length}</div><div class="label">Cases</div></div>
            `;
            const cases = document.getElementById("cases");
            cases.innerHTML = data.cases.map(item => `
                <tr>
                    <td><strong>${esc(item.case_id)}</strong><div class="muted">${esc(item.targets.join(", "))}</div></td>
                    <td>${item.stubs}</td>
                    <td>${item.attempt_records.length}</td>
                    <td>${item.max_backtracks}</td>
                    <td>${Number(item.mean_proof_steps).toFixed(2)}</td>
                    <td>${esc(item.friction_mix || "-")}</td>
                </tr>
            `).join("");
            const attempts = document.getElementById("attempts");
            const rows = data.cases.flatMap(item => item.attempt_records.map(attempt => `
                <tr>
                    <td>${esc(attempt.case_id)}</td>
                    <td>${esc(attempt.target_name)}</td>
                    <td class="${attempt.status === "ok" ? "status-ok" : "status-error"}">${esc(attempt.status)}</td>
                    <td>${esc(attempt.friction)}</td>
                    <td>${attempt.proof_steps ?? "-"}</td>
                    <td>${attempt.backtracks ?? "-"}</td>
                    <td><pre>${esc((attempt.error_message || "").slice(0, 180))}</pre></td>
                </tr>
            `));
            attempts.innerHTML = rows.join("");
        }
        load().catch(error => {
            document.getElementById("status").textContent = `Failed to load report: ${error}`;
        });
    </script>
</body>
</html>
"""
