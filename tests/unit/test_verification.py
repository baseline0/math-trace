"""Unit tests for verification vocabulary contracts.

Tests validate both valid and invalid states of the verification system,
ensuring the specification from AGMAI-READY.md is enforced in code.
"""

from datetime import date

import pytest

from math_trace.verification import (
    EquationVerification,
    VerificationRecord,
    VerificationStatus,
)


class TestVerificationStatus:
    """Tests for VerificationStatus enum."""

    def test_all_six_statuses_exist(self):
        """Verify all six status categories are defined."""
        statuses = [
            VerificationStatus.SOURCE_VERIFIED,
            VerificationStatus.TRANSCRIPTION_VERIFIED,
            VerificationStatus.SYMBOLIC_VERIFIED,
            VerificationStatus.NUMERICALLY_VERIFIED,
            VerificationStatus.FORMALLY_VERIFIED,
            VerificationStatus.HISTORICAL_INTERPRETATION,
        ]
        assert len(statuses) == 6
        assert len(set(statuses)) == 6  # All unique

    def test_status_values_match_spec(self):
        """Verify enum values match AGMAI-READY.md specification."""
        assert VerificationStatus.SOURCE_VERIFIED.value == "source_verified"
        assert VerificationStatus.TRANSCRIPTION_VERIFIED.value == "transcription_verified"
        assert VerificationStatus.SYMBOLIC_VERIFIED.value == "symbolic_verified"
        assert VerificationStatus.NUMERICALLY_VERIFIED.value == "numerically_verified"
        assert VerificationStatus.FORMALLY_VERIFIED.value == "formally_verified"
        assert VerificationStatus.HISTORICAL_INTERPRETATION.value == "historical_interpretation"

    def test_statuses_are_str_enum(self):
        """Verify statuses can be used as strings."""
        status = VerificationStatus.SOURCE_VERIFIED
        assert str(status) == "source_verified"
        assert status.value == "source_verified"


class TestVerificationRecord:
    """Tests for VerificationRecord dataclass."""

    def test_minimal_record(self):
        """Test creation with only required field 'by'."""
        record = VerificationRecord(by="human")
        assert record.by == "human"
        assert record.date is None
        assert record.note is None
        assert record.test_file is None
        assert record.tolerance is None

    def test_complete_record(self):
        """Test creation with all fields populated."""
        record = VerificationRecord(
            by="test_sir.py",
            date=date(2026, 9, 22),
            note="SIR equilibrium test",
            test_file="tests/unit/test_sir.py",
            tolerance=1e-6,
        )
        assert record.by == "test_sir.py"
        assert record.date == date(2026, 9, 22)
        assert record.note == "SIR equilibrium test"
        assert record.test_file == "tests/unit/test_sir.py"
        assert record.tolerance == 1e-6

    def test_human_review_record(self):
        """Test typical human review record (AGMAI example)."""
        record = VerificationRecord(
            by="human",
            date=date(2026, 9, 22),
            note="Kermack-McKendrick 1927 inspected",
        )
        assert record.by == "human"
        assert record.date == date(2026, 9, 22)
        assert record.note == "Kermack-McKendrick 1927 inspected"

    def test_test_based_record(self):
        """Test typical test-based verification record."""
        record = VerificationRecord(
            by="test_sir.py",
            date=date(2026, 9, 22),
            test_file="tests/unit/test_sir.py",
        )
        assert record.by == "test_sir.py"
        assert record.test_file == "tests/unit/test_sir.py"

    def test_numeric_verification_record(self):
        """Test typical numeric verification with tolerance."""
        record = VerificationRecord(
            by="test_sir_numerics.py",
            tolerance=1e-6,
            note="SIR equilibrium S*=N/R₀ within tolerance",
        )
        assert record.by == "test_sir_numerics.py"
        assert record.tolerance == 1e-6

    def test_by_cannot_be_empty(self):
        """Test that 'by' field cannot be empty or whitespace."""
        with pytest.raises(ValueError, match="by must be non-empty"):
            VerificationRecord(by="")

        with pytest.raises(ValueError, match="by must be non-empty"):
            VerificationRecord(by="   ")

    def test_by_required_is_validated_in_post_init(self):
        """Test validation happens during initialization."""
        # Valid
        record = VerificationRecord(by="human")
        assert record.by == "human"

        # Invalid
        with pytest.raises(ValueError):
            VerificationRecord(by="")


