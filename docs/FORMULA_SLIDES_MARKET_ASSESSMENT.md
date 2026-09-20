# Formula-Driven Slides: Market Assessment & Honest Positioning

**Document Date:** 2026-09-19  
**Status:** Evaluating viability for PyPI publication  
**Author:** Mark Alexiuk

---

## Executive Summary

**The Idea:** A system (tooling + conventions) that enables researchers to:
- Define formulas once in SymPy (source of truth)
- Reference formulas in Marp/Markdown slides via `{{formula:id|params}}`
- Auto-render KaTeX math, linked to source code
- Export presentation PDFs with formula traceability

**Honest Assessment:** This solves a **real but narrow problem** for academic researchers. It's valuable for us and a specific audience, but not a mass-market product.

**PyPI Publication:** Reasonable as a niche utility, but only if we commit to maintenance and clear positioning.

---

## The Problem We're Solving

### Current State: Formula-to-Slide Friction

**Scenario 1: The Researcher's Pain**

```
Day 1: Define formulas in SymPy (model.py)
Day 2: Manually type them into LaTeX/Beamer presentation
Day 3: Update a formula in model.py
Day 4: Forget to update the presentation
Day 5: Conference attendee catches discrepancy
Day 6: Credibility damaged
```

**Scenario 2: The Presenter's Pain**

- **LaTeX/Beamer:** Beautiful math, but rigid aesthetics, steep learning curve
- **Google Slides/Keynote:** Beautiful slides, but math rendering is janky (screenshots of equations!)
- **PowerPoint:** Same problem
- **Marp:** Clean slides + KaTeX math, but no connection to code

### The Itch We're Scratching

**For formula-heavy research presentations** (ML, scientific computing, optimization, formal methods):

1. **Reproducibility:** Formulas in slides must match code
2. **Aesthetics:** Math must render beautifully (not screenshots)
3. **Productivity:** Edit in IDE, see live preview
4. **Portability:** Export PDF that works everywhere
5. **Simplicity:** Markdown > LaTeX; VS Code > terminal

---

## Market Analysis: Who Will Care?

### Primary Audience: Academic Researchers

**Size:** ~50-100K researchers publishing papers + presenting

**Characteristics:**
- Write in Python/SymPy (ML, optimization, formal methods)
- Present at conferences (CS, math, stats, physics)
- Value reproducibility and code traceability
- Use VS Code or similar editors
- Often frustrated with Beamer/LaTeX

**Pain Points:**
- Formula-code sync is manual and error-prone
- Beamer is painful; alternatives lack math
- Presentations often contradict papers/code

**Willingness to Adopt:**
- **High** if it's simple (Markdown-first)
- **Moderate** if it requires new concepts
- **Low** if it adds complexity

### Secondary Audience: Software Educators

**Size:** ~10-50K (university + online educators)

**Characteristics:**
- Teach algorithms, data structures, optimization
- Want beautiful math + clean code examples
- Present to students + conferences
- Value reproducibility and explainability

**Pain Points:**
- "This formula in the slide doesn't match the code students see"
- Math rendering is the hardest part
- Keeping slides updated as code evolves

**Willingness to Adopt:**
- **High** if it's a drop-in Marp enhancement

### Tertiary Audience: Technical Communicators

**Size:** ~5-20K (bloggers, technical writers)

**Characteristics:**
- Write technical blogs, tutorials, documentation
- Use Markdown natively
- Want embedded formulas that trace to code
- Often frustrated with math rendering

**Pain Points:**
- Markdown support for math is inconsistent
- Math in blog posts often becomes stale vs. code

**Willingness to Adopt:**
- **Moderate** (not their primary workflow)

### Who Won't Care (Be Honest)

- **Enterprise developers** — Don't write formula-heavy docs
- **Web/mobile developers** — Not their problem space
- **DevOps/SRE** — No formulas in their presentations
- **Business analysts** — Audience doesn't need LaTeX math

---

## Competitive Landscape

