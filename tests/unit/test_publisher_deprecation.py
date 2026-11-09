"""TypstPublisher is deprecated in favour of tool-publish (`tool-publish render-typst`)."""

from __future__ import annotations

import warnings

import pytest

from math_trace.publishers import TypstPublisher


def test_constructing_typst_publisher_emits_deprecation_warning() -> None:
    with pytest.warns(DeprecationWarning, match="tool-publish"):
        TypstPublisher()


def test_deprecation_warning_points_at_the_caller() -> None:
    with pytest.warns(DeprecationWarning) as record:
        TypstPublisher()
    assert record[0].filename == __file__


def test_typst_publisher_still_constructs_and_is_a_publisher() -> None:
    from math_trace.publishers import Publisher

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        publisher = TypstPublisher()
    assert isinstance(publisher, Publisher)
