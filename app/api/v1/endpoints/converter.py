from fastapi import APIRouter, status
from app.core.converter import integer_to_roman, roman_to_integer
from app.schemas import (
    ErrorResponse,
    FromRomanRequest,
    FromRomanResponse,
    ToRomanRequest,
    ToRomanResponse,
)

router = APIRouter(prefix="/convert", tags=["converter"])


@router.post(
    "/to-roman",
    response_model=ToRomanResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Out of range integer error"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
)
def convert_to_roman(payload: ToRomanRequest) -> ToRomanResponse:
    """Converts an integer between 1 and 3999 to a standard Roman numeral."""
    result = integer_to_roman(payload.value)
    return ToRomanResponse(value=payload.value, roman=result)


@router.post(
    "/from-roman",
    response_model=FromRomanResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Invalid Roman numeral error"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
    },
)
def convert_from_roman(payload: FromRomanRequest) -> FromRomanResponse:
    """Converts a standard Roman numeral to its integer representation."""
    result = roman_to_integer(payload.roman)
    return FromRomanResponse(roman=payload.roman.strip().upper(), value=result)
