#set page(margin: (left: 2cm, right: 2cm, top: 2cm, bottom: 2cm))
#set text(font: "New Computer Modern", size: 11pt)

#import "generated/formulas.typ": *

= Control Systems: Linear Systems & PID Controllers

_Feedback control design and stability analysis_

== 1. Introduction
Control systems maintain desired behavior by using feedback. We model linear systems in state-space form and design controllers to achieve stability and performance.

== 2. State-Space Representation
Linear systems are described by coupled first-order ODEs:

#figure(
  align(center, block[
    $dot(x) = A x + B u$ \
    $y = C x + D u$
  ]),
  caption: [State-space form (from model.py:30)]
)

Where x is state, u is input, y is output. A, B, C, D are system matrices.

== 3. Eigenvalues & Stability
A system is stable if all eigenvalues of A have negative real parts:

#figure(
  align(center, $Re(λ_i) < 0 space "for all" space i$),
  caption: [Stability criterion (from model.py:85)]
)

Unstable eigenvalues → divergent response. Marginally stable → oscillations.

== 4. Open-Loop vs Closed-Loop
Without feedback (open-loop), system behavior is uncontrolled. With feedback (closed-loop), we adjust input u based on error to track a reference.

== 5. PID Control
Proportional-Integral-Derivative control computes:

#figure(
  align(center, $u = K_p e + K_i integral(e) + K_d dot(e)$),
  caption: [PID control law (from model.py:120)]
)

Where e = reference - output. Each term addresses different performance aspects.

== 6. Proportional Control
Proportional term provides immediate response to error. Higher K_p → faster response but can cause oscillation.

== 7. Integral Control
Integrates accumulated error to eliminate steady-state error. Too much integral action → instability.

== 8. Derivative Control
Derivative term dampens oscillations by reacting to error rate of change. Sensitive to measurement noise.

== 9. Tuning & Trade-offs
PID tuning balances speed (rise time), overshoot, and settling time:
- High K_p: fast but oscillatory
- High K_i: eliminates offset but slow
- High K_d: dampens but noisy

Ziegler-Nichols and other methods guide tuning for specific applications.

== 10. Conclusion
State-space representation provides a unified framework for analyzing linear systems. Feedback control via PID adjusts system behavior to meet specifications. Trade-offs between speed, stability, and robustness drive controller design.

---

#set text(size: 9pt, fill: gray)

_Paper generated from model.py and main.typ. All formulas traced to source code._
