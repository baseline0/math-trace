"""Verification vocabulary and status tracking for equations and formulas.

## Specification Map

| Invariant | Source | Enforcement |
|---|---|---|
| Six distinct verification statuses (source, transcription, symbolic, numeric, formal, historical) | docs/AGMAI-READY.md § Verification Vocabulary | `VerificationStatus` StrEnum with test coverage |
| Each status is independent; unverified statuses are omitted, not set to False | docs/AGMAI-READY.md § Verification Vocabulary | `VerificationRecord` dataclass rules tested |
| Every equation must have at least one verification status | docs/AGMAI-READY.md § Verification Vocabulary | `test_equation_requires_verification` validates schema |
| VerificationRecord fields: by (required), date (optional), note (optional) | docs/AGMAI-READY.md lines 157-169 | `test_verification_record_schema` validates structure |

---

This module codifies the verification vocabulary from AGMAI-READY.md, replacing passive markdown
with executable dataclass contracts and enum definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum


class VerificationStatus(StrEnum):
    """Six independent verification status categories (non-collapsing).

    Each represents a distinct form of verification that an equation can have.
    They do NOT collapse into one "verified" badge; instead, each is tracked
    independently. An equation can be source_verified but not transcription_verified.

    Attributes:
        SOURCE_VERIFIED: Human inspected the cited source document.
        TRANSCRIPTION_VERIFIED: Equation faithfully transcribed from verified source.
        SYMBOLIC_VERIFIED: Symbolic identities or transformations proven valid.
        NUMERICALLY_VERIFIED: Numerical checks passed over defined test cases.
        FORMALLY_VERIFIED: Theorem prover established stated property.
        HISTORICAL_INTERPRETATION: Human-curated historical claim (not mathematical proof).
    """

    SOURCE_VERIFIED = "source_verified"
    """Cited source was inspected by human (e.g., 'Kermack-McKendrick 1927 paper reviewed')."""

    TRANSCRIPTION_VERIFIED = "transcription_verified"
    """Equation faithfully transcribed from source (e.g., 'test_sir.py: equation matches Kermack form exactly')."""

    SYMBOLIC_VERIFIED = "symbolic_verified"
    """Symbolic identities or transformations passed (e.g., 'test_algebra.py: SIR + SEIR identity proven')."""

    NUMERICALLY_VERIFIED = "numerically_verified"
    """Numerical checks passed over defined test cases (e.g., 'test_sir_numerics.py: SIR equilibrium within 1e-6')."""

    FORMALLY_VERIFIED = "formally_verified"
    """Theorem prover established stated property (e.g., 'Lean: conservation law proven under assumptions')."""

    HISTORICAL_INTERPRETATION = "historical_interpretation"
    """Human-curated historical claim, not mathematical proof (e.g., 'This formulation became standard after 1970')."""


@dataclass
class VerificationRecord:
    """Record of a single verification status for an equation.

    Each VerificationStatus may have its own VerificationRecord with metadata
    about who/what performed the verification, when, and any notes.

    Attributes:
        by: Who or what performed verification (e.g., "human", "test_sir.py", "Lean")
        date: When verification was performed (optional).
        note: Optional human-readable note (e.g., reason, specific test name, citation).
        test_file: Optional reference to test file (for test-based verifications).
        tolerance: Optional numeric tolerance (for numerically_verified).

    Examples:
        # Human review of source document
        VerificationRecord(by="human", date=date(2026, 9, 22),
                          note="Kermack-McKendrick 1927 inspected")

        # Automated test verification
        VerificationRecord(by="test_sir.py", date=date(2026, 9, 22),
                          test_file="tests/unit/test_sir.py")

        # Numerical verification with tolerance
        VerificationRecord(by="test_sir_numerics.py", tolerance=1e-6,
                          note="SIR equilibrium S*=N/R₀ within tolerance")
    """

    by: str
    """Who or what performed verification (required). Examples: "human", "test_sir.py", "Lean"."""

    date: date | None = None
    """When verification was performed (optional)."""

    note: str | None = None
    """Human-readable explanation or reference (optional)."""

    test_file: str | None = None
    """Path to test file performing verification (optional, for test-based verifications)."""

    tolerance: float | None = None
    """Numeric tolerance threshold (optional, for numerically_verified)."""

    def __post_init__(self) -> None:
        """Validate that 'by' is non-empty."""
        if not self.by or not self.by.strip():
            raise ValueError("VerificationRecord.by must be non-empty")


@dataclass
class EquationVerification:
    """Complete verification status for a single equation.

    An equation's verification is a dictionary mapping VerificationStatus → VerificationRecord.
    Unverified statuses are omitted (not set to None or False).

    Rules (enforced by tests):
    - Each equation MUST have at least one status in its verification dict.
    - Each status is independent; absence means "not yet verified", never "not applicable".
    - Unknown statuses should be omitted, never left ambiguous.

    Attributes:
        verifications: Mapping of status → record. Omitted statuses are None.

    Examples:
        # Minimal: source verified only
        eq = EquationVerification(
            verifications={
                VerificationStatus.SOURCE_VERIFIED: VerificationRecord(
                    by="human", date=date(2026, 9, 22)
                )
            }
        )
        assert eq.verifications[VerificationStatus.SOURCE_VERIFIED] is not None
        assert eq.verifications.get(VerificationStatus.FORMALLY_VERIFIED) is None

        # Full: multiple verifications
        eq = EquationVerification(
            verifications={
                VerificationStatus.SOURCE_VERIFIED: VerificationRecord(by="human", date=date(2026, 9, 22)),
                VerificationStatus.TRANSCRIPTION_VERIFIED: VerificationRecord(by="test_sir.py"),
                VerificationStatus.NUMERICALLY_VERIFIED: VerificationRecord(
                    by="test_sir_numerics.py", tolerance=1e-6
                ),
            }
        )
    """

    verifications: dict[VerificationStatus, VerificationRecord | None] = field(default_factory=dict)
    """Mapping of VerificationStatus → VerificationRecord. Omitted keys mean "not yet verified"."""

    def __post_init__(self) -> None:
        """Validate that at least one verification status is present."""
        if not self.verifications:
            raise ValueError("EquationVerification must have at least one verification status")

        # Ensure at least one record is non-None
        if all(v is None for v in self.verifications.values()):
            raise ValueError("EquationVerification must have at least one non-None verification record")

    def is_verified(self, status: VerificationStatus) -> bool:
        """Check if a specific status has been verified.

        Args:
            status: The VerificationStatus to check.

        Returns:
            True if the status has a VerificationRecord, False otherwise (including if omitted).
        """
        return self.verifications.get(status) is not None

    def all_statuses(self) -> list[VerificationStatus]:
        """Return list of all verified statuses (excluding None values).

        Returns:
            List of VerificationStatus values that have been verified.
        """
        return [status for status, record in self.verifications.items() if record is not None]
