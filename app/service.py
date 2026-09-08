"""Domain service executing high-precision arithmetic calculations."""

from decimal import Decimal, DivisionByZero as DecDivisionByZero
from app.exceptions import DivisionByZeroError, InvalidOperatorError
from app.schemas import CalculationRequest, CalculationResponse, OperationType


class CalculatorService:
    """Pure Python domain engine providing stateless arithmetic evaluations."""

    @staticmethod
    def calculate(request: CalculationRequest) -> CalculationResponse:
        """Evaluate calculation request with decimal precision.

        Raises:
            DivisionByZeroError: If division by zero is attempted.
            InvalidOperatorError: If an unrecognized operation is specified.
        """
        a: Decimal = request.operand_a
        b: Decimal = request.operand_b
        operation: OperationType = request.operation

        if operation == OperationType.ADD:
            result = a + b
        elif operation == OperationType.SUBTRACT:
            result = a - b
        elif operation == OperationType.MULTIPLY:
            result = a * b
        elif operation == OperationType.DIVIDE:
            if b == Decimal("0"):
                raise DivisionByZeroError("Division by zero is not permitted.")
            try:
                result = a / b
            except DecDivisionByZero as exc:
                raise DivisionByZeroError("Division by zero is not permitted.") from exc
        else:
            raise InvalidOperatorError(f"Unsupported operation: {operation}")

        return CalculationResponse(
            operand_a=a,
            operand_b=b,
            operation=operation,
            result=result,
        )
