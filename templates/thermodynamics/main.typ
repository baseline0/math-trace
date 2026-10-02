#set page(margin: (left: 2cm, right: 2cm, top: 2cm, bottom: 2cm))
#set text(font: "New Computer Modern", size: 11pt)

#import "generated/formulas.typ": *

= Thermodynamics: Ideal Gas & Carnot Cycle

_Fundamental equations of heat, work, and entropy_

== 1. Introduction
Thermodynamics describes energy transformations in physical systems. We examine ideal gases and the limits of heat-to-work conversion via the Carnot cycle.

== 2. Ideal Gas Law
The equation of state for an ideal gas relates pressure, volume, temperature, and moles:

#figure(
  align(center, $P V = n R T$),
  caption: [Ideal gas law (from model.py:20)]
)

Where R = 8.314 J/(mol·K). Valid when intermolecular forces are negligible.

== 3. Internal Energy
Internal energy depends only on temperature for an ideal gas:

#figure(
  align(center, $U = n C_v T$),
  caption: [Internal energy (from model.py:45)]
)

Where C_v is heat capacity at constant volume. For monatomic gases, C_v = (3/2)R.

== 4. First Law of Thermodynamics
Energy is conserved: heat absorbed equals internal energy change plus work done by the system:

#figure(
  align(center, $"d"U = δQ - δW$),
  caption: [First law (from model.py:50)]
)

This is conservation of energy applied to thermodynamic systems.

== 5. Work Done
For isobaric (constant pressure) processes:

#figure(
  align(center, $W = P Δ V$),
  caption: [Work in isobaric process (from model.py:55)]
)

Work is the area under a P-V curve during expansion or compression.

== 6. Entropy
Entropy measures disorder and irreversibility:

#figure(
  align(center, $S = n C_v ln(T) + n R ln(V) + S_0$),
  caption: [Entropy of ideal gas (from model.py:65)]
)

In irreversible processes, total entropy increases (2nd law).

== 7. Carnot Cycle
The Carnot cycle is the most efficient heat engine operating between two temperatures:

- Isothermal expansion (absorb heat)
- Adiabatic expansion (cool down)
- Isothermal compression (reject heat)
- Adiabatic compression (warm up)

No real engine can exceed Carnot efficiency.

== 8. Carnot Efficiency
Maximum efficiency achievable:

#figure(
  align(center, $η = 1 - T_"cold" / T_"hot"$),
  caption: [Carnot efficiency (from model.py:75)]
)

Efficiency depends only on temperatures, not device design. Higher temperature difference → higher efficiency.

== 9. Heat Capacity
Heat capacity is the energy needed to raise temperature by 1 K:

#figure(
  align(center, $C_P = C_V + R$),
  caption: [Mayer relation (from model.py:90)]
)

Heat capacity at constant pressure exceeds that at constant volume because energy goes to both internal energy and expansion work.

== 10. Conclusion
The ideal gas law and thermodynamic laws describe energy flow in physical systems. The Carnot cycle establishes fundamental limits on efficiency. Real engines, refrigerators, and heat pumps approach but never exceed these theoretical bounds.

---

#set text(size: 9pt, fill: gray)

_Paper generated from model.py and main.typ. All formulas traced to source code._
