"""FastAPI application entry point for the Roman Numeral Service."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.api.v1.endpoints import router as v1_router


def create_app() -> FastAPI:
    application = FastAPI(
        title="Roman Numeral Conversion Service",
        description="Stateless microservice for standard Roman-Arabic bidirectional conversions.",
        version="1.0.0",
    )

    @application.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    application.include_router(v1_router)
    application.include_router(v1_router, prefix="/api/v1")

    @application.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
    def health_check() -> dict[str, str]:
        return {"status": "ok", "service": "roman-numeral-converter"}

    return application


app = create_app()
