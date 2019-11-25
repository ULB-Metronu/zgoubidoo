"""Zgoubidoo's

More details here.
TODO
"""
from typing import List, Optional, Union, Iterable, Tuple
import numpy as _np
import pandas as _pd
import lmfit
from ..magnetique import Dipole as _Dipole
from ..magnetique import PolarMagnet as _PolarMagnet
from ..magnetique import Multipole as _Multipole
from ..magnetique import Quadrupole as _Quadrupole
from ..magnetique import Drift as _Drift
from ..commands import Collimator as _Collimator
from ..commands import Marker as _Marker
from ..commands import Ymy as _Ymy
from ..actions import Fit as _Fit
from ..actions import FitType as _FitType
from ..commands import Chamber as _Chamber
from ..particules import Proton as _Proton
from ..commands import ChangeRef as _ChangeRef
from ..beam import Beam as _Beam
from ..beam import BeamInputDistribution as _BeamInputDistribution
from ... import ureg as _ureg
from ... import Q_ as _Q
from ...input import Input as _Input
from ...mappings import MappedParametersType as _MappedParametersType
from ... import Kinematics as _Kinematics
from ...zgoubi import Zgoubi as _Zgoubi
from ...zgoubi import ZgoubiResults as _ZgoubiResults
from ...polarity import PolarityType as _PolarityType
from ...polarity import Polarity as _Polarity
from ...polarity import HorizontalPolarity as _HorizontalPolarity
from ...polarity import VerticalPolarity as _VerticalPolarity
from ...fieldmaps import EngeModel as _EngeModel
import zgoubidoo


