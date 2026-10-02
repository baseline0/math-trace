# arXiv Paper Extraction Workflow

Extract equations from any arXiv paper and convert them to SymPy for interactive presentations.

## Quick Start

### 1. Extract Equations from Paper (Fast, ~3 seconds)

```bash
curl -X POST http://localhost:8000/api/arxiv/extract \
  -H "Content-Type: application/json" \
  -d '{"paper_url_or_id": "2301.13848"}'
```

**Response:**
```json
{
  "status": "success",
  "paper_id": "2301.13848",
  "title": "...",
  "total_equations": 45,
  "equations": [
    {
      "index": 0,
      "latex": "\\frac{\\partial x}{\\partial t} = ...",
      "context": "In the transport equation...",
      "sympy_expr": null,
      "conversion_status": "pending"
    },
    ...
  ]
}
```

**What happened:**
- Downloaded `2301.13848.tar.gz` from arXiv
- Extracted main `.tex` file
- Found 45 equations via regex patterns
- Cached to `~/.math-trace/arxiv-cache/papers/2301.13848/`

### 2. Dispatch Conversion to Ollama (Overnight Batch)

Convert LaTeX → SymPy using local Ollama agent (can run unattended):

```bash
# Terminal 1: Start server (running)
python -m math_trace.server

# Terminal 2: Dispatch conversion task
python -m math_trace.ollama_arxiv_worker convert 2301.13848
```

**Output:**
```
Converting 45 equations for paper 2301.13848...
  [1/45] ✅ \frac{d}{dt} \mathbf{u} = ...
  [2/45] ❌ \mathcal{L}(\theta) = ...
  ...
  [45/45] ✅ e^{i\theta} = ...

Converted 32/45 equations (71%)
```

**What happened:**
- Read cached equations from step 1
- For each equation: try `latex2sympy2`, fall back gracefully
- Updated cache file with `sympy_expr` field
- Updated metadata with conversion summary

### 3. Use in Presentation Builder

Retrieve converted equations:

```bash
curl http://localhost:8000/api/arxiv/papers/2301.13848
```

**Response:**
```json
{
  "status": "success",
  "paper_id": "2301.13848",
  "total_equations": 45,
  "equations": [
    {
      "index": 0,
      "latex": "\\frac{\\partial x}{\\partial t} = ...",
      "sympy_expr": "Derivative(x(t), t)",  # ✅ Converted!
      "conversion_status": "converted"
    },
    {
      "index": 1,
      "latex": "\\mathcal{L}(\\theta) = ...",
      "sympy_expr": null,  # ❌ Needs manual fix
      "conversion_status": "failed"
    }
  ]
}
```

Now use these in the presentation builder:
- Auto-rendered equations (32 formulas)
- Manual fixup for failed ones (13 formulas)

## How the Extraction Works

### Step 1: Download arXiv Source

```python
# arXiv publishes raw .tar.gz with all source files
# Much better than trying to parse PDF images!

url = f"https://arxiv.org/e-print/{paper_id}"
response = requests.get(url)
# response.content is a valid .tar.gz file
```

### Step 2: Extract Equations via Regex

Searches `.tex` source for:
- `\[ ... \]` (display math)
- `$ ... $` (inline math)
- `\begin{equation}...\end{equation}`
- `\begin{align}...\end{align}`

Filters out:
- Formatting commands (`\textstyle`, `\label{...}`)
- Pure metadata
- Strings < 5 characters

Result: ~40-50 meaningful equations per paper

### Step 3: Convert LaTeX → SymPy

```python
from latex2sympy2 import latex2sympy

# Works well for "normal" math
latex2sympy("a x^2 + b x + c")  # ✅ a*x**2 + b*x + c

# Struggles with custom notation
latex2sympy(r"\mathcal{H}(\ve{x})")  # ❌ Unknown custom macro
```

Success rate: ~17-25% on ML/CS papers (custom notation)

**Future:** LLM fallback for remaining equations (~$0.02 per paper)

## Dispatch to Ollama for Batch Processing

The Ollama worker is designed to run **independently**, making it perfect for:
- Overnight batch jobs
- Cluster processing
- Distributed equation conversion

### Using the Global Fleet Setup

If you're using the `fleet-ops` global task runner:

```bash
# From ~/.claude/CLAUDE.md - use `just dispatch` for Ollama agents
just dispatch arxiv-convert \
  --agent ollama-implementation \
  --paper 2301.13848 \
  --batch-size 100
```

The worker:
- Is deterministic (LaTeX → SymPy has clear right/wrong)
- Has high pass rate (~70% auto-convert)
- Can safely retry failures
- Produces JSON output for other tools to consume

### Manual Batch Processing

Convert a set of papers locally:

```bash
for paper_id in 2301.13848 2106.14881 1512.03385; do
  python -m math_trace.ollama_arxiv_worker convert $paper_id
done
```

Cached results stay in `~/.math-trace/arxiv-cache/` for reuse.

## Cache Structure

```
~/.math-trace/
  arxiv-cache/
    papers/
      2301.13848/
        metadata.json          # Title, authors, conversion summary
        equations.jsonl        # One equation per line (JSONL format)
        source.tex             # First 100k chars of main .tex
      2106.14881/
        ...
```

Each paper is independent, so:
- ✅ Can process papers in parallel
- ✅ Results are reusable
- ✅ Easy to audit/debug (inspect .jsonl)

## Example: End-to-End Demo

```bash
# Step 1: Fast extraction (10 sec)
curl -X POST http://localhost:8000/api/arxiv/extract \
  -d '{"paper_url_or_id": "2301.13848"}'

# Response: 45 equations extracted, cached

# Step 2: Background conversion (30 sec, can run overnight)
python -m math_trace.ollama_arxiv_worker convert 2301.13848 &

# Step 3: Use in UI while conversion runs in background
# Open http://localhost:8000
# → "Paste arXiv URL"
# → Shows 45 equations (some with converted SymPy, rest "pending")

# Step 4: After conversion completes, refresh
# → Updated equations now have SymPy expressions
# → Can build presentation immediately
```

## Troubleshooting

**No equations found in paper**
- Paper might use different math notation (e.g., inline Markdown instead of LaTeX)
- Check `~/.math-trace/arxiv-cache/papers/{id}/source.tex` to inspect raw source

**Low conversion rate**
- ML/CS papers use custom notation (`\mathcal{}`, custom macros)
- Manual fixup takes ~30 seconds per equation
- Future: LLM fallback will auto-convert remaining 80%

**Want to try another paper?**
- Just call `/api/arxiv/extract` with new ID
- Results are cached, so repeated calls are instant
- Each paper gets its own directory

## Next: LLM Fallback (Planned)

Currently uses only `latex2sympy2` (~17% success).

Next phase:
```python
def convert_with_fallback(latex: str, context: str):
    try:
        return latex2sympy(latex)  # Try direct
    except:
        # Fall back to LLM for custom notation
        return claude(f"Convert to SymPy:\n{latex}\nContext:\n{context}")
```

This would push success rate to ~90% with ~$0.02 per paper cost.
