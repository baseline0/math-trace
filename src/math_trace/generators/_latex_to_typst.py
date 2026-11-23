"""LaTeX-to-Typst conversion helpers used by SymPyToTypst."""

from __future__ import annotations

import re

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
        "binom",
        "root",
        "op",
        "upright",
        "sqrt",
        "hat",
        "bar",
        "dot",
        "tilde",
        "vec",
        "bold",
    }
)

_DIFFERENTIAL_NAME = re.compile(r"^d[A-Za-zα-ωΑ-Ω]$")


def differential_term(order: str | None, variable: str, power: str | None) -> str:
    """Build one differential term, e.g. ("2", "\\psi", None) -> "d^2 \\psi"."""
    order_part = f"^{order}" if order else ""
    return f"d{order_part} {variable}{power or ''}"


def is_differential(ident: str) -> bool:
    """True for a two-character differential token such as dU, dx or dτ."""
    return bool(_DIFFERENTIAL_NAME.match(ident))


def extract_brace_content(s: str, start: int) -> tuple[str, int]:
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


def replace_macro(latex: str, macro: str, replacement: str) -> str:
    """Replace LaTeX macro with Typst equivalent, handling nested braces."""
    result = []
    pattern = "\\" + macro
    i = 0

    while i < len(latex):
        if latex[i : i + len(pattern)] == pattern:
            i += len(pattern)
            while i < len(latex) and latex[i] in " \t":
                i += 1

            args = []
            while i < len(latex) and latex[i] == "{":
                arg, i = extract_brace_content(latex, i)
                args.append(arg)
                j = i
                while j < len(latex) and latex[j] in " \t":
                    j += 1
                if j < len(latex) and latex[j] == "{":
                    i = j

            if args:
                try:
                    result.append(replacement.format(*args))
                except IndexError:
                    result.append(pattern)
            else:
                result.append(pattern)
        else:
            result.append(latex[i])
            i += 1

    return "".join(result)


def replace_root_index(latex: str) -> str:
    """Replace \\sqrt[n]{x} with root(n, x). The radicand is read with brace matching, so it may nest."""
    pattern = re.compile(r"\\sqrt\s*\[([^\]]*)\]\s*\{")
    parts: list[str] = []
    i = 0
    while match := pattern.search(latex, i):
        parts.append(latex[i : match.start()])
        radicand, i = extract_brace_content(latex, match.end() - 1)
        parts.append(f"root({match.group(1).strip()}, {radicand})")
    parts.append(latex[i:])
    return "".join(parts)


def upright_or_operator(match: re.Match[str]) -> str:
    """Render \\mathrm{X}: a single letter stays upright (the differential d), a word becomes an operator name."""
    name = match.group(1)
    return f"upright({name})" if len(name) == 1 else f'op("{name}")'


def unwrap_function_arguments(typst: str, names: list[str]) -> str:
    """Drop the grouping braces LaTeX writes after a function name: sin{(t)} becomes sin(t)."""
    alternatives = [re.escape(name) for name in sorted(names, key=len, reverse=True)]
    alternatives.append(r'op\("[A-Za-z]+"\)')
    pattern = re.compile(r"\b(" + "|".join(alternatives) + r")\s*\{")
    parts: list[str] = []
    i = 0
    while match := pattern.search(typst, i):
        parts.append(typst[i : match.start()])
        name = match.group(1)
        content, i = extract_brace_content(typst, match.end() - 1)
        content = content.strip()
        parts.append(name + content if content.startswith("(") else f"{name} {content}")
    parts.append(typst[i:])
    return "".join(parts)


def differential_fraction(match: re.Match[str]) -> str:
    """Render a differential fraction as (d x)/(d y), keeping order and power."""
    num = differential_term(match.group(1), match.group(2), match.group(3))
    den = differential_term(match.group(4), match.group(5), match.group(6))
    return f"({num})/({den})"
