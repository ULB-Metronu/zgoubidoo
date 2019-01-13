"""Utility functions."""
from typing import Pattern as _Pattern
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
