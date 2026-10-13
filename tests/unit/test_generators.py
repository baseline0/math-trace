"""
Tests for formula generators: SymPy → LaTeX → Typst conversion.

These tests verify the core conversion pipeline that affects all
published mathematics. High coverage here is critical for correctness.
"""

import pytest
import sympy as sp

from math_trace.generators import SymPyToTypst, TypstEnvironmentBuilder


class TestSymPyToTypstBasic:
    """Test basic SymPy → Typst conversion."""

    def test_simple_arithmetic(self):
        """Convert simple arithmetic expressions."""
        converter = SymPyToTypst()

        # Basic operations
        x = sp.Symbol("x")
        expr = x + 1
        result = converter.convert(expr)
        assert "x" in result
        assert "1" in result

    def test_multiplication(self):
        """Convert multiplication expressions."""
        converter = SymPyToTypst()

        x, y = sp.symbols("x y")
        expr = x * y
        result = converter.convert(expr)

        # Should contain both variables
        assert "x" in result
        assert "y" in result

    def test_power_expression(self):
        """Convert power expressions."""
        converter = SymPyToTypst()

        x = sp.Symbol("x")
        expr = x**2
        result = converter.convert(expr)

        assert "x" in result
        # Power should be represented (either as ^ or superscript)
        assert len(result) > 0


class TestSymPyToTypstBraces:
    """Test brace extraction and balanced brace handling."""

    def test_extract_simple_braces(self):
        """Extract content from simple braces."""
        converter = SymPyToTypst()

        content, end = converter._extract_brace_content("{hello} world", 0)
        assert content == "hello"
        assert end == 7  # Position after }

    def test_extract_nested_braces(self):
        """Extract content with nested braces."""
        converter = SymPyToTypst()

        content, _end = converter._extract_brace_content("{a{b}c}", 0)
        assert content == "a{b}c"

    def test_extract_multiple_nested_levels(self):
        """Extract content with multiple nesting levels."""
        converter = SymPyToTypst()

        content, _end = converter._extract_brace_content("{a{b{c}d}e}", 0)
        assert content == "a{b{c}d}e"

    def test_extract_invalid_position(self):
        """Handle extraction from invalid position."""
        converter = SymPyToTypst()

        # Not starting with brace
        content, end = converter._extract_brace_content("not{braced}", 0)
        assert content == ""
        assert end == 0


class TestSymPyToTypstBinomial:
    """Test binomial coefficient conversion."""

    def test_binomial_simple(self):
        """Convert binomial coefficient."""
        converter = SymPyToTypst()

        n, k = sp.symbols("n k")
        expr = sp.binomial(n, k)
        result = converter.convert(expr)

        # Should contain binom function or similar
        assert len(result) > 0
        # Should have n and k
        assert "n" in result
        assert "k" in result

    def test_binomial_with_numbers(self):
        """Convert binomial with numeric values."""
        converter = SymPyToTypst()

        expr = sp.binomial(5, 2)
        result = converter.convert(expr)

        assert len(result) > 0

    def test_binom_macro_replacement(self):
        """Test direct binomial macro replacement."""
        converter = SymPyToTypst()

        latex = r"\binom{n}{2}"
        result = converter._replace_binom(latex)

        assert "binom" in result
        assert "n" in result
        assert "2" in result


class TestSymPyToTypstGreekLetters:
    """Test Greek letter conversion."""

    def test_alpha_conversion(self):
        """Convert alpha symbol."""
        converter = SymPyToTypst()

        sp.Symbol("alpha")
        result = converter._latex_to_typst(r"\alpha")

        assert "α" in result

    def test_beta_conversion(self):
        """Convert beta symbol."""
        converter = SymPyToTypst()

        result = converter._latex_to_typst(r"\beta")
        assert "β" in result

    def test_pi_conversion(self):
        """Convert pi symbol."""
        converter = SymPyToTypst()

        result = converter._latex_to_typst(r"\pi")
        assert "π" in result

    def test_multiple_greek_letters(self):
        """Convert expression with multiple Greek letters."""
        converter = SymPyToTypst()

        result = converter._latex_to_typst(r"\alpha + \beta + \gamma")

        assert "α" in result
        assert "β" in result
        assert "γ" in result


class TestSymPyToTypstTrigonometric:
    """Test trigonometric function conversion."""

    def test_sin_conversion(self):
        """Convert sin function."""
        converter = SymPyToTypst()

        result = converter._latex_to_typst(r"\sin(x)")

        assert "sin" in result
        assert r"\sin" not in result  # Backslash should be removed

    def test_cos_conversion(self):
        """Convert cos function."""
        converter = SymPyToTypst()

        result = converter._latex_to_typst(r"\cos(x)")
        assert "cos" in result

    def test_log_conversion(self):
        """Convert log function."""
        converter = SymPyToTypst()

        result = converter._latex_to_typst(r"\log(x)")
        assert "log" in result

    def test_exp_conversion(self):
        """Convert exp function."""
        converter = SymPyToTypst()

        result = converter._latex_to_typst(r"\exp(x)")
        assert "exp" in result