class DipoleIBA(_Dipole):
    """IBA generic dipole.

    The main feature is to provide a method to compute extra drift length taken by the polar extension of the field map.

    Examples:
        >>> d = DipoleIBA()
        >>> d.extra_drift()
    """

    @property
    def extra_drift(self) -> _ureg.Quantity:
        """Compute the extra drift length of the field map extension.

        See Also:
            `_PolarMagnet.drift_length_from_polar`.

        Returns:
            the drift lenght.
        """
        return _PolarMagnet.drift_length_from_polar(radius=self.radius,
                                                    magnet_angle=self.AT,
                                                    poles_angle=self.OMEGA_E - self.OMEGA_S)

    def process_fit_field_profile(self, fit: lmfit.model.ModelResult):
        """

        Args:
            fit:

        Returns:

        """
        self.LAM_E = fit.best_values['lam_e'] * _ureg.m
        self.LAM_S = fit.best_values['lam_s'] * _ureg.m
        self.C0_E = fit.best_values['ce_0']
        self.C1_E = fit.best_values['ce_1']
        self.C2_E = fit.best_values['ce_2']
        self.C3_E = fit.best_values['ce_3']
        self.C4_E = fit.best_values['ce_4']
        self.C5_E = fit.best_values['ce_5']
        self.C0_S = fit.best_values['cs_0']
        self.C1_S = fit.best_values['cs_1']
        self.C2_S = fit.best_values['cs_2']
        self.C3_S = fit.best_values['cs_3']
        self.C4_S = fit.best_values['cs_4']
        self.C5_S = fit.best_values['cs_5']
        #self.XL = (fit.best_values['offset_s'] - fit.best_values['offset_e']) * _ureg.m


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
        self._field_profile_model = _EngeModel()
        self._field_profile_model.params['ce_0'].set(vary=True)
        self._field_profile_model.params['ce_1'].set(vary=False)
        self._field_profile_model.params['ce_2'].set(vary=True)
        self._field_profile_model.params['ce_3'].set(vary=True)
        self._field_profile_model.params['ce_4'].set(vary=True)
        self._field_profile_model.params['ce_5'].set(vary=True)
        self._field_profile_model.params['cs_0'].set(vary=True)
        self._field_profile_model.params['cs_1'].set(vary=False)
        self._field_profile_model.params['cs_2'].set(vary=True)
        self._field_profile_model.params['cs_3'].set(vary=True)
        self._field_profile_model.params['cs_4'].set(vary=True)
        self._field_profile_model.params['cs_5'].set(vary=True)
        self._field_profile_model.params['offset_e'].set(value=134, min=0, max=400)
        self._field_profile_model.params['offset_s'].set(value=1302, min=1000, max=1400)
        self._field_profile_model.params['lam_e'].set(value=99)
        self._field_profile_model.params['lam_s'].set(value=75)
        self._field_profile_model.params['amplitude'].set(value=-2.0)
        self._field_profile_model.params['field_offset'].set(vary=True, value=0.0, min=-1e-3, max=1e-3)


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
        self._field_profile_model = _EngeModel()
        self._field_profile_model.params['ce_0'].set(vary=True)
        self._field_profile_model.params['ce_1'].set(vary=False)
        self._field_profile_model.params['ce_2'].set(vary=True)
        self._field_profile_model.params['ce_3'].set(vary=True)
        self._field_profile_model.params['ce_4'].set(vary=True)
        self._field_profile_model.params['ce_5'].set(vary=True)
        self._field_profile_model.params['cs_0'].set(vary=True)
        self._field_profile_model.params['cs_1'].set(vary=False)
        self._field_profile_model.params['cs_2'].set(vary=True)
        self._field_profile_model.params['cs_3'].set(vary=True)
        self._field_profile_model.params['cs_4'].set(vary=True)
        self._field_profile_model.params['cs_5'].set(vary=True)
        self._field_profile_model.params['offset_e'].set(value=400, min=0, max=500)
        self._field_profile_model.params['offset_s'].set(value=2000, min=1500, max=2300)
        self._field_profile_model.params['lam_e'].set(value=50)
        self._field_profile_model.params['lam_s'].set(value=50)
        self._field_profile_model.params['amplitude'].set(value=-2.0)
        self._field_profile_model.params['field_offset'].set(vary=True, value=0.0, min=-1e-3, max=1e-3)


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
        'XPAS': 1.0 * _ureg.mm,
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
        self._field_profile_model = _EngeModel()
        self._field_profile_model.params['ce_0'].set(vary=True)
        self._field_profile_model.params['ce_1'].set(vary=False)
        self._field_profile_model.params['ce_2'].set(vary=True)
        self._field_profile_model.params['ce_3'].set(vary=True)
        self._field_profile_model.params['ce_4'].set(vary=True)
        self._field_profile_model.params['ce_5'].set(vary=True)
        self._field_profile_model.params['cs_0'].set(vary=True)
        self._field_profile_model.params['cs_1'].set(vary=False)
        self._field_profile_model.params['cs_2'].set(vary=True)
        self._field_profile_model.params['cs_3'].set(vary=True)
        self._field_profile_model.params['cs_4'].set(vary=True)
        self._field_profile_model.params['cs_5'].set(vary=True)
        self._field_profile_model.params['offset_e'].set(value=400, min=0, max=500)
        self._field_profile_model.params['offset_s'].set(value=2000, min=1500, max=2300)
        self._field_profile_model.params['lam_e'].set(value=50)
        self._field_profile_model.params['lam_s'].set(value=50)
        self._field_profile_model.params['amplitude'].set(value=-2.0)
        self._field_profile_model.params['field_offset'].set(vary=True, value=0.0, min=-1e-3, max=1e-3)


