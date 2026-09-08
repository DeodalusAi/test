"""FastAPI application factory and lifecycle entrypoint."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.api import router as calculator_router
from app.exceptions import CalculatorException, DivisionByZeroError, InvalidOperatorError
from app.schemas import ProblemDetail


def create_app() -> FastAPI:
    """Construct and configure FastAPI application instance."""
    application = FastAPI(
        title="Production-Ready FastAPI Calculator Service",
        version="1.0.0",
        description="Stateless microservice delivering high-precision arithmetic calculations.",
    )

    @application.exception_handler(DivisionByZeroError)
    async def division_by_zero_handler(request: Request, exc: DivisionByZeroError) -> JSONResponse:
        problem = ProblemDetail(
            type="https://errors.example.com/division-by-zero",
            title="Division By Zero",
            status=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
            instance=request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=problem.model_dump(),
        )

    @application.exception_handler(InvalidOperatorError)
    async def invalid_operator_handler(request: Request, exc: InvalidOperatorError) -> JSONResponse:
        problem = ProblemDetail(
            type="https://errors.example.com/invalid-operator",
            title="Invalid Operator",
            status=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
            instance=request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=problem.model_dump(),
        )

    @application.exception_handler(CalculatorException)
    async def calculator_exception_handler(request: Request, exc: CalculatorException) -> JSONResponse:
        problem = ProblemDetail(
            type="https://errors.example.com/calculation-error",
            title="Calculation Error",
            status=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
            instance=request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=problem.model_dump(),
        )

    @application.get("/health", tags=["system"], status_code=status.HTTP_200_OK)
    async def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    application.include_router(calculator_router)
    return application


app = create_app()
