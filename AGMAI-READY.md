# math-trace: AGMAI-Ready Contract

**Version**: 1.0 (Sep 22, 2026)  
**Status**: Contract for v0.9.0-rc1 and v1.0.0 releases  
**Audience**: AGMAI, academic researchers, AI companies auditing mathematical claims

---

## What math-trace Is

A framework for tracing equations from source code through symbolic representation, verification, and publication.

**Workflow**: Python (SymPy) → LaTeX → Typst → PDF + JSON provenance

---

## What math-trace Guarantees

### Guaranteed Features (v0.9.0+)

- ✅ **Equation extraction from SymPy** — Equations defined in `src/model.py` are automatically exported to LaTeX
- ✅ **Typst paper generation** — Equations render in publication-quality Typst documents
- ✅ **Source-line traceability** — Every equation tagged with filename and line number
- ✅ **Metadata schema** — Consistent equation records (name, LaTeX, description, assumptions, units, verification status)
- ✅ **One-command build** — `just paper` generates complete paper from fresh checkout
- ✅ **Test coverage** — All templates pass unit tests (90%+ line coverage)
- ✅ **Reproducibility** — Same seed → deterministic outputs over 100 runs
- ✅ **Clean installation** — Works in fresh Python 3.11–3.13 environment with `uv sync`

### Experimental Features (Optional, May Change)

- 🔬 Lean formalization (optional per template; theorems may remain incomplete)
- 🔬 Palomar registry integration (optional; metadata format may evolve)
- 🔬 Interactive visualizations (Streamlit/Jupyter; UI may redesign)

---

## What math-trace Does NOT Verify

**Explicitly out of scope**:

- ❌ Empirical adequacy — An equation matching experimental data
- ❌ Parameter estimation — Fitting constants to real-world measurements
- ❌ Implementation correctness — That external libraries (SymPy, NumPy) behave as documented
- ❌ Numerical stability — That floating-point arithmetic remains stable over long simulations
- ❌ Physical realism — That a model captures relevant phenomena (e.g., SIR ignores age structure)
- ❌ Scientific validity — That a theory is correct, only that it was transcribed faithfully
- ❌ Domain expertise — That users understand the assumptions and limitations

**Implication**: A green "verified" checkmark means "this equation was transcribed correctly from source and passes unit tests," NOT "this equation correctly models reality."

---

## Supported Environments

### Required

- **Python**: 3.11, 3.12, 3.13 (3.10 or earlier not supported)
- **SymPy**: ≥1.12
- **Operating System**: macOS (Intel or Apple Silicon), Linux (Ubuntu 20.04+), Windows (WSL2)

### Optional

- **Typst**: ≥0.10 (required for PDF generation; installable via `cargo install typst-cli`)
- **Lean**: 4.0+ (required only for Lean formalization optional components)

### Not Supported

- Python 3.10 or earlier
- Windows native cmd.exe (use WSL2 or PowerShell)
- SymPy 1.11 or earlier (compatibility breakage)

---

## Equation-Template Public API

### Required Fields (Every Equation Must Have)

```python
@dataclass
class Equation:
    name: str
        # Human-readable: "SIR Rate Equations", "Attention Mechanism"
        # Used in LaTeX captions and JSON export
    
    latex: str
        # Sympy-generated or manually verified
        # Example: r"S' = -\beta S I / N"
    
    description: str
        # 1-2 sentences, what does this equation represent
        # Example: "Change in susceptible population due to transmission"
    
    source_file: str
        # Where in codebase: "src/epidemiology/model.py"
    
    source_line: int
        # Line number in source file where equation is defined
    
    assumptions: List[str]
        # Every assumption that makes this equation valid
        # Example: ["S ≥ 0", "I ≥ 0", "R ≥ 0", "S + I + R = N", "β > 0", "γ > 0"]
        # Do NOT omit; list everything
    
    units: Dict[str, str]
        # Dimensions of each variable
        # Example: {"S": "persons", "β": "1/days", "γ": "1/days", "N": "persons"}
    
    verification_status: Dict[str, VerificationRecord]
        # See Verification Vocabulary section below
        # Example: {
        #   "source_verified": VerificationRecord(by="human", date="2026-09-22"),
        #   "transcription_verified": VerificationRecord(by="test", test_file="test_sir.py"),
        #   "numerically_verified": VerificationRecord(by="test", test_file="test_sir_numerics.py"),
        #   "formally_verified": None,  # Not attempted
        # }
```

### Optional Fields

```python
    historical_context: Optional[str]
        # Narrative: where this equation came from, how notation evolved
        # Example: "Kermack-McKendrick (1927) modeled infection as exponential..."
    
    citations: List[Citation]
        # Peer-reviewed sources
        # Example: [Citation(authors="Kermack, McKendrick", year=1927, doi="...")]
    
    related_equations: List[str]
        # Names of related equations (e.g., "SIR to SEIR transition")
    
    transformations: List[str]
        # How this equation relates to others (e.g., "SEIR with γ_e=0 reduces to SIR")
```

### Verification Vocabulary (Distinct, Non-Collapsing)

**Six Status Categories** — Never collapse into one "verified" badge:

| Status | Meaning | Example |
|--------|---------|---------|
| `source_verified` | Cited source was inspected by human | "Kermack-McKendrick 1927 paper reviewed" |
| `transcription_verified` | Equation faithfully transcribed from source | "test_sir.py: equation matches Kermack form exactly" |
| `symbolic_verified` | Symbolic identities or transformations passed | "test_algebra.py: SIR + SEIR identity proven" |
| `numerically_verified` | Numerical checks passed over defined test cases | "test_sir_numerics.py: SIR equilibrium S*=N/R₀ within 1e-6" |
| `formally_verified` | Theorem prover established stated property | "Lean: conservation law proven under assumptions" |
| `historical_interpretation` | Human-curated historical claim (not mathematical proof) | "This formulation became standard after 1970" |

