"""Comprehensive domain unit tests for bidirectional Roman numeral conversions with off-by-one boundary cases."""

import pytest
from app.core.converter import int_to_roman, roman_to_int


@pytest.mark.parametrize(
    "arabic, expected_roman",
    [
        # Boundary: Min valid value
        (1, "I"),
        (2, "II"),
        # Boundary: Additive to subtractive transition (3 vs 4)
        (3, "III"),
        (4, "IV"),
        # Boundary: Subtractive to base (4 vs 5)
        (5, "V"),
        (6, "VI"),
        (7, "VII"),
        # Boundary: Upper subtractive boundary (8 vs 9 vs 10)
        (8, "VIII"),
        (9, "IX"),
        (10, "X"),
        # Additional transitional checkpoints
        (39, "XXXIX"),
        (40, "XL"),
        (49, "XLIX"),
        (50, "L"),
        (89, "LXXXIX"),
        (90, "XC"),
        (99, "XCIX"),
        (100, "C"),
        (399, "CCCXCIX"),
        (400, "CD"),
        (499, "CDXCIX"),
        (500, "D"),
        (899, "DCCCXCIX"),
        (900, "CM"),
        (999, "CMXCIX"),
        (1000, "M"),
        (1994, "MCMXCIV"),
        (2024, "MMXXIV"),
        (3000, "MMM"),
        # Boundary: Max valid value
        (3999, "MMMCMXCIX"),
    ],
)
def test_int_to_roman_valid_cases(arabic: int, expected_roman: str) -> None:
    assert int_to_roman(arabic) == expected_roman


@pytest.mark.parametrize(
    "roman, expected_arabic",
    [
        ("I", 1),
        ("II", 2),
        ("III", 3),
        ("IV", 4),
        ("V", 5),
        ("VI", 6),
        ("VII", 7),
        ("VIII", 8),
        ("IX", 9),
        ("X", 10),
        ("XXXIX", 39),
        ("XL", 40),
        ("XLIX", 49),
        ("L", 50),
        ("XC", 90),
        ("C", 100),
        ("CD", 400),
        ("D", 500),
        ("CM", 900),
        ("M", 1000),
        ("MCMXCIV", 1994),
        ("MMXXIV", 2024),
        ("MMMCMXCIX", 3999),
    ],
)
def test_roman_to_int_valid_cases(roman: str, expected_arabic: int) -> None:
    assert roman_to_int(roman) == expected_arabic


def test_roman_to_int_case_insensitive_and_whitespace() -> None:
    assert roman_to_int("  iv  ") == 4
    assert roman_to_int("mmmcmxcix") == 3999
    assert roman_to_int("  Xiv ") == 14


@pytest.mark.parametrize(
    "invalid_arabic",
    [
        -100,
        -1,
        0,     # Lower out-of-bounds boundary
        4000,  # Upper out-of-bounds boundary
        4001,
        10000,
    ],
)
def test_int_to_roman_range_errors(invalid_arabic: int) -> None:
    with pytest.raises(ValueError, match="out of bounds"):
        int_to_roman(invalid_arabic)


@pytest.mark.parametrize(
    "invalid_type_value",
    [None, 1.5, "10", True, False, [], {}],
)
def test_int_to_roman_type_errors(invalid_type_value: object) -> None:
    with pytest.raises(TypeError):
        int_to_roman(invalid_type_value)  # type: ignore


@pytest.mark.parametrize(
    "invalid_roman",
    [
        "",            # Empty string
        "   ",         # Whitespace string
        "IIII",        # 4 identical numerals repeated
        "VV",          # Repeated 5s
        "XXXX",        # 4 identical 10s
        "LL",          # Repeated 50s
        "CCCC",        # 4 identical 100s
        "DD",          # Repeated 500s
        "MMMM",        # 4000 invalid upper bound repetition
        "IL",          # Non-standard subtractive pair
        "IC",          # Non-standard subtractive pair
        "ID",          # Non-standard subtractive pair
        "IM",          # Non-standard subtractive pair
        "VX",          # V cannot be subtracted
        "VL",          # V cannot be subtracted
        "XD",          # X can only precede L or C
        "XM",          # X can only precede L or C
        "LC",          # L cannot be subtracted
        "DM",          # D cannot be subtracted
        "IIV",         # Double subtraction
        "XXL",         # Double subtraction
        "CCD",         # Double subtraction
        "IXI",         # Invalid additive post-subtractive ordering
        "ABC",         # Invalid characters
        "XIV1",        # Mixed characters
    ],
)
def test_roman_to_int_invalid_sequences(invalid_roman: str) -> None:
    with pytest.raises(ValueError):
        roman_to_int(invalid_roman)


@pytest.mark.parametrize(
    "invalid_type",
    [None, 10, True, 3.14, ["X"], {"roman": "X"}],
)
def test_roman_to_int_type_errors(invalid_type: object) -> None:
    with pytest.raises(TypeError):
        roman_to_int(invalid_type)  # type: ignore


def test_bidirectional_roundtrip_all_boundary_transitions() -> None:
    critical_boundaries = [
        1, 2, 3, 4, 5, 8, 9, 10,
        39, 40, 41, 49, 50, 51,
        89, 90, 91, 99, 100, 101,
        399, 400, 401, 499, 500, 501,
        899, 900, 901, 999, 1000, 1001,
        3998, 3999,
    ]
    for val in critical_boundaries:
        roman = int_to_roman(val)
        back_to_arabic = roman_to_int(roman)
        assert back_to_arabic == val, f"Mismatch for value {val}: got {back_to_arabic} via {roman}"
