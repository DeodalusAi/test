"""Main FastAPI application initialization."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.api.v1.routes import router as conversion_router


def create_application() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="Production Roman Numeral Converter Service",
        version="1.0.0",
        description="FastAPI-based Roman numeral bidirectional converter service.",
    )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    app.include_router(conversion_router)
    return app


app = create_application()