class TestEquationVerification:
    """Tests for EquationVerification dataclass."""

    def test_minimal_verification_single_status(self):
        """Test with single verification status (minimum required)."""
        ev = EquationVerification(verifications={VerificationStatus.SOURCE_VERIFIED: VerificationRecord(by="human")})
        assert ev.is_verified(VerificationStatus.SOURCE_VERIFIED)
        assert not ev.is_verified(VerificationStatus.FORMALLY_VERIFIED)

    def test_multiple_independent_verifications(self):
        """Test that multiple statuses can be verified independently."""
        ev = EquationVerification(
            verifications={
                VerificationStatus.SOURCE_VERIFIED: VerificationRecord(by="human", date=date(2026, 9, 22)),
                VerificationStatus.TRANSCRIPTION_VERIFIED: VerificationRecord(by="test_sir.py"),
                VerificationStatus.NUMERICALLY_VERIFIED: VerificationRecord(by="test_sir_numerics.py", tolerance=1e-6),
            }
        )
        assert ev.is_verified(VerificationStatus.SOURCE_VERIFIED)
        assert ev.is_verified(VerificationStatus.TRANSCRIPTION_VERIFIED)
        assert ev.is_verified(VerificationStatus.NUMERICALLY_VERIFIED)
        assert not ev.is_verified(VerificationStatus.FORMALLY_VERIFIED)
        assert not ev.is_verified(VerificationStatus.SYMBOLIC_VERIFIED)
        assert not ev.is_verified(VerificationStatus.HISTORICAL_INTERPRETATION)

    def test_agmai_example_json_structure(self):
        """Test the exact AGMAI-READY.md example structure (lines 157-169)."""
        ev = EquationVerification(
            verifications={
                VerificationStatus.SOURCE_VERIFIED: VerificationRecord(
                    by="human",
                    date=date(2026, 9, 22),
                    note="Kermack-McKendrick 1927 inspected",
                ),
                VerificationStatus.TRANSCRIPTION_VERIFIED: VerificationRecord(by="test_sir.py", date=date(2026, 9, 22)),
                VerificationStatus.NUMERICALLY_VERIFIED: VerificationRecord(by="test_sir_numerics.py", tolerance=1e-6),
                # AGMAI specifies null for unverified statuses; we omit them
            }
        )
        assert ev.is_verified(VerificationStatus.SOURCE_VERIFIED)
        assert ev.is_verified(VerificationStatus.TRANSCRIPTION_VERIFIED)
        assert ev.is_verified(VerificationStatus.NUMERICALLY_VERIFIED)
        # These are not in the dict (omitted, not None)
        assert not ev.is_verified(VerificationStatus.FORMALLY_VERIFIED)

    def test_all_statuses_method(self):
        """Test all_statuses() returns only verified (non-None) statuses."""
        ev = EquationVerification(
            verifications={
                VerificationStatus.SOURCE_VERIFIED: VerificationRecord(by="human"),
                VerificationStatus.NUMERICALLY_VERIFIED: VerificationRecord(by="test"),
            }
        )
        verified = ev.all_statuses()
        assert len(verified) == 2
        assert VerificationStatus.SOURCE_VERIFIED in verified
        assert VerificationStatus.NUMERICALLY_VERIFIED in verified
        assert VerificationStatus.FORMALLY_VERIFIED not in verified

    def test_requires_at_least_one_verification(self):
        """Test that empty verification dict is rejected."""
        with pytest.raises(ValueError, match="at least one verification status"):
            EquationVerification(verifications={})

    def test_rejects_all_none_verifications(self):
        """Test that dict with only None values is rejected."""
        with pytest.raises(ValueError, match="at least one non-None"):
            EquationVerification(
                verifications={
                    VerificationStatus.SOURCE_VERIFIED: None,
                    VerificationStatus.FORMALLY_VERIFIED: None,
                }
            )

    def test_is_verified_checks_specific_status(self):
        """Test is_verified() method for specific status checks."""
        record = VerificationRecord(by="test_sir.py")
        ev = EquationVerification(verifications={VerificationStatus.TRANSCRIPTION_VERIFIED: record})

        assert ev.is_verified(VerificationStatus.TRANSCRIPTION_VERIFIED) is True
        assert ev.is_verified(VerificationStatus.SOURCE_VERIFIED) is False
        assert ev.is_verified(VerificationStatus.FORMALLY_VERIFIED) is False

    def test_historical_interpretation_verification(self):
        """Test historical_interpretation status (human-curated claim)."""
        ev = EquationVerification(
            verifications={
                VerificationStatus.HISTORICAL_INTERPRETATION: VerificationRecord(
                    by="human",
                    note="This formulation became standard after 1970",
                )
            }
        )
        assert ev.is_verified(VerificationStatus.HISTORICAL_INTERPRETATION)

    def test_formal_verification_with_lean(self):
        """Test formally_verified status with Lean theorem prover."""
        ev = EquationVerification(
            verifications={
                VerificationStatus.FORMALLY_VERIFIED: VerificationRecord(
                    by="Lean",
                    note="conservation law proven under assumptions",
                )
            }
        )
        assert ev.is_verified(VerificationStatus.FORMALLY_VERIFIED)

    def test_symbolic_verification(self):
        """Test symbolic_verified status."""
        ev = EquationVerification(
            verifications={
                VerificationStatus.SYMBOLIC_VERIFIED: VerificationRecord(
                    by="test_algebra.py",
                    note="SIR + SEIR identity proven",
                )
            }
        )
        assert ev.is_verified(VerificationStatus.SYMBOLIC_VERIFIED)


