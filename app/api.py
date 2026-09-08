"""Calculation API routes and dependency definitions."""

from fastapi import APIRouter, Depends, status
from app.schemas import CalculationRequest, CalculationResponse, ProblemDetail
from app.service import CalculatorService


def get_calculator_service() -> CalculatorService:
    """FastAPI dependency provider for CalculatorService."""
    return CalculatorService()


router = APIRouter(prefix="/api/v1", tags=["calculator"])


@router.post(
    "/calculate",
    response_model=CalculationResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute arithmetic operation",
    description="Performs addition, subtraction, multiplication, or division with Decimal precision.",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ProblemDetail,
            "description": "Mathematical or domain evaluation error.",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Request validation error.",
        },
    },
)
def calculate_endpoint(
    request: CalculationRequest,
    service: CalculatorService = Depends(get_calculator_service),
) -> CalculationResponse:
    """Endpoint executing calculation via domain service."""
    return service.calculate(request)
