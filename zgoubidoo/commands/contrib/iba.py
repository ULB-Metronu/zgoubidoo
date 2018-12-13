"""Zgoubidoo's interfaces to purefly magnetic Zgoubi commands.

More details here.
TODO
"""
from typing import NoReturn
from ..magnetique import PolarMagnet as _PolarMagnet
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
        'B0': 14 * _ureg.kilogauss,  # It is important to keep it expressed in kilogauss here
        'AT': 50 * _ureg.degree,
        'ACENT': 25 * _ureg.degree,
        'RM': 1600 * _ureg.mm,
    }

    def post_init(self,
                  magnet_opening=50 * _ureg.degree,
                  poles_opening=40 * _ureg.degree,
                  entrance_pole_trim=0 * _ureg.degree,
                  exit_pole_trim=0 * _ureg.degree,
                  entrance_fringe_lambda=9 * _ureg.cm,
                  exit_fringe_lambda=9 * _ureg.cm,
                  **kwargs,
                  ) -> NoReturn:
        """
        TODO
        Args:
            magnet_opening: total angular opening of the magnet (i.e. of the field map)
            poles_opening: angular opening of the poles
            entrance_pole_trim: angular shift of the entrance pole
            exit_pole_trim: angular shift of the exit pole
            entrance_fringe_lambda: effective length of the entrance fringe field
            exit_fringe_lambda: effective length of the exit fringe field
        Example:
            >>> b1g = B1G()
            >>> b1g.fit()

        """
        self.LABEL1 = self.__class__.__name__
        self.AT = magnet_opening
        self.ACENT = self.AT / 2
        self.OMEGA_E = poles_opening / 2 - entrance_pole_trim
        self.OMEGA_S = -poles_opening / 2 + entrance_pole_trim
        self.LAM_E = entrance_fringe_lambda
        self.LAM_S = exit_fringe_lambda
        self.RE = _PolarMagnet.efb_offset_from_polar(radius=self.RM,
                                                     magnet_angle=magnet_opening,
                                                     poles_angle=poles_opening
                                                     )
        self.RS = _PolarMagnet.efb_offset_from_polar(radius=self.RM,
                                                     magnet_angle=magnet_opening,
                                                     poles_angle=poles_opening
                                                     )
        self.TE = _PolarMagnet.efb_angle_from_polar(magnet_angle=magnet_opening,
                                                    poles_angle=poles_opening
                                                    )
        self.TS = -_PolarMagnet.efb_angle_from_polar(magnet_angle=magnet_opening,
                                                     poles_angle=poles_opening
                                                     )


class B2G(_Dipole):
    """Proteus One 70 degree dipole.

    Examples:
        >>> B2G()
    """
    PARAMETERS = {
        'B0': 14 * _ureg.kilogauss,  # It is important to keep it expressed in kilogauss here
        'RM': 1500 * _ureg.mm,
    }

    def post_init(self,
                  magnet_opening=80 * _ureg.degree,
                  poles_opening=70 * _ureg.degree,
                  entrance_pole_trim=0 * _ureg.degree,
                  exit_pole_trim=0 * _ureg.degree,
                  entrance_fringe_lambda=9 * _ureg.cm,
                  exit_fringe_lambda=9 * _ureg.cm,
                  **kwargs,
                  ) -> NoReturn:
        """
        TODO
        Args:
            magnet_opening: total angular opening of the magnet (i.e. of the field map)
            poles_opening: angular opening of the poles
            entrance_pole_trim: angular shift of the entrance pole
            exit_pole_trim: angular shift of the exit pole
            entrance_fringe_lambda: effective length of the entrance fringe field
            exit_fringe_lambda: effective length of the exit fringe field
        Example:
            >>> b2g = B2G()
            >>> b2g.fit()

        """
        self.LABEL1 = self.__class__.__name__
        self.AT = magnet_opening
        self.ACENT = self.AT / 2
        self.OMEGA_E = poles_opening / 2 - entrance_pole_trim
        self.OMEGA_S = -poles_opening / 2 + entrance_pole_trim
        self.LAM_E = entrance_fringe_lambda
        self.LAM_S = exit_fringe_lambda
        self.RE = _PolarMagnet.efb_offset_from_polar(radius=self.RM,
                                                     magnet_angle=magnet_opening,
                                                     poles_angle=poles_opening
                                                     )
        self.RS = _PolarMagnet.efb_offset_from_polar(radius=self.RM,
                                                     magnet_angle=magnet_opening,
                                                     poles_angle=poles_opening
                                                     )
        self.TE = _PolarMagnet.efb_angle_from_polar(magnet_angle=magnet_opening,
                                                    poles_angle=poles_opening
                                                    )
        self.TS = -_PolarMagnet.efb_angle_from_polar(magnet_angle=magnet_opening,
                                                     poles_angle=poles_opening
                                                     )


