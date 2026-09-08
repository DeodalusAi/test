"""Pydantic models and validation schemas for Roman numeral conversion."""

import re
from pydantic import BaseModel, Field, field_validator

MIN_ROMAN_VALUE = 1
MAX_ROMAN_VALUE = 3999

# Standard subtractive Roman numeral pattern for 1 to 3999
ROMAN_REGEX_PATTERN = (
    r"^(?!$)"
    r"M{0,3}"
    r"(CM|CD|D?C{0,3})"
    r"(XC|XL|L?X{0,3})"
    r"(IX|IV|V?I{0,3})$"
)
ROMAN_REGEX = re.compile(ROMAN_REGEX_PATTERN)


class ToRomanRequest(BaseModel):
    """Request schema for Arabic to Roman conversion."""

    value: int = Field(
        ...,
        ge=MIN_ROMAN_VALUE,
        le=MAX_ROMAN_VALUE,
        description=f"Integer value between {MIN_ROMAN_VALUE} and {MAX_ROMAN_VALUE}",
        examples=[1, 4, 9, 42, 3999],
    )


class ToRomanResponse(BaseModel):
    """Response schema for Arabic to Roman conversion."""

    arabic: int = Field(..., description="Input Arabic integer value")
    roman: str = Field(..., description="Resulting Roman numeral string")


class ToArabicRequest(BaseModel):
    """Request schema for Roman to Arabic conversion."""

    roman: str = Field(
        ...,
        min_length=1,
        max_length=15,
        description="Standard Roman numeral string between I and MMMCMXCIX",
        examples=["I", "IV", "IX", "XLII", "MMMCMXCIX"],
    )

    @field_validator("roman")
    @classmethod
    def validate_roman_string(cls, v: str) -> str:
        normalized = v.strip().upper()
        if not normalized:
            raise ValueError("Roman numeral string cannot be empty or whitespace.")
        if not ROMAN_REGEX.match(normalized):
            raise ValueError(
                f"Invalid Roman numeral format: '{v}'. Must be a standard Roman sequence between 1 and 3999."
            )
        return normalized


class ToArabicResponse(BaseModel):
    """Response schema for Roman to Arabic conversion."""

    roman: str = Field(..., description="Input Roman numeral string")
    arabic: int = Field(..., description="Resulting Arabic integer value")
