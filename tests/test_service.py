"""Unit tests targeting the arithmetic domain service."""

from decimal import Decimal
import pytest
from app.exceptions import DivisionByZeroError, InvalidOperatorError
from app.schemas import CalculationRequest, OperationType
from app.service import CalculatorService


@pytest.fixture
def service() -> CalculatorService:
    return CalculatorService()


def test_service_addition(service: CalculatorService) -> None:
    req = CalculationRequest(
        operand_a=Decimal("10.25"),
        operand_b=Decimal("5.75"),
        operation=OperationType.ADD,
    )
    res = service.calculate(req)
    assert res.result == Decimal("16.00")
    assert res.operation == OperationType.ADD


def test_service_subtraction(service: CalculatorService) -> None:
    req = CalculationRequest(
        operand_a=Decimal("10.50"),
        operand_b=Decimal("12.75"),
        operation=OperationType.SUBTRACT,
    )
    res = service.calculate(req)
    assert res.result == Decimal("-2.25")


def test_service_multiplication(service: CalculatorService) -> None:
    req = CalculationRequest(
        operand_a=Decimal("3.5"),
        operand_b=Decimal("2.0"),
        operation=OperationType.MULTIPLY,
    )
    res = service.calculate(req)
    assert res.result == Decimal("7.00")


def test_service_division(service: CalculatorService) -> None:
    req = CalculationRequest(
        operand_a=Decimal("10"),
        operand_b=Decimal("4"),
        operation=OperationType.DIVIDE,
    )
    res = service.calculate(req)
    assert res.result == Decimal("2.5")


def test_service_precision_preservation_avoids_drift(service: CalculatorService) -> None:
    # 0.1 + 0.2 in floating point produces 0.30000000000000004
    req = CalculationRequest(
        operand_a=Decimal("0.1"),
        operand_b=Decimal("0.2"),
        operation=OperationType.ADD,
    )
    res = service.calculate(req)
    assert res.result == Decimal("0.3")


def test_service_extreme_numbers(service: CalculatorService) -> None:
    huge = Decimal("1" + "0" * 30)
    req = CalculationRequest(
        operand_a=huge,
        operand_b=huge,
        operation=OperationType.ADD,
    )
    res = service.calculate(req)
    assert res.result == Decimal("2" + "0" * 30)


def test_service_division_by_zero_raises(service: CalculatorService) -> None:
    req = CalculationRequest(
        operand_a=Decimal("42"),
        operand_b=Decimal("0"),
        operation=OperationType.DIVIDE,
    )
    with pytest.raises(DivisionByZeroError) as exc_info:
        service.calculate(req)
    assert "Division by zero" in exc_info.value.message


def test_service_invalid_operator_branch(service: CalculatorService) -> None:
    req = CalculationRequest(
        operand_a=Decimal("1"),
        operand_b=Decimal("1"),
        operation=OperationType.ADD,
    )
    # Override with invalid operation to test domain guard
    object.__setattr__(req, "operation", "unsupported_op")
    with pytest.raises(InvalidOperatorError):
        service.calculate(req)
