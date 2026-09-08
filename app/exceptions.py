class RomanConverterException(Exception):
    """Base exception for Roman converter domain errors."""
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class OutOfRangeIntegerException(RomanConverterException):
    """Raised when an integer is outside the supported range [1, 3999]."""
    def __init__(self, value: int) -> None:
        super().__init__(f"Integer value {value} is out of range. Must be between 1 and 3999 inclusive.")
        self.value = value


class InvalidRomanNumeralException(RomanConverterException):
    """Raised when a Roman numeral string violates standard syntax or range rules."""
    def __init__(self, roman: str, reason: str = "Invalid Roman numeral syntax") -> None:
        super().__init__(f"{reason}: '{roman}'")
        self.roman = roman
        self.reason = reason
