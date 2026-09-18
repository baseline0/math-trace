# Simple Physics Template

A fork-friendly template for publishing physics papers with formula-to-code traceability.

## What's Included

- **model.py** — Define physics formulas using SymPy
- **simulate.py** — Run simulations and generate data
- **build_paper.py** — Build pipeline (formulas → figures → PDF)
- **main.typ** — Publication-quality paper template (Typst)
- **generated/** — Output directory (formulas, figures, PDF)

## Quick Start

```bash
# 1. Export formulas to Typst
python model.py

# 2. Run simulation and generate figures
python simulate.py

# 3. Build complete paper (all steps)
python build_paper.py
```

Or from the parent math-trace directory:

```bash
cd templates/simple-physics
python ../../../examples/membrane-dynamics/build_paper.py  # Reuse build script
```

## How to Adapt This Template

### Step 1: Edit `model.py`

Define your own physics equations:

```python
def export_formulas() -> dict:
    x, t, m = sp.symbols('x t m', real=True)

    formulas = {
        "my_equation": {
            "latex": sp.latex(...),
            "description": "What this equation means",
            "source_line": 15,
        },
    }
    return formulas
```

### Step 2: Edit `simulate.py`

Implement your physics simulation:

```python
def simulate_my_system(...) -> tuple[np.ndarray, np.ndarray]:
    # Your physics here
    return time_array, data_array
```

### Step 3: Edit `main.typ`

Update the paper narrative, include your formulas and figures:

```typst
#include "generated/formulas.typ"

#figure(image("generated/figures/my-figure.png"))
```

### Step 4: Build

```bash
python build_paper.py
```

## Output

- `generated/formulas.typ` — Typst definitions of all formulas
- `generated/figures/*.png` — Matplotlib figures from simulation
- `main.pdf` — Final paper (requires Typst; see install instructions)

## Install Typst

If you want PDF output:

```bash
# From parent directory:
cd ../..
just install-typst
```

Or manually: https://github.com/typst/typst/releases

## Files Generated

```
templates/simple-physics/
├── model.py                 ← Edit: your physics formulas
├── simulate.py              ← Edit: your simulation code
├── main.typ                 ← Edit: your paper narrative
├── build_paper.py           ← Build pipeline (run once)
├── physics_equations.json   ← Auto-generated from model.py
├── generated/
│   ├── formulas.typ         ← Auto-generated Typst definitions
│   └── figures/
│       └── oscillator.png   ← Auto-generated figure
└── main.pdf                 ← Auto-generated (needs Typst)
```

## Why This Structure?

1. **model.py is source of truth** — Formulas live in Python, not scattered in Typst
2. **simulate.py is reproducible** — Every figure is generated from code, not hand-drawn
3. **build_paper.py is deterministic** — Same input always produces same output
4. **Traceable** — Click "source_line" in metadata to jump to formula definition

## Next Steps

1. Fork this directory: `cp -r templates/simple-physics ../my-physics-paper`
2. Edit model.py, simulate.py, main.typ with your content
3. Run `python build_paper.py`
4. Commit your paper and formulas to version control
5. Share your .typ and figures with collaborators

## Troubleshooting

**"No module named 'sympy'"**
```bash
cd ../..
uv add sympy matplotlib
```

**"Typst not found"**
```bash
cd ../..
just install-typst
```

**Figures not generating**
- Check `simulate.py` runs without errors: `python simulate.py`
- Ensure `generated/figures/` directory exists

**PDF not generated**
- Typst is optional; formulas and figures work without it
- To generate PDF: install Typst and run `python build_paper.py` again

## Learn More

See [TEMPLATE-USAGE.md](../TEMPLATE-USAGE.md) for advanced customization.

See [math-trace README](../../README.md) for the full framework.
