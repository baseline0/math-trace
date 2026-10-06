"""Formal verification layer: Prove mathematical theorems.

## Architecture: Pluggable Proof Frameworks

This module defines the abstraction for formal verification of mathematical
claims. By decoupling the proof framework from the rest of the pipeline,
we can swap proof systems without affecting formula definitions or publishing.

## Design Principle: Optional Formal Verification

Currently uses Lean 4 with Mathlib for optional formal proofs. Proofs are
not required—they are an opt-in layer for researchers who want machine-verified
assurance of their mathematical claims.

**Migration Path:** If Lean becomes unmaintained:
1. Implement CoqFramework or IsabelleFramework
2. Change one line: proof_framework = CoqFramework()
3. Theorems still get verified (just in different language)

## Implementations

- **LeanFramework:** Uses Lean 4 with Mathlib (current)
  - Modern, actively maintained
  - Strong ecosystem for mathematics

- **CoqFramework:** Uses Coq (hypothetical alternative)
  - Mature, long-standing ecosystem
  - Good for foundational mathematics

## To Add a New Proof Framework

1. Subclass ProofFramework
2. Implement verify(theorem: str) -> bool
3. Implement export_to_registry(proof: str) -> str
4. Update examples to use the new framework (optional)

Example:
    class IsabelleFramework(ProofFramework):
        def verify(self, theorem: str) -> bool:
            # Shell out to Isabelle/HOL
            return success
        def export_to_registry(self, proof: str) -> str:
            # Submit to Isabelle registry
            return registry_link

See Also:
    - formula.py: Formula abstraction (source of claims)
    - examples/*/build_paper.py: Orchestration (optional proof layer)
    - https://palomar.tech: Public proof registry
"""

from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod


class ProofFramework(ABC):
    """Base class for formal verification frameworks.

    Verifies mathematical theorems in a formal proof assistant.
    Subclasses implement specific proof languages (Lean, Coq, Isabelle, etc.).

    Proofs are OPTIONAL. If proof verification fails or is unavailable,
    the paper still publishes with unverified formulas.
    """

    @abstractmethod
    def verify(self, theorem: str) -> bool:
        """Verify a theorem in this proof framework.

        Args:
            theorem: Theorem statement (in framework syntax)

        Returns:
            True if theorem is proven, False if not or if verification fails
        """
        pass

    @abstractmethod
    def export_to_registry(self, proof: str) -> str:
        """Export proof to a public registry.

        Args:
            proof: Proof code (in framework syntax)

        Returns:
            URL or identifier of the proof in the registry
        """
        pass


class LeanFramework(ProofFramework):
    """Verifies theorems using Lean 4 with Mathlib.

    RATIONALE: Lean 4 is actively maintained, has a growing ecosystem,
    and is particularly strong for formalizing pure mathematics.

    SETUP REQUIRED:
        - Install Lean 4: https://lean-lang.org/
        - Set up Mathlib: lakeroot
        - Optional: Palomar account for proof registry

    MIGRATION PATH: If Lean's development stalls or becomes incompatible
    with our needs, implement CoqFramework or IsabelleFramework using the
    same interface. All upstream code continues to work.

    Example usage:
        framework = LeanFramework()
        if framework.verify("theorem my_result : ..."):
            registry_url = framework.export_to_registry(proof_code)
            print(f"Proof available at {registry_url}")
    """

    def verify(self, theorem: str) -> bool:
        """Verify theorem using Lean 4.

        Args:
            theorem: Lean 4 theorem statement and proof

        Returns:
            True if Lean accepts the proof, False otherwise
        """
        try:
            # Create a temporary Lean file and run `lean` type-checker
            result = subprocess.run(
                ["lake", "env", "lean", "--check"],
                input=theorem.encode(),
                capture_output=True,
                timeout=30,
            )
            return result.returncode == 0

        except FileNotFoundError:
            # Lean/lake not installed—verification unavailable but not fatal
            return False

    def export_to_registry(self, proof: str) -> str:
        """Export proof to Palomar registry.

        Args:
            proof: Lean 4 proof code

        Returns:
            Local proof ID (format: palomar.internal/proof/{hash})

        Note:
            Full Palomar API integration is a future enhancement.
            Currently returns a local hash-based identifier.

        Raises:
            RuntimeError: If export fails (encoding errors, etc.)
        """
        try:
            import hashlib

            proof_hash = hashlib.sha256(proof.encode()).hexdigest()[:8]
            return f"palomar.internal/proof/{proof_hash}"

        except Exception as e:
            raise RuntimeError(f"Failed to generate proof ID: {e}")


class CoqFramework(ProofFramework):
    """Verifies theorems using Coq (hypothetical alternative).

    RATIONALE: Coq is a mature, long-standing proof assistant with an
    excellent ecosystem. Use this if Lean becomes incompatible or we
    need stronger foundational guarantees.

    SETUP REQUIRED:
        - Install Coq: https://coq.inria.fr/
        - Install proof-checkers via opam

    This is a hypothetical implementation—currently not used but available
    if Lean's maintenance becomes a concern.

    MIGRATION PATH: To use Coq instead of Lean, change one line:
        proof_framework = CoqFramework()
    All upstream code continues to work unchanged.
    """

    def verify(self, theorem: str) -> bool:
        """Verify theorem using Coq.

        Args:
            theorem: Coq theorem statement and proof

        Returns:
            True if Coq accepts the proof, False otherwise
        """
        try:
            result = subprocess.run(
                ["coqchk"],
                input=theorem.encode(),
                capture_output=True,
                timeout=30,
            )
            return result.returncode == 0

        except FileNotFoundError:
            # Coq not installed
            return False

    def export_to_registry(self, proof: str) -> str:
        """Export proof to a proof registry.

        Args:
            proof: Coq proof code

        Returns:
            URL or identifier of proof in registry
        """
        # Placeholder implementation
        import hashlib

        proof_hash = hashlib.sha256(proof.encode()).hexdigest()[:8]
        return f"coq-registry.org/proof/{proof_hash}"
