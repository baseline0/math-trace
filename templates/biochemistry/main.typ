#set document(title: "Enzyme Kinetics", author: "Your Name")
#set page(numbering: "1")
#set heading(numbering: "1.")

= Enzyme Kinetics: Analysis of Michaelis-Menten Kinetics

#set text(font: "New Computer Modern")

== Introduction

Enzyme kinetics describes how biochemical catalysts speed up reactions. This paper studies the Michaelis-Menten model—one of the most important equations in biochemistry. By linking every formula to Python code, we demonstrate publication-quality research in molecular biology.

== Theoretical Framework

=== The Michaelis-Menten Equation

The Michaelis-Menten equation relates reaction velocity to substrate concentration:

#include "generated/formulas.typ"

Where:
- $v$ is the reaction velocity (μmol/min)
- $V_max$ is the maximum velocity (μmol/min)
- $S$ is the substrate concentration (mM)
- $K_m$ is the Michaelis constant (mM)

=== Biological Interpretation

The Michaelis constant $K_m$ is the substrate concentration at which velocity is half-maximal: $v = V_max / 2$. It reflects the affinity of the enzyme for its substrate:

- Low $K_m$ = high affinity (substrate is "sticky")
- High $K_m$ = low affinity (substrate binds weakly)

=== Catalytic Efficiency

The catalytic efficiency combines both speed and selectivity:

// Catalytic efficiency formula included from generated/formulas.typ

Enzymes with high $k_cat / K_m$ values are both fast and specific.

== Experimental Data

We measure reaction velocity across a range of substrate concentrations (0.01–50 mM) using spectrophotometric assay with measurement uncertainty.

#figure(
  image("generated/figures/kinetics.png", width: 100%),
  caption: [Michaelis-Menten kinetics (left) and Lineweaver-Burk double-reciprocal plot (right) for simulated enzyme data with experimental error]
)

The data shows classic saturation kinetics: at low substrate, velocity increases linearly; at high substrate, velocity plateaus near $V_max$. The Lineweaver-Burk plot (right) linearizes the data for easier parameter estimation.

== Conclusion

Michaelis-Menten kinetics remains the foundation of enzyme characterization. By publishing formulas alongside simulation code, we make our research reproducible and enable others to adapt our methods to their own enzyme systems.

#set text(size: 10pt)

---

_Generated with math-trace: formula-to-code traceability for researchers_
