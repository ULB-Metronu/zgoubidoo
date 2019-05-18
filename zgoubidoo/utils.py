"""Utility functions."""
from typing import Pattern as _Pattern, List, Any
import re as _re

_re_f_float_neg: _Pattern = _re.compile(r'(-?[0-9.]*)(-\d\d\d)')
"""A regex pattern matching Fortran quasi-float format."""


def fortran_float(input_string: str) -> float:
    """
    Returns a float of the input string, just like `float(input_string)`, but allowing for Fortran's string formatting
    to screw it up when you have very small numbers (like 0.31674-103 instead of 0.31674E-103 ).

    See Also:
        https://gist.github.com/chernals/fb6177e2e8b423d4647242e44ce25cec

    Args:
        input_string: the string to be converted to float.

    Returns:
        a float representing the input value.

    Raises:
        ValueError: in case it is not possible to convert the input string.

    Example:
        >>> fortran_float('0.31674-103')
        3.1674e-104
    """
    try:
        fl = float(input_string)
    except ValueError:
        match = _re_f_float_neg.match(input_string.strip())
        if match:
            processed_string: str = match.group(1)+'E'+match.group(2)
            fl = float(processed_string)
        else:
            raise ValueError(f"Failed to convert {input_string:s} to float")
    return fl


def intersperse(lst: List, item: Any) -> List:
    """
    Inserts an item in-between every element of a list.

    Args:
        lst: the list of elements
        item: the item to be interspersed

    Returns:
        A new list list with the interspersed items.

    Example:
        >>> intersperse([1,2,3], 'a')
        [1, 'a', 2, 'a', 3]
    """
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result
