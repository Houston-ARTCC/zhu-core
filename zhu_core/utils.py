def base26encode(int_n):
    """
    Returns the base 26 integer representation of a string.
    """
    str_n = ''
    while int_n > 25:
        int_n, r = divmod(int_n, 26)
        str_n = chr(r + 65) + str_n
    str_n = chr(int_n + 65) + str_n
    return str_n


def base26decode(str_n):
    """
    Returns the string representation of a base 26 integer.
    """
    int_n = 0
    for pos, char in enumerate(str_n):
        int_n += (ord(char) - 65) * (26 ** (len(str_n) - pos - 1))
    return int_n
