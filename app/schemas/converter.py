"""Pydantic v2 request and response schemas for Roman Numeral conversion."""

from pydantic import BaseModel, ConfigDict, Field

ROMAN_REGEX_PATTERN = r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"


class IntegerToRomanRequest(BaseModel):
    """Request schema for integer to Roman numeral conversion."""

    model_config = ConfigDict(extra="forbid")

    number: int = Field(
        ...,
        ge=1,
        le=3999,
        description="Integer value between 1 and 3999 inclusive to convert to Roman numeral.",
        examples=[1994],
    )


class RomanToIntegerRequest(BaseModel):
    """Request schema for Roman numeral to integer conversion."""

    model_config = ConfigDict(extra="forbid")

    roman: str = Field(
        ...,
        min_length=1,
        max_length=15,
        pattern=ROMAN_REGEX_PATTERN,
        description="Standard Roman numeral string in the range I to MMMCMXCIX (1 to 3999).",
        examples=["MCMXCIV"],
    )


class IntegerToRomanResponse(BaseModel):
    """Response schema containing original integer and Roman numeral representation."""

    model_config = ConfigDict(extra="forbid")

    number: int = Field(..., description="The input integer.")
    roman: str = Field(..., description="The converted Roman numeral representation.")


class RomanToIntegerResponse(BaseModel):
    """Response schema containing original Roman numeral and integer representation."""

    model_config = ConfigDict(extra="forbid")

    roman: str = Field(..., description="The input Roman numeral.")
    number: int = Field(..., description="The converted integer value.")


class ErrorDetailResponse(BaseModel):
    """Standardized error response payload."""

    model_config = ConfigDict(extra="forbid")

    detail: str = Field(..., description="Human-readable error explanation.")