| Tool | Strengths | Weaknesses | Formula Support |
|------|-----------|-----------|-----------------|
| **LaTeX/Beamer** | Beautiful math, powerful | Steep curve, ugly output, slow | Native, perfect |
| **Google Slides** | Easy, cloud, collaboration | Math via screenshots | Poor (hacks only) |
| **Keynote/PowerPoint** | Polished, accessible | No code support, math is bad | Poor (screenshots) |
| **Jupyter Notebooks** | Code + math, interactive | Not for presentations | Good (MathJax) |
| **Marp** | Clean, Markdown, KaTeX | No formula traceability | Good (KaTeX) |
| **Revealjs** | Web-based, professional | Requires HTML knowledge | Depends on renderer |
| **reveal-md** | Markdown + Revealjs | Less polished than Marp | Good (MathJax) |
| **Quarto** | Code + narrative + math | Overkill for slides, slower iteration | Good (MathJax) |
| **Formula-Driven Marp** | Traceable formulas, Markdown, KaTeX, IDE-native | Niche, requires adoption of conventions | Excellent (traceable) |

**Gap in Market:** No existing tool couples formula traceability + Markdown + beautiful math + IDE integration.

---

## Honest Assessment: What Are We Building?

### Not a Replacement for Beamer
- Beamer users have already invested heavily
- They *want* LaTeX math
- Our tool doesn't displace them

### Not a General-Purpose Presentation Tool
- We're not competing with Google Slides or Keynote
- We're solving a specific problem: formula traceability

### Actually a Niche Tool
- **Best case:** Academics writing formula-heavy talks stop using Beamer, try us
- **Realistic case:** A handful of researchers use it for their own work
- **Honest case:** We're building this for ourselves first, then generalizing if others find it useful

### Not a Long-Term Business
- No venture capital opportunity here
- No "10x users" potential
- No path to enterprise licenses
- This is infrastructure for a community of hundreds, not thousands

---

## PyPI Publication: Is It Worth It?

### Arguments For Publishing

✅ **Legitimate use case** — Researchers doing this manually today  
✅ **No direct competitor** — Gap in market  
✅ **Low maintenance burden** — Simple CLI + Python library  
✅ **Clear audience** — Easy to find and pitch to  
✅ **Establishes authority** — "We built the tool for formula-driven slides"  
✅ **GitHub discoverability** — Gets easier to find via PyPI  

### Arguments Against Publishing

❌ **Niche audience** — Maybe 1K active users long-term  
❌ **Maintenance cost** — Must support Python 3.x, dependencies, bug fixes  
❌ **API stability pressure** — PyPI users expect semver, deprecation periods  
❌ **Documentation burden** — Tutorials, examples, troubleshooting  
❌ **We don't know if it works yet** — Untested hypothesis  
❌ **Could become technical debt** — Abandoned projects on PyPI hurt credibility  

### Recommendation: **Conditional Yes**

**Phase 1 (Now):** Build it for the membrane repo. Use it. Iterate.

**Phase 2 (In 3-6 months):** If we've used it successfully for:
- Writing papers with formula traceability
- Presenting at conferences with live slides
- Teaching classes where formulas match code
- And we've gotten positive feedback from others trying it

**Then: Phase 3 (PyPI)** — Publish as `formula-slides` with:
- Clear positioning: "Niche tool for academic researchers"
- Honest documentation about use cases
- Examples that match our actual workflow
- Commitment to maintenance (or clear sunset path)

---

## Implementation Path (If We Decide Yes)

### Minimal Viable Product (MVP)

```python
# This is what we'd release to PyPI
from formula_slides import FormulaPresentation, Formula

# Define formulas (in model.py)
formulas = [
    Formula(id="f_input", expr=sp.Integer(3), parameters={}),
    Formula(id="f_rule", expr=sp.Lambda((n,), 2*n), parameters={"n": sp.Symbol("n")}),
]

# Build presentation (in build_slides.py)
presentation = FormulaPresentation(
    markdown_file="presentation.md",
    formulas=formulas,
    output_format="marp"  # or "pdf"
)
presentation.render()
```

