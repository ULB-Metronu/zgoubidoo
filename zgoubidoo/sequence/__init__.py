"""High-level interface (API) for Zgoubi.

The high-level API adds a level of abstraction on top of low-level API (using `Input` and `Command`).
"""
import numpy as _np
from dataclasses import dataclass as _dataclass
from .sequence import Sequence, ZgoubidooSequenceException
from .srloss import srloss


@_dataclass
class Coordinates:
    """Particle coordinates in 6D phase space.

    Follows Zgoubi's convention.

    Examples:
        >>> c = Coordinates()
        >>> c.y
        0.0
        >>> c = Coordinates(1.0, 1.0, 0.0, 0.0, 0.0, 0.0)
        >>> c.t
        1.0
    """
    y: float = 0
    """Horizontal plane coordinate."""
    t: float = 0
    """Horizontal plane angle."""
    z: float = 0
    """Vertical plane coordinate"""
    p: float = 0
    """Vertical plane angle."""
    x: float = 0
    """Longitudinal coordinate."""
    d: float = 1
    """Off-momentum offset"""
    iex: int = 1
    """Particle alive status."""

    def __getitem__(self, item: int):
        return getattr(self, list(self.__dataclass_fields__.keys())[item])

    @property
    def array(self) -> _np.array:
        """Provides a numpy array."""
        return _np.array(self.list)

    @property
    def list(self) -> list:
        """Provides a flat list."""
        return list(self.__dict__.values())
