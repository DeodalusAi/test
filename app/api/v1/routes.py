"""FastAPI routes for Roman numeral conversions."""

from fastapi import APIRouter, HTTPException, status
from app.domain.converter import from_roman, to_roman
from app.schemas.converter import (
    ErrorDetailResponse,
    IntegerToRomanRequest,
    IntegerToRomanResponse,
    RomanToIntegerRequest,
    RomanToIntegerResponse,
)

router = APIRouter(prefix="/convert", tags=["Conversion"])


@router.post(
    "/to-roman",
    response_model=IntegerToRomanResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorDetailResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation Error"},
    },
    summary="Convert Integer to Roman Numeral",
)
def convert_to_roman(payload: IntegerToRomanRequest) -> IntegerToRomanResponse:
    """Converts an integer within [1, 3999] into its Roman numeral string representation."""
    try:
        roman_numeral = to_roman(payload.number)
        return IntegerToRomanResponse(number=payload.number, roman=roman_numeral)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post(
    "/to-integer",
    response_model=RomanToIntegerResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorDetailResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation Error"},
    },
    summary="Convert Roman Numeral to Integer",
)
def convert_to_integer(payload: RomanToIntegerRequest) -> RomanToIntegerResponse:
    """Converts a Roman numeral string into its integer value."""
    try:
        integer_val = from_roman(payload.roman)
        return RomanToIntegerResponse(roman=payload.roman, number=integer_val)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
