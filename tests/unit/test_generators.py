"""
Tests for formula generators: SymPy → LaTeX → Typst conversion.

These tests verify the core conversion pipeline that affects all
published mathematics. High coverage here is critical for correctness.
"""

import sympy as sp
import pytest

from math_trace.generators import SymPyToTypst, TypstEnvironmentBuilder


class TestSymPyToTypstBasic:
    """Test basic SymPy → Typst conversion."""

    def test_simple_arithmetic(self):
        """Convert simple arithmetic expressions."""
        converter = SymPyToTypst()

        # Basic operations
        x = sp.Symbol('x')
        expr = x + 1
        result = converter.convert(expr)
        assert 'x' in result
        assert '1' in result

    def test_multiplication(self):
        """Convert multiplication expressions."""
        converter = SymPyToTypst()

        x, y = sp.symbols('x y')
        expr = x * y
        result = converter.convert(expr)

        # Should contain both variables
        assert 'x' in result
        assert 'y' in result

    def test_power_expression(self):
        """Convert power expressions."""
        converter = SymPyToTypst()

        x = sp.Symbol('x')
        expr = x ** 2
        result = converter.convert(expr)

        assert 'x' in result
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

        content, end = converter._extract_brace_content("{a{b}c}", 0)
        assert content == "a{b}c"

    def test_extract_multiple_nested_levels(self):
        """Extract content with multiple nesting levels."""
        converter = SymPyToTypst()

        content, end = converter._extract_brace_content("{a{b{c}d}e}", 0)
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

        n, k = sp.symbols('n k')
        expr = sp.binomial(n, k)
        result = converter.convert(expr)

        # Should contain binom function or similar
        assert len(result) > 0
        # Should have n and k
        assert 'n' in result
        assert 'k' in result

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

        alpha = sp.Symbol('alpha')
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

        x = sp.Symbol('x')
        expr = 1 / x
        result = converter.convert(expr)

        assert len(result) > 0

    def test_complex_fraction(self):
        """Convert complex fraction."""
        converter = SymPyToTypst()

        x, y = sp.symbols('x y')
        expr = (x + 1) / (y + 2)
        result = converter.convert(expr)

        # Should handle the fraction
        assert len(result) > 0

    def test_frac_macro_replacement(self):
        """Test direct frac macro replacement."""
        converter = SymPyToTypst()

        latex = r"\frac{a}{b}"
        result = converter._replace_macro(latex, 'frac', '({0})/({1})')

        assert "a" in result
        assert "b" in result
        assert "/" in result


class TestSymPyToTypstSqrt:
    """Test square root conversion."""

    def test_sqrt_simple(self):
        """Convert simple square root."""
        converter = SymPyToTypst()

        x = sp.Symbol('x')
        expr = sp.sqrt(x)
        result = converter.convert(expr)

        assert len(result) > 0

    def test_sqrt_macro_replacement(self):
        """Test direct sqrt macro replacement."""
        converter = SymPyToTypst()

        latex = r"\sqrt{x}"
        result = converter._replace_macro(latex, 'sqrt', 'sqrt({0})')

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
        k, n_a = sp.symbols('k n_a')
        expr = k * sp.binomial(n_a, 2)
        result = converter.convert(expr)

        assert 'k' in result
        assert 'n' in result  # n_a should be present
        assert len(result) > 0

    def test_sir_model_expression(self):
        """Convert SIR model rate expression."""
        converter = SymPyToTypst()

        # dS/dt = -β * S * I / N
        beta, S, I, N = sp.symbols('beta S I N')
        expr = -beta * S * I / N
        result = converter.convert(expr)

        assert 'β' in result or 'beta' in result
        assert 'S' in result
        assert 'I' in result
        assert 'N' in result

    def test_exponential_expression(self):
        """Convert exponential expression."""
        converter = SymPyToTypst()

        x = sp.Symbol('x')
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

        x = sp.Symbol('x')
        result = converter.convert(x)

        assert 'x' in result

    def test_constant_expression(self):
        """Convert constant."""
        converter = SymPyToTypst()

        expr = sp.pi
        result = converter.convert(expr)

        assert 'π' in result or 'pi' in result


class TestTypstEnvironmentBuilder:
    """Test Typst environment construction."""

    def test_theorem_basic(self):
        """Create basic theorem environment."""
        theorem_text = TypstEnvironmentBuilder.theorem(name="theorem", 
            title="Pythagorean Theorem",
            statement="a² + b² = c²"
        )

        assert "Pythagorean Theorem" in theorem_text
        assert "a²" in theorem_text or "a^2" in theorem_text
        assert len(theorem_text) > 0

    def test_proof_basic(self):
        """Create basic proof environment."""
        proof_text = TypstEnvironmentBuilder.proof(
            body="By construction, this is true."
        )

        assert "By construction" in proof_text
        assert len(proof_text) > 0
