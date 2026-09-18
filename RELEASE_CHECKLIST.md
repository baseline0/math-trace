# Release Qualification Checklist

## ✅ Build & Workflow

- [x] **Formula generation**: SymPy → LaTeX → Typst conversion works end-to-end
  - Fixed: Nested brace handling for `\binom{n_{a}}{2}` 
  - Added: Robust `_extract_brace_content()` parser in `SymPyToTypst`
  - Refactored: `build_paper.py` to use proper converter module

- [x] **Typst compilation**: main.typ → main.pdf (164 KB)
  - Fixed: Deprecated `label:` syntax → modern `<label>` notation
  - Fixed: Math mode variable syntax (Δ t vs Δt)

- [x] **Full pipeline**: `just paper` (clean build, all steps)
  - model.py → JSON export ✅
  - LaTeX → Typst formulas ✅
  - Simulation & figures ✅
  - PDF compilation ✅

## ✅ Testing

- [x] **Unit tests**: 16/16 passing
  - Model export and formula definitions
  - Simulation determinism and correctness
  - Traceability chain (code → math → paper)
  - Monotonicity theorem verification

- [x] **Type checking**: mypy with numpy-safe config
  - Added: mypy to dev dependencies
  - Configured: Skip external library errors

## ✅ Documentation & Commands

- [x] **Justfile recipes**: All working
  - `just paper` — Full build
  - `just test` — Test suite
  - `just typecheck` — Type checking
  - `just help` — Documentation

## Release Status

**Ready for release.** All core functionality works, tests pass, PDF builds successfully.

### Known Limitations
- Typst installation required for PDF generation (not a failure—formulas ready without it)
- Formula converter handles common LaTeX patterns; exotic commands may need extension

### Next Steps (Post-Release)
- Consider adding CI/CD pipeline (GitHub Actions for automated builds)
- Add more examples beyond membrane dynamics
- Extend Lean formalization coverage
