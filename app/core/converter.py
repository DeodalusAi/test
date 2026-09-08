"""Core domain converter engine for bidirectional Roman numeral translation."""

import re

MIN_ROMAN_INT = 1
MAX_ROMAN_INT = 3999

ORDERED_NUMERAL_PAIRS = (
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

ROMAN_CHAR_VALUES = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}

STRICT_ROMAN_PATTERN = re.compile(
    r"^(?!$)"
    r"M{0,3}"
    r"(CM|CD|D?C{0,3})"
    r"(XC|XL|L?X{0,3})"
    r"(IX|IV|V?I{0,3})$"
)


def int_to_roman(value: int) -> str:
    """Convert an Arabic integer in the range [1, 3999] to a Roman numeral string.

    Raises:
        TypeError: If value is not an integer.
        ValueError: If value is outside [1, 3999].
    """
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"Value must be an integer, got {type(value).__name__}")

    if value < MIN_ROMAN_INT or value > MAX_ROMAN_INT:
        raise ValueError(
            f"Value {value} out of bounds. Standard Roman numerals support values from {MIN_ROMAN_INT} to {MAX_ROMAN_INT}."
        )

    remaining = value
    roman_chunks = []
    for arabic, roman in ORDERED_NUMERAL_PAIRS:
        if remaining == 0:
            break
        count, remaining = divmod(remaining, arabic)
        if count > 0:
            roman_chunks.append(roman * count)

    return "".join(roman_chunks)


def roman_to_int(roman: str) -> int:
    """Convert a Roman numeral string in the range [1, 3999] to an Arabic integer.

    Raises:
        TypeError: If roman is not a string.
        ValueError: If roman string is malformed or out of standard range.
    """
    if not isinstance(roman, str):
        raise TypeError(f"Roman numeral must be a string, got {type(roman).__name__}")

    normalized = roman.strip().upper()
    if not normalized:
        raise ValueError("Roman numeral string cannot be empty.")

    if not STRICT_ROMAN_PATTERN.match(normalized):
        raise ValueError(f"Invalid Roman numeral sequence: '{roman}'.")

    total = 0
    length = len(normalized)
    for i in range(length):
        current_val = ROMAN_CHAR_VALUES[normalized[i]]
        if i + 1 < length and current_val < ROMAN_CHAR_VALUES[normalized[i + 1]]:
            total -= current_val
        else:
            total += current_val

    # Verification guarantee: round-trip must match identically
    if int_to_roman(total) != normalized:
        raise ValueError(f"Invalid non-canonical Roman numeral: '{roman}'.")

    return total
