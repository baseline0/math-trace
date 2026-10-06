#!/usr/bin/env python3
"""Example: Interactive formula-driven presentation with HTMX.

Demonstrates how to build a presentation where:
1. Formulas are defined in Python (SymPy)
2. Slides reference formulas by ID
3. Clicking formulas evaluates them live
4. Formulas trace back to source code

## Usage

```bash
cd examples/
python presentation-example.py
# Open http://localhost:8000 in your browser
```

## Features

- **Live computation:** Click formula → server evaluates → results appear
- **Source traceability:** Each formula shows its source file + line number
- **Beautiful math:** MathJax renders all math notation
- **Keyboard navigation:** Arrow keys to navigate slides
- **Export:** Print to PDF from browser
"""

from math_trace.formula import Formula
from math_trace.presentation_server import PresentationServer


def build_presentation():
    """Build example presentation with interactive formulas."""

    # Create server
    server = PresentationServer(
        title="Interactive Math-Trace Talk",
        theme="white",
        transition="slide",
    )

    # Slide 1: Title
    server.add_slide(
        title="Formula-Driven Presentations",
        content="""
        <p>Using <strong>SymPy</strong> formulas to create interactive slides.</p>
        <p style="margin-top: 2em; color: #666; font-size: 0.8em;">
            💡 Click any formula to evaluate it live with current parameters
        </p>
        """,
    )

    # Slide 2: Introduction
    server.add_slide(
        title="The Problem We're Solving",
        content="""
        <ul>
            <li>Formulas defined in code (SymPy)</li>
            <li>Manually typed into presentations → errors</li>
            <li>Updates require manual sync → drift</li>
            <li>No way to verify formulas match code</li>
        </ul>
        <p style="margin-top: 2em;"><strong>Solution:</strong> Define once, reference everywhere.</p>
        """,
    )

    # Slide 3: Rate Law (with interactive formulas)
    rate_formula = Formula(
        name="Rate Law",
        latex=r"k \binom{n}{2}",
        description="Collision rate between n particles",
        source_line=42,
    )

    server.add_formula_slide(
        title="Chemical Kinetics",
        formulas={"rate": rate_formula},
        parameters={"k": 1.5, "n": 10},
        description="Rate of bimolecular reactions",
    )

    # Slide 4: Michaelis-Menten Kinetics
    michaelis_menten = Formula(
        name="Michaelis-Menten",
        latex=r"v = \frac{V_{max} [S]}{K_m + [S]}",
        description="Enzyme reaction velocity",
        source_line=87,
    )

    server.add_formula_slide(
        title="Enzyme Kinetics",
        formulas={"michaelis_menten": michaelis_menten},
        parameters={"V_max": 100, "K_m": 5, "S": 10},
        description="Steady-state enzyme reaction rates",
    )

    # Slide 5: Equilibrium
    equilibrium = Formula(
        name="Equilibrium Constant",
        latex=r"K = \frac{[C][D]}{[A][B]}",
        description="Ratio of product to reactant concentrations",
        source_line=120,
    )

    server.add_formula_slide(
        title="Chemical Equilibrium",
        formulas={"equilibrium": equilibrium},
        parameters={"C": 2, "D": 3, "A": 1, "B": 1},
        description="Equilibrium expression for aA + bB ⇌ cC + dD",
    )

    # Slide 6: Integration with Code
    server.add_slide(
        title="Source Traceability",
        content="""
        <p>Each formula is <strong>linked to its source code</strong>:</p>
        <ul>
            <li>File: model.py</li>
            <li>Line number: where formula is defined</li>
            <li>Version control: commits that changed it</li>
            <li>Tests: that verify it matches code</li>
        </ul>
        <p style="margin-top: 2em; color: #666; font-size: 0.9em;">
            ✓ Presentations and code <strong>stay in sync</strong>
        </p>
        """,
    )

    # Slide 7: How It Works
    server.add_slide(
        title="Architecture",
        content="""
        <ol style="font-size: 0.9em;">
            <li><strong>Define:</strong> Formulas in model.py (SymPy)</li>
            <li><strong>Export:</strong> List formulas with metadata (name, source_line)</li>
            <li><strong>Reference:</strong> Slides mention formula by ID</li>
            <li><strong>Render:</strong> Server converts to LaTeX/MathJax</li>
            <li><strong>Interactive:</strong> Click formula → live evaluation</li>
            <li><strong>Export:</strong> Print to PDF with all formulas</li>
        </ol>
        <p style="margin-top: 1em; color: #666;">
            <small>Uses: SymPy, Revealjs, MathJax, HTMX, FastAPI</small>
        </p>
        """,
    )

    # Slide 8: Closing
    server.add_slide(
        title="Key Benefits",
        content="""
        <ul>
            <li>📝 <strong>Single source of truth</strong> — formulas defined in code</li>
            <li>🎯 <strong>No manual sync</strong> — update code, slides update automatically</li>
            <li>✓ <strong>Verifiable</strong> — formulas traced to source</li>
            <li>🎨 <strong>Beautiful output</strong> — MathJax rendering</li>
            <li>⚡ <strong>Interactive</strong> — live formula evaluation</li>
        </ul>
        """,
    )

    return server


if __name__ == "__main__":
    server = build_presentation()
    server.run(host="127.0.0.1", port=8000)
