"""Zgoubidoo's interfaces to purefly magnetic Zgoubi commands.

More details here.
TODO
"""
from typing import List
import numpy as _np
import pandas as _pd
from ..magnetique import Dipole as _Dipole
from ..magnetique import PolarMagnet as _PolarMagnet
from ..magnetique import Bend as _Bend
from ..magnetique import Quadrupole as _Quadrupole
from ..magnetique import FakeDrift as _FakeDrift
from ..commands import Collimator as _Collimator
from ..commands import Marker as _Marker
from ..commands import Ymy as _Ymy
from ..commands import Fit as _Fit
from ..particules import Proton as _Proton
from ..objet import Objet2 as _Objet2
from ... import ureg as _ureg
from ...input import Input as _Input
from ...physics import Kinematics as _Kinematics
from ...zgoubi import Zgoubi as _Zgoubi
from ...zgoubi import ZgoubiRun as _ZgoubiRun
from ...polarity import PolarityType as _PolarityType
from ...polarity import Polarity as _Polarity
from ...polarity import HorizontalPolarity as _HorizontalPolarity
from ...polarity import VerticalPolarity as _VerticalPolarity
import zgoubidoo


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
        'RM': 1500 * _ureg.mm,
    }

    def post_init(self,
                  magnet_opening=50 * _ureg.degree,
                  poles_opening=40 * _ureg.degree,
                  entrance_pole_trim=0 * _ureg.degree,
                  exit_pole_trim=0 * _ureg.degree,
                  entrance_fringe_lambda=9 * _ureg.cm,
                  exit_fringe_lambda=9 * _ureg.cm,
                  **kwargs,
                  ):
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
                  ):
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
                  ):
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
        'SK': 90 * _ureg.degree,
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
    def post_init(self,
                  polarity: _PolarityType = _HorizontalPolarity,
                  p=None,
                  l_eff: float = None,
                  gradient: float = 0.0,
                  **kwargs
                  ):
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
    def polarity(self) -> str:
        """

        Returns:

        """
        return str(self._polarity)

    @polarity.setter
    def polarity(self, value: _PolarityType):
        self._polarity = value

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
            raise Exception("Trying to set a quadrupole with a negative current. Change the polarity instead.")
        self._current = current
        self._gradient = _np.poly1d(self.p)(current) / self.l_eff

    @property
    def gradient(self):
        """

        Returns:

        """
        return int(self._polarity) * self._gradient

    @gradient.setter
    def gradient(self, gradient):
        if gradient < 0.0:
            raise Exception("Trying to set a quadrupole with a negative gradient. Change the polarity instead.")
        self._gradient = gradient
        self._current = _np.roots([self.p[0], self.p[1], self.p[2] - _np.abs(gradient * self.l_eff)])[1]
        super().gradient = gradient

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
        if value > 0:
            self._polarity = _HorizontalPolarity
        elif value == 0 :
            self._polarity = _Polarity
        else:
            self._polarity = _VerticalPolarity
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

    def post_init(self, polarity: _PolarityType = _HorizontalPolarity, **kwargs):
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

    def post_init(self, polarity: _PolarityType = _HorizontalPolarity, **kwargs):
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

    def post_init(self, polarity: _PolarityType = _HorizontalPolarity, **kwargs):
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

    def post_init(self, polarity: _PolarityType = _HorizontalPolarity, **kwargs):
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
        'POLARITY': _VerticalPolarity,
    }


class Q2G(QWall):
    """Proteus One 'Q2G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q2G',
        'POLARITY': _HorizontalPolarity,
    }


class Q3G(QShort):
    """Proteus One 'Q3G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q3G',
        'POLARITY': _HorizontalPolarity,
    }


class Q4G(QShort):
    """Proteus One 'Q4G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q4G',
        'POLARITY': _VerticalPolarity,
    }


class Q5G(QLong):
    """Proteus One 'Q5G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q5G',
        'POLARITY': _HorizontalPolarity,
    }


class Q6G(QShort):
    """Proteus One 'Q6G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q6G',
        'POLARITY': _VerticalPolarity,
    }


class Q7G(QShort):
    """Proteus One 'Q7G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q7G',
        'POLARITY': _HorizontalPolarity,
    }


class HorizontalSlits(_Collimator):
    """Proteus One horizontal slits.

    """
    pass


class VerticalSlits(_Collimator):
    """Proteus One vertical slits.

    """
    pass