class SMX(_Multipole):
    """Proteus One inline (horizontal) scanning magnet.

    """
    PARAMETERS = {
        'XL': 0.26317552187769017 * _ureg.m,
        'LAM_E': 0.03879980891555799 * _ureg.m,
        'C0_E': 2.260586829767431,
        'C2_E': -0.08454912439481363,
        'C3_E': 0.03165152479873875,
        'C4_E': -0.016368674101593452,
        'C5_E': 0.002271083461208103,
        'LAM_S': 0.019573704193528198 * _ureg.m,
        'C0_S': 0.007471653696559507,
        'C2_S': -0.1596436867616995,
        'C3_S': 0.02917407661831325,
        'C4_S': -0.0022865133242955886,
        'C5_S': 7.362703656240262e-05,
    }

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        self.LABEL1 = self.__class__.__name__
        self._field_profile_model = _EngeModel()
        self._field_profile_model.params['ce_0'].set(vary=True)
        self._field_profile_model.params['ce_1'].set(vary=False)
        self._field_profile_model.params['ce_2'].set(vary=True)
        self._field_profile_model.params['ce_3'].set(vary=True)
        self._field_profile_model.params['ce_4'].set(vary=True)
        self._field_profile_model.params['ce_5'].set(vary=True)
        self._field_profile_model.params['cs_0'].set(vary=True)
        self._field_profile_model.params['cs_1'].set(vary=False)
        self._field_profile_model.params['cs_2'].set(vary=True)
        self._field_profile_model.params['cs_3'].set(vary=True)
        self._field_profile_model.params['cs_4'].set(vary=True)
        self._field_profile_model.params['cs_5'].set(vary=True)
        self._field_profile_model.params['offset_e'].set(value=0.2, min=0.1, max=0.3)
        self._field_profile_model.params['offset_s'].set(value=0.5, min=0.35, max=0.55)
        self._field_profile_model.params['lam_e'].set(value=0.03)
        self._field_profile_model.params['lam_s'].set(value=0.03)
        self._field_profile_model.params['amplitude'].set(value=-0.82, min=-0.9, max=-0.75)
        self._field_profile_model.params['field_offset'].set(vary=True, value=0.0, min=-1e-3, max=1e-3)

    def process_fit_field_profile(self, fit: lmfit.model.ModelResult):
        """

        Args:
            fit:

        Returns:

        """
        self.LAM_E = fit.best_values['lam_e'] * _ureg.m
        self.LAM_S = fit.best_values['lam_s'] * _ureg.m
        self.C0_E = fit.best_values['ce_0']
        self.C1_E = fit.best_values['ce_1']
        self.C2_E = fit.best_values['ce_2']
        self.C3_E = fit.best_values['ce_3']
        self.C4_E = fit.best_values['ce_4']
        self.C5_E = fit.best_values['ce_5']
        self.C0_S = fit.best_values['cs_0']
        self.C1_S = fit.best_values['cs_1']
        self.C2_S = fit.best_values['cs_2']
        self.C3_S = fit.best_values['cs_3']
        self.C4_S = fit.best_values['cs_4']
        self.C5_S = fit.best_values['cs_5']
        self.XL = (fit.best_values['offset_s'] - fit.best_values['offset_e']) * _ureg.m


class SMY(_Multipole):
    """Proteus One crossline (vertical) scanning magnet.

    """
    PARAMETERS = {
        'XL': 0.15221715277508374 * _ureg.m,
        'R1': 90 * _ureg.degree,
        'LAM_E': 0.037857895089871904 * _ureg.m,
        'C0_E': 0.1999859299335233,
        'C2_E': 0.08542911466613756,
        'C3_E': -0.028865773164774223,
        'C4_E': -0.004292970946705814,
        'C5_E': 0.00536700990602016,
        'LAM_S': 0.03846389166292385 * _ureg.m,
        'C0_S': 0.2482542942709081,
        'C2_S': 0.02638766212507734,
        'C3_S': 0.008102763875877633,
        'C4_S': -0.006877068617401515,
        'C5_S': 0.0007046649650343981,
    }

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        self.LABEL1 = self.__class__.__name__
        self._field_profile_model = _EngeModel()
        self._field_profile_model.params['ce_0'].set(vary=True)
        self._field_profile_model.params['ce_1'].set(vary=False)
        self._field_profile_model.params['ce_2'].set(vary=True)
        self._field_profile_model.params['ce_3'].set(vary=True)
        self._field_profile_model.params['ce_4'].set(vary=True)
        self._field_profile_model.params['ce_5'].set(vary=True)
        self._field_profile_model.params['cs_0'].set(vary=True)
        self._field_profile_model.params['cs_1'].set(vary=False)
        self._field_profile_model.params['cs_2'].set(vary=True)
        self._field_profile_model.params['cs_3'].set(vary=True)
        self._field_profile_model.params['cs_4'].set(vary=True)
        self._field_profile_model.params['cs_5'].set(vary=True)
        self._field_profile_model.params['offset_e'].set(value=0.1, min=0.1, max=0.4)
        self._field_profile_model.params['offset_s'].set(value=0.7, min=0.4, max=0.8)
        self._field_profile_model.params['lam_e'].set(value=0.035)
        self._field_profile_model.params['lam_s'].set(value=0.035)
        self._field_profile_model.params['amplitude'].set(value=-0.4, min=-0.6, max=-0.3)
        self._field_profile_model.params['field_offset'].set(value=0.0, min=-1e-3, max=1e-3)

    def process_fit_field_profile(self, fit: lmfit.model.ModelResult):
        """

        Args:
            fit:

        Returns:

        """
        self.LAM_E = fit.best_values['lam_e'] * _ureg.m
        self.LAM_S = fit.best_values['lam_s'] * _ureg.m
        self.C0_E = fit.best_values['ce_0']
        self.C1_E = fit.best_values['ce_1']
        self.C2_E = fit.best_values['ce_2']
        self.C3_E = fit.best_values['ce_3']
        self.C4_E = fit.best_values['ce_4']
        self.C5_E = fit.best_values['ce_5']
        self.C0_S = fit.best_values['cs_0']
        self.C1_S = fit.best_values['cs_1']
        self.C2_S = fit.best_values['cs_2']
        self.C3_S = fit.best_values['cs_3']
        self.C4_S = fit.best_values['cs_4']
        self.C5_S = fit.best_values['cs_5']
        self.XL = (fit.best_values['offset_s'] - fit.best_values['offset_e']) * _ureg.m


