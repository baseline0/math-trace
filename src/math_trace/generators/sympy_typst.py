"""Convert SymPy expressions and LaTeX to Typst math notation."""

from __future__ import annotations

import re

import sympy as sp

from ._latex_to_typst import (
    _DIFFERENTIAL_FRAC,
    _SPACE_BETWEEN_LETTER_AND_GREEK,
    SYMBOL_MAP,
    TYPST_BARE_NAMES,
    differential_fraction,
    extract_brace_content,
    is_differential,
    replace_macro,
    replace_root_index,
    unwrap_function_arguments,
    upright_or_operator,
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
        """Extract balanced brace content starting from position start."""
        return extract_brace_content(s, start)

    def _replace_macro(self, latex: str, macro: str, replacement: str) -> str:
        """Replace LaTeX macro with Typst equivalent, handling nested braces."""
        return replace_macro(latex, macro, replacement)

    def _replace_root_index(self, latex: str) -> str:
        """Replace \\sqrt[n]{x} with root(n, x)."""
        return replace_root_index(latex)

    @staticmethod
    def _upright_or_operator(match: re.Match[str]) -> str:
        return upright_or_operator(match)

    def _unwrap_function_arguments(self, typst: str, names: list[str]) -> str:
        return unwrap_function_arguments(typst, names)

    @staticmethod
    def _differential_fraction(match: re.Match[str]) -> str:
        return differential_fraction(match)

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
        latex = sp.latex(expr)
        return self._latex_to_typst(latex)

    def _latex_to_typst(self, latex: str) -> str:
        """Convert LaTeX string to Typst notation."""
        typst = latex

        typst = self._replace_binom(typst)
        typst = self._replace_root_index(typst)
        typst = _DIFFERENTIAL_FRAC.sub(self._differential_fraction, typst)
        typst = self._replace_macro(typst, "frac", "({0})/({1})")
        typst = self._replace_macro(typst, "sqrt", "sqrt({0})")

        for accent in ("hat", "bar", "dot", "tilde", "vec"):
            typst = self._replace_macro(typst, accent, accent + "({0})")
        typst = self._replace_macro(typst, "mathbf", "bold({0})")
        typst = self._replace_macro(typst, "text", '"{0}"')

        typst = re.sub(r"\\operatorname\s*\{([A-Za-z]+)\}", r'op("\1")', typst)
        typst = re.sub(r"\\mathrm\s*\{([A-Za-z]+)\}", self._upright_or_operator, typst)

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

        typst = re.sub(r"\\left\(", "(", typst)
        typst = re.sub(r"\\right\)", ")", typst)
        typst = self._unwrap_function_arguments(typst, trig_functions)

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

        for name in sorted(SYMBOL_MAP, key=len, reverse=True):
            replacement = SYMBOL_MAP[name]
            typst = re.sub(rf"\\{name}(?![A-Za-z])", lambda _m: replacement, typst)
        typst = re.sub(r"\\(left|right)(?![A-Za-z])", "", typst)
        typst = _SPACE_BETWEEN_LETTER_AND_GREEK.sub(" ", typst)

        typst = typst.replace(r"\cdot", "·")
        typst = typst.replace(r"\times", "×")
        typst = typst.replace(r"\div", "÷")
        typst = typst.replace(r"\rightarrow", "->")
        typst = typst.replace(r"\leftarrow", "<-")
        typst = typst.replace(r"\leftrightarrow", "<->")

        typst = self._quote_identifiers(typst)
        typst = self._unwrap_scripts(typst)
        typst = re.sub(r"\{([a-z]+\([^{}]*\))\}", r"\1", typst)
        typst = self._unwrap_remaining_groups(typst)

        return typst

    def _unwrap_remaining_groups(self, typst: str) -> str:
        """Drop bare LaTeX grouping braces that reach the end of conversion."""
        parts: list[str] = []
        i = 0
        while (start := typst.find("{", i)) != -1:
            parts.append(typst[i:start])
            content, end = extract_brace_content(typst, start)
            if end == start:
                break
            content = content.strip()
            parts.append(content if re.fullmatch(r"[A-Za-z0-9]", content) else f"({content})")
            i = end
        parts.append(typst[i:])
        return "".join(parts)

    def _unwrap_scripts(self, typst: str) -> str:
        """Render LaTeX script braces the way Typst reads them."""
        pattern = re.compile(r"[_^]\{")
        parts: list[str] = []
        i = 0
        while match := pattern.search(typst, i):
            parts.append(typst[i : match.start()])
            marker = match.group(0)[0]
            content, i = extract_brace_content(typst, match.end() - 1)
            content = self._unwrap_scripts(content).strip()
            if re.fullmatch(r'"[^"]*"|[A-Za-z0-9]', content):
                parts.append(marker + content)
            else:
                parts.append(f"{marker}({content})")
        parts.append(typst[i:])
        return "".join(parts)

    def _quote_identifiers(self, typst: str) -> str:
        """Quote multi-letter identifiers and subscripts in Typst math mode."""
        result = []
        i = 0
        while i < len(typst):
            if typst[i] == '"':
                end = typst.find('"', i + 1)
                end = len(typst) if end == -1 else end + 1
                result.append(typst[i:end])
                i = end
                continue
            if typst[i].isalpha():
                ident_start = i
                while i < len(typst) and typst[i].isalpha():
                    i += 1
                ident = typst[ident_start:i]

                if i < len(typst) and typst[i] == "_":
                    i += 1
                    if i < len(typst) and typst[i] == "{":
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

                        if len(ident) > 1 and ident not in TYPST_BARE_NAMES:
                            result.append(f'"{ident}"')
                        else:
                            result.append(ident)
                        result.append("_")
                        result.append("{")
                        if subscript_content.isalpha() and len(subscript_content) > 1:
                            result.append(f'"{subscript_content}"')
                        else:
                            result.append(subscript_content)
                        result.append("}")
                    else:
                        result.append(ident)
                        result.append("_")
                        if i < len(typst):
                            result.append(typst[i])
                            i += 1
                elif is_differential(ident):
                    result.append(f"d {ident[1]}")
                elif len(ident) > 1 and ident not in TYPST_BARE_NAMES:
                    result.append(f'"{ident}"')
                else:
                    result.append(ident)
            else:
                result.append(typst[i])
                i += 1
        return "".join(result)

    def binomial_to_readable(self, n: sp.Symbol, k: int) -> str:
        """Convert binomial coefficient to readable form."""
        return f"C({n}, {k})"