class B3G(_Dipole):
    """Proteus One 60 degree dipole.

    Examples:
        >>> B3G()

    """
    PARAMETERS = {
        'B0': 14 * _ureg.kilogauss,  # It is important to keep it expressed in kilogauss here
        'RM': 1600 * _ureg.mm,
        'LAM_E': 9 * _ureg.cm,
        'C0_E': 0.67634054,  # Obtained from field map fit
        'C1_E': 1.15776841,  # Obtained from field map fit
        'C2_E': -0.16937986,  # Obtained from field map fit
        'C3_E': 0.07696388,  # Obtained from field map fit
        'SHIFT_E': 0 * _ureg.cm,
        'LAM_S': 9 * _ureg.cm,
        'C0_S': 0.77890820,  # Obtained from field map fit
        'C1_S': 0.94490545,  # Obtained from field map fit
        'C2_S': -0.13034787,  # Obtained from field map fit
        'C3_S': 0.02948957,  # Obtained from field map fit
        'SHIFT_S': 0 * _ureg.cm,
        'XPAS': 0.1 * _ureg.mm,
    }

    def post_init(self,
                  magnet_opening=70 * _ureg.degree,
                  poles_opening=60 * _ureg.degree,
                  entrance_pole_trim=1.125 * _ureg.degree,
                  exit_pole_trim=1.125 * _ureg.degree,
                  entrance_fringe_lambda=9 * _ureg.cm,
                  exit_fringe_lambda=9 * _ureg.cm,
                  entrance_pole_curvature=1e9 * _ureg.cm,
                  exit_pole_curvature=1e9 * _ureg.cm,
                  **kwargs,
                  ) -> NoReturn:
        """
        TODO
        Args:
            magnet_opening: total angular opening of the magnet (i.e. of the field map)
            poles_opening: angular opening of the poles
            entrance_pole_trim: angular shift of the entrance pole
            exit_pole_trim: angular shift of the exit pole
            entrance_fringe_lambda: effective length of the entrance fringe field
            exit_fringe_lambda: effective length of the exit fringe field
            entrance_pole_curvature: curvature of the  pole at the entrance of the magnet
            exit_pole_curvature: curvature of the pole at the exit of the magnet
        Example:
            >>> b3g = B3G()
            >>> b3g.fit()

        """
        self.LABEL1 = self.__class__.__name__
        self.AT = magnet_opening
        self.ACENT = self.AT / 2
        self.OMEGA_E = poles_opening / 2 - entrance_pole_trim
        self.OMEGA_S = -poles_opening / 2 + entrance_pole_trim
        self.LAM_E = entrance_fringe_lambda
        self.LAM_S = exit_fringe_lambda
        self.RE = _PolarMagnet.efb_offset_from_polar(radius=self.RM,
                                                     magnet_angle=magnet_opening,
                                                     poles_angle=poles_opening
                                                     )
        self.RS = _PolarMagnet.efb_offset_from_polar(radius=self.RM,
                                                     magnet_angle=magnet_opening,
                                                     poles_angle=poles_opening
                                                     )
        self.TE = _PolarMagnet.efb_angle_from_polar(magnet_angle=magnet_opening,
                                                    poles_angle=poles_opening
                                                    )
        self.TS = -_PolarMagnet.efb_angle_from_polar(magnet_angle=magnet_opening,
                                                     poles_angle=poles_opening
                                                     )


class SMX(_Bend):
    """Proteus One inline (horizontal) scanning magnet.

    """
    PARAMETERS = {
        'XL': 159 * _ureg.mm,
    }

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        self.LABEL1 = self.__class__.__name__


class SMY(_Bend):
    """Proteus One crossline (vertical) scanning magnet.

    """
    PARAMETERS = {
        'XL': 109 * _ureg.mm,
    }

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        self.LABEL1 = self.__class__.__name__


class QLong(_Quadrupole):
    """Proteus One long quadrupole.

    """
    PARAMETERS = {
        'XL': 490 * _ureg.mm,
    }


class QShort(_Quadrupole):
    """Proteus One short quadrupole.

    """
    PARAMETERS = {
        'XL': 290 * _ureg.mm,
    }


class QWall(_Quadrupole):
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