class T1G(_Multipole):
    """Proteus One steering magnet.

    """
    PARAMETERS = {
        'XL': 209.1 * _ureg.mm,
        'B1': 1e-6 * _ureg.gauss,
    }

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        self.LABEL1 = self.__class__.__name__


class T2G(_Multipole):
    """Proteus One steering magnet.

    """
    PARAMETERS = {
        'XL': 209.1 * _ureg.mm,
        'B1': 1e-6 * _ureg.gauss,
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
        self._gradient = 0.0
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
        return self._current

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
        """Set the current."""
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
        elif value == 0:
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
        if self._current is not None:
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
        if self._current is not None:
            self.current = self._current

    @property
    def B0(self):
        return self.gradient * self.R0.to('m').magnitude * _ureg.tesla


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


class Q1C(QShort):
    """Proteus One 'Q1C' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q1C',
        'POLARITY': _VerticalPolarity,
    }


class Q2C(QShort):
    """Proteus One 'Q2C' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q2C',
        'POLARITY': _VerticalPolarity,
    }


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

    def post_init(self,
                  **kwargs,
                  ):
        """
        TODO
        Args:
            **kwargs:

        Example:
            >>> q3g = Q3G()

        """
        self._field_profile_model = _EngeModel()
        self._field_profile_model.params['ce_0'].set(vary=True)
        self._field_profile_model.params['ce_1'].set(vary=False)
        self._field_profile_model.params['ce_2'].set(vary=True)
        self._field_profile_model.params['ce_3'].set(vary=True)
        self._field_profile_model.params['ce_4'].set(vary=True)
        self._field_profile_model.params['ce_5'].set(vary=True)
        self._field_profile_model.params['cs_0'].set(vary=True)
        self._field_profile_model.params['cs_1'].set(vary=False)
        self._field_profile_model.params['cs_2'].set(vary=True)
        self._field_profile_model.params['cs_3'].set(vary=True)
        self._field_profile_model.params['cs_4'].set(vary=True)
        self._field_profile_model.params['cs_5'].set(vary=True)
        self._field_profile_model.params['offset_e'].set(value=100, min=0, max=200)
        self._field_profile_model.params['offset_s'].set(value=400, min=300, max=500)
        self._field_profile_model.params['lam_e'].set(value=50)
        self._field_profile_model.params['lam_s'].set(value=50)
        self._field_profile_model.params['amplitude'].set(value=0.2)
        self._field_profile_model.params['field_offset'].set(vary=True, value=0.0, min=-1e-3, max=1e-3)


