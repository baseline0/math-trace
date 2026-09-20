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

## Conclusion

**This is a good tool to build.** It solves a real problem for academic researchers (including us). Publishing to PyPI is reasonable, but only if we're honest about the niche and committed to maintenance.

**Recommendation:** Build it now. Use it for the membrane paper. See if others find it valuable. Revisit the PyPI decision in 6 months with real usage data.

**If we decide to publish:** Position it as a niche utility, not a general-purpose tool. Better to be honest about scope than to overpromise and disappoint.

---

## References & Related Work

- **Marp:** https://marp.app (Markdown → presentation engine)
- **KaTeX:** https://katex.org (Fast LaTeX math rendering)
- **Jupyter & nbconvert:** Formula support in notebooks (inspiration)
- **Quarto:** https://quarto.org (Code + narrative, heavier than we need)
- **Beamer:** https://ctan.org/pkg/beamer (Gold standard for math, but painful)

---

**Next Step:** Implement the MVP in the membrane repo. Iterate based on real usage.
