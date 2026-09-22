# Membrane Computing: Reference Implementation for math-trace Golden Path

**Status**: Production-proven formula infrastructure (conference presentation)  
**Location**: `/home/mark/projects/membrane/paper/model.py` + `presentation.md`  
**Role**: Template for replication to other domains (Epidemiology, Quantum, Control, etc.)

---

## Why Membrane Is Our Golden Path

### What Makes It Ideal

1. **Production-validated** — Already used in real conference presentation (no theory, real friction data)
2. **Formula class maturity** — Enhanced `Formula` with:
   - Source line tracking (`source_line`)
   - Locked SymPy rendering (deterministic LaTeX)
   - Symbol aliasing (code name → display name)
   - Assumption locking per symbol
3. **One-command pipeline** — `just present` automates: export → build → validate → index
4. **Audit trail** — Commit hash + LaTeX hash for reproducibility
5. **Real code** — Not a spec; 200+ lines of proven infrastructure
6. **Friction collection underway** — Phase 2 gathering real user feedback

### What It Proves to AGMAI

- ✅ Deterministic rendering (same formula → same LaTeX every time)
- ✅ Versioning (formulas tracked independently from code)
- ✅ Validation (pre-commit hooks catch formula drift)
- ✅ Integration (SymPy → Marp → Typst → PDF)
- ✅ Traceability (commit hash + LaTeX hash in index)

---

## Current State (What Membrane Has)

### Formula Infrastructure

**`Formula` class** (`paper/model.py:20–50`):
```python
@dataclass
class Formula:
    id: str
    name: str
    expr: sp.Expr
    description: str
    source_line: int
    parameters: dict = field(default_factory=dict)
    
    # Locked rendering options (reproducibility)
    rendering_opts: dict = field(
        default_factory=lambda: {
            "mode": "plain",
            "fold_short_frac": False,
            "mul_symbol": "cdot",
        }
    )
    
    # Symbol display mapping
    symbols: dict = field(default_factory=dict)  # e.g., {"n": r"\theta"}
    
    # Locked assumptions per symbol
    assumptions: dict = field(default_factory=dict)
```

**What it does**:
- ✅ Tracks source line (equation defined at line X in model.py)
- ✅ Locks SymPy rendering options (same formula always renders identically)
- ✅ Symbol aliasing (code uses `n`, display shows `θ`)
- ✅ Assumptions per symbol

**What it's missing** (for AGMAI contract):
- ❌ Explicit assumptions as list (currently in `assumptions: dict`, need `assumptions: List[str]`)
- ❌ Units dictionary (`units: Dict[str, str]`)
- ❌ Domain constraints (`domains: Dict[str, str]`)
- ❌ Verification status vocabulary (source_verified, transcription_verified, etc.)
- ❌ Expected failure tests (tests assume success; need to test invalid inputs)

### Build Pipeline

**`just present`** (Justfile):
```bash
just present              # Full: export → build → validate → index
just formula-check       # Verify consistency (CI)
just paper              # Build Typst paper
just paper-all          # Paper + presentation
```

**What it does**:
- ✅ Exports SymPy equations to LaTeX
- ✅ Validates formulas (completeness checks)
- ✅ Generates formula index with LaTeX hashing
- ✅ Builds Marp presentation + Typst paper

**What it's missing** (for reproducibility):
- ❌ Integration test (one command from git clone → PDF)
- ❌ Failure tests (verify system rejects malformed inputs)
- ❌ Documentation (README explaining verification story)

### Testing & Validation

**Current** (`stress_test_formulas.py`):
- ✅ 5 stress tests (all passing)
- ✅ Symbol assumption completeness checks
- ✅ LaTeX hashing validation

**Missing**:
- ❌ Expected failure tests (negative parameters, invalid domains, etc.)
- ❌ Integration test (full pipeline from scratch)
- ❌ Determinism test (same run produces identical output 100 times)

---

## What Needs to Be Added (Weeks 2–3)

### Phase 1: Enhance Formula Class (4–6 hrs)

**Goal**: Add AGMAI contract fields without breaking existing code

**Changes to `paper/model.py`**:

1. **Add explicit assumptions list** (1 hr):
   ```python
   @dataclass
   class Formula:
       # ... existing fields ...
       
       assumptions: List[str]  # ["n ≥ 0", "k > 0", "differentiable", ...]
       units: Dict[str, str]   # {"n": "persons", "k": "1/days"}
       domains: Dict[str, str] # {"n": "[0, ∞)", "k": "(0, ∞)"}
   ```
   - Document P-System constraints (hierarchical membrane, multisets, parallelism)
   - Map variables to units + domains

2. **Add verification status** (1 hr):
   ```python
   from enum import Enum
   
   class VerificationStatus(Enum):
       SOURCE_VERIFIED = "source_verified"
       TRANSCRIPTION_VERIFIED = "transcription_verified"
       SYMBOLIC_VERIFIED = "symbolic_verified"
       NUMERICALLY_VERIFIED = "numerically_verified"
       FORMALLY_VERIFIED = "formally_verified"
       HISTORICAL_INTERPRETATION = "historical_interpretation"
   
   @dataclass
   class Formula:
       # ... existing fields ...
       verification: Dict[VerificationStatus, bool]
   ```
   - Mark which formulas have been verified (and in what way)

3. **Expand symbols metadata** (1 hr):
   - Document why each symbol is aliased
   - Add descriptions to symbol mappings
   - Link to historical context (if any)

