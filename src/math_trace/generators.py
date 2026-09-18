"""
Formula generators: Convert between SymPy, LaTeX, and Typst representations.

This module provides utilities for converting symbolic mathematics
(SymPy expressions) to publication-ready formats (LaTeX, Typst).
"""

import re
from typing import Dict, Tuple

import sympy as sp


class SymPyToTypst:
    """Convert SymPy expressions to Typst math notation."""

    def __init__(self) -> None:
        """Initialize the converter."""
        self.latex_to_typst_map: Dict[str, str] = {
            r'\frac': 'frac',  # Typst uses frac() function
            r'\left(': '(',
            r'\right)': ')',
            r'\cdot': '*',
            r'\times': '*',
            r'\alpha': 'alpha',
            r'\beta': 'beta',
            r'\gamma': 'gamma',
        }

    def _extract_brace_content(self, s: str, start: int) -> Tuple[str, int]:
        """Extract balanced brace content starting from position start.

        Returns tuple of (content, end_position) where end_position is after closing brace.
        """
        if start >= len(s) or s[start] != '{':
            return '', start

        depth = 0
        i = start
        while i < len(s):
            if s[i] == '{':
                depth += 1
            elif s[i] == '}':
                depth -= 1
                if depth == 0:
                    return s[start + 1:i], i + 1
            i += 1
        return '', len(s)

    def _replace_binom(self, latex: str) -> str:
        """Replace \\binom{n}{k} with binom(n, k), handling nested braces."""
        result = []
        i = 0
        while i < len(latex):
            if latex[i:i+6] == r'\binom':
                i += 6
                # Skip optional whitespace
                while i < len(latex) and latex[i] in ' \t':
                    i += 1
                # Extract first arg
                if i < len(latex) and latex[i] == '{':
                    arg1, i = self._extract_brace_content(latex, i)
                    # Skip optional whitespace
                    while i < len(latex) and latex[i] in ' \t':
                        i += 1
                    # Extract second arg
                    if i < len(latex) and latex[i] == '{':
                        arg2, i = self._extract_brace_content(latex, i)
                        result.append(f'binom({arg1}, {arg2})')
                    else:
                        result.append(r'\binom')
                else:
                    result.append(r'\binom')
            else:
                result.append(latex[i])
                i += 1
        return ''.join(result)

    def convert(self, expr: sp.Expr) -> str:
        """
        Convert SymPy expression to Typst notation.

        Args:
            expr: SymPy expression

        Returns:
            Typst-formatted string
        """
        # First convert to LaTeX
        latex = sp.latex(expr)

        # Then apply LaTeX → Typst conversions
        typst = self._latex_to_typst(latex)

        return typst

    def _latex_to_typst(self, latex: str) -> str:
        """
        Convert LaTeX string to Typst notation.

        This is a simple regex-based converter for common patterns.
        More complex conversions may require external tools like tex2typst.

        Args:
            latex: LaTeX string

        Returns:
            Typst-compatible string
        """
        typst = latex

        # Common substitutions (order matters for nested patterns)
        # \binom{n}{k} → binom(n, k); handles nested braces like n_{a}
        typst = self._replace_binom(typst)

        # \frac{a}{b} → (a)/(b) or a/b
        typst = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', typst)

        # Parentheses
        typst = re.sub(r'\\left\(', '(', typst)
        typst = re.sub(r'\\right\)', ')', typst)

        # Greek letters (simplified)
        typst = typst.replace(r'\alpha', 'α')
        typst = typst.replace(r'\beta', 'β')
        typst = typst.replace(r'\gamma', 'γ')
        typst = typst.replace(r'\delta', 'δ')
        typst = typst.replace(r'\epsilon', 'ε')
        typst = typst.replace(r'\lambda', 'λ')
        typst = typst.replace(r'\mu', 'μ')
        typst = typst.replace(r'\pi', 'π')

        # Operators
        typst = typst.replace(r'\cdot', '·')
        typst = typst.replace(r'\times', '×')
        typst = typst.replace(r'\div', '÷')

        # Powers and subscripts are already preserved in SymPy LaTeX output
        # (^ for superscript, _ for subscript)

        return typst

    def binomial_to_readable(self, n: sp.Symbol, k: int) -> str:
        """
        Convert binomial coefficient to readable form.

        C(n, k) = n! / (k! * (n-k)!)

        Args:
            n: SymPy variable
            k: Integer k

        Returns:
            Human-readable string
        """
        return f"C({n}, {k})"


class TypstEnvironmentBuilder:
    """Build Typst theorem/proof environments with proper formatting."""

    @staticmethod
    def theorem(
        name: str,
        title: str,
        statement: str,
        label: str | None = None,
    ) -> str:
        """
        Generate a Typst theorem environment.

        Args:
            name: Internal identifier
            title: Theorem title
            statement: Mathematical statement
            label: Optional label for cross-reference

        Returns:
            Typst theorem block
        """
        label_str = f"\n  label: <{label}>" if label else ""

        return f"""{name}: [#strong[{title}]][
  {statement}
]{label_str}
"""

    @staticmethod
    def proof(body: str) -> str:
        """
        Generate a Typst proof environment.

        Args:
            body: Proof text and equations

        Returns:
            Typst proof block
        """
        return f"""#proof[
  {body}
  #qed
]
"""


if __name__ == '__main__':
    # Quick test
    converter = SymPyToTypst()

    # Test basic conversion
    x = sp.Symbol('x')
    expr = x**2 + 2*x + 1
    typst = converter.convert(expr)
    print(f"Expression: {expr}")
    print(f"LaTeX: {sp.latex(expr)}")
    print(f"Typst: {typst}")