class TestVerificationIndependence:
    """Tests validating the independence principle from AGMAI-READY.md."""

    def test_each_status_independent_subset_combinations(self):
        """Test all combinations of status independence."""
        # Test that we can have any subset without requirement of others
        combinations = [
            {VerificationStatus.SOURCE_VERIFIED},
            {VerificationStatus.TRANSCRIPTION_VERIFIED},
            {VerificationStatus.SOURCE_VERIFIED, VerificationStatus.FORMALLY_VERIFIED},
            {
                VerificationStatus.SOURCE_VERIFIED,
                VerificationStatus.TRANSCRIPTION_VERIFIED,
                VerificationStatus.SYMBOLIC_VERIFIED,
            },
        ]

        for combo in combinations:
            verifications = {status: VerificationRecord(by="test") for status in combo}
            ev = EquationVerification(verifications=verifications)
            # All in combo should be verified, all others should not
            for status in VerificationStatus:
                if status in combo:
                    assert ev.is_verified(status), f"{status} should be verified"
                else:
                    assert not ev.is_verified(status), f"{status} should not be verified"

    def test_transcription_without_source_valid(self):
        """Test that transcription can be verified without source verification."""
        # This is explicitly allowed by independence principle
        ev = EquationVerification(
            verifications={VerificationStatus.TRANSCRIPTION_VERIFIED: VerificationRecord(by="test_sir.py")}
        )
        assert ev.is_verified(VerificationStatus.TRANSCRIPTION_VERIFIED)
        assert not ev.is_verified(VerificationStatus.SOURCE_VERIFIED)

    def test_numeric_without_symbolic_valid(self):
        """Test that numeric verification doesn't require symbolic verification."""
        ev = EquationVerification(
            verifications={
                VerificationStatus.NUMERICALLY_VERIFIED: VerificationRecord(by="test_numerics.py", tolerance=1e-6)
            }
        )
        assert ev.is_verified(VerificationStatus.NUMERICALLY_VERIFIED)
        assert not ev.is_verified(VerificationStatus.SYMBOLIC_VERIFIED)


class TestVerificationSchemaIntegration:
    """Integration tests for complete verification workflows."""

    def test_sir_epidemiology_complete_example(self):
        """Test the complete SIR example from AGMAI-READY.md."""
        # From AGMAI-READY.md lines 157-169
        ev = EquationVerification(
            verifications={
                VerificationStatus.SOURCE_VERIFIED: VerificationRecord(
                    by="human",
                    date=date(2026, 9, 22),
                    note="Kermack-McKendrick 1927 inspected",
                ),
                VerificationStatus.TRANSCRIPTION_VERIFIED: VerificationRecord(by="test_sir.py", date=date(2026, 9, 22)),
                VerificationStatus.NUMERICALLY_VERIFIED: VerificationRecord(by="test_sir_numerics.py", tolerance=1e-6),
            }
        )

        assert ev.all_statuses() == [
            VerificationStatus.SOURCE_VERIFIED,
            VerificationStatus.TRANSCRIPTION_VERIFIED,
            VerificationStatus.NUMERICALLY_VERIFIED,
        ]

    def test_minimal_source_only_equation(self):
        """Test minimal equation (source verified only)."""
        ev = EquationVerification(
            verifications={
                VerificationStatus.SOURCE_VERIFIED: VerificationRecord(
                    by="human",
                    date=date(2026, 9, 22),
                    note="Paper reviewed",
                )
            }
        )
        assert len(ev.all_statuses()) == 1
        assert ev.is_verified(VerificationStatus.SOURCE_VERIFIED)

    def test_historical_interpretation_standalone(self):
        """Test historical claim can exist on its own."""
        ev = EquationVerification(
            verifications={
                VerificationStatus.HISTORICAL_INTERPRETATION: VerificationRecord(
                    by="human",
                    note="Standard formulation post-1970",
                )
            }
        )
        assert ev.is_verified(VerificationStatus.HISTORICAL_INTERPRETATION)
        assert len(ev.all_statuses()) == 1