class TestSymPyToTypstFraction:
    """Test fraction handling."""

    def test_simple_fraction(self):
        """Convert simple fraction."""
        converter = SymPyToTypst()

        x = sp.Symbol("x")
        expr = 1 / x
        result = converter.convert(expr)

        assert len(result) > 0

    def test_complex_fraction(self):
        """Convert complex fraction."""
        converter = SymPyToTypst()

        x, y = sp.symbols("x y")
        expr = (x + 1) / (y + 2)
        result = converter.convert(expr)

        # Should handle the fraction
        assert len(result) > 0

    def test_frac_macro_replacement(self):
        """Test direct frac macro replacement."""
        converter = SymPyToTypst()

        latex = r"\frac{a}{b}"
        result = converter._replace_macro(latex, "frac", "({0})/({1})")

        assert "a" in result
        assert "b" in result
        assert "/" in result


class TestSymPyToTypstSqrt:
    """Test square root conversion."""

    def test_sqrt_simple(self):
        """Convert simple square root."""
        converter = SymPyToTypst()

        x = sp.Symbol("x")
        expr = sp.sqrt(x)
        result = converter.convert(expr)

        assert len(result) > 0

    def test_sqrt_macro_replacement(self):
        """Test direct sqrt macro replacement."""
        converter = SymPyToTypst()

        latex = r"\sqrt{x}"
        result = converter._replace_macro(latex, "sqrt", "sqrt({0})")

        assert "sqrt" in result
        assert "x" in result


class TestSymPyToTypstParentheses:
    """Test parentheses conversion."""

    def test_left_right_parens(self):
        """Convert \\left( and \\right) to regular parentheses."""
        converter = SymPyToTypst()

        latex = r"\left( a \right)"
        result = converter._latex_to_typst(latex)

        # Should not have \left or \right
        assert r"\left" not in result
        assert r"\right" not in result
        # Should have regular parens
        assert "(" in result
        assert ")" in result


class TestSymPyToTypstComplexExpressions:
    """Test conversion of complex mathematical expressions."""

    def test_rate_law_expression(self):
        """Convert realistic rate law expression."""
        converter = SymPyToTypst()

        # Rate law: k * n_a * (n_a - 1) / 2
        k, n_a = sp.symbols("k n_a")
        expr = k * sp.binomial(n_a, 2)
        result = converter.convert(expr)

        assert "k" in result
        assert "n" in result  # n_a should be present
        assert len(result) > 0

    def test_sir_model_expression(self):
        """Convert SIR model rate expression."""
        converter = SymPyToTypst()

        # dS/dt = -β * S * I / N (epidemiological notation: S=susceptible, I=infected, N=population)
        beta, S, I, N = sp.symbols("beta S I N")
        expr = -beta * S * I / N
        result = converter.convert(expr)

        assert "β" in result or "beta" in result
        assert "S" in result
        assert "I" in result
        assert "N" in result

    def test_exponential_expression(self):
        """Convert exponential expression."""
        converter = SymPyToTypst()

        x = sp.Symbol("x")
        expr = sp.exp(x)
        result = converter.convert(expr)

        assert len(result) > 0


class TestSymPyToTypstEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_expression(self):
        """Handle empty or minimal expressions."""
        converter = SymPyToTypst()

        expr = sp.Integer(0)
        result = converter.convert(expr)

        assert result is not None
        assert len(result) > 0

    def test_symbol_only(self):
        """Convert single symbol."""
        converter = SymPyToTypst()

        x = sp.Symbol("x")
        result = converter.convert(x)

        assert "x" in result

    def test_constant_expression(self):
        """Convert constant."""
        converter = SymPyToTypst()

        expr = sp.pi
        result = converter.convert(expr)

        assert "π" in result or "pi" in result


class TestTypstEnvironmentBuilder:
    """Test Typst environment construction."""

    def test_theorem_basic(self):
        """Create basic theorem environment."""
        theorem_text = TypstEnvironmentBuilder.theorem(
            name="theorem", title="Pythagorean Theorem", statement="a² + b² = c²"
        )

        assert "Pythagorean Theorem" in theorem_text
        assert "a²" in theorem_text or "a^2" in theorem_text
        assert len(theorem_text) > 0

    def test_proof_basic(self):
        """Create basic proof environment."""
        proof_text = TypstEnvironmentBuilder.proof(body="By construction, this is true.")

        assert "By construction" in proof_text
        assert len(proof_text) > 0


