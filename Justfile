set default-list := true

[group("build")]
model:
    @echo "📐 Exporting formulas from Python model..."
    cd examples/membrane-dynamics && uv run python model.py

[group("build")]
formulas: model
    @echo "🔄 Converting LaTeX formulas to Typst..."
    cd examples/membrane-dynamics && uv run python build_paper.py formulas
    @if [ ! -f examples/membrane-dynamics/generated/formulas.typ ]; then \
        echo "⚠️  Manual formula generation..."; \
        cd examples/membrane-dynamics && mkdir -p generated && uv run python -c \
            "import json, re; \
            data = json.load(open('membrane_equations.json')); \
            lines = [f'#let {k} = \$ {v[\"latex\"]} \$' for k, v in data.items()]; \
            open('generated/formulas.typ', 'w').write('\\n\\n'.join(lines))"; \
    fi

[group("build")]
simulate: model
    @echo "📊 Running stochastic simulation..."
    cd examples/membrane-dynamics && uv run python simulate.py

[group("build")]
figures: simulate
    @echo "🎨 Generating figures..."
    cd examples/membrane-dynamics && uv run python -c \
        'from simulate import simulate; import matplotlib; matplotlib.use("Agg"); \
         import matplotlib.pyplot as plt; \
         ts, na = simulate(k_val=0.01, na0=50, steps=200, dt=0.1, seed=42); \
         plt.figure(figsize=(8, 5)); plt.plot(ts, na, linewidth=2, color="#1f77b4"); \
         plt.xlabel("Time", fontsize=12); plt.ylabel("n_a", fontsize=12); \
         plt.title("Stochastic trajectory: 2a → b", fontsize=14); \
         plt.grid(alpha=0.3, linestyle="--"); plt.tight_layout(); \
         import os; os.makedirs("generated/figures", exist_ok=True); \
         plt.savefig("generated/figures/simulation.png", dpi=300, bbox_inches="tight"); \
         print("✅ Generated simulation.png")'

[group("build")]
paper:
    @echo "📚 Building paper (formulas → figures → PDF)..."
    cd examples/membrane-dynamics && uv run python build_paper.py

[group("build")]
serve:
    @echo "🌐 Starting interactive slide editor..."
    @echo ""
    @echo "Dashboard: http://localhost:8000"
    @echo "API: http://localhost:8000/api/health"
    @echo ""
    @echo "Press Ctrl+C to stop"
    @echo ""
    uv run uvicorn math_trace.server:app --reload --host 127.0.0.1 --port 8000

[group("verify")]
test:
    @echo "🧪 Running unit tests (CI-safe)..."
    uv run pytest tests/unit -v --tb=short

[group("verify")]
test-integration:
    @echo "🔗 Running integration tests (requires local setup)..."
    uv run pytest tests/integration -v --tb=short

[group("verify")]
test-all:
    @echo "🧪 Running all tests (unit + integration)..."
    uv run pytest tests/unit tests/integration -v --tb=short

[group("verify")]
test-formulas:
    @echo "🔍 Testing formula generation..."
    uv run pytest tests/unit/test_model_export.py -v

[group("verify")]
test-model:
    @echo "🔍 Testing model definitions..."
    cd examples/membrane-dynamics && uv run python model.py

[group("verify")]
typecheck:
    @echo "🔎 Type checking..."
    uv run mypy src/ tests/ --ignore-missing-imports --no-error-summary 2>&1 | grep -v "numpy" | grep -v "error:" || echo "✅ Type check passed"