### Feature Scope (MVP)

**Core:**
- Parse `{{formula:id|params}}` syntax
- Substitute SymPy expressions as KaTeX
- Add traceability comments (source lines)
- Export to Marp-compatible Markdown

**NOT in MVP:**
- Web UI for editing
- Live server mode
- Custom themes
- Jupyter integration
- Lean formalization (that's math-trace)

### Dependencies

```toml
[project]
dependencies = [
    "sympy>=1.12",
    "pyyaml>=6.0",
]
```

Very lightweight. No JavaScript, no frontend framework.

---

## Honest Positioning for PyPI

### If We Publish, Here's the Pitch

**Name:** `formula-slides`  
**Tagline:** "Traceable formulas in Marp presentations"

**Description:**
```
A tool for researchers and educators writing formula-heavy presentations.

Define your formulas ONCE in SymPy (source of truth), then reference them
in Marp/Markdown slides. Formulas render beautifully with KaTeX, and every
equation in your presentation links back to the code that generated it.

Ideal for:
- Presenting research papers at conferences
- Teaching algorithms and optimization
- Ensuring formula-code consistency

Use this if:
✓ You write in Python/SymPy
✓ You present with Marp/Markdown
✓ You care about reproducibility
✓ You want beautiful math without LaTeX

Not ideal if:
✗ You prefer LaTeX/Beamer
✗ You need extensive design customization
✗ Your audience is business, not technical
```

### Market Positioning (Honest)

- **Not:** "Replace Beamer"
- **Not:** "The next PowerPoint"
- **Actually:** "Better than manually sync-ing formulas between code and slides"

---

## Risk Assessment

### What Could Go Wrong?

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Low adoption | High | Medium | Accept it; tool is still valuable for us |
| Dependency break (SymPy API change) | Medium | Medium | Pin versions, add CI tests |
| Users expect more features | Medium | Low | Clear documentation of scope |
| Maintenance burden | Medium | Medium | Automate with CI/CD, set expectations |
| Competing tool emerges | Low | Low | Our tool is proven; ours works |

### What We're Optimizing For

- **Correctness:** Formulas must be accurate (our primary goal)
- **Simplicity:** Users should understand how it works (Markdown is key)
- **Maintainability:** We can support this long-term without burnout
- **Niche fit:** Better to be best-in-class for researchers than mediocre for everyone

---

## Decision Framework

### Publish to PyPI If:

1. ✅ We use it successfully for 2+ presentations
2. ✅ We get unsolicited requests from 3+ other researchers
3. ✅ The core is stable (API hasn't changed in 2 months)
4. ✅ We're willing to maintain it for 2+ years
5. ✅ Documentation is clear and honest

### Don't Publish If:

1. ❌ We abandon it after the first paper
2. ❌ It becomes "one more thing" we have to support
3. ❌ Users want features outside our scope
4. ❌ Maintenance feels like a burden vs. a pleasure

---

## Feedback & Iteration Log

### Feedback Round 1: Early Viability Check (2026-09-19)

**Griller's Assessment:**
> "Your assessment is correct: this is a **valuable niche tool** with a clear audience and a real problem to solve. The key to success is **rigorous traceability** (not just generation), **workflow integration** (CI + one-command builds), and **scope discipline**."

**Key Stresses Identified:**

1. **Traceability Must Be Auditable, Not Just Generated**
   - Current approach: "Traceability comments (source lines)" in rendered output
   - Problem: Only comments—not verified linkage
   - Fix: Add **formula index** (auto-generated slide/page) listing every formula ID, source file/line, and rendered form
   - Fix: Make formula linkage visible in PDF metadata or slide notes, not just comments
   - Status: ⚠️ *To implement before MVP*

2. **Parameter Handling & Assumptions Edge Cases**
   - Problem: Symbol renaming (paper uses $\theta$, code uses `theta_hat`)
   - Problem: SymPy assumptions affect printing (positive, real, integer)
   - Problem: Same formula, different forms (expanded vs factored)
   - Fix: Add **symbol mapping layer** for aliasing
   - Fix: **Lock SymPy assumptions** explicitly in `Formula` definition
   - Fix: Support **form variants** via `{{formula:id|form=expanded}}`
   - Status: 🔴 *Critical gap—must address before real usage*

3. **Workflow Integration (CLI + CI + Editor)**
   - Current: `python build_slides.py` is manual, optional
   - Problem: If it's an extra step, it gets skipped → drift returns
   - Fix: Integrate into single `just` target (e.g., `just present`)
   - Fix: Add **CI check** that fails if formula IDs are missing or rendering fails
   - Fix: **Actionable error messages** ("Formula `foo` not found; used in presentation.md:42")
   - Bonus: VS Code snippet for `{{formula:...}}` autocomplete
   - Status: ⚠️ *MVP scope; refine based on pilot*

4. **Avoiding "Abandoned PyPI Project" Fate**
   - Risk: Feature creep (themes, live server, Jupyter, plugins)
   - Mitigation: **Scope lock** at publication—publish small stable API only
   - Mitigation: **Version pinning policy** for SymPy and dependencies
   - Mitigation: **Sunset clause** (if we stop using it, archive as read-only)
   - Status: ✅ *Accepted; will codify in docs*

**How This Feedback Changes Our Plan:**

| Aspect | Before | After |
|--------|--------|-------|
| **Traceability** | Comments only | **Deterministic rendering + formula index (first-class output) + CI gates** |
| **Parameters** | Basic `\|param=value` | **Symbol aliasing + assumption snapshots + actionable errors** |
| **Rendering** | "Generate LaTeX once" | **Locked SymPy settings + reproducible across versions** |
| **Workflow** | Manual CLI | **One command: `just present` (build + Marp + index)** |
| **Validation** | Wishful thinking | **CI check fails on missing formulas or mismatched index** |
| **Scope** | Open-ended | **Locked API + explicit deferrals + sunset clause** |
| **Pilot** | "Use it internally" | **Conference presentation + friction log + community validation** |

---

## Feedback Round 2: Design Specifics (2026-09-19)

**Key Insight from Validator:**
> "Without deterministic rendering, auditable artifacts, and CI gates, 'traceability' is marketing. With them, it's a verifiable property of your repo."

This shifts us from "nice tool" to **"research infrastructure."**

### 1. Deterministic Rendering Lock (Critical)

**Problem:** SymPy's `latex()` output can change with versions, assumptions, or settings.

**Solution:** Wrap SymPy printing with explicit, locked options:

```python
# In Formula class
@dataclass
class Formula:
    id: str
    expr: sp.Expr
    # NEW: Lock rendering parameters
    rendering_opts: dict = field(default_factory=lambda: {
        "mode": "plain",  # or "equation"
        "fold_short_frac": False,
        "mul_symbol": "cdot",  # explicit multiplication symbol
    })
    assumptions: dict = field(default_factory=dict)  # e.g., {"n": {"positive": True}}
    
    def to_latex(self) -> str:
        """Render with locked settings for reproducibility."""
        # Apply assumptions to symbols
        expr_with_assumptions = self.expr
        for sym_name, sym_assumptions in self.assumptions.items():
            # Replace symbol with one that has assumptions
            pass
        # Render with locked options
        return sp.latex(expr_with_assumptions, **self.rendering_opts)
```

**Validation:**
- Same `id` must always render to the same LaTeX (across SymPy versions)
- Rendering options stored in formula index (so reviewers can reproduce)
- CI pins SymPy minor version; documents upgrade path

**Status:** Must implement before real usage

### 2. Formula Index as First-Class Output

**Current:** Comments in generated Markdown  
**New:** Dedicated slide + appendix listing every formula with full traceability

**Generated `formula_index.md` (auto-created):**

```markdown
# Formula Index
*Auto-generated from model.py via build_slides.py*

## Used Formulas

| ID | Source | LaTeX | Parameters | SymPy Version | Assumptions |
|----|--------|-------|------------|----------------|------------|
| `mult_input` | model.py:106 | $3$ | none | 1.14.0 | none |
| `mult_rule1` | model.py:113 | $\lambda n. 2n$ | n | 1.14.0 | n: positive=True |
| ... | ... | ... | ... | ... | ... |

## Usage Map

- **presentation.md:110** — `{{formula:mult_rule1}}`
- **presentation.md:111** — `{{formula:mult_input}}`
```

**Why This Matters:**
- Reviewers can verify every equation in the slides
- If SymPy rendering changes, the index diff will flag it
- Auditable proof that formulas match source code

**Implementation:**
```python
def generate_formula_index(formulas: dict, markdown_path: str) -> str:
    """Create formula index with usage map and traceability."""
    # Scan markdown for all {{formula:...}} references
    # Cross-check against FORMULAS dict
    # Generate table with rendering, source, assumptions
    # Flag missing or unused formulas
```

**Status:** ✅ Must be Phase 1

### 3. Symbol Aliasing & Assumptions

**Problem:** Code uses `n`, slides want to display as $\theta$. SymPy assumptions (positive, real, integer) affect printing.

**Solution:** Store symbol mappings and assumptions per formula:

```python
Formula(
    id="f_rule",
    expr=sp.Lambda((n,), 2*n),
    # NEW: Symbol display mapping
    symbols={"n": r"\theta"},  # code uses n, display as θ
    # NEW: Lock assumptions
    assumptions={"n": {"positive": True, "real": True}},
    rendering_opts={"mul_symbol": "cdot"}
)
```

**Validation in Error Messages:**
```
Error: Parameter 'n' in {{formula:f_rule|n=2}} is invalid.
Expected parameters: {} (formula has no parameters, n is a symbol)
Hint: If you meant to parameterize, use a form variant like {{formula:f_rule|form=evaluate_n=2}} (not yet supported)
```

**Status:** Must implement before real usage

### 4. CI Gate (Non-Negotiable)

**Goal:** Make formula drift *impossible* by failing the build if formulas mismatch.

**`just present` target:**
```bash
present:
    # Export formulas
    python paper/build_slides.py
    
    # Invoke Marp (fail if rendering errors)
    marp presentation_generated.md -o presentation.pdf
    
    # Generate formula index and check for missing formulas
    python paper/validate_formulas.py
    
    # If index changed, fail with diff (catches silent changes)
    git diff --exit-code formula_index.md || \
        (echo "Formula index changed—review and commit"; exit 1)
```

**CI Job (GitHub Actions):**
```yaml
- name: Build presentation
  run: |
    pip install sympy==1.14.0 marp-cli
    just present
    
- name: Check formula consistency
  run: |
    python paper/validate_formulas.py --strict
```

**Validation:**
- Missing formula ID → build fails with clear message
- Formula rendering changed → index diff flags it
- SymPy version mismatch → CI requires explicit upgrade

**Status:** ✅ Must be Phase 1

### 5. Actionable Error Messages

**Current:** Cryptic "formula not found"  
**New:** Help the user fix it

```
Error in presentation.md:110
  {{formula:missing_id}} — formula not found

Available formulas:
  - mult_input (line 106)
  - mult_rule1 (line 113)
  - mult_step1_output (line 120)
  - mult_final (line 127)

Hint: Did you mean {{formula:mult_rule1}}?
```

**Status:** ✅ Phase 1

### 6. One-Command Workflow

```bash
# Everything: export formulas → render slides → generate index
just present

# Optional: view PDF
open presentation.pdf formula_index.pdf
```

**Status:** ✅ Phase 1

---

## Updated Phase 1 Specification (MVP with Teeth)

**Phase 1 is no longer "basic substitution." It's "auditable formula rendering."**

```
Phase 1 Deliverables:
  ✓ Formula ID + metadata (name, description, source_line)
  ✓ Symbol aliasing (code `n` → display `θ`)
  ✓ Locked SymPy assumptions (reproducible rendering)
  ✓ Locked rendering options (mode, mul_symbol, fold_short_frac)
  ✓ {{formula:id}} substitution with error handling
  ✓ Formula index generation (table + usage map)
  ✓ `just present` one-command build
  ✓ CI gate (missing formulas, index changes)
  ✓ Actionable error messages
  
Deferred (Post-Pilot):
  - Form variants (|form=expanded)
  - VS Code snippets
  - Advanced parameter handling
  - Symbol renaming in rendered output (?)
```

---

## Validation Criteria (Measurable)

**Before considering PyPI, we must prove:**

1. ✅ **Reproducibility:** Same formula renders identically across SymPy versions (minor bumps)
2. ✅ **Auditability:** Formula index diffs catch all changes; no silent drift
3. ✅ **Usability:** `just present` succeeds in CI without manual steps
4. ✅ **Real Usage:** Used for 2+ conference presentations without critical friction
5. ✅ **Community Pull:** 3+ unsolicited requests from other researchers (not sales pitches)

---

## Bottom Line

The validator is right: this is no longer "nice-to-have traceability." It's **"formula drift detection by default."** With deterministic rendering, auditable artifacts, and CI gates, researchers can trust that:

> "Every formula in this presentation matches the code—we can verify it."

That's a tool worth maintaining.

**Validator's Bottom Line:**
> "Build it for yourselves first, use it in anger, and revisit PyPI once you've proven it across multiple talks."

**Our Commitment:**
We will use this for the membrane paper's next conference presentation and collect friction points before considering PyPI publication.

---

## Updated Implementation Roadmap

### Phase 1 (MVP - Now)
- [x] Basic formula substitution (`{{formula:id}}`)
- [x] Source line comments in output
- [ ] **Formula index generator** (auto-create appendix listing all formulas)
- [ ] **Locked SymPy assumptions** (explicit `mode`, `fold_frac`, etc.)
- [ ] **Actionable error messages** ("Formula `X` at presentation.md:42 not found")

### Phase 2 (Real Usage - Membrane Conference Talk)
- [ ] Integrate into `just present` target
- [ ] Add CI check for missing formula IDs
- [ ] Test symbol mapping / form variants
- [ ] Collect friction points from live usage
- [ ] Document lessons learned

### Phase 3 (Generalization - 6+ Months)
- [ ] Revisit PyPI based on usage data
- [ ] If publishing: Lock API, pin dependencies, add sunset clause
- [ ] If not: Mark as internal tool, document for team reuse

---

## Conclusion

**This is a good tool to build,** and the feedback validates both the problem and the approach. The key differentiator—**code-coupled formula rendering with auditable traceability**—is what will earn trust from researchers.

**Immediate Actions:**
1. Implement formula index generator
2. Lock SymPy printing assumptions
3. Add parameter mapping layer
4. Integrate into CI and build workflow
5. **Use it for membrane paper's conference presentation**

**Decision Point:** In 6 months, after real usage, revisit PyPI publication with concrete data on:
- How many presentations have we used it for?
- What friction points emerged in CI/workflow?
- Did unsolicited interest from others materialize?
- Are we committed to maintaining it long-term?

**If we publish:** Position as a niche utility with scope locked, version policy clear, and sunset clause documented.

---

## References & Related Work

- **Marp:** https://marp.app (Markdown → presentation engine)
- **KaTeX:** https://katex.org (Fast LaTeX math rendering)
- **Jupyter & nbconvert:** Formula support in notebooks (inspiration)
- **Quarto:** https://quarto.org (Code + narrative, heavier than we need)
- **Beamer:** https://ctan.org/pkg/beamer (Gold standard for math, but painful)
- **TexSlide:** https://texslide.com (LaTeX-focused, different audience)

---

**Next Step:** Implement Phase 1 (formula index, assumptions locking) in membrane repo. Use for conference presentation. Collect real feedback.
