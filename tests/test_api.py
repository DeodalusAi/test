"""Integration tests for FastAPI conversion endpoints."""

import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "roman-numeral-converter"}


@pytest.mark.parametrize(
    "endpoint_prefix",
    ["", "/api/v1"],
)
class TestConversionEndpoints:
    def test_post_to_roman_success(self, endpoint_prefix: str) -> None:
        response = client.post(f"{endpoint_prefix}/convert/to-roman", json={"value": 1994})
        assert response.status_code == 200
        data = response.json()
        assert data["arabic"] == 1994
        assert data["roman"] == "MCMXCIV"

    def test_get_to_roman_success(self, endpoint_prefix: str) -> None:
        response = client.get(f"{endpoint_prefix}/convert/to-roman?value=3999")
        assert response.status_code == 200
        data = response.json()
        assert data["arabic"] == 3999
        assert data["roman"] == "MMMCMXCIX"

    def test_post_to_arabic_success(self, endpoint_prefix: str) -> None:
        response = client.post(f"{endpoint_prefix}/convert/to-arabic", json={"roman": "MMXXIV"})
        assert response.status_code == 200
        data = response.json()
        assert data["roman"] == "MMXXIV"
        assert data["arabic"] == 2024

    def test_get_to_arabic_success(self, endpoint_prefix: str) -> None:
        response = client.get(f"{endpoint_prefix}/convert/to-arabic?roman=XLII")
        assert response.status_code == 200
        data = response.json()
        assert data["roman"] == "XLII"
        assert data["arabic"] == 42

    def test_post_to_roman_boundary_edge_cases(self, endpoint_prefix: str) -> None:
        # Lower boundary
        r_min = client.post(f"{endpoint_prefix}/convert/to-roman", json={"value": 1})
        assert r_min.status_code == 200
        assert r_min.json() == {"arabic": 1, "roman": "I"}

        # Upper boundary
        r_max = client.post(f"{endpoint_prefix}/convert/to-roman", json={"value": 3999})
        assert r_max.status_code == 200
        assert r_max.json() == {"arabic": 3999, "roman": "MMMCMXCIX"}

    def test_post_to_roman_out_of_bounds_422(self, endpoint_prefix: str) -> None:
        for invalid_val in [0, 4000, -10]:
            response = client.post(f"{endpoint_prefix}/convert/to-roman", json={"value": invalid_val})
            assert response.status_code == 422

    def test_get_to_roman_out_of_bounds_422(self, endpoint_prefix: str) -> None:
        for invalid_val in [0, 4000]:
            response = client.get(f"{endpoint_prefix}/convert/to-roman?value={invalid_val}")
            assert response.status_code == 422

    def test_post_to_arabic_malformed_input_422(self, endpoint_prefix: str) -> None:
        for invalid_roman in ["IIII", "VV", "ABC", "MMMM", "IXI"]:
            response = client.post(f"{endpoint_prefix}/convert/to-arabic", json={"roman": invalid_roman})
            assert response.status_code == 422

    def test_get_to_arabic_malformed_input_400(self, endpoint_prefix: str) -> None:
        for invalid_roman in ["IIII", "MMMM", "XYZ"]:
            response = client.get(f"{endpoint_prefix}/convert/to-arabic?roman={invalid_roman}")
            assert response.status_code == 400

    def test_empty_payload_post(self, endpoint_prefix: str) -> None:
        r1 = client.post(f"{endpoint_prefix}/convert/to-roman", json={})
        assert r1.status_code == 422
        r2 = client.post(f"{endpoint_prefix}/convert/to-arabic", json={})
        assert r2.status_code == 422
