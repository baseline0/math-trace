# Template Usage Guide

This directory contains **fork-friendly templates** for publishing research papers with formula-to-code traceability.

## What Are Templates?

Templates are complete, working examples organized by scientific domain:

- **simple-physics/** — Classical mechanics, oscillations, dynamics
- **biochemistry/** — Enzyme kinetics, protein-ligand binding, metabolism
- **[Add your domain here!]** — Statistics, neuroscience, materials science, etc.

Each template includes:

1. **model.py** — Define formulas using SymPy (source of truth)
2. **simulate.py** — Run simulations and generate data
3. **build_paper.py** — Build pipeline (formulas → figures → PDF)
4. **main.typ** — Publication-quality paper template
5. **README.md** — Domain-specific customization guide

## Quick Start: Use a Template

### 1. Choose a Template

```bash
cd templates/simple-physics  # or biochemistry/
```

### 2. Run the Build

```bash
python build_paper.py
```

You'll get:
- `generated/formulas.typ` — All your SymPy equations in Typst format
- `generated/figures/*.png` — Matplotlib figures from your simulation
- `main.pdf` — Final publication (if Typst installed)

### 3. Customize

Edit these files for your research:

- **model.py** — Replace example equations with YOUR formulas
- **simulate.py** — Replace example simulation with YOUR physics
- **main.typ** — Update narrative, figures, and conclusions
- **README.md** — Document your domain-specific parameters

## Workflow: From Template to Publication

### Example: Adapting simple-physics/ to Your Domain

#### Step 1: Copy the Template

```bash
cd templates/
cp -r simple-physics ../my-optical-physics
cd ../my-optical-physics
```

#### Step 2: Update model.py

Replace harmonic oscillator formulas with your domain:

```python
def export_formulas() -> dict:
    # Your domain here: optics, photonics, waves, etc.
    theta, n1, n2 = sp.symbols('theta n_1 n_2', real=True)
    
    formulas = {
        "snells_law": {
            "latex": sp.latex(sp.Eq(n1 * sp.sin(theta), n2 * sp.sin(sp.Symbol('theta_t')))),
            "description": "Snell's law of refraction",
            "source_line": 18,
        },
    }
    return formulas
```

#### Step 3: Update simulate.py

Replace the oscillator simulation with your physics:

```python
def simulate_light_refraction(...):
    # Your simulation here: ray tracing, diffraction, etc.
    theta_in = np.linspace(0, 90, 100)
    theta_out = np.arcsin(np.sin(np.radians(theta_in)) * n1/n2)
    return theta_in, np.degrees(theta_out)
```

#### Step 4: Update main.typ

Edit the paper to describe YOUR research:

```typst
= Refraction and Snell's Law

#figure(image("generated/figures/refraction.png"))

// Include your formulas
#include "generated/formulas.typ"
```

#### Step 5: Build & Publish

```bash
python build_paper.py

# Commit to git
git add model.py simulate.py main.typ generated/
git commit -m "My optical physics paper"
```

## Advanced: Custom Figures & Analysis

### Multiple Figures in One Paper

Edit `simulate.py` to generate multiple figures:

```python
def generate_figures() -> bool:
    # Generate multiple figures
    fig_path_1 = Path('generated/figures/measurement.png')
    fig_path_2 = Path('generated/figures/analysis.png')
    
    # ... generate both ...
    
    return True
```

Then reference them in `main.typ`:

```typst
#figure(image("generated/figures/measurement.png"), caption: [Raw data])
#figure(image("generated/figures/analysis.png"), caption: [Processed results])
```

### Linking to External Lean Proofs

If your research has formal proofs, link to Palomar registry:

```typst
== Formal Verification

See @palomar:my-theorem for Lean 4 formalization.
```

In `build_paper.py`, add Palomar linking:

```python
# Link to Lean formalization
palomar_url = "https://palomar.ridge.ai/my-theorem"
print(f"📋 Formal proof: {palomar_url}")
```

### Data-Driven Figures

Use pandas + seaborn for complex plots:

```python
import pandas as pd
import seaborn as sns

df = pd.read_csv('experimental_data.csv')
sns.pairplot(df, hue='treatment')
plt.savefig('generated/figures/correlations.png')
```

## Publishing Your Paper

### Option 1: Keep in math-trace

If your research is part of the math-trace project, commit it alongside other domains:

```bash
git add templates/my-domain/
git commit -m "Add: my-domain research paper"
git push
```

### Option 2: Fork as Standalone Repo

Create your own repository based on a template:

```bash
# Create new repo
gh repo create my-physics-paper --public
git init my-physics-paper
cp -r templates/simple-physics/* my-physics-paper/
cd my-physics-paper
git add -A
git commit -m "Initial commit: physics paper template"
git push
```

Your repo now has:
- ✅ Formula-to-code traceability
- ✅ Reproducible simulations
- ✅ Publication-quality output (Typst)
- ✅ Git history of all changes
- ✅ Open science: anyone can fork and adapt

### Option 3: Publish to arXiv/Journal

When ready for publication:

1. Ensure all formulas, figures, and code are committed
2. Generate final PDF: `python build_paper.py` + install Typst if needed
3. Add bibliography to main.typ:

```typst
#bibliography("references.bib")
```

4. Generate bibliography: `typst compile main.typ`
5. Upload `main.pdf` to arXiv, journal submission, etc.
6. Link to repository: "Code and data: https://github.com/your-username/my-paper"

## Creating New Templates

Want to add a new domain? Follow this pattern:

### 1. Create Directory

```bash
mkdir -p templates/your-domain
```

### 2. Copy Core Files

Use any existing template as a base:

```bash
cp templates/simple-physics/{model.py,simulate.py,build_paper.py,main.typ} templates/your-domain/
```

### 3. Customize

Edit the four files for your domain's formulas and simulations.

### 4. Document

Create a comprehensive README:

```bash
cat > templates/your-domain/README.md << 'EOF'
# Your Domain Template

[Domain description, references, example parameters]

## Customization

[Domain-specific instructions]

## References

[Academic citations]
EOF
```

### 5. Test

```bash
cd templates/your-domain
python model.py
python simulate.py
python build_paper.py
```

Verify all files are generated without errors.

### 6. Contribute Back

Add your template to math-trace:

```bash
git add templates/your-domain/
git commit -m "Add: your-domain template with [key feature]"
git push
```

Other researchers can now fork it for their work!

## File Structure Reference

```
math-trace/
├── README.md                   # Main project README
├── CONTRIBUTING.md             # Contribution guidelines
├── pyproject.toml              # Python package config
├── Justfile                    # Build recipes
│
├── src/math_trace/             # Python library
│   ├── __init__.py
│   ├── sympy_to_typst.py       # LaTeX → Typst conversion
│   └── typst_env.py            # Typst environment builder
│
├── examples/                   # Complete example
│   └── membrane-dynamics/      # Stochastic P-systems example
│       ├── model.py            # SymPy formulas
│       ├── simulate.py         # Simulation code
│       ├── build_paper.py      # Build pipeline
│       ├── main.typ            # Paper template
│       └── lean/               # Lean 4 formalization (optional)
│
├── templates/                  # Fork-friendly templates
│   ├── TEMPLATE-USAGE.md       # This file
│   ├── simple-physics/         # Template: Classical mechanics
│   │   ├── model.py
│   │   ├── simulate.py
│   │   ├── build_paper.py
│   │   ├── main.typ
│   │   └── README.md
│   └── biochemistry/           # Template: Enzyme kinetics
│       ├── model.py
│       ├── simulate.py
│       ├── build_paper.py
│       ├── main.typ
│       └── README.md
│
└── tests/                      # Tests for library + examples
    ├── test_model_export.py
    └── integration/
```

## Troubleshooting

**"FileNotFoundError: No such file or directory"**
- Ensure you're in the correct directory: `cd templates/simple-physics`
- Check file exists: `ls model.py simulate.py`

**"ImportError: No module named 'sympy'"**
```bash
cd ../..  # Go to math-trace root
uv add sympy matplotlib numpy
```

**PDF not generating (Typst error)**
- Install Typst: `just install-typst`
- Check main.typ syntax: `typst compile main.typ --diagnostic`

**Formulas not rendering in Typst**
- Check `generated/formulas.typ` exists: `ls generated/formulas.typ`
- Verify LaTeX-to-Typst conversion worked
- Try simpler formula first: test a single `#let` statement

## FAQ

**Q: Can I use the same formula in multiple papers?**

A: Yes! Copy your `model.py` to a new template directory. The build system regenerates formulas from the same source, ensuring consistency across papers.

**Q: How do I cite other research in my paper?**

A: Add BibTeX to main.typ:

```typst
#bibliography("references.bib", style: "ieee")
```

Create `references.bib` with your citations.

**Q: Can I add interactive plots (Jupyter, Plotly)?**

A: Templates use static Matplotlib figures for publication. For interactive exploration, create a separate Jupyter notebook that imports your `simulate.py`.

**Q: How do I add peer review feedback?**

A: Track revisions in git:

```bash
git commit -m "Revise: Add missing equation per reviewer #2"
git commit -m "Revise: Clarify experimental methodology"
```

Your git history documents the peer review process.

**Q: Can I use this for thesis chapters?**

A: Yes! Create one template per chapter:

```bash
templates/chapter-1-introduction/
templates/chapter-2-methods/
templates/chapter-3-results/
```

Each has its own model.py, figures, and main.typ. Then combine into a thesis document.

## Learn More

- **Main README**: [../README.md](../README.md)
- **Contributing**: [../CONTRIBUTING.md](../CONTRIBUTING.md)
- **Simple Physics Template**: [simple-physics/README.md](simple-physics/README.md)
- **Biochemistry Template**: [biochemistry/README.md](biochemistry/README.md)
- **Typst Documentation**: https://typst.app/docs
- **SymPy Documentation**: https://docs.sympy.org

---

**Questions?** Open an issue: https://github.com/baseline0/math-trace/issues
