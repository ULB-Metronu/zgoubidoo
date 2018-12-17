"""Zgoubidoo's interfaces to purefly magnetic Zgoubi commands.

More details here.
TODO
"""
from typing import NoReturn, Optional
import numpy as _np
from ..magnetique import Dipole as _Dipole
from ..magnetique import PolarMagnet as _PolarMagnet
from ..magnetique import Bend as _Bend
from ..magnetique import Quadrupole as _Quadrupole
from ..commands import Collimator as _Collimator
from ..commands import ZgoubidooException as _ZgoubidooException
from ... import ureg as _ureg


class DipoleIBA(_Dipole):
    """IBA generic dipole.

    """

    @property
    def extra_drift(self) -> _ureg.Quantity:
        """

        Returns:

        """
        return _PolarMagnet.drift_length_from_polar(radius=self.radius,
                                                    magnet_angle=self.AT,
                                                    poles_angle=self.OMEGA_E - self.OMEGA_S)


class B1G(DipoleIBA):
    """Proteus One 40 degree dipole.

    Examples:
        >>> B1G()
    """
    PARAMETERS = {
        'LABEL1': 'B1G',
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


class B2G(DipoleIBA):
    """Proteus One 70 degree dipole.

    Examples:
        >>> B2G()
    """
    PARAMETERS = {
        'LABEL1': 'B2G',
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


class B3G(DipoleIBA):
    """Proteus One 60 degree dipole.

    Examples:
        >>> B3G()

    """
    PARAMETERS = {
        'LABEL1': 'B3G',
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


class QuadrupoleIBA(_Quadrupole):
    """IBA generic quadrupole.

    Support for gradient/current conversion and for polarity.
    """
    def post_init(self, polarity=None, p=None, l_eff=None, gradient=0.0, **kwargs):
        """

        Args:
            polarity:
            p:
            l_eff:
            gradient:
            **kwargs:

        Returns:

        """
        self._current = 0.0
        self._gradient = gradient
        if self.PARAMETERS.get('POLARITY'):
            self.polarity = self.POLARITY
        else:
            self.polarity = polarity
        self.__P = p
        self.__L_EFF = l_eff

    @property
    def polarity(self):
        """

        Returns:

        """
        if self._polarity is None:
            raise _ZgoubidooException("Polarity must be explicitely set.")
        elif self._polarity == 1.:
            return 'HORIZONTAL'
        elif self._polarity == -1.:
            return 'VERTICAL'

    @polarity.setter
    def polarity(self, value):
        err = 'Polarity of quadrupole should be HORIZONTAL or VERTICAL'
        try:
            if value is None:
                raise _ZgoubidooException(err)
            elif value.upper() == 'HORIZONTAL':
                self._polarity = 1.
            elif value.upper() == 'VERTICAL':
                self._polarity = -1.
            else:
                raise _ZgoubidooException(err)
        except AttributeError:
            raise _ZgoubidooException(err)

    @property
    def current(self):
        """

        Returns:

        """
        try:
            return self._current
        except AttributeError:
            raise Exception("Hello")

    @current.setter
    def current(self, current):
        if current < 0.0:
            raise Exception("Trying to set a quadrupole with a negative current. Adjust the polarity instead.")
        self._current = current
        self._gradient = _np.poly1d(self.p)(current) / self.l_eff

    @property
    def gradient(self):
        """

        Returns:

        """
        return self._polarity * self._gradient

    @gradient.setter
    def gradient(self, gradient):
        if gradient < 0.0:
            raise Exception("Trying to set a quadrupole with a negative gradient. Adjust the polarity instead.")
        self._gradient = gradient
        self._current = _np.roots([self.p[0], self.p[1], self.p[2] - _np.abs(gradient * self.l_eff)])[1]

    def set_value(self, value):
        self.current = value

    @property
    def k1(self):
        """

        Returns:

        """
        return self.gradient

    @k1.setter
    def k1(self, value):
        self._gradient = _np.abs(value)
        self._polarity = _np.sign(value)
        self._current = _np.roots([self.p[0], self.p[1], self.p[2] - _np.abs(self._gradient * self.l_eff)])[1]

    @property
    def p(self):
        """

        Returns:

        """
        return self.__P

    @p.setter
    def p(self, value):
        self.__P = value
        self.current = self._current

    @property
    def l_eff(self):
        """

        Returns:

        """
        return self.__L_EFF

    @l_eff.setter
    def l_eff(self, value):
        self.__L_EFF = value
        self.current = self._current


class QLong(QuadrupoleIBA):
    """Proteus One long quadrupole.

    """
    PARAMETERS = {
        'XL': 490 * _ureg.mm,
    }

    def post_init(self, polarity: Optional[str]=None, **kwargs):
        """

        Args:
            polarity:
            **kwargs:

        Returns:

        """
        super().post_init(polarity=polarity,
                          p=[-2.45367E-05, 8.09526E-02, -6.91149E-03],
                          l_eff=0.490)


class QShort(QuadrupoleIBA):
    """Proteus One short quadrupole.

    """
    PARAMETERS = {
        'XL': 290 * _ureg.mm,
    }

    def post_init(self, polarity: Optional[str]=None, **kwargs):
        """

        Args:
            polarity:
            **kwargs:

        Returns:

        """

        super().post_init(polarity=polarity,
                          p=[-2.27972E-05, 4.98563E-02, -1.58432E-02],
                          l_eff=0.290)


class QWall(QuadrupoleIBA):
    """Proteus One 'wall' quadrupole.

    """
    PARAMETERS = {
        'XL': 297 * _ureg.mm,
    }

    def post_init(self, polarity: Optional[str]=None, **kwargs):
        """

        Args:
            polarity:
            **kwargs:

        Returns:

        """
        super().post_init(polarity=polarity,
                          p=[-2.23625E-06, 2.46011E-02, 8.21584E-04],
                          l_eff=0.297)


class QPMQ(QuadrupoleIBA):
    """Proteus One 'PMQ' quadrupole.

    """
    PARAMETERS = {
        'XL': 297 * _ureg.mm,
    }

    def post_init(self, polarity: Optional[str] = None, **kwargs):
        """

        Args:
            polarity:
            **kwargs:

        Returns:

        """
        super().post_init(polarity=polarity,
                          gradient=17.5)


class Q1G(QWall):
    """Proteus One 'Q1G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q1G',
        'POLARITY': 'VERTICAL',
    }


class Q2G(QWall):
    """Proteus One 'Q2G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q2G',
        'POLARITY': 'HORIZONTAL',
    }


class Q3G(QShort):
    """Proteus One 'Q3G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q3G',
        'POLARITY': 'HORIZONTAL',
    }


class Q4G(QShort):
    """Proteus One 'Q4G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q4G',
        'POLARITY': 'VERTICAL',
    }


class Q5G(QLong):
    """Proteus One 'Q5G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q5G',
        'POLARITY': 'HORIZONTAL',
    }


class Q6G(QShort):
    """Proteus One 'Q6G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q6G',
        'POLARITY': 'VERTICAL',
    }


class Q7G(QShort):
    """Proteus One 'Q7G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q7G',
        'POLARITY': 'HORIZONTAL',
    }


class HorizontalSlits(_Collimator):
    """Proteus One horizontal slits.

    """
    pass


class VerticalSlits(_Collimator):
    """Proteus One vertical slits.

    """
    pass