4. **Integration test** (1–2 hrs):
   - Write `integration_test.py`
   - Runs: git checkout → uv sync → just present → verify PDF matches reference
   - Determinism test: run 10 times, all outputs identical

**Deliverable**: Enhanced Formula class + integration test, backward compatible

---

### Phase 2: Expand Tests (3–4 hrs)

**Goal**: Test both success and expected failure cases

**Add to `stress_test_formulas.py`**:

1. **Success case tests** (already exist):
   - Equation definition completeness ✅
   - Symbol assumption coverage ✅

2. **Failure case tests** (NEW):
   - Negative population (should reject)
   - Zero rates (should reject)
   - Missing assumptions (should flag)
   - Mismatched units (should error)
   - Render instability (same formula, different SymPy version?)

3. **Determinism test** (NEW):
   - Run formula rendering 100 times
   - Verify identical LaTeX output each time
   - Confirm commit hash consistency

4. **Integration test** (NEW):
   - `git clone` fresh checkout
   - `uv sync`
   - `just present`
   - Verify `presentation.pdf` exists + is valid
   - Verify `formula_index.md` is complete

**Deliverable**: Test suite covering normal + edge + integration cases

---

### Phase 3: Documentation (2–3 hrs)

**Goal**: Explain membrane as golden path exemplar

**Create**:

1. **`MEMBRANE-STRUCTURE.md`** (1 hr):
   - How Formula class works (source line, rendering, assumptions)
   - How to replicate pattern for new domains
   - When to deviate (and why to document it)

2. **`VERIFICATION-STORY.md`** (1 hr):
   - How Membrane demonstrates each verification status
   - What's been verified (source, transcription, symbolic)
   - What remains unverified (empirical, formal proofs)
   - How AGMAI can audit the claims

3. **Update README.md** (0.5 hr):
   - Link to membrane as reference
   - Explain golden path pattern
   - Quick reproducibility instructions

**Deliverable**: Documentation explaining Membrane pattern for replication

---

## Replication Pattern (Weeks 4–5)

Once Membrane is enhanced, other templates follow this exact structure:

### For Each New Template (e.g., Epidemiology):

1. **Copy Membrane structure**:
   ```
   templates/epidemiology/
   ├── model.py               (SymPy formulas with enhanced Formula class)
   ├── scenarios/             (reference implementations)
   ├── tests/                 (unit + integration tests)
   ├── presentation.md        (formula-driven slides)
   └── build_paper.py         (export logic)
   ```

2. **Populate with domain-specific content**:
   - Define SIR/SEIR equations in SymPy
   - Document assumptions, units, domains
   - Create scenarios (COVID baseline, Measles, Ebola)
   - Write presentation.md

3. **Run test suite**:
   - All formulas must pass assumptions checks
   - Integration test: `just present` → PDF
   - Determinism test: same output 100x

4. **External review**:
   - Someone unfamiliar with code follows setup
   - Verifies claims against sources
   - Reports friction

---

## Success Criteria (Week 3)

**Membrane is ready as golden path when**:

- ✅ Formula class has assumptions, units, domains fields
- ✅ Verification status vocabulary integrated
- ✅ Integration test passes (git clone → PDF)
- ✅ Failure tests catch invalid inputs
- ✅ Determinism test confirms reproducibility
- ✅ Documentation explains replication pattern
- ✅ One external reviewer successfully replicates

---

## Integration with AGMAI Demo (Week 7–8)

**Membrane → equations-history → math-trace demo flow**:

1. **equations-history**: "P-systems originated with Gheorghe Păun in 1998. Here's the conceptual evolution."
2. **Membrane (math-trace)**: "Here's the modern formulation (Membrane v0.9.0):
   - Formula class with assumptions, units, domains
   - Deterministic rendering + audit trail
   - Integration tests confirming reproducibility
   - Verification statuses showing what's been checked"
3. **Formalization** (optional): "Lean proofs available for key theorems"

**AGMAI takeaway**: "This is what formula-driven research looks like. Help us standardize it."

---

## Risk Mitigation

**Risk**: Membrane changes break existing functionality  
**Mitigation**: All changes backward compatible; version bump if needed

**Risk**: Replication pattern doesn't generalize  
**Mitigation**: Test on 1–2 templates (Epidemiology, Quantum) before claiming it works

**Risk**: Integration test is flaky  
**Mitigation**: Run 10 times in CI/CD before declaring success

---

## Timeline

| Week | Task | Deliverable |
|------|------|-------------|
| **1** | ✅ Contracts frozen | AGMAI-READY.md for both projects |
| **2** | Enhance Membrane | Formula class + integration test |
| **3** | Expand tests + docs | Failure tests, determinism test, README updates |
| **4–5** | Replicate (parallel) | Epidemiology + Quantum templates |
| **6** | External review + v0.9.0-rc1 | Release candidate with friction collected |
| **7–8** | AGMAI demo | Integration of equations-history + math-trace |

---

## Related Documents

- [AGMAI-READY.md](./AGMAI-READY.md) — Contract for math-trace
- [EPIDEMIOLOGY-GOLDEN-PATH.md](./EPIDEMIOLOGY-GOLDEN-PATH.md) — Template structure (Membrane will exemplify this)
- [Competitive Positioning](../../../.claude/projects/-home-mark-projects-math-trace/memory/competitive_positioning.md) — Why Membrane + math-trace is unique

---

**Version**: 1.0 (Sep 22, 2026)  
**Status**: Ready for Week 2 enhancement  
**Owner**: Mark Alexiuk
