# ADR-001: Choose Typst Over LaTeX for Paper Formatting

## Status
Accepted

## Context

We need a formatting system for publishing mathematical papers that:
1. Integrates cleanly with code-generated formulas
2. Supports modern markup (like Markdown)
3. Enables automatic formula insertion from Python/SymPy
4. Compiles quickly and reliably
5. Produces high-quality PDFs

Options evaluated:
- **LaTeX (pdflatex, LuaLaTeX)**: Mature, widely used, but complex ecosystem and slow iteration
- **Typst**: Modern, simpler syntax, built for code generation, excellent PDF output
- **Markdown + Pandoc**: Simpler but limited mathematical control

## Decision

Use **Typst** as the primary formatting engine for all papers in math-trace.

## Rationale

1. **Code Generation**: Typst's simpler syntax makes it easier to generate formulas programmatically from Python/SymPy
2. **Faster Iteration**: Typst compiles in milliseconds; LaTeX takes seconds per compile
3. **Modern Syntax**: Typst reads like markup (similar to YAML/JSON), not a macro language
4. **Integrated Package Management**: Typst's package ecosystem is curated and reliable
5. **PDF Quality**: Produces output comparable to LaTeX with better defaults
6. **Mathematics Support**: Native support for mathematical expressions via standard LaTeX-like syntax

## Consequences

### Positive
- Faster paper development cycle (sub-second compile times)
- Easier onboarding for contributors unfamiliar with LaTeX
- Generated formulas integrate naturally into Typst documents
- Strong community and growing ecosystem

### Negative
- Smaller ecosystem than LaTeX (fewer specialized packages)
- Some users may be more familiar with LaTeX
- Newer tool (stability still improving)

## Alternatives Considered

### LaTeX
```latex
% Complex to generate programmatically
\frac{k n_a (n_a - 1)}{2}
\begin{theorem}[Monotonicity]
  Let $k > 0$...
\end{theorem}
```

### Typst
```typst
// Clean, code-friendly syntax
$ (k n_a (n_a - 1)) / 2 $
#theorem[Monotonicity][
  Let $k > 0$...
]
```

## Implementation

1. Install Typst: `cargo install typst-cli`
2. Use Typst for all `.typ` documents
3. Generate formulas as Typst imports via `#include`
4. Provide Justfile recipes for compilation

## References

- [Typst Documentation](https://typst.app/docs/)
- [Typst GitHub](https://github.com/typst/typst)
- [Comparison: Typst vs LaTeX](https://typst.app/docs/reference/math/align/)
