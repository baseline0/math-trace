# math-trace Architecture: Design for Longevity

**Problem:** math-trace depends on SymPy, Typst, and Lean. What if they stop being maintained?

**Solution:** Modular architecture so libraries can be swapped without rewriting the core workflow.

---

## Core Abstraction: The Formula Pipeline

```
Source Formula     Formula Export      Publishing     Proof (Optional)
(SymPy)        →   (LaTeX/Typst)   →   (Typst PDF)  →  (Lean + Palomar)
```

Each stage is **decoupled**. If SymPy becomes unmaintained, we swap it for an alternative without rewriting downstream stages.

---

## 1. Formula Definition Layer

**Currently:** SymPy (Python symbolic math)

**Abstraction:** Define formulas in a common intermediate representation (IR)

```python
# Current: formulas are SymPy expressions
import sympy as sp
rate_law = k * sp.binomial(n_a, 2)

# Future: wrap in a Formula abstraction
class Formula:
    """Represents a mathematical formula."""
    def to_latex(self) -> str: ...
    def to_typst(self) -> str: ...
    def to_mathml(self) -> str: ...
    def to_lean(self) -> str: ...

# Swap SymPy for alternative:
class SymPyFormula(Formula):
    def __init__(self, sympy_expr):
        self.expr = sympy_expr
    def to_latex(self) -> str:
        return sp.latex(self.expr)

# Or swap for MathBox (hypothetical alternative):
class MathBoxFormula(Formula):
    def __init__(self, mathbox_expr):
        self.expr = mathbox_expr
    def to_latex(self) -> str:
        return mathbox_expr.export("latex")
```

**Migration path:** If SymPy stops being maintained:
1. Implement `AlternativeFormula` class for new library
2. Update `model.py` to use new class
3. Rest of pipeline unchanged (exports still produce LaTeX/Typst)

---

## 2. Export Layer (LaTeX → Typst)

**Currently:** Regex-based conversion in `build_paper.py`

**Abstraction:** Plugin-based exporters

```python
class LatexToTypstConverter:
    """Converts LaTeX to Typst markup."""
    def convert(self, latex_str: str) -> str:
        # Current: simple regex replacements
        # Future: could use proper LaTeX parser
        pass

class LatexExporter:
    """Base class for LaTeX-based exports."""
    def export(self, formulas: dict[str, Formula]) -> str:
        # Generates LaTeX from formulas
        # Works with any formula source (SymPy, MathBox, etc.)
        pass
```

**Migration path:** If Typst's math syntax changes:
1. Implement new `LatexToTypstConverter` with updated rules
2. All formula definitions continue to work (they export to LaTeX)
3. Only the conversion step changes

---

## 3. Publishing Layer (LaTeX → PDF)

**Currently:** Typst compiler (external tool)

**Abstraction:** Publisher interface

```python
class Publisher:
    """Base class for publishing LaTeX to PDF."""
    def compile(self, tex_file: Path) -> bytes:
        """Returns PDF bytes."""
        pass

class TypstPublisher(Publisher):
    """Uses Typst compiler."""
    def compile(self, tex_file: Path) -> bytes:
        # shell out to typst compile
        pass

class LatexPublisher(Publisher):
    """Uses pdflatex (fallback)."""
    def compile(self, tex_file: Path) -> bytes:
        # shell out to pdflatex
        pass

# In build_paper.py:
publisher = TypstPublisher()  # Or LatexPublisher()
pdf_bytes = publisher.compile(main_typst_file)
```

**Migration path:** If Typst stops being maintained:
1. Implement `LatexPublisher` using pdflatex/XeLaTeX
2. Change one line: `publisher = LatexPublisher()`
3. Paper still builds (just using different compiler)

---

## 4. Formalization Layer (Optional Lean)

**Currently:** Lean 4 proofs, manual link to Palomar

**Abstraction:** Proof framework interface

```python
class ProofFramework:
    """Base class for formal verification frameworks."""
    def verify(self, theorem: str) -> bool:
        """Returns True if theorem can be proven."""
        pass
    def export_to_registry(self, proof: str) -> str:
        """Returns registry link (e.g., Palomar URL)."""
        pass

class LeanFramework(ProofFramework):
    """Uses Lean 4 with Mathlib."""
    def verify(self, theorem: str) -> bool:
        # shell out to lake
        pass
    def export_to_registry(self, proof: str) -> str:
        # Posts to Palomar registry
        pass

class CoqFramework(ProofFramework):
    """Uses Coq (hypothetical alternative)."""
    def verify(self, theorem: str) -> bool:
        # shell out to coqc
        pass
```

**Migration path:** If Lean becomes unmaintained:
1. Implement `CoqFramework` or `IsabelleFramework`
2. Change one line in pipeline
3. Proofs still verified (just in different language)
4. Note: Palomar link format may need update

