"""Type system for polarities.

"""
from typing import SupportsInt, SupportsFloat


class PolarityType(type, SupportsInt, SupportsFloat):
    """Metaclass to construct polarity types. Supports conversion to float and int."""
    def __float__(cls):
        return int(cls)

    def __int__(cls):
        return cls.P

    def __str__(cls):
        return cls.__name__.rstrip('Polarity')


class Polarity(metaclass=PolarityType):
    """Base class to build polarity."""
    P = 0


class HorizontalPolarity(Polarity):
    """Positive polarity."""
    P = 1


class VerticalPolarity(Polarity):
    """Negative polarity."""
    P = -1