class Q4G(QShort):
    """Proteus One 'Q4G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q4G',
        'POLARITY': _VerticalPolarity,
    }

    def post_init(self,
                  **kwargs,
                  ):
        """
        TODO
        Args:
            **kwargs:

        Example:
            >>> q4g = Q4G()

        """
        self._field_profile_model = _EngeModel()
        self._field_profile_model.params['ce_0'].set(vary=True)
        self._field_profile_model.params['ce_1'].set(vary=False)
        self._field_profile_model.params['ce_2'].set(vary=True)
        self._field_profile_model.params['ce_3'].set(vary=True)
        self._field_profile_model.params['ce_4'].set(vary=True)
        self._field_profile_model.params['ce_5'].set(vary=True)
        self._field_profile_model.params['cs_0'].set(vary=True)
        self._field_profile_model.params['cs_1'].set(vary=False)
        self._field_profile_model.params['cs_2'].set(vary=True)
        self._field_profile_model.params['cs_3'].set(vary=True)
        self._field_profile_model.params['cs_4'].set(vary=True)
        self._field_profile_model.params['cs_5'].set(vary=True)
        self._field_profile_model.params['offset_e'].set(value=100, min=0, max=200)
        self._field_profile_model.params['offset_s'].set(value=400, min=300, max=500)
        self._field_profile_model.params['lam_e'].set(value=50)
        self._field_profile_model.params['lam_s'].set(value=50)
        self._field_profile_model.params['amplitude'].set(value=0.2)
        self._field_profile_model.params['field_offset'].set(vary=True, value=0.0, min=-1e-3, max=1e-3)


class Q5G(QLong):
    """Proteus One 'Q5G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q5G',
        'POLARITY': _HorizontalPolarity,
    }

    def post_init(self,
                  **kwargs,
                  ):
        """
        TODO
        Args:
            **kwargs:

        Example:
            >>> q5g = Q5G()

        """
        self._field_profile_model = _EngeModel()
        self._field_profile_model.params['ce_0'].set(vary=True)
        self._field_profile_model.params['ce_1'].set(vary=False)
        self._field_profile_model.params['ce_2'].set(vary=True)
        self._field_profile_model.params['ce_3'].set(vary=True)
        self._field_profile_model.params['ce_4'].set(vary=True)
        self._field_profile_model.params['ce_5'].set(vary=True)
        self._field_profile_model.params['cs_0'].set(vary=True)
        self._field_profile_model.params['cs_1'].set(vary=False)
        self._field_profile_model.params['cs_2'].set(vary=True)
        self._field_profile_model.params['cs_3'].set(vary=True)
        self._field_profile_model.params['cs_4'].set(vary=True)
        self._field_profile_model.params['cs_5'].set(vary=True)
        self._field_profile_model.params['offset_e'].set(value=275, min=100, max=350)
        self._field_profile_model.params['offset_s'].set(value=883, min=700, max=950)
        self._field_profile_model.params['lam_e'].set(value=100)
        self._field_profile_model.params['lam_s'].set(value=100)
        self._field_profile_model.params['amplitude'].set(value=-0.25)
        self._field_profile_model.params['field_offset'].set(vary=True, value=0.0, min=-1e-3, max=1e-3)


