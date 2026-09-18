# Biochemistry Template

A fork-friendly template for publishing biochemistry papers with formula-to-code traceability.

## What's Included

- **model.py** — Define biochemistry formulas using SymPy
- **simulate.py** — Simulate enzyme kinetics and generate data
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

## How to Adapt This Template

### Step 1: Edit `model.py`

Define your own biochemistry equations (receptor binding, kinetics, thermodynamics):

```python
def export_formulas() -> dict:
    k_on, k_off, Kd = sp.symbols('k_on k_off K_d', positive=True)

    formulas = {
        "binding_affinity": {
            "latex": sp.latex(sp.Eq(Kd, k_off / k_on)),
            "description": "Dissociation constant from kinetic rates",
            "source_line": 15,
        },
    }
    return formulas
```

### Step 2: Edit `simulate.py`

Implement your biochemical simulation:

```python
def simulate_my_assay(...) -> tuple[np.ndarray, np.ndarray]:
    # Your biochemistry here
    return data_array, result_array
```

### Step 3: Edit `main.typ`

Update the paper narrative, include your formulas and figures.

### Step 4: Build

```bash
python build_paper.py
```

## Example: Michaelis-Menten Enzyme Kinetics

This template demonstrates **enzyme kinetics** with:

- **Michaelis-Menten equation** — classic model of enzyme catalysis
- **Simulation** — realistic enzyme data with measurement noise
- **Figures** — Michaelis-Menten curve + Lineweaver-Burk double-reciprocal plot
- **Paper** — complete writeup explaining the theory and results

Key parameters:
- `Vmax = 100.0 μmol/min` — maximum reaction velocity
- `Km = 5.0 mM` — substrate affinity
- `S range: 0.01–50 mM` — substrate concentration range

## Domain Ideas

Biochemistry has many fascinating systems you can model:

### Protein-Ligand Binding
- Dose-response curves (EC50, Hill coefficient)
- Binding kinetics (k_on, k_off, Kd)
- Allosteric effects

### Metabolic Pathways
- Flux-balance analysis
- Feedback inhibition
- Multi-enzyme cascades

### Gene Regulation
- Transcription rate equations
- Protein synthesis + degradation
- Genetic circuits

### Drug Pharmacokinetics
- Absorption, distribution, metabolism, excretion (ADME)
- Half-life and steady-state concentration
- Drug-target interactions

## Output Files

```
templates/biochemistry/
├── model.py                      ← Edit: your biochemistry formulas
├── simulate.py                   ← Edit: your simulation code
├── main.typ                      ← Edit: your paper narrative
├── build_paper.py                ← Build pipeline (run once)
├── biochemistry_equations.json   ← Auto-generated from model.py
├── generated/
│   ├── formulas.typ              ← Auto-generated Typst definitions
│   └── figures/
│       └── kinetics.png          ← Auto-generated figure
└── main.pdf                      ← Auto-generated (needs Typst)
```

## Troubleshooting

**"No module named 'sympy'"**
```bash
cd ../..
uv add sympy matplotlib numpy
```

**Simulation doesn't run**
```bash
# Test simulate.py directly
python simulate.py

# If that fails, check imports
python -c "import numpy; import matplotlib; print('OK')"
```

**Figures not generating**
- Ensure `generated/figures/` directory exists: `mkdir -p generated/figures`
- Check that `simulate.py` runs without errors

**"Typst not found"**
```bash
cd ../..
just install-typst
```

## Next Steps

1. Fork this directory: `cp -r templates/biochemistry ../my-kinetics-paper`
2. Edit model.py with your enzyme equations
3. Edit simulate.py with your kinetics simulation
4. Edit main.typ with your paper narrative
5. Run `python build_paper.py`
6. Commit and share your reproducible research!

## References

- Michaelis, L., & Menten, M. (1913). "Die Kinetik der Invertinwirkung"
- Lineweaver, H., & Burk, D. (1934). "The Determination of Enzyme Dissociation Constants"
- Cornish-Bowden, A. (2012). "Fundamentals of Enzyme Kinetics" (Wiley)

## Learn More

See [TEMPLATE-USAGE.md](../TEMPLATE-USAGE.md) for advanced customization.

See [math-trace README](../../README.md) for the full framework.