---

## Current Dependency Tree

```
math-trace/
├── src/math_trace/        # Orchestration + abstractions
│   ├── formula.py         # Abstract formula representation
│   ├── exporters.py       # LaTeX/Typst converters
│   ├── publishers.py      # PDF publishers (Typst, LaTeX)
│   └── proofs.py          # Lean framework interface
│
├── examples/membrane-dynamics/
│   ├── model.py           # Uses: SymPy
│   ├── simulate.py        # Uses: NumPy
│   ├── build_paper.py     # Uses: Typst (external), Lean (external)
│   └── main.typ           # Typst document
│
└── pyproject.toml         # Declares deps: sympy, numpy, typst
```

**Hard dependencies:**
- Python 3.11+ (language)
- NumPy (simulations)
- SymPy (formulas) — **SWAPPABLE**
- Typst (PDF generation) — **SWAPPABLE** (fallback: pdflatex)
- Lean 4 (proofs) — **OPTIONAL**

**Soft dependencies:**
- Matplotlib (figures) — could swap for Plotly, Seaborn, etc.
- Palomar (proof registry) — could swap for other registries

---

## Resilience Roadmap

### Year 1: Establish Baselines (2026)

- [x] SymPy for formulas
- [x] Typst for typesetting
- [x] Lean for proofs
- [x] Modular architecture

### Year 2: Add Alternatives (2027)

- [ ] LaTeX fallback publisher (if Typst stalls)
- [ ] MathBox formula support (if SymPy stalls)
- [ ] Coq proof support (parallel to Lean)

### Year 3+: Evaluate & Swap (2028+)

- Monitor maintenance status of dependencies
- Swap implementations as needed
- Keep core abstractions stable

---

## Testing Strategy

**Each abstraction layer has unit tests:**

```python
# Test formula abstraction
def test_sympy_formula_to_latex():
    f = SymPyFormula(sp.Symbol('x')**2 + 1)
    assert "x^2" in f.to_latex()

# Test publisher abstraction
def test_typst_publisher():
    pub = TypstPublisher()
    pdf = pub.compile("test.typ")
    assert len(pdf) > 0  # Valid PDF

def test_latex_publisher_fallback():
    pub = LatexPublisher()
    pdf = pub.compile("test.tex")
    assert len(pdf) > 0
```

**When swapping libraries:**
1. Implement new class (e.g., `MathBoxFormula`)
2. Write unit tests (same interface as `SymPyFormula`)
3. Update `model.py` to use new class
4. Run full integration tests (end-to-end paper build)

---

## Example: Swap SymPy for MathBox

**If SymPy becomes unmaintained and MathBox becomes the standard:**

### Step 1: Implement Adapter

```python
# src/math_trace/formula.py

class MathBoxFormula(Formula):
    """Adapter for MathBox symbolic math."""
    def __init__(self, expr: mb.Expression):
        self.expr = expr
    
    def to_latex(self) -> str:
        return self.expr.to_latex()
    
    def to_typst(self) -> str:
        latex = self.to_latex()
        return LatexToTypstConverter().convert(latex)
```

### Step 2: Update Model

```python
# examples/membrane-dynamics/model.py

# Before
import sympy as sp
rate_law = sp.Symbol('k') * sp.binomial(sp.Symbol('n'), 2)

# After
import mathbox as mb
rate_law = MathBoxFormula(
    mb.Symbol('k') * mb.binomial(mb.Symbol('n'), 2)
)
```

### Step 3: Rest of Pipeline Unchanged

```python
# build_paper.py still works!
formulas = export_formulas()  # Returns MathBoxFormula objects
for name, formula in formulas.items():
    latex = formula.to_latex()  # Works (implements interface)
    typst = formula.to_typst()  # Works (uses converter)
```

**Result:** Only 3 files changed. Core pipeline untouched.

---

## Design Principles

1. **Inversion of Control:** Core pipeline doesn't care how formulas are defined, only that they export to LaTeX
2. **Pluggable Backends:** Each layer can be swapped independently
3. **Stable Interfaces:** Formula, Publisher, ProofFramework classes define contracts
4. **Tested Abstractions:** Each abstraction has unit tests that verify the contract
5. **Graceful Degradation:** Lean proofs optional, Typst can fall back to LaTeX

---

## Conclusion

math-trace is resilient because it **separates concerns**:

- Formula definition (currently SymPy, could be MathBox)
- Formula export (currently LaTeX, could be MathML)
- PDF generation (currently Typst, could be LaTeX)
- Formal verification (currently Lean, could be Coq)

If any library stops being maintained, we can swap it without rewriting the entire codebase.

**The goal:** A workflow that outlives any single library choice.
