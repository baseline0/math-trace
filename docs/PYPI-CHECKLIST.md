# PyPI Release Checklist

Before pushing to PyPI, verify the following:

## 1. Security & Secrets Scrubbing ✅ (Automated via pre-commit)

- [ ] **No `.env` files:** pre-commit blocks `.env`, `.env.local`, `.env.*.local`
- [ ] **No hardcoded credentials:** Ruff rule `S` (bandit) catches hardcoded passwords, API keys
- [ ] **No large files:** pre-commit blocks files >500 KB
- [ ] **No private keys:** Prevents `.key`, `.pem`, `*.private` from being committed
- [ ] **Inspect dist/ manually:**
  ```bash
  uv build
  tar -tzf dist/math-trace-*.tar.gz | head -20  # Check sdist contents
  unzip -l dist/math-trace-*.whl | head -20     # Check wheel contents
  ```

## 2. Essential Metadata ✅ (All verified)

- [ ] **`pyproject.toml` valid:** TOML syntax checked by pre-commit
  - `name`: package name (must be unique on PyPI)
  - `version`: semantic versioning (e.g., `0.1.0`)
  - `description`: short one-liner
  - `authors`: with email
  - `requires-python`: minimum Python version
  - `dependencies`: all runtime dependencies listed
  - `license`: MIT, Apache-2.0, or other OSI-approved license

- [ ] **LICENSE file exists:** `/home/mark/projects/math-trace/LICENSE` (MIT)

- [ ] **README.md well-formed:**
  - Renders correctly on PyPI
  - Includes quick install instructions
  - Links to documentation
  - Shows basic usage example

## 3. Code Quality ✅ (Automated via ruff)

- [ ] **No security issues:** Ruff rule `S` (bandit) detects:
  - Hardcoded secrets
  - SQL injection risks
  - Insecure randomness
  - Use of `assert` in production code

- [ ] **No obvious bugs:** Ruff rule `B` (bugbear) detects:
  - Mutable defaults in function arguments
  - Unintended equality comparisons
  - Missing `return` statements

- [ ] **Type hints present:** Docstrings and type hints on public APIs

## 4. Version Alignment ✅ (Manual verification)

Keep versions in sync before each release:

```bash
# Check versions match
grep "version" pyproject.toml
grep "__version__" src/math_trace/__init__.py

# They should both say: 0.1.0 (or whatever version you're releasing)
```

## 5. TestPyPI Dry-Run (Recommended)

Before pushing to production PyPI:

```bash
# Build artifacts
uv build

# Set TestPyPI token (ask maintainer for credentials or use Trusted Publishers)
export PYPI_TOKEN=pypi-...

# Publish to TestPyPI
uv publish --repository testpypi

# Test installation in a fresh environment
python -m venv /tmp/test-math-trace
source /tmp/test-math-trace/bin/activate
pip install -i https://test.pypi.org/simple/ math-trace

# Verify imports work
python -c "import math_trace; print(math_trace.__version__)"

# Try CLI (if applicable)
math-trace --help
```

## 6. Release Workflow

```bash
# 1. Update versions in both files
#    - pyproject.toml line 3
#    - src/math_trace/__init__.py line 26

# 2. Commit and tag
git add pyproject.toml src/math_trace/__init__.py
git commit -m "bump: version 0.1.0 → 0.2.0"
just prep-release 0.2.0

# 3. Build artifacts (pre-commit ensures no secrets/large files)
just build-release

# 4. Publish to PyPI
just publish-release

# 5. Verify on PyPI
#    https://pypi.org/project/math-trace/
```

## 7. What Pre-Commit Validates

- ✅ `detect-private-key`: Prevents hardcoded API keys, credentials
- ✅ `check-added-large-files`: Prevents >500 KB files (catch accidental data, models)
- ✅ `check-toml`: Validates `pyproject.toml` syntax
- ✅ `prevent-direct-secrets`: Custom hook to block `.env`, `.key`, `.pem` in src/
- ✅ `check-no-env-in-dist`: Custom hook to verify no `.env` in build artifacts

## 8. What Ruff Validates

**Security (`S` rule):**
- Hardcoded passwords or API keys
- SQL injection risks
- Insecure random number generators
- Dangerous pickle/pickle usage
- Assert statements in production code

**Code Quality (`B` rule):**
- Mutable default arguments
- Comparison to None (should use `is`)
- Missing return in function
- Unreachable code

## 9. After Publishing

Once on PyPI:

- [ ] Test installation from PyPI: `pip install math-trace`
- [ ] Verify imports and CLI work
- [ ] Tag the release on GitHub: `git tag v0.2.0 && git push --tags`
- [ ] Create GitHub Release with changelog
- [ ] Announce on social media (optional)

## Notes

- **Versions are immutable:** Once `0.1.0` is published, you cannot re-upload. If there's a bug, bump to `0.1.1`.
- **Trusted Publishers:** Use GitHub OIDC instead of storing PyPI tokens in `.env`. See [PyPI Trusted Publishers docs](https://docs.pypi.org/trusted-publishers/).
- **2FA Required:** PyPI requires Two-Factor Authentication on your account.
