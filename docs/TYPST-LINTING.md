# Typst Linting in math-trace

We use a **three-layer system** to catch Typst syntax errors early and keep `.typ` files working across the codebase.

---

## Quick overview

| Layer | What it does | When | Audience |
|-------|-------------|------|----------|
| **Automation** | `typst compile` + extra checks | Every commit | CI, contributors |
| **Documentation** | Explanations of common errors | Reference | Developers stuck |
| **Examples** | Working `.typ` files you can copy | While editing | Template users |

**Result:** Errors are caught before they reach users, and developers know exactly how to fix them.

---

## What happens when you commit a `.typ` file

### 1. Local (Before pushing)

**Optional:** If you've installed the pre-commit hook (`pre-commit install`):

```bash
$ git commit
→ pre-commit runs scripts/check_typst.py
→ If errors, commit is blocked with suggestions
→ You fix them and try again
```

This is the fastest feedback loop.

### 2. CI (GitHub Actions)

When you push or open a PR:

```bash
→ GitHub runs .github/workflows/lint-typst.yml
→ Calls scripts/check_typst.py
→ Reports results inline on your PR
→ Blocks merge if errors found
```

**Error on your PR?** Click the "Details" link to see:
- Which file and line failed.
- Why it failed.
- What the suggested fix is.
- Link to relevant section of TYPST-GOTCHAS.md.

### 3. You fix it

Look up the error in [TYPST-GOTCHAS.md](TYPST-GOTCHAS.md), fix it locally, commit again.

---

## The three layers explained

### Layer 1: Automated Checks (`scripts/check_typst.py`)

**Core checks (always run):**
- ✅ Compilation: `typst compile` runs on every `.typ` file
- ✅ Includes: All `#include` files actually exist
- ✅ Diagnostics: Typst's built-in error reporting

**Experimental checks (opt-in via `MATH_TRACE_TYPST_STRICT=1`):**
- ⚠️ Bold text with `/*`: Detects risky patterns (`*lean/*` → error)
- ⚠️ Comment balance: Flags mismatched `/*` and `*/` (ignores code blocks)

**Note:** Experimental checks are disabled by default. To enable locally or in CI:
```bash
MATH_TRACE_TYPST_STRICT=1 python scripts/check_typst.py
```

**When they run:**
- **Pre-commit hook** (if installed): Before you commit
- **GitHub Actions** (always): When you push to main or open a PR

**What happens:**
- Errors block the commit/merge.
- Warnings are reported but don't block.
- Each error includes a suggested fix + link to docs.

### Layer 2: Documentation (`docs/TYPST-GOTCHAS.md`)

**Content:**
- 10 common Typst pitfalls you'll encounter.
- For each: the problem, why it happens, how to fix it, and examples.

**When to read:**
- CI gave you an error and you're not sure why.
- You're writing a new `.typ` file and want to avoid common mistakes.
- You want to understand Typst's syntax quirks specific to math-trace.

**Quick jump:**
Use the **index at the top** of `TYPST-GOTCHAS.md` to find your error quickly:

```md
| CI error / symptom              | Section |
|---------------------------------|---------|
| unclosed delimiter near /* | §1 (Block comment collision) |
| file not found for #include | §4 (Missing #include files) |
```

### Layer 3: Examples (`examples/`, `templates/`)

**What they are:**
- Real `.typ` files from this repo.
- Each file has been validated by CI (so it definitely compiles).
- Each follows best practices we recommend.

**Where to find patterns:**
- `examples/membrane-dynamics/main.typ` – See real formulas, figures, references.
- `templates/simple-physics/main.typ` – See a minimal template.
- `templates/biochemistry/main.typ` – See another domain example.

**How to use them:**
1. Find a similar file to what you want to write.
2. Copy its structure.
3. Adapt formulas, figures, text for your paper.
4. Run `just paper` to build.
5. If CI complains, check `TYPST-GOTCHAS.md`.

---

## If CI fails on your PR

