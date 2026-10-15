-- Copied verbatim from Challenge.lean at Palomar Sidorenko commit ba6f109bf01436ca15e55fdf5d35dbea85ffd9c9 (lines 44-52).
-- Read by build_table.py's transcription and the reference contract test; do not edit by hand.
/-- The exact positive constant displayed in Theorem 1.1 for r >= 3. -/
def paperConstant (r : ℕ) : ℝ :=
  (1 / (4 * (r : ℝ) ^ 2)) *
    Real.rpow (4 / (r : ℝ)) (1 / (r : ℝ)) *
    Real.rpow (1 - 1 / (r : ℝ)) (2 - 2 / (r : ℝ))

/-- The claimed gap from density one for an m-edge forbidden hypergraph. -/
def paperGap (r m : ℕ) : ℝ :=
  paperConstant r / Real.rpow (m : ℝ) (((r : ℝ) - 1) / (r : ℝ))
