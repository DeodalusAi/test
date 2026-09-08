"""Domain exception hierarchy for arithmetic operations."""


class CalculatorException(Exception):
    """Base exception for all calculator domain errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class DivisionByZeroError(CalculatorException):
    """Raised when an arithmetic division by zero is attempted."""

    def __init__(self, message: str = "Cannot divide by zero.") -> None:
        super().__init__(message)


class InvalidOperatorError(CalculatorException):
    """Raised when an unsupported operator is supplied to the domain engine."""

    def __init__(self, message: str = "Unsupported arithmetic operator provided.") -> None:
        super().__init__(message)
