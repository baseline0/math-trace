# math-trace: Positioning & Scope

**What problem does math-trace solve?**

math-trace bridges the gap between research formulas and research code. It's a workflow, not a platform.

---

## The Problem

When researchers publish computational papers, formulas live in LaTeX (PDF), while code lives on GitHub. They diverge.

**Current workflow (error-prone):**
```
Researcher writes formula in LaTeX
    ↓
Code team implements formula (hopefully matches)
    ↓
Paper published (formula and code now disconnected)
    ↓
Six months later: "Which version is correct?"
```

**math-trace workflow (auditable):**
```
Researcher writes formula in SymPy (source of truth)
    ↓
Automatic export to Typst
    ↓
Code runs against formulas (validation)
    ↓
Paper generated with traced formulas
    ↓
Git commit ties formula → code → figure → proof
```

---

## Who This Is For

### ✅ Perfect Fit

**Computational researchers** who:
- Write papers with mathematical models
- Implement simulations in Python
- Care about formula-code correctness
- Want reproducible research (GitHub-friendly)
- Appreciate version control for formulas

**Examples:**
- Stochastic process modeling
- Differential equations with numerical solutions
- Machine learning with explicit loss functions
- Systems biology (pathway modeling)
- Physics simulations with experimental validation

**Formal methods researchers** who:
- Publish theorems alongside proofs
- Want to link Lean/Coq proofs to SymPy formulas
- Use Palomar registry for formalization

### ⚠️ Fits With Caveats

**Data scientists** who:
- Use Jupyter for exploration (fine)
- Want publication-grade output (use Quarto instead)
- Want formula-to-code linking in a notebook (Pluto.jl is better)

**Research groups** that:
- Already use Overleaf + GitHub (can still use math-trace, but workflow changes)
- Work primarily in LaTeX (Typst adds friction, but is worth it)

### ❌ Not a Fit

**Pure mathematicians** (no code)
- math-trace needs simulation/code to shine

**Exploratory data science** (notebooks first)
- Jupyter or Pluto better
- math-trace is for publication, not exploration

**One-off scripts** (not publication-grade)
- Overkill to set up SymPy + Typst + build pipeline

**Language ecosystems outside Python** (R, Julia, Rust)
- math-trace is Python-first
- Can integrate, but not native

---

## Why This Niche Matters

### The Hidden Cost of Formula-Code Mismatch

Research is reproducible on paper only if:
1. Formulas in paper match implementation
2. Implementation matches reported results
3. All three are version-controlled

**Without math-trace:** Researchers must maintain:
- LaTeX source (1 copy)
- Paper PDF (derived, not version-controlled)
- Python code (separate repo)
- Manual synchronization (error-prone)

**With math-trace:** Single source of truth:
- SymPy formulas in code
- Auto-export to Typst
- All tied to Git commits
- Reproducible by construction

### Who Wins

**Readers:**
- Click formula in PDF → jump to model.py:line → see exact implementation
- Run `git checkout <commit>` → regenerate paper exactly as published
- Extend research: fork repo, change formula, re-run pipeline

**Authors:**
- One edit to model.py updates paper automatically (no manual syncing)
- CI/CD validates formulas match code before publishing
- Reduced errors (hand-typed formulas → auto-exported)

**Research groups:**
- Standardize on formula-code traceability
- Onboard new team members (formulas are in code, not scattered)
- Reuse templates across projects

---

## Positioning Statement

> **math-trace** is an integration layer for researchers who value formula-code correctness.
>
> It's not a replacement for Jupyter, Quarto, or Lean. It's a workflow that connects them: SymPy (formulas) → Typst (publication) → Lean (proofs), with code as the single source of truth.
>
> Use it if:
> - Your paper has a mathematical model
> - Your model has a simulation
> - You want readers to trace formulas back to code
>
> Don't use it if:
> - You're doing exploratory analysis (Jupyter)
> - You're publishing from R/tidyverse (Quarto)
> - You're writing pure theory with no code (LaTeX)

---

## Competitive Landscape

| Tool | Formulas | Code | Publication | Proof | Formula→Code |
|------|----------|------|-------------|-------|--------------|
| **Jupyter** | ✅ Markdown | ✅ | ⚠️ HTML | ❌ | ❌ |
| **Quarto** | ✅ Markdown | ✅ | ✅ HTML/PDF | ❌ | ❌ |
| **Typst + SymPy** | ✅ Manual | ✅ Separate | ✅ | ❌ | ❌ |
| **Pluto.jl** | ✅ Reactive | ✅ Julia | ⚠️ Limited | ❌ | ❌ |
| **Lean + Mathlib** | ✅ Formal | ⚠️ Proofs | ❌ | ✅ | ❌ |
| **math-trace** | ✅ SymPy | ✅ Python | ✅ Typst | ✅ Lean/opt | ✅ Automatic |

**math-trace's unique value:** Automatic formula export with optional formalization.

---

## Market Size Estimate

**Total academic researchers:** ~2M worldwide

**Computational researchers:** ~200K (10%)
- Biology/chemistry: 50K
- Physics/astronomy: 40K
- Machine learning: 40K
- Math/applied math: 30K
- Economics/social sciences: 20K
- Earth sciences: 20K

**Likely to adopt math-trace:** 5-10% of computational researchers

**Target audience:** 10K–20K researchers globally

**This is a real niche, not a mass-market tool.**

---

## Success Metrics (12-month horizon)

| Metric | Target | How to Measure |
|--------|--------|-----------------|
| **Adoption** | 50+ GitHub stars | tracker |
| **Publications** | 3+ papers using math-trace | arXiv search |
| **Template forks** | 5+ domain templates forked | GitHub forks |
| **Community** | 10+ issues/discussions | GitHub |
| **PyPI** | 100+ monthly downloads | PyPI stats |

---

## What math-trace Is NOT

- **Not a research platform** — No cloud infrastructure, no user accounts
- **Not a notebook replacement** — Not for exploration, only publication
- **Not a proof assistant** — Lean is optional, not required
- **Not a replacement for Quarto** — Different use case (publication-grade math)
- **Not a package manager** — Doesn't manage dependencies beyond Python

---

## The Long Game

**Year 1 (2026):** Establish workflow + publish example papers on arXiv

**Year 2 (2027):** Community grows, new templates for different domains

**Year 3 (2028):** Used in research group pipelines; cited in published papers

**Year 5+ (2031):** Standard tool in computational research workflows

**The goal is NOT market dominance. It's finding 10-20K researchers who care about formula-code traceability and giving them a tool that works.**

---

## Conclusion

math-trace fills a specific, defensible niche: computational researchers who want formulas and code to stay in sync, with optional formal verification.

It's not for everyone. But for the researchers it's for, it solves a real problem that nothing else addresses.

**The litmus test:** Would you rather write a paper with disconnected formulas and code, or with formulas that are automatically linked to code? If the latter appeals to you, math-trace is for you.
