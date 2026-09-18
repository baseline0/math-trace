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
        "from simulate import simulate; import matplotlib; matplotlib.use('Agg'); \
         import matplotlib.pyplot as plt; \
         ts, na = simulate(k_val=0.01, na0=50, steps=200, dt=0.1, seed=42); \
         plt.figure(figsize=(8, 5)); plt.plot(ts, na, linewidth=2, color='#1f77b4'); \
         plt.xlabel('Time', fontsize=12); plt.ylabel('\\$n_a\\$', fontsize=12); \
         plt.title('Stochastic trajectory of \\$2a \\to b\\$', fontsize=14); \
         plt.grid(alpha=0.3, linestyle='--'); plt.tight_layout(); \
         import os; os.makedirs('generated/figures', exist_ok=True); \
         plt.savefig('generated/figures/simulation.png', dpi=300, bbox_inches='tight'); \
         print('✅ Generated simulation.png')"

[group("build")]
pdf: formulas figures
    @echo "📝 Compiling Typst document..."
    @if command -v typst &> /dev/null; then \
        cd examples/membrane-dynamics && typst compile main.typ && echo "✅ Generated main.pdf"; \
    else \
        echo "⚠️  typst not found. Install: cargo install typst-cli"; \
        echo "   Or visit: https://github.com/typst/typst/releases"; \
    fi

[group("build")]
paper: pdf
    @echo "🎉 Paper complete: examples/membrane-dynamics/main.pdf"
    @ls -lh examples/membrane-dynamics/main.pdf 2>/dev/null || echo "⚠️  PDF not found (typst may not be installed)"

[group("verify")]
test:
    @echo "🧪 Running tests..."
    uv run pytest tests/ -v --tb=short

[group("verify")]
test-formulas:
    @echo "🔍 Testing formula generation..."
    uv run pytest tests/test_model_export.py -v

[group("verify")]
test-model:
    @echo "🔍 Testing model definitions..."
    cd examples/membrane-dynamics && uv run python model.py

[group("verify")]
typecheck:
    @echo "🔎 Type checking..."
    uv run mypy src/ tests/ --ignore-missing-imports

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

[group("help")]
help:
    @echo "🎓 math-trace: Formula-to-code traceability"
    @echo ""
    @echo "BUILD:"
    @echo "  just model     — Export formulas from SymPy (source of truth)"
    @echo "  just formulas  — Convert LaTeX formulas to Typst"
    @echo "  just simulate  — Run stochastic simulation"
    @echo "  just figures   — Generate matplotlib figures"
    @echo "  just pdf       — Compile Typst document to PDF"
    @echo "  just paper     — Full build (formulas + figures + pdf)"
    @echo ""
    @echo "VERIFY:"
    @echo "  just test          — Run full test suite"
    @echo "  just test-formulas — Test formula generation"
    @echo "  just test-model    — Test model definitions"
    @echo "  just typecheck     — Type check code"
    @echo ""
    @echo "UTILITIES:"
    @echo "  just clean      — Remove generated files"
    @echo "  just view-paper — Open main.pdf in viewer"
    @echo "  just help       — Show this message"
