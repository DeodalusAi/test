from pydantic import BaseModel, Field


class ToRomanRequest(BaseModel):
    value: int = Field(..., description="Integer value to convert to Roman numeral (1 to 3999)")


class ToRomanResponse(BaseModel):
    value: int = Field(..., description="Original integer value")
    roman: str = Field(..., description="Converted Roman numeral string")


class FromRomanRequest(BaseModel):
    roman: str = Field(..., min_length=1, max_length=15, description="Roman numeral string to convert to integer")


class FromRomanResponse(BaseModel):
    roman: str = Field(..., description="Original Roman numeral string")
    value: int = Field(..., description="Converted integer value")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Descriptive error message")
