from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.api.v1.endpoints.converter import router as converter_router
from app.exceptions import InvalidRomanNumeralException, OutOfRangeIntegerException


def create_app() -> FastAPI:
    application = FastAPI(
        title="Roman Numeral Conversion Service",
        version="1.0.0",
        description="Stateless REST service providing bidirectional Roman numeral conversions.",
    )

    @application.exception_handler(OutOfRangeIntegerException)
    def handle_out_of_range_exception(_: Request, exc: OutOfRangeIntegerException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    @application.exception_handler(InvalidRomanNumeralException)
    def handle_invalid_roman_exception(_: Request, exc: InvalidRomanNumeralException) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.message},
        )

    application.include_router(converter_router, prefix="/api/v1")
    return application


app = create_app()
