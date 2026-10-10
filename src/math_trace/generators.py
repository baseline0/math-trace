"""
Formula generators: Convert between SymPy, LaTeX, and Typst representations.

This module provides utilities for converting symbolic mathematics
(SymPy expressions) to publication-ready formats (LaTeX, Typst).
"""

from __future__ import annotations

import re

import sympy as sp

# LaTeX operators and symbols with their Typst equivalents.
SYMBOL_MAP: dict[str, str] = {
    "sum": "sum",
    "prod": "product",
    "int": "integral",
    "partial": "partial",
    "nabla": "nabla",
    "infty": "infinity",
    "hbar": "ℏ",
    "langle": "⟨",
    "rangle": "⟩",
    "in": "∈",
    "iff": "⇔",
    "approx": "≈",
    "leq": "<=",
    "geq": ">=",
    "neq": "!=",
    "quad": " ",
}

# Differential fractions such as \frac{dS}{dt} or \frac{\partial^2\psi}{\partial x^2}.
# Each side is d, an optional order (d^2), a variable (x or \psi), and an optional power.
_DIFFERENTIAL_OPERAND: str = r"d(?:\^\{?(\d+)\}?)?(\\[A-Za-z]+|[A-Za-z])(\^\{?\d+\}?)?"
_DIFFERENTIAL_FRAC = re.compile(rf"\\frac\{{{_DIFFERENTIAL_OPERAND}\}}\{{{_DIFFERENTIAL_OPERAND}\}}")

# Greek letters and ℏ render as symbols, but Typst reads "Eψ" as one unknown name.
# A space between a letter and an adjacent Greek symbol keeps them separate.
_GREEK_CHARS: str = "Α-Ωα-ωℏ"
_SPACE_BETWEEN_LETTER_AND_GREEK = re.compile(
    rf"(?<=[A-Za-z])(?=[{_GREEK_CHARS}])|(?<=[{_GREEK_CHARS}])(?=[A-Za-z{_GREEK_CHARS}])"
)


def _differential_term(order: str | None, variable: str, power: str | None) -> str:
    """Build one differential term, e.g. ("2", "\\psi", None) -> "d^2 \\psi"."""
    order_part = f"^{order}" if order else ""
    return f"d{order_part} {variable}{power or ''}"


# Names Typst resolves as functions or built-in symbols. They must stay unquoted:
# "log"(x) is a string, and "integral" is not the integral symbol.
TYPST_BARE_NAMES: frozenset[str] = frozenset(
    {
        "sin",
        "cos",
        "tan",
        "cot",
        "sec",
        "csc",
        "arcsin",
        "arccos",
        "arctan",
        "sinh",
        "cosh",
        "tanh",
        "log",
        "sum",
        "product",
        "integral",
        "partial",
        "nabla",
        "infinity",
        "ln",
        "exp",
        "sqrt",
        "hat",
        "bar",
        "dot",
        "tilde",
        "vec",
        "bold",
        "upright",
    }
)