class TestLatexToTypstMacros:
    """Macros that the template equations use and that Typst must receive as valid syntax."""

    def _convert(self, latex: str) -> str:
        return SymPyToTypst()._latex_to_typst(latex)

    def test_accent_macro_becomes_typst_function(self):
        assert self._convert(r"\hat{y}_{ic}") == r'hat(y)_"ic"'

    def test_mathbf_becomes_bold(self):
        assert self._convert(r"\mathbf{h}_j") == "bold(h)_j"

    def test_text_becomes_string_literal_and_is_not_requoted(self):
        assert self._convert(r"W_{\text{self}}") == 'W_"self"'

    def test_sum_and_integral_stay_bare_symbol_names(self):
        assert self._convert(r"\sum_i") == "sum_i"
        assert self._convert(r"\int x") == "integral x"

    def test_in_does_not_rewrite_int(self):
        assert self._convert(r"\int") == "integral"
        assert self._convert(r"j \in N") == "j ∈ N"

    def test_log_is_a_function_not_a_string(self):
        assert self._convert(r"\log(x)") == "log(x)"

    def test_hbar_maps_to_typst_symbol(self):
        assert self._convert(r"\hbar \omega") == "ℏ ω"


class TestTypstFunctionRendering:
    """Typst must read these as functions, not as literal text or braces (TODO tech debt, 2026-10-13)."""

    @pytest.mark.parametrize(
        ("latex", "typst"),
        [
            (r"\binom{n}{k} x", "binom(n, k) x"),
            (r"\sin{\left(t \right)}", "sin(t )"),
            (r"\sin{x}", "sin x"),
            (r"\cos{\theta} + \sin{\left(2 t\right)}", "cos θ + sin(2 t)"),
            (r"\log{\left(x\right)}", "log(x)"),
        ],
    )
    def test_function_names_render_without_quotes_or_braces(self, latex: str, typst: str):
        assert SymPyToTypst()._latex_to_typst(latex) == typst


class TestTypstScriptRendering:
    """Typst shows braces after ^ and _ literally, so script groups are unwrapped (TODO tech debt, 2026-10-13)."""

    @pytest.mark.parametrize(
        ("latex", "typst"),
        [
            (r"x^{2}", "x^2"),
            (r"x^{-1}", "x^(-1)"),
            (r"x_{ic}", 'x_"ic"'),
            (r"x_{\text{self}}", 'x_"self"'),
            (r"x^{\frac{1}{2}}", "x^((1)/(2))"),
        ],
    )
    def test_script_braces_are_unwrapped(self, latex: str, typst: str):
        assert SymPyToTypst()._latex_to_typst(latex) == typst


class TestTypstGroupingRendering:
    """SymPy's grouping braces around a single function call are dropped, so Typst does not show them."""

    def test_sympy_braced_binomial_renders_without_braces(self):
        k, n = sp.symbols("k n_a")
        assert SymPyToTypst()._latex_to_typst(sp.latex(k * sp.binomial(n, 2))) == "k binom(n_a, 2)"


class TestTypstBareGroupRendering:
    """Bare LaTeX grouping braces are dropped, so Typst does not print them (TODO tech debt, 2026-10-13)."""

    @pytest.mark.parametrize(
        ("latex", "typst"),
        [
            ("{x}", "x"),
            ("{a + b}", "(a + b)"),
            (r"x_{i}^{2} + {a + b}", "x_i^2 + (a + b)"),
            (r"\left|{x}\right|", "|x|"),
        ],
    )
    def test_bare_groups_render_without_braces(self, latex: str, typst: str):
        assert SymPyToTypst()._latex_to_typst(latex) == typst


class TestTypstOperatorRendering:
    """Operator names and roots render as Typst functions, not stray macros (TODO tech debt, 2026-10-13)."""

    @pytest.mark.parametrize(
        ("latex", "typst"),
        [
            (r"\operatorname{Abs}{\left(x \right)}", 'op("Abs")(x )'),
            (r"\operatorname{argmax}_{x}", 'op("argmax")_x'),
            (r"\mathrm{d}x", "upright(d)x"),
            (r"\mathrm{max}{x}", 'op("max") x'),
        ],
    )
    def test_operator_names_render_as_typst_operators(self, latex: str, typst: str):
        assert SymPyToTypst()._latex_to_typst(latex) == typst

    @pytest.mark.parametrize(
        ("latex", "typst"),
        [
            (r"\sqrt[3]{x}", "root(3, x)"),
            (r"\sqrt[n]{\frac{1}{2}}", "root(n, (1)/(2))"),
            (r"\sqrt{x}", "sqrt(x)"),
        ],
    )
    def test_roots_keep_their_index(self, latex: str, typst: str):
        assert SymPyToTypst()._latex_to_typst(latex) == typst

    @pytest.mark.parametrize(
        ("latex", "typst"),
        [
            (r"e^{- \frac{x^{2}}{2}}", "e^(- (x^2)/(2))"),
            (r"x^{y^{2}}", "x^(y^2)"),
            (r"x^{a^{b^{c}}}", "x^(a^(b^c))"),
            (r"x_{a_{b_{c}}}", "x_(a_(b_c))"),
        ],
    )
    def test_nested_script_braces_are_all_unwrapped(self, latex: str, typst: str):
        assert SymPyToTypst()._latex_to_typst(latex) == typst
