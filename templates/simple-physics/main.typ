#set document(title: "Harmonic Oscillator", author: "Your Name")
#set page(numbering: "1")
#set heading(numbering: "1.")

= Harmonic Oscillator: A Complete Study

#set text(font: "New Computer Modern")

== Introduction

This paper studies the classical harmonic oscillator—a system where a restoring force is proportional to displacement. This template demonstrates formula-to-code traceability for publication-quality physics papers.

== Theory

=== Newton's Second Law

The fundamental equation of motion for a harmonic oscillator is:

#include "generated/formulas.typ"

Where:
- $x(t)$ is the displacement from equilibrium
- $m$ is the mass of the oscillator
- $k$ is the spring constant

=== Angular Frequency

The natural frequency of oscillation depends on the mass and stiffness:

// Angular frequency formula included from generated/formulas.typ

For our simulation, we use $omega = 0.5$ rad/s and $m = 1$ kg.

== Simulation Results

We simulate the harmonic oscillator over 20 seconds using Euler integration with small Gaussian noise for realism.

#figure(
  image("generated/figures/oscillator.png", width: 100%),
  caption: [Simulated trajectory of a harmonic oscillator with damping noise]
)

The figure shows the oscillatory behavior: the system alternates between maximum positive and negative displacement, passing through equilibrium at regular intervals.

== Energy Conservation

For an ideal harmonic oscillator (no damping), total mechanical energy is conserved:

// Total energy formula included from generated/formulas.typ

This energy oscillates between kinetic and potential forms but maintains constant total.

== Conclusion

The harmonic oscillator is fundamental to classical mechanics and has applications across physics, engineering, and beyond. By linking every formula to its source in Python, we enable reproducible, publication-quality research.

#set text(size: 10pt)

---

_Generated with math-trace: formula-to-code traceability for researchers_