**Rules**:
- Each status is **independent** — a equation can have source_verified=true, but transcription_verified=false
- If a status is not attempted, omit it (don't set to False)
- Every equation must have **at least one status** (even if just `source_verified: human-reviewed`)
- An unknown status should be explicitly marked as None or omitted, never left ambiguous

**Example Record**:
```json
{
  "name": "SIR Rate Equations",
  "latex": "S' = -β S I / N; I' = β S I / N - γ I; R' = γ I",
  "verification": {
    "source_verified": {"by": "human", "date": "2026-09-22", "note": "Kermack-McKendrick 1927 inspected"},
    "transcription_verified": {"by": "test_sir.py", "date": "2026-09-22"},
    "numerically_verified": {"by": "test_sir_numerics.py", "tolerance": 1e-6},
    "formally_verified": null,
    "symbolic_verified": null,
    "historical_interpretation": {"by": "human", "claim": "Became standard epidemiological model post-1970"}
  }
}
```

---

## Supported Use Cases

### Primary (v0.9.0+)

- 🟢 **Academic research papers** — Publish equations with traceability to code
- 🟢 **Educational materials** — Teach formula derivation with source code
- 🟢 **Reproducible research** — Readers can regenerate figures from code
- 🟢 **Audit trails** — Mathematicians verify equation transcription
- 🟢 **Code documentation** — Auto-generate papers from model.py

### Secondary (v0.9.0–1.0.0)

- 🟡 **AI company auditing** — Review assumptions and verification statuses
- 🟡 **Formal verification** — Subset of equations proven in Lean

### Not Supported

- 🔴 **Live code-to-paper synchronization** — Papers are snapshots, not live docs
- 🔴 **Automatic parameter fitting** — math-trace provides structure, not estimation
- 🔴 **Numerical simulation** — math-trace generates derivations; execution is user's responsibility
- 🔴 **Real-time data ingestion** — Static papers only

---

## Template Ecosystem

### Five Core Templates (v0.9.0)

Each template follows identical contract:

| Template | Equations | Assumptions | Tests | Paper | Status |
|----------|-----------|-------------|-------|-------|--------|
| Epidemiology (SIR/SEIR) | 6 | Listed, comprehensive | 90%+ coverage | 10-section golden path | Core |
| Quantum Systems | 5 | Listed, comprehensive | 90%+ coverage | 10-section (replicating Epi structure) | Core |
| Control Systems | 5 | Listed, comprehensive | 90%+ coverage | 10-section | Core |
| Graph Neural Networks | 5 | Listed, comprehensive | 90%+ coverage | 10-section | Core |
| Thermodynamics | 5 | Listed, comprehensive | 90%+ coverage | 10-section | Core |

### Adding New Templates

To add a new template:

1. Create `templates/{domain}/src/model.py` with equations in SymPy
2. Each equation must have: name, LaTeX, description, assumptions, units, source_line
3. Write `templates/{domain}/tests/` covering success and failure cases (90%+ coverage)
4. Write `templates/{domain}/paper.typ` with 10 sections (see Epidemiology golden path)
5. Verify assumptions and units match epidemiology schema conventions
6. External reviewer confirms reproducibility
7. Tag in changelog as "new template added"

---

## Release Versioning

### v0.9.0-rc1 (Release Candidate, Week 6)

- ✅ All 5 templates complete (code + tests)
- ✅ Epidemiology paper = golden path (10 sections, 100% claims verified)
- ✅ Other 4 papers replicate Epi structure
- ✅ Test coverage 90%+ on all templates
- ✅ CHANGELOG.md, CITATION.cff, LICENSE, clean install verified
- ✅ External reviewer confirmed reproducibility
- ⚠️ API not yet frozen (may have breaking changes before v1.0.0)

### v0.9.0 (Release)

- Same as rc1, feedback incorporated

### v1.0.0 (When Ready)

- ✅ All from v0.9.0
- ✅ API declared stable (no breaking changes without major version bump)
- ✅ Lean formalization on ≥3 templates (optional but included)
- ✅ Zenodo DOI minted
- ✅ Downstream citations demonstrating adoption

---

## Known Limitations (Honest)

1. **SymPy constraints** — Only equations expressible in SymPy are supported; complex piecewise functions, special functions may need manual workarounds
2. **Unit tracking** — Units are metadata only; no automatic dimensional analysis or conversion
3. **Symbolic verification** — Limited to polynomial and rational function identities; transcendental proofs require Lean
4. **Scalability** — Papers with 100+ equations may have slow compile times
5. **Peer review** — math-trace does not replace scientific review; it supplements it
6. **Historical accuracy** — We cite sources but cannot verify archival historical claims beyond academic databases
7. **Implementation fidelity** — Test coverage is local; does not guarantee correctness when equations are embedded in larger systems

---

## Approval & Sign-Off

**Contract finalized**: Sep 22, 2026  
**Author**: Mark Alexiuk  
**Reviewers**: (External review pending v0.9.0-rc1)

**Next checkpoint**: Week 1 (Sep 22–29) — Contract freeze complete, ready for golden path (Epidemiology paper)

---

**For AGMAI**: This contract defines what math-trace is, what it guarantees, and what it explicitly does not verify. The verification vocabulary prevents collapsing distinct claims into one badge. The Epidemiology golden path will demonstrate rigor in all dimensions: assumptions, traceability, reproducibility, and candid limitations.
