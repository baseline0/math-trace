"""Formula generators: SymPy/LaTeX to Typst conversion and Typst environments."""

from .sympy_typst import SymPyToTypst
from .typst_env import TypstEnvironmentBuilder

__all__ = ["SymPyToTypst", "TypstEnvironmentBuilder"]

if __name__ == "__main__":
    import sympy as sp

    converter = SymPyToTypst()
    x = sp.Symbol("x")
    expr = x**2 + 2 * x + 1
    typst = converter.convert(expr)
    print(f"Expression: {expr}")
    print(f"LaTeX: {sp.latex(expr)}")
    print(f"Typst: {typst}")
