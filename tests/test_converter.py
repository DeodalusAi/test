"""Comprehensive test suite for Roman Numeral conversion service and boundary transitions."""

import pytest
from fastapi.testclient import TestClient

from app.domain.converter import from_roman, to_roman
from app.main import app

client = TestClient(app)

# Boundary transition matrices for off-by-one testing
BOUNDARY_CASES = [
    # 1 lower bound
    (1, "I"),
    # 3-4-5 transitions
    (3, "III"),
    (4, "IV"),
    (5, "V"),
    # 8-9-10 transitions
    (8, "VIII"),
    (9, "IX"),
    (10, "X"),
    # 39-40-41 transitions
    (39, "XXXIX"),
    (40, "XL"),
    (41, "XLI"),
    # 89-90-91 transitions
    (89, "LXXXIX"),
    (90, "XC"),
    (91, "XCI"),
    # 399-400-401 transitions
    (399, "CCCXCIX"),
    (400, "CD"),
    (401, "CDI"),
    # 899-900-901 transitions
    (899, "DCCCXCIX"),
    (900, "CM"),
    (901, "CMI"),
    # Intermediate checks
    (1994, "MCMXCIV"),
    (2023, "MMXXIII"),
    # 3999 upper bound
    (3999, "MMMCMXCIX"),
]


@pytest.mark.parametrize("expected_int, roman_str", BOUNDARY_CASES)
def test_domain_to_roman_boundaries(expected_int: int, roman_str: str) -> None:
    """Verify correct to_roman domain translation across key boundary steps."""
    assert to_roman(expected_int) == roman_str


@pytest.mark.parametrize("expected_int, roman_str", BOUNDARY_CASES)
def test_domain_from_roman_boundaries(expected_int: int, roman_str: str) -> None:
    """Verify correct from_roman domain translation across key boundary steps."""
    assert from_roman(roman_str) == expected_int


@pytest.mark.parametrize("out_of_bound_num", [0, -1, -500, 4000, 4001, 10000])
def test_domain_to_roman_out_of_bounds(out_of_bound_num: int) -> None:
    """Verify ValueError on out-of-range integer to Roman domain inputs."""
    with pytest.raises(ValueError, match="out of valid range"):
        to_roman(out_of_bound_num)


@pytest.mark.parametrize(
    "invalid_roman",
    [
        "",
        "   ",
        "IIII",
        "VV",
        "XXXX",
        "CCCC",
        "MMMM",
        "IC",
        "IL",
        "XD",
        "XM",
        "VX",
        "ABC",
        "123",
        "IVX",
    ],
)
def test_domain_from_roman_invalid_inputs(invalid_roman: str) -> None:
    """Verify ValueError on malformed or non-canonical Roman domain inputs."""
    with pytest.raises(ValueError):
        from_roman(invalid_roman)


@pytest.mark.parametrize("expected_int, roman_str", BOUNDARY_CASES)
def test_api_to_roman_boundary_transitions(expected_int: int, roman_str: str) -> None:
    """Verify API endpoint /convert/to-roman with boundary transitions."""
    response = client.post("/convert/to-roman", json={"number": expected_int})
    assert response.status_code == 200
    data = response.json()
    assert data == {"number": expected_int, "roman": roman_str}


@pytest.mark.parametrize("expected_int, roman_str", BOUNDARY_CASES)
def test_api_from_roman_boundary_transitions(expected_int: int, roman_str: str) -> None:
    """Verify API endpoint /convert/to-integer with boundary transitions."""
    response = client.post("/convert/to-integer", json={"roman": roman_str})
    assert response.status_code == 200
    data = response.json()
    assert data == {"roman": roman_str, "number": expected_int}


@pytest.mark.parametrize("out_of_bound_num", [0, -1, 4000, 5000])
def test_api_to_roman_validation_error(out_of_bound_num: int) -> None:
    """Verify HTTP 422 Unprocessable Entity when integer violates boundary constraints."""
    response = client.post("/convert/to-roman", json={"number": out_of_bound_num})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.parametrize(
    "invalid_roman",
    ["", "IIII", "MMMM", "IL", "invalid", "12"]
)
def test_api_from_roman_validation_error(invalid_roman: str) -> None:
    """Verify HTTP 422 Unprocessable Entity on schema validation failure for Roman numerals."""
    response = client.post("/convert/to-integer", json={"roman": invalid_roman})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_api_extra_fields_forbidden() -> None:
    """Verify extra fields are rejected according to schema config."""
    response = client.post("/convert/to-roman", json={"number": 10, "extra": "val"})
    assert response.status_code == 422


def test_api_invalid_payload_type() -> None:
    """Verify HTTP 422 when payload type is mismatched."""
    response = client.post("/convert/to-roman", json={"number": "not-a-number"})
    assert response.status_code == 422