class SymPyToTypst:
    """Convert SymPy expressions to Typst math notation."""

    def __init__(self) -> None:
        """Initialize the converter."""
        self.latex_to_typst_map: dict[str, str] = {
            r"\frac": "frac",  # Typst uses frac() function
            r"\left(": "(",
            r"\right)": ")",
            r"\cdot": "*",
            r"\times": "*",
            r"\alpha": "alpha",
            r"\beta": "beta",
            r"\gamma": "gamma",
        }

    def _extract_brace_content(self, s: str, start: int) -> tuple[str, int]:
        """Extract balanced brace content starting from position start.

        Returns tuple of (content, end_position) where end_position is after closing brace.
        """
        if start >= len(s) or s[start] != "{":
            return "", start

        depth = 0
        i = start
        while i < len(s):
            if s[i] == "{":
                depth += 1
            elif s[i] == "}":
                depth -= 1
                if depth == 0:
                    return s[start + 1 : i], i + 1
            i += 1
        return "", len(s)

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
        pattern = "\\" + macro
        i = 0

        while i < len(latex):
            if latex[i : i + len(pattern)] == pattern:
                i += len(pattern)
                # Skip optional whitespace
                while i < len(latex) and latex[i] in " \t":
                    i += 1

                # Extract arguments (one or more)
                args = []
                while i < len(latex) and latex[i] == "{":
                    arg, i = self._extract_brace_content(latex, i)
                    args.append(arg)
                    # Skip optional whitespace
                    while i < len(latex) and latex[i] in " \t":
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

        return "".join(result)

    @staticmethod
    def _differential_fraction(match: re.Match[str]) -> str:
        """Render a differential fraction as (d x)/(d y), keeping order and power.

        Groups 1-3 are the numerator (order, variable, power); groups 4-6 the denominator.
        """
        num = _differential_term(match.group(1), match.group(2), match.group(3))
        den = _differential_term(match.group(4), match.group(5), match.group(6))
        return f"({num})/({den})"

    def _replace_binom(self, latex: str) -> str:
        """Replace \\binom{n}{k} with binom(n, k), handling nested braces."""
        return self._replace_macro(latex, "binom", "binom({0}, {1})")

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
        typst = _DIFFERENTIAL_FRAC.sub(self._differential_fraction, typst)
        typst = self._replace_macro(typst, "frac", "({0})/({1})")
        typst = self._replace_macro(typst, "sqrt", "sqrt({0})")

        # Accents and styling: \hat{y} → hat(y), \mathbf{h} → bold(h), \text{x} → "x"
        for accent in ("hat", "bar", "dot", "tilde", "vec"):
            typst = self._replace_macro(typst, accent, accent + "({0})")
        typst = self._replace_macro(typst, "mathbf", "bold({0})")
        typst = self._replace_macro(typst, "text", '"{0}"')

        # Function names: remove backslash and convert to lowercase (Typst uses plain text)
        # e.g., \sin, \cos, \log → sin, cos, log
        trig_functions = [
            "sin",
            "cos",
            "tan",
            "cot",
            "sec",
            "csc",
            "arcsin",
            "arccos",
            "arctan",
            "sinh",
            "cosh",
            "tanh",
            "log",
            "ln",
            "exp",
        ]
        for func in trig_functions:
            typst = typst.replace("\\" + func, func)

        # Parentheses
        typst = re.sub(r"\\left\(", "(", typst)
        typst = re.sub(r"\\right\)", ")", typst)

        # Greek letters (comprehensive set)
        greek_map = {
            r"\alpha": "α",
            r"\beta": "β",
            r"\gamma": "γ",
            r"\delta": "δ",
            r"\epsilon": "ε",
            r"\zeta": "ζ",
            r"\eta": "η",
            r"\theta": "θ",
            r"\iota": "ι",
            r"\kappa": "κ",
            r"\lambda": "λ",
            r"\mu": "μ",
            r"\nu": "ν",
            r"\xi": "ξ",
            r"\omicron": "ο",
            r"\pi": "π",
            r"\rho": "ρ",
            r"\sigma": "σ",
            r"\tau": "τ",
            r"\upsilon": "υ",
            r"\phi": "φ",
            r"\chi": "χ",
            r"\psi": "ψ",
            r"\omega": "ω",
            r"\Gamma": "Γ",
            r"\Delta": "Δ",
            r"\Theta": "Θ",
            r"\Lambda": "Λ",
            r"\Xi": "Ξ",
            r"\Pi": "Π",
            r"\Sigma": "Σ",
            r"\Upsilon": "Υ",
            r"\Phi": "Φ",
            r"\Psi": "Ψ",
            r"\Omega": "Ω",
        }
        for latex_char, typst_char in greek_map.items():
            typst = typst.replace(latex_char, typst_char)

        # Operators and symbols. Longest names first, with a word boundary, so that
        # \in does not rewrite the start of \int.
        for name in sorted(SYMBOL_MAP, key=len, reverse=True):
            typst = re.sub(rf"\\{name}(?![A-Za-z])", lambda _m, n=name: SYMBOL_MAP[n], typst)
        typst = re.sub(r"\\(left|right)(?![A-Za-z])", "", typst)
        typst = _SPACE_BETWEEN_LETTER_AND_GREEK.sub(" ", typst)

        # Operators
        typst = typst.replace(r"\cdot", "·")
        typst = typst.replace(r"\times", "×")
        typst = typst.replace(r"\div", "÷")

        # Arrows
        typst = typst.replace(r"\rightarrow", "->")
        typst = typst.replace(r"\leftarrow", "<-")
        typst = typst.replace(r"\leftrightarrow", "<->")

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
            # Copy string literals (from \text{...}) through unchanged
            if typst[i] == '"':
                end = typst.find('"', i + 1)
                end = len(typst) if end == -1 else end + 1
                result.append(typst[i:end])
                i = end
                continue
            # Check if we're at the start of an identifier
            if typst[i].isalpha():
                # Collect the base identifier
                ident_start = i
                while i < len(typst) and typst[i].isalpha():
                    i += 1
                ident = typst[ident_start:i]

                # Check if there's a subscript
                if i < len(typst) and typst[i] == "_":
                    # Found subscript
                    i += 1  # skip the underscore
                    if i < len(typst) and typst[i] == "{":
                        # Extract subscript content
                        i += 1
                        subscript_content_start = i
                        depth = 1
                        while i < len(typst) and depth > 0:
                            if typst[i] == "{":
                                depth += 1
                            elif typst[i] == "}":
                                depth -= 1
                            i += 1
                        subscript_content = typst[subscript_content_start : i - 1]

                        # Quote base if multi-letter
                        if len(ident) > 1 and ident not in TYPST_BARE_NAMES:
                            result.append(f'"{ident}"')
                        else:
                            result.append(ident)
                        result.append("_")
                        result.append("{")

                        # Quote subscript if it's multi-letter text (not a number)
                        if subscript_content.isalpha() and len(subscript_content) > 1:
                            result.append(f'"{subscript_content}"')
                        else:
                            result.append(subscript_content)

                        result.append("}")
                    else:
                        # Single character subscript
                        result.append(ident)
                        result.append("_")
                        if i < len(typst):
                            result.append(typst[i])
                            i += 1
                elif len(ident) > 1 and ident not in TYPST_BARE_NAMES:
                    # Multi-letter identifier without subscript
                    result.append(f'"{ident}"')
                else:
                    # Single letter
                    result.append(ident)
            else:
                result.append(typst[i])
                i += 1
        return "".join(result)

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


if __name__ == "__main__":
    # Quick test
    converter = SymPyToTypst()

    # Test basic conversion
    x = sp.Symbol("x")
    expr = x**2 + 2 * x + 1
    typst = converter.convert(expr)
    print(f"Expression: {expr}")
    print(f"LaTeX: {sp.latex(expr)}")
    print(f"Typst: {typst}")
