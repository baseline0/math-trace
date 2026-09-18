# Examples Directory

This directory contains complete, working examples of papers built with math-trace.

Each example is a **reference pattern** — validated by CI/CD to compile correctly and demonstrate best practices.

---

## membrane-dynamics/

**What it is:** A minimal stochastic P-system paper using generated formulas and Lean formalization.

**Key features:**
- SymPy model → Typst formulas (automatic)
- Stochastic simulation with matplotlib
- Typst paper with citations and formal verification
- Lean proof tied to Palomar registry

**Files:**
- `model.py` — SymPy formulas (source of truth)
- `simulate.py` — Gillespie algorithm simulation
- `build_paper.py` — Build pipeline (formulas → figures → PDF)
- `main.typ` — Publication template
- `lean/` — Lean formalization (optional)

**Referenced in docs:**
- `docs/TYPST-GOTCHAS.md` §1 — Shows correct escaping of `/*` in bold text (line 78)
- `docs/TYPST-LINTING.md` — Demonstrates full workflow

**How to use:**
1. See it build: `cd membrane-dynamics && just paper`
2. Copy its structure: start your own `model.py`, `main.typ`
3. Adapt for your domain: change formulas, simulation, narrative

---

## Using examples as templates

### Step 1: Choose an example

```bash
cd examples/membrane-dynamics
```

### Step 2: Review the files

- `model.py` — How formulas are defined
- `simulate.py` — How to run simulations
- `main.typ` — How to structure a paper
- `build_paper.py` — How the build pipeline works

### Step 3: Copy and adapt

```bash
# Copy the example to a new project
cp -r . ../../my-research-paper

# Edit for your domain
cd ../../my-research-paper
vim model.py     # Change formulas
vim simulate.py  # Change simulation
vim main.typ     # Change narrative
```

### Step 4: Build

```bash
python build_paper.py
```

---

## Example structure

All examples follow this pattern:

```
example-name/
├── model.py                    # SymPy formulas (SOURCE OF TRUTH)
├── simulate.py                 # Simulation code
├── build_paper.py              # Build orchestration
├── main.typ                    # Typst paper template
├── lean/                       # Lean formalization (optional)
│   ├── Challenge.lean          # Theorem statement
│   ├── Solution.lean           # Proof
│   └── formalization.yaml      # Metadata + Palomar
├── generated/                  # Auto-generated (not in git)
│   ├── formulas.typ
│   └── figures/
└── [model-name]_equations.json # Auto-generated
```

---

## CI/CD validation

Every example is validated by `scripts/check_typst.py`:

- ✅ `model.py` exports formulas without errors
- ✅ `simulate.py` runs without errors
- ✅ `build_paper.py` generates formulas and figures
- ✅ `main.typ` has valid Typst syntax (compiles with diagnostics)

**If an example fails CI**, it's a regression and must be fixed immediately.

---

## Adding a new example

To add another example to this directory:

1. **Create the directory:**
   ```bash
   mkdir example-new-domain
   cd example-new-domain
   ```

2. **Copy from an existing example:**
   ```bash
   cp ../membrane-dynamics/{model,simulate,build_paper,main.typ}.py .
   ```

3. **Adapt for your domain:**
   - Edit `model.py`: change formulas
   - Edit `simulate.py`: change simulation
   - Edit `main.typ`: change narrative
   - Update docstrings and comments

4. **Test locally:**
   ```bash
   python model.py
   python simulate.py
   python build_paper.py
   ```

5. **Commit:**
   ```bash
   git add example-new-domain/
   git commit -m "examples: Add example-new-domain"
   ```

6. **CI validates it** — If it passes, it becomes a reference pattern.

---

## See also

- **Templates:** `templates/` — Fork-friendly starting points
- **Docs:** `docs/TYPST-LINTING.md` — How we validate Typst
- **Gotchas:** `docs/TYPST-GOTCHAS.md` — Common Typst syntax issues
- **Getting started:** `docs/getting-started-external.md` — For new users

---

**Questions?** Open an issue: https://github.com/baseline0/math-trace/issues