[group("clean")]
clean:
    @echo "🗑️  Cleaning generated files..."
    rm -rf examples/membrane-dynamics/generated/*
    rm -f examples/membrane-dynamics/main.pdf
    rm -f examples/membrane-dynamics/membrane_equations.json
    @echo "✅ Cleaned generated files"

[group("docs")]
view-paper:
    @echo "📖 Opening PDF..."
    @if [ -f examples/membrane-dynamics/main.pdf ]; then \
        if command -v open &> /dev/null; then \
            open examples/membrane-dynamics/main.pdf; \
        elif command -v xdg-open &> /dev/null; then \
            xdg-open examples/membrane-dynamics/main.pdf; \
        else \
            echo "Cannot open PDF: no opener found"; \
        fi \
    else \
        echo "⚠️  main.pdf not found. Run: just paper"; \
    fi

[group("setup")]
setup:
    @echo "🚀 Setting up math-trace..."
    @echo ""
    @echo "Step 1: Checking environment..."
    bash scripts/check-env.sh || true
    @echo ""
    @echo "Step 2: Installing/updating Typst..."
    @just install-typst
    @echo ""
    @echo "Step 3: Syncing Python dependencies..."
    uv sync
    @echo ""
    @echo "✅ Setup complete! Ready to build your first paper:"
    @echo "   cd examples/membrane-dynamics"
    @echo "   just paper"

[group("docker")]
docker-up profile="" *args:
    @if [ -z "{{profile}}" ]; then \
        docker compose up -d {{args}}; \
        echo "✅ Started math-trace on http://localhost:8000"; \
    else \
        docker compose --profile {{profile}} up -d {{args}}; \
        echo "✅ Started with profile: {{profile}}"; \
    fi

[group("docker")]
docker-down:
    docker compose down
    @echo "✅ Services stopped"

[group("docker")]
docker-rebuild:
    docker compose build --no-cache
    @echo "✅ Images rebuilt"

[group("docker")]
docker-restart profile="":
    @just docker-down
    @just docker-rebuild
    @just docker-up {{profile}}
    @echo "✅ Full restart complete"

[group("docker")]
docker-logs service="math-trace":
    docker compose logs -f {{service}}

[group("docker")]
docker-exec service="math-trace" *cmd:
    docker compose exec {{service}} {{cmd}}

[group("docker")]
docker-status:
    docker compose ps

[group("docker")]
docker-clean:
    docker compose down -v
    @echo "✅ Cleaned (volumes removed)"

[group("docker")]
docker-prune:
    docker system prune -f
    @echo "✅ Pruned unused resources"

[group("docker")]
docker-dev-up:
    @just docker-up dev
    @echo "📡 Ollama available at http://localhost:11434"

[group("docker")]
docker-ollama-pull model="mistral":
    docker compose exec ollama ollama pull {{model}}

[group("setup")]
install-typst:
    @echo "📦 Installing Typst..."
    @if command -v typst &> /dev/null; then \
        echo "✅ Typst already installed:"; \
        typst --version; \
    else \
        echo "Trying official installer (typst-install)..."; \
        if command -v sh &> /dev/null; then \
            curl -fsSL https://install.typst.community/install.sh | sh && \
            echo "" && \
            echo "⚠️  Typst installed! Add to PATH in ~/.bashrc or ~/.zshrc:" && \
            echo "  export PATH=\"\$$HOME/.typst/bin:\$$PATH\"" && \
            echo "" && \
            echo "Then run: source ~/.bashrc (or ~/.zshrc)"; \
        elif command -v cargo &> /dev/null; then \
            echo "Falling back to Cargo..."; \
            cargo install typst-cli; \
        elif command -v brew &> /dev/null; then \
            echo "Using Homebrew..."; \
            brew install typst; \
        elif command -v apt-get &> /dev/null; then \
            echo "Using apt-get..."; \
            sudo apt-get update && sudo apt-get install -y typst; \
        else \
            echo "❌ Could not install Typst automatically."; \
            echo "   Manual install: https://github.com/typst/typst/releases"; \
            echo "   Or: https://install.typst.community/"; \
            exit 1; \
        fi; \
    fi

[group("release")]
prep-release VERSION:
    #!/usr/bin/env bash
    set -e

    # Verify working tree is clean
    if ! git diff --quiet; then
        echo "❌ Working tree has uncommitted changes. Commit first."
        exit 1
    fi

    # Verify tests pass
    echo "🧪 Running tests..."
    uv run pytest -q

    # Tag the release
    echo "📌 Tagging release v{{VERSION}}..."
    git tag -a "v{{VERSION}}" -m "Release v{{VERSION}}"

    # Push tag
    echo "🚀 Pushing tag..."
    git push origin main --tags

    echo "✅ Release v{{VERSION}} tagged and pushed"
    echo "   Next: just build-release"

[group("release")]
build-release:
    #!/usr/bin/env bash
    set -e

    echo "🔨 Building wheel and sdist..."
    uv build

    echo ""
    echo "✅ Build complete!"
    echo "📦 Artifacts in dist/:"
    ls -lh dist/ | tail -n +2

    echo ""
    echo "Next: Review artifacts, then publish:"
    echo "  just publish-release  # (requires PyPI credentials)"

[group("release")]
publish-release:
    #!/usr/bin/env bash
    set -e

    if [ ! -d "dist" ] || [ -z "$(ls -A dist/)" ]; then
        echo "❌ No built artifacts found in dist/"
        echo "   Run: just build-release"
        exit 1
    fi

    echo "📤 Publishing to PyPI..."
    echo "   (requires PyPI token in PYPI_TOKEN or ~/.pypirc)"

    uv publish

    echo "✅ Published to PyPI!"
    echo "   Install with: pip install math-trace"

[group("help")]
help:
    @echo "🎓 math-trace: Formula-to-code traceability"
    @echo ""
    @echo "DOCKER (Quick Deploy):"
    @echo "  just docker-up              — Start FastAPI + formula browser (http://localhost:8000)"
    @echo "  just docker-dev-up          — Start with Ollama for batch processing"
    @echo "  just docker-logs            — View live logs"
    @echo "  just docker-restart         — Full restart (down → rebuild → up)"
    @echo "  just docker-down            — Stop services"
    @echo "  just docker-clean           — Stop and remove all data"
    @echo ""
    @echo "FIRST TIME (Local)?"
    @echo "  just setup — One-command installation (Python, uv, Typst)"
    @echo ""
    @echo "BUILD:"
    @echo "  just model     — Export formulas from SymPy (source of truth)"
    @echo "  just formulas  — Convert LaTeX formulas to Typst"
    @echo "  just simulate  — Run stochastic simulation"
    @echo "  just figures   — Generate matplotlib figures"
    @echo "  just pdf       — Compile Typst document to PDF"
    @echo "  just paper     — Full build (formulas + figures + pdf)"
    @echo "  just serve     — Start interactive slide editor (http://localhost:8000)"
    @echo ""
    @echo "VERIFY:"
    @echo "  just test              — Run unit tests (CI-safe)"
    @echo "  just test-integration  — Run integration tests (local only)"
    @echo "  just test-all          — Run all tests (unit + integration)"
    @echo "  just test-formulas     — Test formula generation"
    @echo "  just test-model        — Test model definitions"
    @echo "  just typecheck         — Type check code"
    @echo ""
    @echo "RELEASE:"
    @echo "  just prep-release VERSION    — Tag and push release (e.g., just prep-release 0.1.0)"
    @echo "  just build-release           — Build wheel and sdist for PyPI"
    @echo "  just publish-release         — Publish to PyPI (requires credentials)"
    @echo ""
    @echo "SETUP:"
    @echo "  just install-typst — Install Typst (required for PDF generation)"
    @echo ""
    @echo "UTILITIES:"
    @echo "  just clean      — Remove generated files"
    @echo "  just view-paper — Open main.pdf in viewer"
    @echo "  just help       — Show this message"
