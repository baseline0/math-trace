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

    def _replace_macro(self, latex: str, macro: str, replacement: str) -> str:
        """Replace LaTeX macro with Typst equivalent, handling nested braces.

        Args:
            latex: LaTeX string
            macro: Macro name (e.g., 'binom', 'frac', 'sqrt')
            replacement: Replacement template (e.g., 'binom({0}, {1})', '({0})/({1})')
                        Use {0}, {1}, etc. for positional placeholders

        Returns:
            Updated string
        """
        result = []
        pattern = '\\' + macro
        i = 0

        while i < len(latex):
            if latex[i:i+len(pattern)] == pattern:
                i += len(pattern)
                # Skip optional whitespace
                while i < len(latex) and latex[i] in ' \t':
                    i += 1

                # Extract arguments (one or more)
                args = []
                while i < len(latex) and latex[i] == '{':
                    arg, i = self._extract_brace_content(latex, i)
                    args.append(arg)
                    # Skip optional whitespace
                    while i < len(latex) and latex[i] in ' \t':
                        i += 1

                if args:
                    # Replace with template if we got all needed args
                    try:
                        result.append(replacement.format(*args))
                    except IndexError:
                        # Fallback if template has wrong number of placeholders
                        result.append(pattern)
                else:
                    result.append(pattern)
            else:
                result.append(latex[i])
                i += 1

        return ''.join(result)

    def _replace_binom(self, latex: str) -> str:
        """Replace \\binom{n}{k} with binom(n, k), handling nested braces."""
        return self._replace_macro(latex, 'binom', 'binom({0}, {1})')

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

        This converter handles common LaTeX macros and symbols with brace-aware replacement.

        Args:
            latex: LaTeX string

        Returns:
            Typst-compatible string
        """
        typst = latex

        # Macro replacements (order matters for nested patterns)
        # Use brace-aware replacement for macros with arguments
        typst = self._replace_binom(typst)
        typst = self._replace_macro(typst, 'frac', '({0})/({1})')
        typst = self._replace_macro(typst, 'sqrt', 'sqrt({0})')

        # Function names: remove backslash and convert to lowercase (Typst uses plain text)
        # e.g., \sin, \cos, \log → sin, cos, log
        trig_functions = [
            'sin', 'cos', 'tan', 'cot', 'sec', 'csc',
            'arcsin', 'arccos', 'arctan',
            'sinh', 'cosh', 'tanh',
            'log', 'ln', 'exp',
        ]
        for func in trig_functions:
            typst = typst.replace('\\' + func, func)

        # Parentheses
        typst = re.sub(r'\\left\(', '(', typst)
        typst = re.sub(r'\\right\)', ')', typst)

        # Greek letters (comprehensive set)
        greek_map = {
            r'\alpha': 'α',
            r'\beta': 'β',
            r'\gamma': 'γ',
            r'\delta': 'δ',
            r'\epsilon': 'ε',
            r'\zeta': 'ζ',
            r'\eta': 'η',
            r'\theta': 'θ',
            r'\iota': 'ι',
            r'\kappa': 'κ',
            r'\lambda': 'λ',
            r'\mu': 'μ',
            r'\nu': 'ν',
            r'\xi': 'ξ',
            r'\omicron': 'ο',
            r'\pi': 'π',
            r'\rho': 'ρ',
            r'\sigma': 'σ',
            r'\tau': 'τ',
            r'\upsilon': 'υ',
            r'\phi': 'φ',
            r'\chi': 'χ',
            r'\psi': 'ψ',
            r'\omega': 'ω',
        }
        for latex_char, typst_char in greek_map.items():
            typst = typst.replace(latex_char, typst_char)

        # Operators
        typst = typst.replace(r'\cdot', '·')
        typst = typst.replace(r'\times', '×')
        typst = typst.replace(r'\div', '÷')

        # Arrows
        typst = typst.replace(r'\rightarrow', '->')
        typst = typst.replace(r'\leftarrow', '<-')
        typst = typst.replace(r'\leftrightarrow', '<->')

        # Quote multi-letter identifiers that aren't already quoted or subscripted
        # This prevents Typst from interpreting ES as E*S
        # Do this AFTER all LaTeX command replacements
        typst = self._quote_identifiers(typst)

        return typst

    def _quote_identifiers(self, typst: str) -> str:
        """Quote multi-letter identifiers and subscripts in Typst math mode.

        Converts multi-letter bare identifiers and multi-letter subscripts to quoted form.
        E.g., ES → "ES", k_{cat} → "k"_{"cat"}, but leaves E, S, E_0 unchanged.
        """
        result = []
        i = 0
        while i < len(typst):
            # Check if we're at the start of an identifier
            if typst[i].isalpha():
                # Collect the base identifier
                ident_start = i
                while i < len(typst) and typst[i].isalpha():
                    i += 1
                ident = typst[ident_start:i]

                # Check if there's a subscript
                if i < len(typst) and typst[i] == '_':
                    # Found subscript
                    i += 1  # skip the underscore
                    if i < len(typst) and typst[i] == '{':
                        # Extract subscript content
                        i += 1
                        subscript_content_start = i
                        depth = 1
                        while i < len(typst) and depth > 0:
                            if typst[i] == '{':
                                depth += 1
                            elif typst[i] == '}':
                                depth -= 1
                            i += 1
                        subscript_content = typst[subscript_content_start:i-1]

                        # Quote base if multi-letter
                        if len(ident) > 1:
                            result.append(f'"{ident}"')
                        else:
                            result.append(ident)
                        result.append('_')
                        result.append('{')

                        # Quote subscript if it's multi-letter text (not a number)
                        if subscript_content.isalpha() and len(subscript_content) > 1:
                            result.append(f'"{subscript_content}"')
                        else:
                            result.append(subscript_content)

                        result.append('}')
                    else:
                        # Single character subscript
                        result.append(ident)
                        result.append('_')
                        if i < len(typst):
                            result.append(typst[i])
                            i += 1
                elif len(ident) > 1:
                    # Multi-letter identifier without subscript
                    result.append(f'"{ident}"')
                else:
                    # Single letter
                    result.append(ident)
            else:
                result.append(typst[i])
                i += 1
        return ''.join(result)

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
