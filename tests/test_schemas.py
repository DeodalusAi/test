"""Unit tests for Pydantic conversion schemas."""

import pytest
from pydantic import ValidationError
from app.schemas.numeral import (
    ToArabicRequest,
    ToArabicResponse,
    ToRomanRequest,
    ToRomanResponse,
)


def test_to_roman_request_valid() -> None:
    req = ToRomanRequest(value=42)
    assert req.value == 42


@pytest.mark.parametrize("invalid_val", [0, -1, 4000, 5000])
def test_to_roman_request_bounds(invalid_val: int) -> None:
    with pytest.raises(ValidationError):
        ToRomanRequest(value=invalid_val)


def test_to_roman_response_model() -> None:
    resp = ToRomanResponse(arabic=10, roman="X")
    assert resp.arabic == 10
    assert resp.roman == "X"


def test_to_arabic_request_valid() -> None:
    req = ToArabicRequest(roman="XIV")
    assert req.roman == "XIV"


def test_to_arabic_request_normalizes_case_and_strip() -> None:
    req = ToArabicRequest(roman="  xciii ")
    assert req.roman == "XCIII"


@pytest.mark.parametrize("invalid_roman", ["", "   ", "IIII", "IVX", "MMMM", "123", "foo"])
def test_to_arabic_request_invalid(invalid_roman: str) -> None:
    with pytest.raises(ValidationError):
        ToArabicRequest(roman=invalid_roman)


def test_to_arabic_response_model() -> None:
    resp = ToArabicResponse(roman="X", arabic=10)
    assert resp.roman == "X"
    assert resp.arabic == 10
