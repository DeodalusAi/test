"""Domain core module for bidirectional Roman numeral conversion."""

import re

ROMAN_TO_VALUE_ORDERED: tuple[tuple[int, str], ...] = (
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

ROMAN_CHAR_VALUES: dict[str, int] = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}

STRICT_ROMAN_REGEX: re.Pattern[str] = re.compile(
    r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
)

MIN_ROMAN_VALUE = 1
MAX_ROMAN_VALUE = 3999


def to_roman(number: int) -> str:
    """Convert an integer between 1 and 3999 to its Roman numeral representation.

    Args:
        number: Integer to convert.

    Returns:
        The canonical Roman numeral string.

    Raises:
        ValueError: If number is out of bounds (number < 1 or number > 3999).
    """
    if not isinstance(number, int) or isinstance(number, bool):
        raise ValueError(f"Input must be an integer, got: {type(number).__name__}")

    if number < MIN_ROMAN_VALUE or number > MAX_ROMAN_VALUE:
        raise ValueError(
            f"Value {number} is out of valid range [{MIN_ROMAN_VALUE}, {MAX_ROMAN_VALUE}]."
        )

    result: list[str] = []
    remaining = number

    for value, symbol in ROMAN_TO_VALUE_ORDERED:
        if remaining == 0:
            break
        count, remaining = divmod(remaining, value)
        if count:
            result.append(symbol * count)

    return "".join(result)


def from_roman(roman: str) -> int:
    """Convert a canonical Roman numeral string to an integer.

    Args:
        roman: Roman numeral string.

    Returns:
        The integer representation.

    Raises:
        ValueError: If the input is not a string, is empty, or violates canonical Roman numeral syntax.
    """
    if not isinstance(roman, str):
        raise ValueError(f"Input must be a string, got: {type(roman).__name__}")

    normalized = roman.strip().upper()

    if not normalized:
        raise ValueError("Roman numeral string cannot be empty.")

    if not STRICT_ROMAN_REGEX.fullmatch(normalized):
        raise ValueError(f"Invalid Roman numeral representation: '{roman}'.")

    total = 0
    length = len(normalized)

    for idx, char in enumerate(normalized):
        curr_val = ROMAN_CHAR_VALUES[char]
        if idx + 1 < length and curr_val < ROMAN_CHAR_VALUES[normalized[idx + 1]]:
            total -= curr_val
        else:
            total += curr_val

    if total < MIN_ROMAN_VALUE or total > MAX_ROMAN_VALUE:
        raise ValueError(
            f"Parsed value {total} is outside supported range [{MIN_ROMAN_VALUE}, {MAX_ROMAN_VALUE}]."
        )

    # Cross-verify canonical representation to guard against non-canonical structures
    if to_roman(total) != normalized:
        raise ValueError(f"Roman numeral '{roman}' is not in canonical format.")

    return total
