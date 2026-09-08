import pytest

from app.roman import int_to_roman

@pytest.mark.parametrize('value, expected', [
    (1, 'I'), (3, 'III'), (4, 'IV'), (5, 'V'), (8, 'VIII'),
    (9, 'IX'), (39, 'XXXIX'), (40, 'XL'), (41, 'XLI'),
    (89, 'LXXXIX'), (90, 'XC'), (399, 'CCCXCIX'),
    (400, 'CD'), (899, 'DCCCXCIX'), (900, 'CM'), (3999, 'MMMCMXCIX'),
])
def test_int_to_roman_boundaries(value, expected):
    assert int_to_roman(value) == expected

@pytest.mark.parametrize('value', [0, -1, 4000])
def test_int_to_roman_rejects_out_of_range_values(value):
    with pytest.raises(ValueError):
        int_to_roman(value)
