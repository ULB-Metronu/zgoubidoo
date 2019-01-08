"""Utility functions."""
from typing import Pattern
import re

re_f_float_neg: Pattern = re.compile(r'(-?[0-9.]*)(-\d\d\d)')
"""A regex pattern matching Fortran quasi-float format."""


def fortran_float(input_string: str) -> float:
    """
    Return a float of the input string, just like `float(input_string)`,
    but allowing for Fortran's string formatting to screw it up when
    you have very small numbers (like 0.31674-103 instead of 0.31674E-103 )

    See Also:
        https://gist.github.com/chernals/fb6177e2e8b423d4647242e44ce25cec
    """
    try:
        fl: float = float(input_string)
    except ValueError:
        match = re_f_float_neg.match(input_string.strip())
        if match:
            processed_string: str = match.group(1)+'E'+match.group(2)
            fl: float = float(processed_string)
        else:
            raise ValueError(f"Failed to convert {input_string} to float")
    return fl
