VALUES = ((1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'), (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I'))

def int_to_roman(value: int) -> str:
    if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 3999:
        raise ValueError('value must be an integer from 1 through 3999')
    result = []
    for number, symbol in VALUES:
        count, value = divmod(value, number)
        result.append(symbol * count)
    return ''.join(result)