**Step-by-step:**

1. **Read the error** on GitHub PR (it will say "Details" under Checks).

2. **Identify the problem** from the error message:
   - Filename and line number
   - What went wrong (e.g., "unclosed delimiter")

3. **Find the solution** in `TYPST-GOTCHAS.md`:
   - Use the index table at the top.
   - Or search for the error keyword.

4. **Apply the fix** locally:
   ```bash
   # Edit the file
   vim examples/membrane-dynamics/main.typ
   
   # Test locally (if you have Typst installed)
   typst compile examples/membrane-dynamics/main.typ /tmp/test.pdf
   
   # Commit
   git add examples/membrane-dynamics/main.typ
   git commit -m "fix: ..."
   git push
   ```

5. **CI runs again** automatically; if it passes, you're done.

---

## Running checks locally (no CI wait)

### Option 1: Pre-commit hook (recommended)

One-time setup:

```bash
# Install pre-commit tool
pip install pre-commit

# Install the hook for this repo
cd /path/to/math-trace
pre-commit install

# Now, every git commit will run Typst checks
```

Usage:

```bash
$ git commit  # Pre-commit runs automatically
```

### Option 2: Manual script run

Anytime, without committing:

```bash
# Check all .typ files
python scripts/check_typst.py

# Check a specific file
python scripts/check_typst.py examples/membrane-dynamics/main.typ

# Run experimental checks too
MATH_TRACE_TYPST_STRICT=1 python scripts/check_typst.py
```

### Option 3: Typst compiler directly

If you have Typst installed (`just install-typst`):

```bash
# Compile to PDF (the real test)
typst compile examples/membrane-dynamics/main.typ /tmp/test.pdf

# Compile with diagnostics
typst compile examples/membrane-dynamics/main.typ /tmp/test.pdf --diagnostic
```

---

## Common errors at a glance

| Error | Cause | Fix |
|-------|-------|-----|
| `unclosed delimiter` | `/*` inside bold text like `*lean/*` | Use `*lean\/*` (escape) or `strong("lean/")` |
| `file not found` | Missing `#include` file | Run `python model.py` to generate it |
| Weird emphasis | Nested bold/italic | Use functions: `strong([...])` instead of `*...*` |
| Path doesn't work | Backslashes in paths | Use forward slashes: `"path/to/file"` |

**For more:** See [TYPST-GOTCHAS.md](TYPST-GOTCHAS.md).

---

## For template maintainers: Adding a new check

The linting system is designed to be easy to extend.

**To add a new check:**

1. **Write a check function** in `scripts/check_typst.py`:

   ```python
   def check_my_new_rule(paths: list[Path]) -> list[Issue]:
       """
       Check for my custom rule.
       
       Why: [explanation]
       See: docs/TYPST-GOTCHAS.md §X
       """
       issues = []
       for path in paths:
           content = path.read_text()
           # ... check content ...
           issues.append(Issue(
               path=str(path),
               line=line_num,
               level="warning",
               message="...",
               suggestion="...",
               doc_section="§X"
           ))
       return issues
   ```

2. **Add to the checklist:**

   - If it's a hard gate (blocks merge): Add to core checks.
   - If it's informational: Add to experimental checks.

3. **Document it:**

   - Add a section to `TYPST-GOTCHAS.md`.
   - Update the index table at the top.
   - Reference it in your check's `doc_section`.

4. **Test it:**

   ```bash
   python scripts/check_typst.py  # Run locally
   # or with a fixture file to test the new rule
   ```

Done! The check now runs in CI and can be used locally.

---

## Reference

- **Checker script:** `scripts/check_typst.py`
- **CI workflow:** `.github/workflows/lint-typst.yml`
- **Error guide:** `docs/TYPST-GOTCHAS.md`
- **Examples:** `examples/`, `templates/`
- **Contributing:** `CONTRIBUTING.md`

---

**Questions?** Open a GitHub issue or discussion: https://github.com/baseline0/math-trace/issues
