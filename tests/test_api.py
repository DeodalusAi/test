"""Integration tests for API router endpoints and dependency injection."""

from decimal import Decimal
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from app.api import get_calculator_service, router
from app.schemas import CalculationRequest, CalculationResponse, OperationType
from app.service import CalculatorService


def test_router_calculate_success() -> None:
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    response = client.post(
        "/api/v1/calculate",
        json={
            "operand_a": "15",
            "operand_b": "3",
            "operation": "divide",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["result"] == "5"
    assert data["operation"] == "divide"


def test_router_dependency_injection_override() -> None:
    app = FastAPI()
    app.include_router(router)

    class MockCalculatorService(CalculatorService):
        @staticmethod
        def calculate(request: CalculationRequest) -> CalculationResponse:
            return CalculationResponse(
                operand_a=request.operand_a,
                operand_b=request.operand_b,
                operation=request.operation,
                result=Decimal("999.99"),
            )

    app.dependency_overrides[get_calculator_service] = lambda: MockCalculatorService()
    client = TestClient(app)

    response = client.post(
        "/api/v1/calculate",
        json={
            "operand_a": "1",
            "operand_b": "1",
            "operation": "add",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["result"] == "999.99"
