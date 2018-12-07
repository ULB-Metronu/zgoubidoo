"""Zgoubidoo's interfaces to purefly magnetic Zgoubi commands.

More details here.
TODO
"""

from ..magnetique import Dipole as _Dipole
from ..magnetique import Quadrupole as _Quadrupole


class B1G(_Dipole):
    """

    """
    pass


class B2G(_Dipole):
    """

    """
    pass


class B3G(_Dipole):
    """

    """
    pass


class QuadrupoleLong(_Quadrupole):
    """

    """
    pass


class QuadrupoleShort(_Quadrupole):
    """

    """
    pass


class QuadrupoleWall(_Quadrupole):
    """

    """
    pass