"""Standard API response types for math-trace.

All endpoints should return ApiResponse for consistent error handling
and client expectations.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Generic, TypeVar

from .constants import API_STATUS_SUCCESS, API_STATUS_ERROR

T = TypeVar("T")


@dataclass
class ApiResponse(Generic[T]):
    """Standard API response wrapper.

    All API endpoints should return this format to ensure:
    - Consistent error handling on clients
    - Predictable response structure
    - Clear distinction between success and error cases
    """

    status: str
    """Either "success" or "error"."""

    data: T | None = None
    """Response payload (only present on success)."""

    error: str | None = None
    """Error message (only present on error)."""

    message: str | None = None
    """Additional context message."""

    code: int = 200
    """HTTP status code (for reference)."""

    @staticmethod
    def success(data: Any, message: str | None = None, code: int = 200) -> ApiResponse:
        """Create a success response.

        Args:
            data: Response payload
            message: Optional additional context
            code: HTTP status code

        Returns:
            ApiResponse with status="success"
        """
        return ApiResponse(
            status=API_STATUS_SUCCESS,
            data=data,
            message=message,
            code=code,
        )

    @staticmethod
    def error(error: str, message: str | None = None, code: int = 400) -> ApiResponse:
        """Create an error response.

        Args:
            error: Error message
            message: Optional additional context
            code: HTTP status code

        Returns:
            ApiResponse with status="error"
        """
        return ApiResponse(
            status=API_STATUS_ERROR,
            error=error,
            message=message,
            code=code,
        )

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict.

        Only includes non-None fields for cleaner JSON.
        """
        result = {"status": self.status}

        if self.data is not None:
            result["data"] = self.data

        if self.error is not None:
            result["error"] = self.error

        if self.message is not None:
            result["message"] = self.message

        return result
