import pytest
from starlette.testclient import TestClient
from app.core.converter import integer_to_roman, roman_to_integer
from app.exceptions import InvalidRomanNumeralException, OutOfRangeIntegerException
from app.main import app

client = TestClient(app)


# =========================================================================
# CORE DOMAIN UNIT TESTS: Integer to Roman
# =========================================================================

@pytest.mark.parametrize(
    "integer_val, expected_roman",
    [
        # Boundary lower values
        (1, "I"),
        (2, "II"),
        (3, "III"),
        (4, "IV"),
        (5, "V"),
        # Subtractive and threshold checks
        (8, "VIII"),
        (9, "IX"),
        (10, "X"),
        (14, "XIV"),
        (39, "XXXIX"),
        (40, "XL"),
        (44, "XLIV"),
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
        (1984, "MCMLXXXIV"),
        (2023, "MMXXIII"),
        (2026, "MMXXVI"),
        # Upper boundary threshold
        (3998, "MMMCMXCVIII"),
        (3999, "MMMCMXCIX"),
    ],
)
def test_integer_to_roman_valid(integer_val: int, expected_roman: str) -> None:
    assert integer_to_roman(integer_val) == expected_roman


@pytest.mark.parametrize(
    "invalid_integer",
    [
        0,
        -1,
        -100,
        4000,
        4001,
        10000,
    ],
)
def test_integer_to_roman_out_of_range(invalid_integer: int) -> None:
    with pytest.raises(OutOfRangeIntegerException) as exc_info:
        integer_to_roman(invalid_integer)
    assert "is out of range" in exc_info.value.message


# =========================================================================
# CORE DOMAIN UNIT TESTS: Roman to Integer
# =========================================================================

@pytest.mark.parametrize(
    "roman_val, expected_integer",
    [
        ("I", 1),
        ("II", 2),
        ("III", 3),
        ("IV", 4),
        ("V", 5),
        ("VIII", 8),
        ("IX", 9),
        ("X", 10),
        ("XIV", 14),
        ("XXXIX", 39),
        ("XL", 40),
        ("XLIV", 44),
        ("XLIX", 49),
        ("L", 50),
        ("XC", 90),
        ("XCIX", 99),
        ("C", 100),
        ("CD", 400),
        ("D", 500),
        ("CM", 900),
        ("CMXCIX", 999),
        ("M", 1000),
        ("MCMLXXXIV", 1984),
        ("MMMCMXCVIII", 3998),
        ("MMMCMXCIX", 3999),
        # Case-insensitivity and whitespace handling
        ("  mmmcmxcix  ", 3999),
        ("mcmlxxxiv", 1984),
        ("iv", 4),
    ],
)
def test_roman_to_integer_valid(roman_val: str, expected_integer: int) -> None:
    assert roman_to_integer(roman_val) == expected_integer


@pytest.mark.parametrize(
    "invalid_roman",
    [
        "",
        "   ",
        "IIII",           # Over 3 consecutive I's
        "XXXX",           # Over 3 consecutive X's
        "CCCC",           # Over 3 consecutive C's
        "MMMM",           # Above 3999
        "VV",             # Repeating non-repeating numeral V
        "LL",             # Repeating non-repeating numeral L
        "DD",             # Repeating non-repeating numeral D
        "IL",             # Invalid subtractive rule (I can only precede V and X)
        "IC",             # Invalid subtractive rule
        "ID",             # Invalid subtractive rule
        "IM",             # Invalid subtractive rule
        "VX",             # V cannot be subtracted
        "XD",             # X can only precede L and C
        "XM",             # X can only precede L and C
        "LC",             # L cannot be subtracted
        "DM",             # D cannot be subtracted
        "IIV",            # Multiple smaller prefix numerals
        "IXI",            # Ambiguous/invalid sequence
        "ABC",            # Non-Roman characters
        "123",            # Digits
        "IV1",            # Mixed alphanumerics
    ],
)
def test_roman_to_integer_invalid(invalid_roman: str) -> None:
    with pytest.raises(InvalidRomanNumeralException):
        roman_to_integer(invalid_roman)


# =========================================================================
# BIDIRECTIONAL ROUNDTRIP PROPERTY TEST
# =========================================================================

def test_bidirectional_roundtrip_all_subtractive_cases() -> None:
    key_values = [1, 4, 5, 9, 10, 40, 50, 90, 100, 400, 500, 900, 1000, 3999]
    for val in key_values:
        roman = integer_to_roman(val)
        assert roman_to_integer(roman) == val


# =========================================================================
# HTTP API INTEGRATION TESTS
# =========================================================================

def test_api_convert_to_roman_success() -> None:
    resp = client.post("/api/v1/convert/to-roman", json={"value": 1984})
    assert resp.status_code == 200
    assert resp.json() == {"value": 1984, "roman": "MCMLXXXIV"}


def test_api_convert_to_roman_boundary_values() -> None:
    # Lower bound (1)
    resp_low = client.post("/api/v1/convert/to-roman", json={"value": 1})
    assert resp_low.status_code == 200
    assert resp_low.json() == {"value": 1, "roman": "I"}

    # Upper bound (3999)
    resp_high = client.post("/api/v1/convert/to-roman", json={"value": 3999})
    assert resp_high.status_code == 200
    assert resp_high.json() == {"value": 3999, "roman": "MMMCMXCIX"}


@pytest.mark.parametrize("out_of_bound_val", [0, -1, 4000, 4001, 10000])
def test_api_convert_to_roman_out_of_range(out_of_bound_val: int) -> None:
    resp = client.post("/api/v1/convert/to-roman", json={"value": out_of_bound_val})
    assert resp.status_code == 400
    data = resp.json()
    assert "detail" in data
    assert "is out of range" in data["detail"]


def test_api_convert_to_roman_unprocessable_payload() -> None:
    resp = client.post("/api/v1/convert/to-roman", json={"value": "not-a-number"})
    assert resp.status_code == 422


def test_api_convert_from_roman_success() -> None:
    resp = client.post("/api/v1/convert/from-roman", json={"roman": "MMXXVI"})
    assert resp.status_code == 200
    assert resp.json() == {"roman": "MMXXVI", "value": 2026}


def test_api_convert_from_roman_case_insensitive() -> None:
    resp = client.post("/api/v1/convert/from-roman", json={"roman": "xiv"})
    assert resp.status_code == 200
    assert resp.json() == {"roman": "XIV", "value": 14}


@pytest.mark.parametrize("invalid_roman_str", ["IIII", "VV", "IL", "VX", "MMMM", "foo"])
def test_api_convert_from_roman_invalid_numeral(invalid_roman_str: str) -> None:
    resp = client.post("/api/v1/convert/from-roman", json={"roman": invalid_roman_str})
    assert resp.status_code == 400
    data = resp.json()
    assert "detail" in data


def test_api_convert_from_roman_empty_string_validation() -> None:
    resp = client.post("/api/v1/convert/from-roman", json={"roman": ""})
    assert resp.status_code == 422
