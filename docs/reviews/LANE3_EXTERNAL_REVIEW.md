# Lane 3 External Review: math-trace v1.0.0 Architecture & Hardening Verification

**Document ID:** `docs/reviews/LANE3_EXTERNAL_REVIEW.md`
**Review Target:** `math-trace` v0.1.0 -> v1.0.0 Release Gate
**Reference Item:** `work-728ab85c3eff` (Lane 3 External Review)
**Evaluator:** Research & Venture Pipeline Specialist (Baseline0 Fleet)
**Date:** 2026-11-26
**Status:** APPROVED

---

## 1. Executive Summary

This external review evaluates the architectural restructuring, public API facade stability, data schema consistency, and resilience hardening of `math-trace` prior to its v1.0.0 release.

Between versions 0.1.0-dev and the current release candidate, large monolithic modules were successfully decomposed into modular packages under `src/math_trace/`. All public facades, backward compatibility aliases, route contracts, and downstream integration seams were verified against 496 hermetic tests.

---

## 2. Package Decomposition Audit

The repository has completed the modularization of six core subsystems into dedicated sub-packages:

| Monolith Module (Legacy) | Refactored Package | Sub-Modules | Public API / Compatibility Boundary |
|---|---|---|---|
| `server.py` | `src/math_trace/server/` | `app.py`, `routes_arxiv.py`, `routes_formulas.py`, `routes_formulas_api.py`, `routes_formulas_browser.py`, `routes_hardness.py`, `ui.py` | Preserved `math_trace.server` imports, route registrations, and test monkeypatching seams. |
| `generators.py` | `src/math_trace/generators/` | `sympy_typst.py`, `_latex_to_typst.py`, `typst_env.py` | Exports `SymPyToTypst`, `TypstEnvironmentBuilder`. |
| `reference_check.py` | `src/math_trace/reference_check/` | `registry.py`, `report.py`, `__main__.py` | CLI entrypoint, report generators, and reference check runners preserved. |
| `formula_records.py` | `src/math_trace/formula_records/` | `models.py`, `normalize.py`, `tags.py`, `io.py`, `builder.py` | Dataclass models (`FormulaRecord`, `FormulaSource`), deterministic ID generation, JSONL I/O. |
| `services.py` | `src/math_trace/services/` | `downloader.py`, `extractor.py`, `builder.py` | `PaperDownloader`, `FormulaExtractor`, `PresentationBuilder`, `ExtractedEquation`. |
| `paper_store.py` | `src/math_trace/paper_store/` | `store.py`, `types.py`, `validation.py` | Paper caching, disk-backed metadata, and validation routines. |

---

## 3. Verification Checklist

### 3.1 Public Facade Stability
- [x] **Root Exports**: `src/math_trace/__init__.py` cleanly re-exports all primary types and functions:
  - `EquationId`, `canonical_srepr`, `expr_hash`
  - `FormulaRecord`, `FormulaSource`, `build_formula_record`, `build_records_from_tex`
  - `extract_display_formulas`, `infer_concept_tags`, `normalize_latex`
  - `read_records_jsonl`, `records_to_jsonl`, `stable_record_id`, `write_records_jsonl`
  - `SymPyToTypst`, `TypstEnvironmentBuilder`
  - `ExtractedEquation`, `FormulaExtractor`, `PaperDownloader`, `PaperMetadata`, `PresentationBuilder`
- [x] **Backward-Compatibility Aliases**: `Formula = ExtractedEquation` is maintained in `__init__.py` and `services/__init__.py`.
- [x] **Symbol Exports Declaration**: Explicit `__all__` containing 20 symbols guarantees clean wildcard and static type checker semantics.

### 3.2 Formula Record Schema Alignment with `collected.json`
- [x] **Dataclass Schema**: `FormulaSource` and `FormulaRecord` in `src/math_trace/formula_records/models.py` define strict typed attributes:
  - `record_id`: deterministic SHA-256 identifier (`stable_record_id`).
  - `latex`: original TeX equation string.
  - `source`: structured `FormulaSource` (fields: `paper_id`, `arxiv_id`, `path`, `file`, `line`, `env`, `url`, `licence`, `source_sha256`).
  - `context`: textual context or sentence surrounding the equation.
  - `concept_tags`: tuple of classification tags.
  - `normalized`: boolean symbolic normalization flag.
  - `canonical_srepr`, `expr_hash`, `sympy_str`, `parse_error`: AST representation and hash metadata.
  - `schema_version`: integer (version 1).
- [x] **Serialization Consistency**: `to_dict()` and `from_dict()` serialize lists and dataclasses canonically, directly matching the JSON schema required by `collected.json` in upstream/downstream knowledge bases (such as `tool-lit-review`).
- [x] **Idempotent I/O**: `write_records_jsonl` and `read_records_jsonl` in `src/math_trace/formula_records/io.py` round-trip records without loss or field mutation.

### 3.3 Server Routes and Error Contract Preservation
- [x] **HTTPException Preservation**: In `src/math_trace/server/routes_formulas_api.py`, `get_formulas` explicitly catches and re-raises `HTTPException` before any broad exception fallback, ensuring standard 404 responses for missing papers rather than leaking accidental 500 internal server errors.
- [x] **Route Registration**: `src/math_trace/server/app.py` mounts routers for arXiv ingestion, formula browser UI, formula JSON API, and proof hardness checks without route drift.
- [x] **Characterization Test Coverage**: Verified by `tests/unit/test_routes_formulas_characterization.py` and `tests/unit/test_server_routes.py`.

### 3.4 Downloader & Extractor Hardening
- [x] **Network Timeout Enforcement**: `PaperDownloader.download` in `src/math_trace/services/downloader.py` executes `urlopen(pdf_url, timeout=30)` with a strict 30-second timeout.
- [x] **URL Scheme Validation**: Explicitly rejects unsupported or dangerous URL schemes; allows only `http` and `https`.
- [x] **Path Traversal Protection**: Archive member extraction sanitizes filenames, preventing `../` traversal, symlink spoofing, and absolute-path writes into host root.
- [x] **Characterization Test Coverage**: Verified by `tests/unit/test_arxiv_extractor_unhappy_paths.py` and `tests/unit/test_build_presentation.py`.

---

## 4. Verification Evidence & Test Run Receipt

All hermetic unit and integration tests were executed via the standard repository recipe:

```bash
$ just test
============================= test session starts ==============================
platform linux -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0
rootdir: /home/mark/projects/math-trace
collected 669 items / 173 deselected / 496 selected

================ 496 passed, 173 deselected, 1 warning in 5.38s ================
```

All 496 tests passed with zero failures or errors.

---

## 5. Review Conclusion

The Lane 3 verification requirements are completely satisfied. The codebase is structurally sound, backward-compatible, resilient against untrusted inputs, and verified by passing test gates.

**Recommendation:** Proceed with v1.0.0 release tagging when market discovery and packaging checklists are finalized.