class Q6G(QShort):
    """Proteus One 'Q6G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q6G',
        'POLARITY': _VerticalPolarity,
    }

    def post_init(self,
                  **kwargs,
                  ):
        """
        TODO
        Args:
            **kwargs:

        Example:
            >>> q6g = Q6G()

        """
        self._field_profile_model = _EngeModel()
        self._field_profile_model.params['ce_0'].set(vary=True)
        self._field_profile_model.params['ce_1'].set(vary=False)
        self._field_profile_model.params['ce_2'].set(vary=True)
        self._field_profile_model.params['ce_3'].set(vary=True)
        self._field_profile_model.params['ce_4'].set(vary=True)
        self._field_profile_model.params['ce_5'].set(vary=True)
        self._field_profile_model.params['cs_0'].set(vary=True)
        self._field_profile_model.params['cs_1'].set(vary=False)
        self._field_profile_model.params['cs_2'].set(vary=True)
        self._field_profile_model.params['cs_3'].set(vary=True)
        self._field_profile_model.params['cs_4'].set(vary=True)
        self._field_profile_model.params['cs_5'].set(vary=True)
        self._field_profile_model.params['offset_e'].set(value=100, min=0, max=200)
        self._field_profile_model.params['offset_s'].set(value=400, min=300, max=500)
        self._field_profile_model.params['lam_e'].set(value=50)
        self._field_profile_model.params['lam_s'].set(value=50)
        self._field_profile_model.params['amplitude'].set(value=0.2)
        self._field_profile_model.params['field_offset'].set(vary=True, value=0.0, min=-1e-3, max=1e-3)


class Q7G(QShort):
    """Proteus One 'Q7G' gantry quadrupole.

    """
    PARAMETERS = {
        'LABEL1': 'Q7G',
        'POLARITY': _HorizontalPolarity,
    }

    def post_init(self,
                  **kwargs,
                  ):
        """
        TODO
        Args:
            **kwargs:

        Example:
            >>> q7g = Q7G()

        """
        self._field_profile_model = _EngeModel()
        self._field_profile_model.params['ce_0'].set(vary=True)
        self._field_profile_model.params['ce_1'].set(vary=False)
        self._field_profile_model.params['ce_2'].set(vary=True)
        self._field_profile_model.params['ce_3'].set(vary=True)
        self._field_profile_model.params['ce_4'].set(vary=True)
        self._field_profile_model.params['ce_5'].set(vary=True)
        self._field_profile_model.params['cs_0'].set(vary=True)
        self._field_profile_model.params['cs_1'].set(vary=False)
        self._field_profile_model.params['cs_2'].set(vary=True)
        self._field_profile_model.params['cs_3'].set(vary=True)
        self._field_profile_model.params['cs_4'].set(vary=True)
        self._field_profile_model.params['cs_5'].set(vary=True)
        self._field_profile_model.params['offset_e'].set(value=100, min=0, max=200)
        self._field_profile_model.params['offset_s'].set(value=400, min=300, max=500)
        self._field_profile_model.params['lam_e'].set(value=50)
        self._field_profile_model.params['lam_s'].set(value=50)
        self._field_profile_model.params['amplitude'].set(value=0.2)
        self._field_profile_model.params['field_offset'].set(vary=True, value=0.0, min=-1e-3, max=1e-3)


class HorizontalSlits(_Collimator):
    """Proteus One horizontal slits.

    """

    PARAMETERS = {
        'J': 0,
        'IFORM': 1,
        'IA': 1,
    }

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        self.LABEL1 = self.__class__.__name__


class SL1G(HorizontalSlits):
    """First vertical collimator

    """
    PARAMETERS = {
        'LABEL1': 'SL1G',
        'C1': 27.5 * _ureg.mm,
        'C2': 1.5 * _ureg.cm,
    }


class SL3G(HorizontalSlits):
    """First vertical collimator

    """
    PARAMETERS = {
        'LABEL1': 'SL3G',
        'C1': 27.5 * _ureg.mm,
        'C2': 0.5 * _ureg.cm,
    }

class VerticalSlits(_Collimator):
    """Proteus One vertical slits.

    """
    PARAMETERS = {
        'J': 0,
        'IFORM': 1,
        'IA': 1,
    }

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        self.LABEL1 = self.__class__.__name__


class SL2G(VerticalSlits):
    """First horizontal collimator

    """
    PARAMETERS = {
        'LABEL1': 'SL2G',
        'C1': 0.6 * _ureg.cm,
        'C2': 27.5 * _ureg.mm,
    }


class ResearchArea:
    """Proteus One research area input sequence."""
    def __init__(self):
        """
        TODO
        """
        pass


class CGTR:
    """Proteus One compact gantry (CGTR) input sequence.

    TODO
    Examples:
        >>> cgtr = CGTR()
        >>> cgtr.shoot()
    """
    def __init__(self,
                 kinematics: _Kinematics = _Kinematics(230 * _ureg.MeV, kinetic=True),
                 b1g: Optional[B1G] = None,
                 b2g: Optional[B2G] = None,
                 b3g: Optional[B3G] = None,
                 t1g: Optional[T1G] = None,
                 t2g: Optional[T2G] = None,
                 q1g: Optional[Q1G] = None,
                 q2g: Optional[Q2G] = None,
                 q3g: Optional[Q3G] = None,
                 q4g: Optional[Q4G] = None,
                 q5g: Optional[Q5G] = None,
                 q6g: Optional[Q6G] = None,
                 q7g: Optional[Q7G] = None,
                 smx: Optional[SMX] = None,
                 smy: Optional[SMY] = None,
                 sl1g: Optional[SL1G] = None,
                 sl2g: Optional[SL2G] = None,
                 sl3g: Optional[SL3G] = None,
                 beam: Optional[_Beam] = None,
                 with_fit: bool = True,
                 ):
        """

        Args:
            kinematics:
            b1g:
            b2g:
            b3g:
            t1g:
            t2g:
            q1g:
            q2g:
            q3g:
            q4g:
            q5g:
            q6g:
            q7g:
            smx:
            smy:
            beam:
            with_fit: if True the dipole magnets of the line will be fit.
        """
        self.b1g: B1G = b1g or B1G()
        self.b2g: B2G = b2g or B2G()
        self.b3g: B3G = b3g or B3G()
        self.t1g: T1G = t1g or T1G()
        self.t2g: T2G = t2g or T2G()
        self.q1g: Q1G = q1g or Q1G()
        self.q2g: Q2G = q2g or Q2G()
        self.q3g: Q3G = q3g or Q3G()
        self.q4g: Q4G = q4g or Q4G()
        self.q5g: Q5G = q5g or Q5G()
        self.q6g: Q6G = q6g or Q6G()
        self.q7g: Q7G = q7g or Q7G()
        self.smx: SMX = smx or SMX()
        self.smy: SMY = smy or SMY()
        self.sl1g: SL1G = sl1g or SL1G()
        self.sl2g: SL2G = sl2g or SL2G()
        self.sl3g: SL3G = sl3g or SL3G()
        self.beam: _Beam = beam or _BeamInputDistribution('BUNCH', slices=1, kinematics=kinematics.brho)
        self.start: _Marker = _Marker('START')
        self.iso: _Marker = _Marker('ISO')

        if with_fit:
            self.fit_dipoles(kinematics=kinematics)

        self.zi: _Input = _Input('CGTR', line=[
            self.beam,
            _Proton(),
            self.start,
            _Collimator('C1G', IA=1, IFORM=2, J=0, C1=5 * _ureg.mm, C2=5 * _ureg.mm),
            _Chamber('Chamber1', IA=1, IFORM=2, J=0, C1=29.75 * _ureg.mm, C2=29.75 * _ureg.mm),
            _Drift
            ('C1G_T1G', XL=9.2995 * _ureg.cm),
            #_ChangeRef(),
            _Ymy(),
            self.t1g,
            _Drift
            ('T1G_T2G', XL=2.09 * _ureg.cm),
            self.t2g,
            _Drift
            ('T2G_Q1G', XL=38.7855 * _ureg.cm),
            self.q1g,
            _Drift
            ('Q1G_Q2G', XL=30.3 * _ureg.cm),
            self.q2g,
            _Drift
            ('Q2G_SL1G', XL=19.719 * _ureg.cm + 3 * _ureg.cm),
            self.sl1g,
            _Drift
            ('SL1G_SL2G', XL=3 * _ureg.cm + 3 * _ureg.cm + 1 * _ureg.cm),
            self.sl2g,
            _Drift
            ('SL2G_B1G', XL=39.734 * _ureg.cm + 3 * _ureg.cm - self.b1g.extra_drift),
            _Chamber(IA=2),
            _Chamber('Chamber2', IA=1, IFORM=1, J=0, C1=2.9 * _ureg.cm, C2=1.29 * _ureg.cm, C3=self.b1g.RM),
            self.b1g,
            _Chamber(IA=2),
            _Ymy(),
            _Chamber('Chamber3', IA=1, IFORM=2, J=0, C1=29.75 * _ureg.mm, C2=29.75 * _ureg.mm),
            _Drift
            ('B1G_Q3G', XL=26.44 * _ureg.cm - self.b1g.extra_drift),
            self.q3g,
            _Drift
            ('Q3G_Q4G', XL=32.6 * _ureg.cm),
            self.q4g,
            _Drift
            ('Q4G_Q5G', XL=33.4 * _ureg.cm),
            self.q5g,
            _Drift
            ('Q5G_Q6G', XL=33.5 * _ureg.cm),
            self.q6g,
            _Drift
            ('Q6G_Q7G', XL=36.0 * _ureg.cm),
            self.q7g,
            _Drift
            ('Q7G_SL3G', XL=16.5682507 * _ureg.cm + 3 * _ureg.cm),
            self.sl3g,
            _Drift
            ('SL3G_B2G', XL=30.9927502 * _ureg.cm + 3 * _ureg.cm - self.b2g.extra_drift),
            _Chamber(IA=2),
            _Chamber('Chamber4', IA=1, IFORM=1, J=0, C1=11/2 * _ureg.cm, C2=2.58/2 * _ureg.cm, C3=self.b2g.RM),
            self.b2g,
            _Chamber(IA=2),
            _Drift
            ('B2G_SMX', XL=31.77 * _ureg.cm - self.b2g.extra_drift - (self.smx.length - 159 * _ureg.mm)/2),
            self.smx,
            _Drift
            ('SMX_SMY', XL=13.04 * _ureg.cm - (self.smx.length - 159 * _ureg.mm)/2 - (self.smy.length - 109 * _ureg.mm)/2),
            self.smy,
            _Drift
            ('SMY_B3G', XL=20.39 * _ureg.cm - self.b3g.extra_drift + self.b3g.extra_drift - (self.smy.length - 109 *_ureg.mm)/2),
            _Collimator('B3G_ENTRY', IA=1, IFORM=1, J=0, C1=11/2 * _ureg.cm, C2=9/2 * _ureg.cm),
            self.b3g,
            _Collimator('B3G_EXIT', IA=1, IFORM=1, J=0, C1=13.65/2 * _ureg.cm, C2=9/2 * _ureg.cm),
            _Drift
            ('FINAL', XL=1101.071 * _ureg.mm - self.b3g.extra_drift +
                                   self.b3g.extra_drift - 0.20950282594698123 * _ureg.meter),
            self.iso,
        ],
                                 )
        self.kinematics = kinematics
        self.tracks: Optional[_pd.DataFrame] = None
        self.results: Optional[_ZgoubiResults] = None

    @property
    def line(self) -> _Input:
        """Provides the full CGTR input sequence.

        Returns:
            the CGTR input sequence.
        """
        return self.zi

    @property
    def gantry_angle(self):
        """Gantry angle (in IBA reference system)."""
        pass

    @gantry_angle.setter
    def gantry_angle(self, angle):
        pass

    def fit_dipoles(self, kinematics: _Kinematics, dipoles: Optional[List[DipoleIBA]] = None):
        """Adjusts the main field of the dipoles according to the beam energy.

        The adjustment is made so that the reference trajectory exists the magnet on axis.

        Args:
            kinematics: the beam kinematics
            dipoles: a list of dipoles to fit
        """
        z = _Zgoubi()
        dipoles = dipoles or [self.b1g, self.b2g, self.b3g]
        for dipole in dipoles:
            dipole.fit(kinematics=kinematics, zgoubi=z)
        z.wait()

    def run(self,
            zgoubi: zgoubidoo.Zgoubi,
            identifier: Optional[_MappedParametersType] = None,
            ):
        """

        Args:
            zgoubi: TODO
            identifier: TODO

        Returns:

        """
        zgoubi(code_input=self.zi, identifier=identifier or {})

    def fit(self,
            zgoubi: zgoubidoo.Zgoubi,
            identifier: _MappedParametersType,
            fit: zgoubidoo.commands.Fit,
            ) -> zgoubidoo.commands.Fit:
        """

        Args:
            zgoubi:
            identifier:
            fit:

        Returns:

        """
        zi = _Input(name=f"FIT_{fit.LABEL1}", line=self.zi.line + [fit])
        zi.IL = 0
        zgoubi(code_input=zi, identifier=identifier)
        return fit

    def shoot(self,
              x: float,
              y: float,
              zgoubi: zgoubidoo.Zgoubi,
              fit_type: _FitType = _Fit,
              ) -> zgoubidoo.commands.Fit:
        """

        Args:
            x:
            y:
            zgoubi: TODO
            fit_type:

        Returns:
            The Fit command (instance object) with the results of the fit.
        """
        fit = fit_type(
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
        fit = self.fit(zgoubi=zgoubi or _Zgoubi(),
                       identifier={'SPOT_X': x, 'SPOT_Y': y},
                       fit=fit,
                       )
        return fit

    def spots(self,
              spots: Iterable[Tuple[float, float]],
              fit_type: _FitType = _Fit,
              with_tracks: bool = False,
              debug_fit: bool = False
              ) -> Union[_pd.DataFrame, List[_Fit]]:
        """

        Args:
            spots:
            fit_type:
            with_tracks:
            debug_fit:

        Returns:

        """
        self.zi.cleanup()
        self.beam.REFERENCE = 1
        z = _Zgoubi()
        fits = [
            self.shoot(x=float(spot[0]), y=float(spot[1]), zgoubi=z, fit_type=fit_type) for spot in spots
        ]
        z.cleanup()
        if debug_fit:
            return fits
        self.zi.IL = 2 if with_tracks else 0
        self.beam.REFERENCE = 0
        for f in fits:
            for p, r in f.results:
                self.zi.update(r.results)
                self.run(zgoubi=z,
                         identifier={**p, **{'SMX.B1': r.results.at[1, 'final'], 'SMY.B1': r.results.at[2, 'final']}},
                         )
        self.results = z.collect()
        tracks = self.results.tracks
        if len(tracks) == 0:
            return tracks
        self.tracks = tracks
        return tracks

    def plot(self,
             artist: zgoubidoo.vis.ZgoubidooPlotlyArtist = None,
             start: Optional[Union[str, zgoubidoo.commands.Command]] = None,
             stop: Optional[Union[str, zgoubidoo.commands.Command]] = None,
             crosshair: bool = True
             ):
        """Plot the P1 beamline.

        TODO

        Args:
            artist: an artist object for the rendering
            start: first element of the beamline to be plotted
            stop: last element of the beamline to be plotted
            crosshair: draw a crosshair indicating the isocenter
        """
        self.line.survey()

        if artist is None:
            artist = zgoubidoo.vis.ZgoubidooPlotlyArtist()

        artist.plot_beamline(self.line)

        return artist
