import re
from typing import Final
from app.exceptions import InvalidRomanNumeralException, OutOfRangeIntegerException

MIN_INT_VALUE: Final[int] = 1
MAX_INT_VALUE: Final[int] = 3999

INT_TO_ROMAN_MAP: Final[tuple[tuple[int, str], ...]] = (
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
)

ROMAN_CHAR_VALUES: Final[dict[str, int]] = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}

STRICT_ROMAN_REGEX: Final[re.Pattern[str]] = re.compile(
    r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
)


def integer_to_roman(value: int) -> str:
    """
    Converts an integer between 1 and 3999 into its standard Roman numeral representation.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        raise OutOfRangeIntegerException(0)
    if value < MIN_INT_VALUE or value > MAX_INT_VALUE:
        raise OutOfRangeIntegerException(value)

    remaining = value
    parts: list[str] = []
    for int_val, numeral in INT_TO_ROMAN_MAP:
        if remaining == 0:
            break
        count, remaining = divmod(remaining, int_val)
        if count > 0:
            parts.append(numeral * count)

    return "".join(parts)


def roman_to_integer(roman: str) -> int:
    """
    Converts a valid standard Roman numeral string into its integer equivalent.
    """
    if not isinstance(roman, str):
        raise InvalidRomanNumeralException(str(roman), "Roman numeral must be a string")

    normalized = roman.strip().upper()
    if not normalized:
        raise InvalidRomanNumeralException(roman, "Roman numeral cannot be empty")

    if not STRICT_ROMAN_REGEX.match(normalized):
        raise InvalidRomanNumeralException(normalized, "Roman numeral does not adhere to standard syntax")

    total = 0
    length = len(normalized)
    for i in range(length):
        current_val = ROMAN_CHAR_VALUES[normalized[i]]
        if i + 1 < length and current_val < ROMAN_CHAR_VALUES[normalized[i + 1]]:
            total -= current_val
        else:
            total += current_val

    if total < MIN_INT_VALUE or total > MAX_INT_VALUE:
        raise InvalidRomanNumeralException(normalized, f"Calculated value {total} is outside supported range [1, 3999]")

    # Strict round-trip check to eliminate non-canonical representations
    if integer_to_roman(total) != normalized:
        raise InvalidRomanNumeralException(normalized, "Non-canonical Roman numeral representation")

    return total
