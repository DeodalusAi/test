"""Unit tests for Pydantic v2 data models and serialization contracts."""

from decimal import Decimal
import pytest
from pydantic import ValidationError
from app.schemas import CalculationRequest, CalculationResponse, OperationType, ProblemDetail


def test_operation_type_enum_values() -> None:
    assert OperationType.ADD == "add"
    assert OperationType.SUBTRACT == "subtract"
    assert OperationType.MULTIPLY == "multiply"
    assert OperationType.DIVIDE == "divide"


def test_calculation_request_valid_decimal_coercion() -> None:
    payload = {
        "operand_a": "10.55",
        "operand_b": 4,
        "operation": "add",
    }
    request = CalculationRequest(**payload)
    assert request.operand_a == Decimal("10.55")
    assert request.operand_b == Decimal("4")
    assert request.operation == OperationType.ADD


def test_calculation_request_extra_fields_forbidden() -> None:
    payload = {
        "operand_a": "10",
        "operand_b": "5",
        "operation": "subtract",
        "unexpected_field": "malicious",
    }
    with pytest.raises(ValidationError) as exc_info:
        CalculationRequest(**payload)
    assert "extra_forbidden" in str(exc_info.value)


def test_calculation_request_invalid_operator() -> None:
    payload = {
        "operand_a": "10",
        "operand_b": "5",
        "operation": "modulus",
    }
    with pytest.raises(ValidationError):
        CalculationRequest(**payload)


def test_calculation_request_invalid_non_numeric_operand() -> None:
    payload = {
        "operand_a": "not-a-number",
        "operand_b": "5",
        "operation": "add",
    }
    with pytest.raises(ValidationError):
        CalculationRequest(**payload)


def test_calculation_response_serialization() -> None:
    response = CalculationResponse(
        operand_a=Decimal("1.23"),
        operand_b=Decimal("4.56"),
        operation=OperationType.MULTIPLY,
        result=Decimal("5.6088"),
    )
    data = response.model_dump()
    assert data["operand_a"] == Decimal("1.23")
    assert data["operand_b"] == Decimal("4.56")
    assert data["operation"] == OperationType.MULTIPLY
    assert data["result"] == Decimal("5.6088")
    assert "calculated_at" in data


def test_problem_detail_model() -> None:
    problem = ProblemDetail(
        type="https://errors.example.com/not-found",
        title="Not Found",
        status=404,
        detail="Resource unavailable",
        instance="/api/v1/resource",
    )
    dump = problem.model_dump()
    assert dump["status"] == 404
    assert dump["title"] == "Not Found"
    assert dump["instance"] == "/api/v1/resource"
