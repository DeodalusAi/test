"""End-to-end integration tests for FastAPI application and error handlers."""

from decimal import Decimal
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}


@pytest.mark.parametrize(
    "op_a, op_b, operation, expected_result",
    [
        ("100.5", "49.5", "add", "150.0"),
        ("100.5", "49.5", "subtract", "51.0"),
        ("12.5", "4", "multiply", "50.0"),
        ("100", "8", "divide", "12.5"),
        ("-50", "-2", "multiply", "100"),
        ("-50", "25", "divide", "-2"),
    ],
)
def test_end_to_end_calculations(
    client: TestClient,
    op_a: str,
    op_b: str,
    operation: str,
    expected_result: str,
) -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"operand_a": op_a, "operand_b": op_b, "operation": operation},
    )
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert Decimal(body["result"]) == Decimal(expected_result)
    assert body["operation"] == operation
    assert "calculated_at" in body


def test_end_to_end_division_by_zero_rfc7807(client: TestClient) -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"operand_a": "100", "operand_b": "0", "operation": "divide"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    error = response.json()
    assert error["type"] == "https://errors.example.com/division-by-zero"
    assert error["title"] == "Division By Zero"
    assert error["status"] == 400
    assert "Division by zero" in error["detail"]
    assert error["instance"] == "/api/v1/calculate"


def test_end_to_end_unprocessable_entity_for_missing_field(client: TestClient) -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"operand_a": "100", "operation": "add"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_end_to_end_unprocessable_entity_for_invalid_operation(client: TestClient) -> None:
    response = client.post(
        "/api/v1/calculate",
        json={"operand_a": "100", "operand_b": "20", "operation": "modulo"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_end_to_end_unprocessable_entity_for_extra_fields(client: TestClient) -> None:
    response = client.post(
        "/api/v1/calculate",
        json={
            "operand_a": "100",
            "operand_b": "20",
            "operation": "add",
            "extra": "not-allowed",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_not_found_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == status.HTTP_404_NOT_FOUND
