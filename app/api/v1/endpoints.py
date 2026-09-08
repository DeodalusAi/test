"""API endpoints for Roman numeral conversions."""

from fastapi import APIRouter, HTTPException, Query, status
from app.core.converter import int_to_roman, roman_to_int
from app.schemas.numeral import (
    ToArabicRequest,
    ToArabicResponse,
    ToRomanRequest,
    ToRomanResponse,
)

router = APIRouter(tags=["Conversion"])


@router.post(
    "/convert/to-roman",
    response_model=ToRomanResponse,
    status_code=status.HTTP_200_OK,
    summary="Convert Arabic integer to Roman numeral via POST body",
)
def post_convert_to_roman(payload: ToRomanRequest) -> ToRomanResponse:
    try:
        roman_str = int_to_roman(payload.value)
        return ToRomanResponse(arabic=payload.value, roman=roman_str)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "/convert/to-roman",
    response_model=ToRomanResponse,
    status_code=status.HTTP_200_OK,
    summary="Convert Arabic integer to Roman numeral via GET query parameter",
)
def get_convert_to_roman(
    value: int = Query(..., ge=1, le=3999, description="Arabic integer between 1 and 3999")
) -> ToRomanResponse:
    try:
        roman_str = int_to_roman(value)
        return ToRomanResponse(arabic=value, roman=roman_str)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post(
    "/convert/to-arabic",
    response_model=ToArabicResponse,
    status_code=status.HTTP_200_OK,
    summary="Convert Roman numeral string to Arabic integer via POST body",
)
def post_convert_to_arabic(payload: ToArabicRequest) -> ToArabicResponse:
    try:
        arabic_val = roman_to_int(payload.roman)
        return ToArabicResponse(roman=payload.roman, arabic=arabic_val)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "/convert/to-arabic",
    response_model=ToArabicResponse,
    status_code=status.HTTP_200_OK,
    summary="Convert Roman numeral string to Arabic integer via GET query parameter",
)
def get_convert_to_arabic(
    roman: str = Query(..., min_length=1, max_length=15, description="Roman numeral string")
) -> ToArabicResponse:
    try:
        validated_request = ToArabicRequest(roman=roman)
        arabic_val = roman_to_int(validated_request.roman)
        return ToArabicResponse(roman=validated_request.roman, arabic=arabic_val)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