class CGTR:
    """Proteus One compact gantry (CGTR) input sequence.

    """
    def __init__(self,
                 kinematics=_Kinematics(230 * _ureg.MeV),
                 b1g=B1G(),
                 b2g=B2G(),
                 b3g=B3G(),
                 q1g=Q1G(),
                 q2g=Q2G(),
                 q3g=Q3G(),
                 q4g=Q4G(),
                 q5g=Q5G(),
                 q6g=Q6G(),
                 q7g=Q7G(),
                 smx=SMX(),
                 smy=SMY(),
                 ):
        """

        Args:
            kinematics:
            b1g:
            b2g:
            b3g:
            q1g:
            q2g:
            q3g:
            q4g:
            q5g:
            q6g:
            q7g:
            smx:
            smy:
        """
        self.b1g = b1g
        self.b2g = b2g
        self.b3g = b3g
        self.q1g = q1g
        self.q2g = q2g
        self.q3g = q3g
        self.q4g = q4g
        self.q5g = q5g
        self.q6g = q6g
        self.q7g = q7g
        self.smx = smx
        self.smy = smy

        b1g.fit(boro=kinematics.brho)
        b2g.fit(boro=kinematics.brho)
        b3g.fit(boro=kinematics.brho)

        self.zi = _Input('CGTR', line=[
            _Objet2('BUNCH', BORO=kinematics.brho).add([[0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]]),
            _Proton(),
            _Marker('START'),
            _Ymy(),
            self.q1g,
            _FakeDrift(XL=30.3 * _ureg.cm),
            self.q2g,
            _FakeDrift(XL=72.42 * _ureg.cm - b1g.extra_drift),
            self.b1g,
            _Ymy(),
            _FakeDrift(XL=26.4 * _ureg.cm - b1g.extra_drift),
            self.q3g,
            _FakeDrift(XL=32.6 * _ureg.cm),
            self.q4g,
            _FakeDrift(XL=33.3 * _ureg.cm),
            self.q5g,
            _FakeDrift(XL=33.6 * _ureg.cm),
            self.q6g,
            _FakeDrift(XL=36.0 * _ureg.cm),
            self.q7g,
            _FakeDrift(XL=60 * _ureg.cm - b2g.extra_drift),
            self.b2g,
            _FakeDrift(XL=26 * _ureg.cm - b2g.extra_drift),
            self.smx,
            _FakeDrift(XL=12 * _ureg.cm),
            self.smy,
            _FakeDrift(XL=19 * _ureg.cm - b3g.extra_drift),
            self.b3g,
            _FakeDrift(XL=1101.071 * _ureg.mm - b3g.extra_drift),
            _Marker('ISO'),
        ],
                         )
        self.tracks = None
        zgoubidoo.survey(beamline=self.line)

    @property
    def line(self):
        """

        Returns:

        """
        return self.zi

    def run(self, fit=None):
        """

        Args:
            self:
            fit:

        Returns:

        """
        z = _Zgoubi()
        if fit is not None:
            self.zi += fit
            z(self.zi())
            self.zi.update(fit.results)
            self.zi -= fit
            out = z(self.zi())
        else:
            out = z(self.zi())
        if out is not None:
            zgoubidoo.survey(beamline=self.line)
        self.tracks = out.tracks
        return out

    def shoot(self, x=0.0, y=0.0):
        """

        Args:
            x:
            y:

        Returns:

        """
        self.scanning = zgoubidoo.commands.Fit(
            PENALTY=1e-8,
            PARAMS=[
                _Fit.Parameter(line=self.zi, place='SMX', parameter=SMX.B1_),
                _Fit.Parameter(line=self.zi, place='SMY', parameter=SMY.B1_),
            ],
            CONSTRAINTS=[
                _Fit.EqualityConstraint(line=self.zi, place='ISO', variable=_Fit.FitCoordinates.Y, value=x),
                _Fit.EqualityConstraint(line=self.zi, place='ISO', variable=_Fit.FitCoordinates.Z, value=y),
            ]
        )
        return self.run(fit=self.scanning)

    def spots(self, spots) -> _pd.DataFrame:
        """

        Args:
            spots:

        Returns:

        """
        tracks: List[_pd.DataFrame] = list()
        for spot in spots:
            _ = self.shoot(x=spot[0], y=spot[1])
            _.tracks['SPOT_X'] = spot[0]
            _.tracks['SPOT_Y'] = spot[1]
            tracks.append(_.tracks)
        df: _pd.DataFrame = _pd.concat(tracks)
        self.tracks = df
        return df

    def plot(self, ax=None, artist: zgoubidoo.vis.ZgoubiPlot = None):
        """

        Args:
            ax:
            artist:

        Returns:

        """
        if artist is None:
            artist = zgoubidoo.vis.ZgoubiMpl(ax=ax)

        zgoubidoo.vis.beamline(beamline=self.line,
                               artist=artist,
                               tracks=self.tracks,
                               )

        artist.ax.set_aspect('equal', 'datalim')
        artist.ax.hlines(0.0, -10, 1000)
