# Typst Syntax Gotchas and Best Practices

When writing `.typ` files for math-trace, watch out for these common Typst syntax issues.

## 1. Block Comments: `/* */` Syntax Collision

**Problem:** In Typst (like C, C++, JavaScript), `/*` starts a block comment. If you write `*lean/*` in bold text, Typst interprets `/*` as the start of a comment, treating everything after it as a comment until it finds `*/`.

**Error Message:**
```
error: unclosed delimiter
  ┌─ main.typ:78:1
  │
78 │ - *lean/* — Description
  │   ^^^^^^ block comment starts here
  │   └─ error: this block comment is never closed
```

**Solutions:**

### ✅ Option 1: Escape the slash (Recommended)
```typst
- *lean\/* — Formal development
```
The backslash tells Typst to treat `/` as a literal character, not part of a comment.

### ✅ Option 2: Use strong() function
```typst
- #strong[lean/] — Formal development
```
Bypasses the `*` markup and uses Typst's explicit strong function.

### ✅ Option 3: Use code formatting
```typst
- `lean/` — Formal development
```
Backticks format as inline code instead of bold.

### ❌ Don't do this:
```typst
- *lean/* — WRONG! Will cause unclosed comment error
```

---

## 2. Nested Emphasis/Bold Issues

**Problem:** Bold and italic cannot nest directly in Typst:

```typst
*this is bold with **extra bold** inside*  // ❌ Won't work
```

**Solution:** Use functions instead:

```typst
#strong[this is bold with #emph[emphasis] inside]  // ✅ Works
```

---

## 3. Backslash in File Paths

**Problem:** Backslashes in Windows paths are interpreted as escape sequences:

```typst
#include "examples\membrane-dynamics\main.typ"  // ❌ Broken on all platforms
```

**Solution:** Always use forward slashes (works on all platforms):

```typst
#include "examples/membrane-dynamics/main.typ"  // ✅ Works everywhere
```

---

## 4. Missing #include Files

**Problem:** If you try to include a file that doesn't exist, you get a cryptic error:

```typst
#include "generated/missing.typ"  // ❌ File doesn't exist
```

**Error:**
```
error: file not found (searched at [...], [...])
```

**Solution:**
1. Check that the file actually exists
2. Verify the path is relative to the current `.typ` file
3. Use forward slashes only

```typst
#include "generated/formulas.typ"  // ✅ Verify file exists
```

**Debug:** Before referencing a file, generate it:
```bash
python model.py  # Creates generated/formulas.typ
```

---

## 5. Special Characters in Text

**Problem:** Some characters have special meaning in Typst and need escaping:

- `#` — starts code expression
- `$` — starts math mode
- `_` — subscript in math mode
- `*` — bold
- `/` — can start comments in some contexts
- `\` — escape character

**Examples:**

```typst
// ❌ Wrong - # starts code
This costs #50 per item

// ✅ Correct - escape or use spaces
This costs "$50" per item
This costs \#50 per item
```

```typst
// ❌ Wrong - _ in text mode
The category_name variable

// ✅ Correct
The `category_name` variable
```

---

## 6. Math Mode vs Text Mode

**Problem:** Forgetting to exit math mode leaves trailing content as math:

```typst
The equation is $x + y$ and we can solve it.
// Everything after the closing $ is treated as text (correct)

The equation is $x + y and we can solve it.
// ❌ ERROR - unclosed math mode
```

**Solution:** Always close math mode with `$`:

```typst
The equation is $x + y$. We can solve it.  // ✅
```

---

## 7. Spacing Around Functions

**Problem:** Typst is whitespace-sensitive in some contexts:

```typst
#let x = 5  // ✅ Good
#let x=5    // ⚠️ May work but less readable
#letx = 5   // ❌ Wrong - "letx" is unknown

#set text(size: 12pt)  // ✅ Good
#set text (size: 12pt) // ⚠️ Space before parens is weird but works
```

**Best practice:** Keep spaces consistent with the examples in docs.

---

## 8. Import vs Include

**Problem:** Confusing `#import` (load Typst modules) with `#include` (insert file contents):

```typst
// Use #include for generated files (formulas.typ)
#include "generated/formulas.typ"

// Use #import for Typst library modules
#import "@preview/package-name:version": *
```

