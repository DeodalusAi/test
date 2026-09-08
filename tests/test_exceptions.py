"""Unit tests for custom calculator domain exceptions."""

from app.exceptions import CalculatorException, DivisionByZeroError, InvalidOperatorError


def test_calculator_exception_inheritance() -> None:
    exc = CalculatorException("Domain evaluation failed.")
    assert isinstance(exc, Exception)
    assert exc.message == "Domain evaluation failed."
    assert str(exc) == "Domain evaluation failed."


def test_division_by_zero_error_defaults() -> None:
    exc = DivisionByZeroError()
    assert isinstance(exc, CalculatorException)
    assert exc.message == "Cannot divide by zero."


def test_division_by_zero_error_custom_message() -> None:
    exc = DivisionByZeroError("Custom zero error")
    assert exc.message == "Custom zero error"


def test_invalid_operator_error_defaults() -> None:
    exc = InvalidOperatorError()
    assert isinstance(exc, CalculatorException)
    assert exc.message == "Unsupported arithmetic operator provided."


def test_invalid_operator_error_custom_message() -> None:
    exc = InvalidOperatorError("Unknown: POW")
    assert exc.message == "Unknown: POW"
