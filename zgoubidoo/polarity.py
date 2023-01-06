"""Type system for polarities.

Examples:
    The conversion to numeric types can be used for easily in numerical expressions:

    >>> gradient = int(HorizontalPolarity) * 3.1415
    >>> gradient
    3.1415

    One major use case consists in type-hinting functions (shown here with default value argument):

    >>> def foo(polarity: PolarityType = HorizontalPolarity): pass

"""
from typing import SupportsFloat as _SupportsFloat
from typing import SupportsInt as _SupportsInt


class PolarityType(type, _SupportsInt, _SupportsFloat):
    """Metaclass to construct polarity types. Supports conversion to float and int."""

    def __float__(cls):
        return float(cls)

    def __int__(cls):
        return cls.P

    def __str__(cls):
        return cls.__name__.replace("P", " ").split()[0]  # No very proud of this...

    def __eq__(self, other):
        return float(self) == other


class Polarity(metaclass=PolarityType):
    """Base class to build polarity."""

    P = 0


class HorizontalPolarity(Polarity):
    """Positive polarity."""

    P = 1


class VerticalPolarity(Polarity):
    """Negative polarity."""

    P = -1
