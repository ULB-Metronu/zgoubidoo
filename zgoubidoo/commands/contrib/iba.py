"""Zgoubidoo's interfaces to purefly magnetic Zgoubi commands.

More details here.
TODO
"""
from typing import NoReturn
from ..magnetique import Dipole as _Dipole
from ..magnetique import Bend as _Bend
from ..magnetique import Quadrupole as _Quadrupole
from ..commands import Collimator as _Collimator
from ... import ureg as _ureg


class B1G(_Dipole):
    """Proteus One 40 degree dipole.

    Examples:
        >>> B1G()
    """
    PARAMETERS = {
        'B0': 1.4 * _ureg.tesla,
        'AT': 50 * _ureg.degree,
        'ACENT': 25 * _ureg.degree,
        'RM': 1600 * _ureg.mm,
    }

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        pass


class B2G(_Dipole):
    """Proteus One 70 degree dipole.

    Examples:
        >>> B2G()
    """
    PARAMETERS = {
        'B0': 1.4 * _ureg.tesla,
        'AT': 80 * _ureg.degree,
        'ACENT': 40 * _ureg.degree,
        'RM': 1500 * _ureg.mm,
    }

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        pass


class B3G(_Dipole):
    """Proteus One 60 degree dipole.

    Examples:
        >>> B3G()

    """
    PARAMETERS = {
        'B0': 1.4 * _ureg.tesla,
        'AT': 70 * _ureg.degree,
        'ACENT': 35 * _ureg.degree,
        'RM': 1600 * _ureg.mm,
    }

    def post_init(self,
                  magnet_opening=70 * _ureg.degree,
                  poles_opening=60 * _ureg.degree,
                  entrance_pole_trim=1.125 * _ureg.degree,
                  exit_pole_trim=1.125 * _ureg.degree,
                  entrance_fringe_lambda=7 * _ureg.cm,
                  exit_fringe_lambda=7 * _ureg.cm,
                  exit_pole_curvature=1e9 * _ureg.cm,
                  **kwargs,
                  ) -> NoReturn:
        """
        TODO
        Args:
            magnet_opening:
            poles_opening:
            entrance_pole_trim:
            exit_pole_trim:
            entrance_fringe_lambda:
            exit_fringe_lambda:
            exit_pole_curvature:

        Example:
            >>> B3G()

        """
        self.LABEL1 = self.__class__.__name__
        self.AT = magnet_opening
        self.ACENT = self.AT / 2
        self.OMEGA_E = poles_opening / 2
        self.OMEGA_S = -poles_opening / 2


class SMX(_Bend):
    """Proteus One inline scanning magnet.

    """
    PARAMETERS = {
        'XL': 159 * _ureg.mm,
    }


class SMY(_Bend):
    """Proteus One crossline scanning magnet.

    """
    PARAMETERS = {
        'XL': 109 * _ureg.mm,
    }


class QuadrupoleLong(_Quadrupole):
    """Proteus One long quadrupole.

    """
    PARAMETERS = {
        'XL': 490 * _ureg.mm,
    }


class QuadrupoleShort(_Quadrupole):
    """Proteus One short quadrupole.

    """
    PARAMETERS = {
        'XL': 290 * _ureg.mm,
    }


class QuadrupoleWall(_Quadrupole):
    """Proteus One 'wall' quadrupole.

    """
    PARAMETERS = {
        'XL': 297 * _ureg.mm,
    }


class HorizontalSlits(_Collimator):
    """Proteus One horizontal slits.

    """
    pass


class VerticalSlits(_Collimator):
    """Proteus One vertical slits.

    """
    pass
