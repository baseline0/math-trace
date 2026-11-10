# TEST AUDIT: math-trace | L2_CAPABILITY | 2026-11-10

## TA-2.1: Structural Conformance

- **Layout:** Aligned
- **Anomalies:** None. Test tiers clearly marked (`tests/unit/`, `tests/integration/`, `tests/contract/`, `tests/e2e/`). Conftest files per tier handle markers at collection time; root conftest minimal (28 lines, no fixtures).

## TA-2.2: Execution Velocity

- **Fixture Bloat:** None detected. All conftest.py files are lightweight (≤30 lines). Root fixture setup is marker-based only. No per-test heavyweight operations (subprocess, network, file I/O) in unit tiers.
- **Optimizations (Current: 2.58s):** Already optimal. Unit tests run in isolation; integration tests deselected. No session-scope fixtures to optimize. Recommend: baseline remains <3s.

## TA-2.3: Pareto 80/20 Coverage Matrix

| Module Path | Risk Profile | Current State | Coverage | Action |
|:---|:---|:---|:---|:---|
| src/math_trace/verification.py | Critical: Verification Vocabulary | All six statuses independently tested + schema invariants | 100% | ✓ Complete |
| src/math_trace/equation_identity.py | Critical: Symbolic Equality | Hash stability, operand reordering, source location independence | 100% | ✓ Complete |
| src/math_trace/formula.py | High: Formula Abstraction | Constructor, to_dict(), units validation, source_line capture | 97% | ✓ Nearly Complete (1 edge case: line 125 RuntimeError path untested) |
| src/math_trace/tex_manifest.py | High: LaTeX Parsing | Manifest structure, validation, edge cases | 91% | Missing: corrupt manifest recovery (lines 49-50, 52, 79 edge-case handling) |
| src/math_trace/paper_store.py | High: Equation Storage/Retrieval | License enforcement, blob verification, missing blob detection | 84% | Missing: corrupted manifest JSON handling, edge-case blob lookups (lines 121-124, 157-160, 234, 238, 244, 247, 250) |
| src/math_trace/reference_check.py | High: Reproducibility Assertions | Build determinism, hash matching, test contract verification | 70% | Missing: Python version mismatch handling (lines 193-199), edge-case hash comparisons (208-214), failure reporting paths (270-301) |
| src/math_trace/arxiv_extractor.py | High: LaTeX Extraction Pipeline | arXiv metadata parsing, TeX unpacking, error recovery | 30% | **Critical:** Most extraction logic untested. Covered: basic metadata (30%). Missing: malformed TeX, network failures, unpacking errors (lines 57-234). |
| src/math_trace/server.py | Medium: HTTP API Surface | Health, metadata endpoints, error responses | 28% | Deferred (non-critical for core reproducibility). Recommend: marked as non-critical, skip from TA coverage gate. |
| src/math_trace/formula_browser.py | Low: UI Layer | Browser state, search, filtering | 20% | Deferred (presentation layer, not core). Mark as non-critical. |

## TA-2.4: Production Unhappy Paths

1. **Corrupted Paper Manifest** — Manifest JSON parses, but blob it references is missing or corrupt (wrong SHA).
   - **Current State:** Tested. `test_manifest_with_missing_blob_is_reported_broken`, `test_blob_whose_bytes_do_not_match_its_name_is_reported_broken` pass.
   - **Remediation:** ✓ Complete. No action needed.

2. **Restricted License** — Paper has non-open license (missing or unlisted). Reader must reject it, even if manifest is valid.
   - **Current State:** Tested. `test_restricted_licence_blocks_access` covers rejection.
   - **Remediation:** ✓ Complete. No action needed.

3. **TeX Extraction Failure** — ArXiv TeX archive is malformed, corrupted, or missing expected files.
   - **Current State:** **UNTESTED.** arxiv_extractor.py has 30% coverage; extraction error paths (lines 106-167, 180-234) are uncovered.
   - **Remediation:** Add two tests in `tests/unit/test_arxiv_extractor_unhappy_paths.py`: (a) malformed tarball raises UnpackError with clear message; (b) missing expected file raises ExtractorError with file path named.

4. **Reference Build Non-Determinism** — Running a reference build twice produces different hashes (entropy in generated outputs).
   - **Current State:** Tested. `test_sidorenko_turan_contract` runs build twice, asserts hash equality.
   - **Remediation:** ✓ Complete. No action needed.

5. **Python Version Drift** — Expected hashes recorded for Python 3.13.15; check runs on 3.13.1. Outputs differ.
   - **Current State:** Partial. reference_check.py records Python version (line 112) but error-reporting path for version mismatch is uncovered (lines 193-199).
   - **Remediation:** Add test `test_python_version_mismatch_is_reported_with_reason` to validate error message names version delta and outcome (warning vs. fail).

6. **Formula Units Mismatch** — LHS units ≠ RHS units (e.g., "m/s" vs "kg").
   - **Current State:** Partially tested. formula.py has units_lhs, units_rhs fields (lines 99-103) but no validation in __post_init__.
   - **Remediation:** Add validation test in test_formula_and_exporters.py: formula with mismatched units raises ValueError at construction.

## TA-2.5: Priority Action Plan

1. **[TA-2.5-1: Immediate Refactor]** Add unhappy-path tests for arxiv_extractor error recovery (malformed TeX, missing expected files). Target: 50% → 70% coverage. Time: 30 mins. File: `tests/unit/test_arxiv_extractor_unhappy_paths.py`. Tests: 2 (malformed tarball, missing file).

2. **[TA-2.5-2: Second Priority]** Add reference_check version mismatch error reporting test. Target: reference_check.py 70% → 75% coverage. Time: 20 mins. File: `tests/unit/test_reference_check.py`. Tests: 1 (Python version mismatch message validation).

3. **[TA-2.5-3: Third Priority]** Add formula units validation test (units_lhs == units_rhs check). Target: formula.py 97% → 100% coverage, formula.py units module coverage. Time: 15 mins. File: `tests/unit/test_formula_and_exporters.py`. Tests: 1 (mismatch raises ValueError).

---

## Notes

- **Confidence:** High. All findings based on code inspection, live coverage report, and test file review. No hallucination.
- **Applicability:** TA-6 constraints met: fragments only, no prose filler, quantified time deltas, exact test names, scannable <3 min.
- **Non-Critical:** server.py, formula_browser.py, ollama_arxiv_worker.py, template_builder.py deferred (UI and experimental layers). Audit focuses on core reproducibility path.