---

## 9. Unclosed Delimiters

**Problem:** Missing closing braces, brackets, or parentheses:

```typst
#let x = [
  This is a block
  // ❌ Missing ]

#set text(size: 12pt
// ❌ Missing )
```

**Solution:** Match all delimiters:

```typst
#let x = [
  This is a block
]  // ✅

#set text(size: 12pt)  // ✅
```

---

## 10. Raw Strings with Backticks

**Problem:** Backticks inside backticks don't work:

```typst
The function `call()` has a `backtick` inside.
// Use backticks to show code:
```

**Solution:** Either use different formatting or escape:

```typst
The function `call()` takes an argument.
The \`backtick\` character is special.

The function #text(font: "monospace", `call()`) has backticks.
```

---

## Typst Syntax Checking

### Automated Checks (CI/CD)

The `.github/workflows/lint-typst.yml` workflow automatically checks:

1. **Syntax validation** — `typst compile` with diagnostic mode
2. **Comment balance** — Matching `/*` and `*/`
3. **Common issues** — `/*` inside bold text
4. **Import verification** — All `#include` files exist

**To run locally:**

```bash
# Install Typst
just install-typst

# Check syntax
typst compile examples/membrane-dynamics/main.typ /tmp/test.pdf

# Check a single file
typst compile templates/simple-physics/main.typ /tmp/test.pdf
```

### Manual Checks

Before committing `.typ` files:

```bash
# 1. Look for unclosed comments
grep -n '/\*' examples/*/main.typ | wc -l
grep -n '\*/' examples/*/main.typ | wc -l
# These should match

# 2. Look for /* inside bold
grep '\*[^*]*/\*' examples/*/main.typ
# Should find nothing (or only escaped: \*/)

# 3. Try to compile
typst compile examples/membrane-dynamics/main.typ /tmp/out.pdf
```

---

## Common Patterns (Examples)

### ✅ Directory reference in text
```typst
Files in the *lean\/* directory are formal proofs.
```

### ✅ File path in text
```typst
See `generated/formulas.typ` for the generated equations.
```

### ✅ Bold text with punctuation
```typst
The key insight is *very important*. You must understand it.
```

### ✅ Escaped special characters
```typst
The variable is `n_a`, not n_a (the underscore matters).
Use \#hashtag to show the literal # character.
```

### ✅ Math with operators
```typst
The rate is $r = k n_a (n_a - 1) / 2$ for the reaction.
```

### ✅ Multiple paragraphs with code
```typst
== Code Structure

Here's the main file:

```python
def formula(x):
    return x ** 2
```

The function above is defined in `model.py`.
```

---

## When You Get an Error

**Error: "unclosed delimiter"**
- Check for unmatched `/* */`, `#{ }`, `[ ]`, or `( )`
- Look for `/*` inside bold text: use `\/*` instead

**Error: "file not found"**
- Verify the file exists: `ls generated/formulas.typ`
- Check the path uses forward slashes: `generated/formulas.typ` not `generated\formulas.typ`
- Make sure you ran `python model.py` first

**Error: "unknown function"**
- Check for typos: `#let` not `#lets`, `#set` not `#sets`
- Verify parentheses/brackets: `#text(size: 12pt)` not `#text size: 12pt`

**Error: "expected X, found Y"**
- Usually a missing delimiter or unclosed string/comment
- Check the line and surrounding context
- Look for unescaped special characters

---

## Best Practices for math-trace

1. **Always escape `/*` inside bold:** Use `\/*` not `/*`
2. **Use forward slashes in paths:** Always `generated/formulas.typ`, never backslashes
3. **Verify includes exist:** Run `python model.py` before building
4. **Test locally first:** `typst compile main.typ test.pdf` before committing
5. **Review CI/CD output:** GitHub Actions will catch syntax errors
6. **Use functions for complex formatting:** `#strong[...]` instead of nested `*...*`

---

## See Also

- [Typst Documentation](https://typst.app/docs/)
- [GitHub: typst/typst](https://github.com/typst/typst)
- [math-trace README](../README.md)
- [build_paper.py](../examples/membrane-dynamics/build_paper.py) — How formulas are generated

---

**Last Updated:** 2026-09-18
