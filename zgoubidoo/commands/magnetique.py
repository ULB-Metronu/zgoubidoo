"""Zgoubidoo's interfaces to purefly magnetic Zgoubi commands.

More details here.
TODO
"""

from typing import Optional, List
import numpy as _np
import pandas as _pd
import parse as _parse
import lmfit
from .particules import ParticuleType as _ParticuleType
from .commands import CommandType as _CommandType
from .actions import FitType as _FitType
from .commands import Command as _Command
from .commands import Marker as _Marker
from .actions import Fit as _Fit
from .actions import Fit2 as _Fit2
from .commands import ZgoubidooException as _ZgoubidooException
from .objet import Objet2 as _Objet2
from .particules import Proton as _Proton
from .. import ureg as _ureg
from .. import Q_ as _Q
from ..zgoubi import Zgoubi as _Zgoubi
from .patchable import Patchable as _Patchable
from .plotable import Plotable as _Plotable
from ..fieldmaps import FieldMap as _FieldMap
from ..units import _cm, _radian, _kilogauss, _degree, _ampere
import zgoubidoo
from georges_core.kinematics import Kinematics as _Kinematics
from georges_core.frame import Frame as _Frame


class MagnetType(_CommandType):
    """Type for magnetic element commands."""
    pass


class Magnet(_Command, _Patchable, _Plotable, metaclass=MagnetType):
    """Base class for all magnetic elements.

    TODO
    """
    PARAMETERS = {
        'HEIGHT': (20 * _ureg.cm, 'Height of the magnet (distance between poles), used by plotting functions.'),
        'POLE_WIDTH': (30 * _ureg.cm, 'Pole width (used for plotting only).'),
        'PIPE_THICKNESS': (2 * _ureg.cm, 'Thickness of the pipe, used by plotting functions.'),
        'PIPE_COLOR': ('grey', 'Color of the pipe, used by plotting functions.'),
        'REFERENCE_FIELD_COMPONENT': ('BZ', 'Orientation of the reference field (used by field maps)'),
        'KINEMATICS': (None, 'A kinematics object.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
        commands (e.g. fit)."""

    def post_init(self, field_map: Optional[_FieldMap] = None, **kwargs):
        """

        Args:
            field_map:
            **kwargs:

        Returns:

        """
        self.field_map = field_map
        # noinspection PyAttributeOutsideInit
        self._field_profile_model = None

    @property
    def field_map(self) -> _FieldMap:
        """Attach a field map to the element."""
        return self._field_map

    @field_map.setter
    def field_map(self, v: _FieldMap):
        # noinspection PyAttributeOutsideInit
        self._field_map = v

    @property
    def field_profile_model(self):
        """A model for the field profile."""
        return self._field_profile_model

    def process_fit_field_profile(self, fit: lmfit.model.ModelResult):
        """
        
        Args:
            fit: 

        Returns:

        """
        pass


class CartesianMagnetType(MagnetType):
    """Type for cartesian magnets."""
    pass


class CartesianMagnet(Magnet, metaclass=CartesianMagnetType):
    """Base class for magnetic elements in cartesian coordinates.

    TODO
    """
    PARAMETERS = {
        'APERTURE_LEFT': (10 * _ureg.cm, 'Aperture size of the magnet, left side (used for plotting only).'),
        'APERTURE_RIGHT': (10 * _ureg.cm, 'Aperture size of the magnet, right side (used for plotting only).'),
        'APERTURE_TOP': (10 * _ureg.cm, 'Aperture size of the magnet, top side (used for plotting only).'),
        'APERTURE_BOTTOM': (10 * _ureg.cm, 'Aperture size of the magnet, bottom side (used for plotting only).'),
        'COLOR': ('black', 'Magnet color for plotting.'),
        'LENGTH_IS_ARC_LENGTH': (False, ''),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
        commands (e.g. fit)."""

    def post_init(self, **kwargs):
        if self.LENGTH_IS_ARC_LENGTH:
            if self.KINEMATICS is None:
                raise _ZgoubidooException("Arc length conversion requested but KINEMATICS not provided.")
            arc_length = self.XL
            field = self.B0 if self.B1 is None else self.B1
            rho = self.KINEMATICS.brho / field
            phi = arc_length / rho
            self.XL = 2 * rho * _np.sin(phi / 2)

    @property
    def rotation(self) -> _Q:
        """

        Returns:

        """
        return self.ALE or 0.0 * _ureg.degree

    @property
    def length(self) -> _Q:
        """

        Returns:

        """
        return self.XL

    @property
    def x_offset(self) -> _Q:
        """

        Returns:

        """
        return self.XCE or 0.0 * _ureg.cm

    @property
    def y_offset(self) -> _Q:
        """

        Returns:

        """
        return self.YCE or 0.0 * _ureg.cm

    @property
    def entry_patched(self) -> Optional[_Frame]:
        """

        Returns:

        """
        if self._entry_patched is None:
            self._entry_patched = self.entry.__class__(self.entry)
            if self.KPOS in (0, 1, 2):
                self._entry_patched.translate_x(-(self.X_E or 0.0 * _ureg.cm))
                self._entry_patched.translate_x(self.x_offset)
                self._entry_patched.translate_y(self.y_offset)
                self._entry_patched.rotate_z(-self.rotation)
            elif self.KPOS == 3:
                self._entry_patched.translate_x(-(self.X_E or 0.0 * _ureg.cm))
                if self.rotation != 0:
                    raise _ZgoubidooException("Non zero ALE incompatible with KPOS = 3.")
                self._entry_patched.rotate_z(
                    -_np.arcsin(
                        (self.XL * self.B1) / (2 * self.KINEMATICS.brho))
                )
                self._entry_patched.translate_y(self.y_offset)
        return self._entry_patched

    @property
    def exit(self) -> Optional[_Frame]:
        """

        Returns:

        """
        if self._exit is None:
            self._exit = self.entry_patched.__class__(self.entry_patched)
            self._exit.translate_x(self.length + (self.X_E or 0.0 * _ureg.cm))
        return self._exit

    @property
    def exit_patched(self) -> Optional[_Frame]:
        """

        Returns:

        """
        if self._exit_patched is None:
            if self.KPOS is None or self.KPOS == 1:
                self._exit_patched = self.exit.__class__(self.exit)
                self._exit_patched.translate_x(-(self.X_S or 0.0 * _ureg.cm))
            elif self.KPOS == 0 or self.KPOS == 2:
                self._exit_patched = self.entry.__class__(self.entry)
                self._exit_patched.translate_x(self.XL or 0.0 * _ureg.cm)
                self._exit_patched.translate_x(-(self.X_S or 0.0 * _ureg.cm))
            elif self.KPOS == 3:
                if self.rotation != 0:
                    raise _ZgoubidooException("Non zero ALE incompatible with KPOS = 3.")
                self._exit_patched = self.exit.__class__(self.exit)
                self._exit_patched.translate_y(-self.y_offset)
                self._exit_patched.rotate_z(
                    -_np.arcsin(
                        (self.XL * self.B1) / (2 * self.KINEMATICS.brho)) * _ureg.radian
                )
        return self._exit_patched

    @property
    def wedge_angle_entrance(self) -> _Q:
        return self.W_E or 0 * _ureg.radians

    @property
    def wedge_angle_exit(self) -> _Q:
        return self.W_S or 0 * _ureg.radians

    @property
    def optical_ref_length(self) -> _Q:
        return self.XL


class PolarMagnetType(MagnetType):
    """Type for polar magnets."""
    pass


class PolarMagnet(Magnet, metaclass=PolarMagnetType):
    """Base class for magnetic elements in polar coordinates.

    TODO
    """
    PARAMETERS = {
        'POLE_WIDTH': 150 * _ureg.cm,
        'APERTURE_LEFT': (10 * _ureg.cm, 'Aperture size of the magnet, left side (used for plotting only).'),
        'APERTURE_RIGHT': (10 * _ureg.cm, 'Aperture size of the magnet, right side (used for plotting only).'),
        'APERTURE_TOP': (10 * _ureg.cm, 'Aperture size of the magnet, top side (used for plotting only).'),
        'APERTURE_BOTTOM': (10 * _ureg.cm, 'Aperture size of the magnet, bottom side (used for plotting only).'),
        'COLOR': 'blue',
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
        commands (e.g. fit)."""

    def adjust_tracks_variables(self, tracks: _pd.DataFrame):
        t = tracks[tracks.LABEL1 == self.LABEL1]
        radius = self.RM.m_as('m')
        angles = 100 * t['X']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ANGLE'] = angles
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'R'] = t['Y']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'R0'] = t['Yo']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'SREF'] = radius * angles + self.entry_sref.m_as('m')
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT'] = t['Y'] - radius
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT0'] = t['Yo'] - radius
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT'] = t['Z']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT0'] = t['Zo']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'X'] = t['Y'] * _np.sin(angles)
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'X0'] = t['Yo'] * _np.sin(angles)
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'Y'] = t['Y'] * _np.cos(angles) - radius
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'Y0'] = t['Yo'] * _np.cos(angles) - radius

    @property
    def angular_opening(self) -> _Q:
        """

        Returns:

        """
        return self.AT or 0 * _ureg.degree

    @property
    def reference_angles(self) -> List[_Q]:
        """

        Returns:

        """
        return [self.ACENT or 0 * _ureg.degree]

    @property
    def entrance_efb(self) -> List[_Q]:
        """

        Returns:

        """
        return [self.OMEGA_E or 0 * _ureg.degree]

    @property
    def exit_efb(self) -> List[_Q]:
        """

        Returns:

        """
        return [self.OMEGA_S or 0 * _ureg.degree]

    @property
    def radius(self) -> _Q:
        """

        Returns:

        """
        return self.RM or 0 * _ureg.cm

    @property
    def length(self) -> _Q:
        """

        Returns:

        """
        return self.angular_opening.to('rad').magnitude * self.radius

    @property
    def entry_patched(self) -> Optional[_Frame]:
        """

        Returns:

        """
        if self._entry_patched is None:
            self._entry_patched = self.entry.__class__(self.entry)
            self._entry_patched.translate_y(self.radius - (self.RE or 0 * _ureg.cm))
            self._entry_patched.rotate_z(-self.TE or 0 * _ureg.degree)
        return self._entry_patched

    @property
    def center(self) -> Optional[_Frame]:
        """

        Returns:

        """
        if self._center is None:
            self._center = self.entry_patched.__class__(self.entry_patched)
            self._center.translate_y(-self.radius)
        return self._center

    @property
    def exit(self) -> Optional[_Frame]:
        """

        Returns:

        """
        if self._exit is None:
            self._exit = self.center.__class__(self.center)
            self._exit.translate_y(self.radius)
            self._exit.rotate_z(-self.angular_opening)
        return self._exit

    @property
    def exit_patched(self) -> Optional[_Frame]:
        """

        Returns:

        """
        if self._exit_patched is None:
            self._exit_patched = self.exit.__class__(self.exit)
            self._exit_patched.translate_y((self.RS or 0 * _ureg.cm) - self.radius)
            self._exit_patched.rotate_z(self.TS or 0 * _ureg.degree)
        return self._exit_patched

    @staticmethod
    def drift_length_from_polar(radius: _Q, magnet_angle: _Q, poles_angle: _Q) -> _Q:
        """

        Args:
            radius: the reference radius of the magnet
            magnet_angle: total angular opening of the magnet (i.e. of the field-map)
            poles_angle: angular opening of the poles

        Returns:

        """
        return radius * _np.tan(((magnet_angle - poles_angle) / 2).to('radian').magnitude)

    @staticmethod
    def efb_offset_from_polar(radius: _Q, magnet_angle: _Q, poles_angle: _Q) -> _Q:
        """

        Args:
            radius: the reference radius of the magnet
            magnet_angle: total angular opening of the magnet (i.e. of the field-map)
            poles_angle: angular opening of the poles

        Returns:

        """
        return radius / _np.cos(((magnet_angle - poles_angle) / 2).to('radian').magnitude)

    @staticmethod
    def efb_angle_from_polar(magnet_angle: _Q, poles_angle: _Q) -> _Q:
        """

        Args:
            magnet_angle: total angular opening of the magnet (i.e. of the field-map)
            poles_angle: angular opening of the poles

        Returns:

        """
        return -(magnet_angle - poles_angle) / 2

    @property
    def entrance_field_boundary_wedge_angle(self) -> List[_Q]:
        return [self.THETA_E]

    @property
    def exit_field_boundary_wedge_angle(self) -> List[_Q]:
        return [self.THETA_S]

    @property
    def n_magnets(self) -> int:
        return 1

    @property
    def entrance_field_boundary_linear_extent_down(self) -> List[_Q]:
        return [-self.U1_E]

    @property
    def entrance_field_boundary_linear_extent_up(self) -> List[_Q]:
        return [self.U2_E]

    @property
    def entrance_field_boundary_linear_radius_up(self) -> List[_Q]:
        return [self.R2_E]

    @property
    def entrance_field_boundary_linear_radius_down(self) -> List[_Q]:
        return [self.R1_E]

    @property
    def exit_field_boundary_linear_extent_down(self) -> List[_Q]:
        return [-self.U1_S]

    @property
    def exit_field_boundary_linear_extent_up(self) -> List[_Q]:
        return [self.U2_S]

    @property
    def exit_field_boundary_linear_radius_up(self) -> List[_Q]:
        return [self.R2_S]

    @property
    def exit_field_boundary_linear_radius_down(self) -> List[_Q]:
        return [self.R1_S]

    @property
    def delta_radius(self) -> List[_Q]:
        return [0 * _ureg.m]

    @property
    def optical_ref_length(self) -> _Q:
        return self.radius * self.angular_opening.m_as('radians')


class PolarMultiMagnetType(PolarMagnetType):
    """Type for polar multi magnets."""
    def __getattr__(cls, key: str):
        try:
            if key.endswith('_'):
                # TODO
                return 42
                return cls.PARAMETERS[key.rstrip('_')][2]
            else:
                super().__getattr__(key)
        except KeyError:
            raise AttributeError(key)


class PolarMultiMagnet(PolarMagnet, metaclass=PolarMultiMagnetType):

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        for i in range(self.N):
            if _degree(self.OMEGA_E[i]) == 0:
                self.OMEGA_E[i] = self.AT / (2 * self.N) + i * self.AT / self.N
            if _degree(self.OMEGA_S[i]) == 0:
                self.OMEGA_S[i] -= (self.AT - self.AT / (2 * self.N) - i * self.AT / self.N)
            if _cm(self.RE) == 0:
                self.RE = self.RM
            if _cm(self.RS) == 0:
                self.RS = self.RM

    @property
    def reference_angles(self) -> List[_Q]:
        return self.ACN

    @property
    def n_magnets(self) -> int:
        return self.N

    @property
    def entrance_efb(self) -> List[_Q]:
        """

        Returns:

        """
        return self.OMEGA_E

    @property
    def exit_efb(self) -> List[_Q]:
        """

        Returns:

        """
        return self.OMEGA_S

    @property
    def delta_radius(self) -> List[_Q]:
        return self.DRM

    @property
    def entrance_field_boundary_wedge_angle(self) -> List[_Q]:
        return self.THETA_E

    @property
    def exit_field_boundary_wedge_angle(self) -> List[_Q]:
        return self.THETA_S

    @property
    def entrance_field_boundary_linear_extent_down(self) -> List[_Q]:
        return -self.U1_E

    @property
    def entrance_field_boundary_linear_extent_up(self) -> List[_Q]:
        return self.U2_E

    @property
    def entrance_field_boundary_linear_radius_up(self) -> List[_Q]:
        return self.R2_E

    @property
    def entrance_field_boundary_linear_radius_down(self) -> List[_Q]:
        return self.R1_E

    @property
    def exit_field_boundary_linear_extent_down(self) -> List[_Q]:
        return -self.U1_S

    @property
    def exit_field_boundary_linear_extent_up(self) -> List[_Q]:
        return self.U2_S

    @property
    def exit_field_boundary_linear_radius_up(self) -> List[_Q]:
        return self.R2_S

    @property
    def exit_field_boundary_linear_radius_down(self) -> List[_Q]:
        return self.R1_S


class AGSMainMagnet(CartesianMagnet):
    r"""AGS main magnet.

    .. rubric:: Zgoubi manual description

    The AGS main magnet is a combined function dipole with straight axis (lines of constant field are straight lines).
    The field computation routines for AGSMM are the same as for MULTIPOL (details in section 1.3.7, page 26),
    however AGSMM has the following four particularities :

    * There are only three multipole components present in AGSMM : dipole, quadrupole and sextupole.

    * The dipole field B0 is drawn from the reference rigidity, Bρref ,
      and follows the latter so to preserve :math:`\rho = B\rho_{ref}/B0` and the orbit deviation L/ρ. In particular,

            * in the absence of acceleration, Bρref ≡ BORO, with BORO the quantity appearing in the object definition
              using [MC]OBJET,

            * in presence of acceleration using CAVITE, Bρref is changed to BORO×Dref at each passage in the cavity,
              with Dref the relative synchronous momentum increase, a quantity that zgoubi updates at cavity traversal.

    * The field indices, quadrupole K1 and sextupole K2, are derived from the reference rigidity, Bρref ,
      via momentum-dependent polynomials, taken from Ref. [39], and following in that the methods found
      in the MAD model of the AGS [40].

    * The AGS main dipole has back-leg windings, used for instance for injection and extraction orbit bumps.

    The number of winding turns and the number of ampere-turns are part of the data in the input data list.
    The intensity in the windings is accounted for in the conversion from total ampere-turns in the magnet to momentum
    and then to magnetic field.
    Note : A consequence of items 2 and 3 is that no field value is required in defining the AGS main magnets
    in the zgoubi.dat input data list.
    """
    KEYWORD = 'AGSMM'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (2, "Print field and coordinates along trajectories", 1),
        'MOD': (1, "Type of dipole magnet"),
        'dL': (0.0 * _ureg.centimeter, "UNUSED"),
        'R0': (10.0 * _ureg.centimeter, 'Radius of the pole tips'),
        'dB1': (0, 'Relative error on dipole component'),
        'dB2': (0, 'Relative error on quadrupole component'),
        'dB3': (0, 'Relative error on sextupole component'),
        'NBLW': (0, 'Number of back-leg windings', 20),
        'WMOD': (1, 'Back-leg winding model',),
        'NW': ([0], 'Number of windings',),
        'I': ([0] * _ureg.ampere, 'Current of windings',),
        'X_E': (0 * _ureg.centimeter, 'Entrance face integration zone for the fringe field', 21),
        'LAM_E': (0 * _ureg.centimeter, 'Entrance face fringe field extent', 22),
        'E2': (0 * _ureg.centimeter, 'Quadrupole fringe field extent', 23),
        'E3': (0 * _ureg.centimeter, 'Sextupole fringe field extent', 24),
        'NCE': (0, 'UNUSED', 30),
        'C0_E': (0, 'Fringe field coefficient C0', 31),
        'C1_E': (1, 'Fringe field coefficient C1', 32),
        'C2_E': (0, 'Fringe field coefficient C2', 33),
        'C3_E': (0, 'Fringe field coefficient C3', 34),
        'C4_E': (0, 'Fringe field coefficient C4', 35),
        'C5_E': (0, 'Fringe field coefficient C5', 36),
        'X_S': (0 * _ureg.centimeter, 'Exit face integration zone for the fringe field', 40),
        'LAM_S': (0 * _ureg.centimeter, 'Exit face fringe field extent', 41),
        'S2': (0 * _ureg.centimeter, 'Quadrupole fringe field extent', 21),
        'S3': (0 * _ureg.centimeter, 'Sextupole fringe field extent', 21),
        'NCS': (0, 'UNUSED', 50),
        'C0_S': (0, 'Fringe field coefficient C0', 51),
        'C1_S': (1, 'Fringe field coefficient C1', 52),
        'C2_S': (0, 'Fringe field coefficient C2', 53),
        'C3_S': (0, 'Fringe field coefficient C3', 54),
        'C4_S': (0, 'Fringe field coefficient C4', 55),
        'C5_S': (0, 'Fringe field coefficient C5', 56),
        'R1': (0 * _ureg.radian, 'Skew angle of field component R1', 60),
        'R2': (0 * _ureg.radian, 'Skew angle of field component R2', 60),
        'R3': (0 * _ureg.radian, 'Skew angle of field component R3', 60),
        'XPAS': (0.1 * _ureg.centimeter, 'Integration step', 70),
        'KPOS': (1, 'Misalignment type', 80),
        'XCE': (0 * _ureg.centimeter, 'x offset', 81),
        'YCE': (0 * _ureg.centimeter, 'y offset', 82),
        'ALE': (0 * _ureg.radian, 'misalignment rotation', 83),
        'XS': (0 * _ureg.centimeter, 'X shift', 81),
        'YS': (0 * _ureg.centimeter, 'Y shift', 81),
        'ZR': (0 * _ureg.centimeter, 'Z rotation', 81),
        'ZS': (0 * _ureg.centimeter, 'Z shift', 81),
        'YR': (0 * _ureg.centimeter, 'Y rotation', 81),
        'COLOR': ('#FF0000', 'Magnet color for plotting.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        if _cm(self.X_E) == 0 and _cm(self.R0) != 0 and self.LAM_E.magnitude != 0:
            self.X_E = 2 * self.R0
        if _cm(self.X_S) == 0 and _cm(self.R0) != 0 and self.LAM_S.magnitude != 0:
            self.X_S = 2 * self.R0

    def __str__(s):
        command = []
        c = f"""
                {super().__str__().rstrip()}
                {s.IL}
                {s.MOD} {_cm(s.dL):.12e}
                {_cm(s.R0):.12e} {s.dB1:.12e} {s.dB2:.12e} {s.dB3:.12e}
                {s.NBLW}[.{s.WMOD}]
             """
        command.append(c)
        c = f""
        for i in range(s.NBLW):
            c += f" {s.NW[i]} {_ampere(s.I[i]):.12e}"

        command.append(c)
        c = f"""
                {_cm(s.X_E):.12e} {_cm(s.LAM_E):.12e} {_cm(s.E2):.12e} {_cm(s.E3):.12e}
                {s.NCE} {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
                {_cm(s.X_S):.12e} {_cm(s.LAM_S):.12e} {_cm(s.S2):.12e} {_cm(s.S3):.12e}
                {s.NCS} {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
                {_radian(s.R1):.12e} {_radian(s.R2):.12e} {_radian(s.R3):.12e}
                {_cm(s.XPAS)}
                """
        command.append(c)

        if s.KPOS in (1, 3):
            c = f"""
                    {s.KPOS} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {_radian(s.ALE):.12e}
                """
        else:
            c = f"""   
                    {s.KPOS} {_cm(s.XS):.12e} {_cm(s.YS):.12e} {_cm(s.ZR):.12e} {_cm(s.ZS):.12e} {_cm(s.YR):.12e}
                """
        command.append(c)
        return ''.join(map(lambda _: _.rstrip(), command))


class AGSQuadrupole(CartesianMagnet):
    """AGS quadrupole.

    .. rubric:: Zgoubi manual description

    The AGS quadrupoles are regular quadrupoles. The simulation of ``AGSQUAD`` uses the same field modelling as
    ``MULTIPOL``, section 1.3.7, page 25. However amperes are provided as input to ``AGSQUAD`` rather than fields,
    the reason being that some of the AGS quadrupoles have two superimposed coil circuits, with separate power
    supplies. It has been dealt with this particularity by allowing for an additional set of multi- pole data in
    ``AGSQUAD``, compared to ``MULTIPOL``.
    The field in ``AGSQUAD`` is computed using transfer functions from the ampere-turns in the coils to magnetic
    field that account for the non-linearity of the magnetic permeability [33].
    """
    KEYWORD = 'AGSQUAD'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (2, "Print field and coordinates along trajectories", 1),
        'XL': (10.0 * _ureg.centimeter, "Magnet length (straight reference frame)", 10),
        'R0': (10.0 * _ureg.centimeter, 'Radius of the pole tips', 11),
        'IW1': (0 * _ureg.ampere, 'Current in windings', 12),
        'IW2': (0 * _ureg.ampere, 'Current in windings', 13),
        'IW3': (0 * _ureg.ampere, 'Current in windings', 14),
        'dIW1': (0, 'Relative error on current', 15),
        'dIW2': (0, 'Relative error on current', 16),
        'dIW3': (0, 'Relative error on current', 17),
        'X_E': (0 * _ureg.centimeter, 'Entrance face integration zone for the fringe field', 20),
        'LAM_E': (0 * _ureg.centimeter, 'Entrance face fringe field extent', 21),
        'NCE': (0, 'UNUSED', 30),
        'C0_E': (0, 'Fringe field coefficient C0', 31),
        'C1_E': (1, 'Fringe field coefficient C1', 32),
        'C2_E': (0, 'Fringe field coefficient C2', 33),
        'C3_E': (0, 'Fringe field coefficient C3', 34),
        'C4_E': (0, 'Fringe field coefficient C4', 35),
        'C5_E': (0, 'Fringe field coefficient C5', 36),
        'X_S': (0 * _ureg.centimeter, 'Exit face integration zone for the fringe field', 40),
        'LAM_S': (0 * _ureg.centimeter, 'Exit face fringe field extent', 41),
        'NCS': (0, 'UNUSED', 50),
        'C0_S': (0, 'Fringe field coefficient C0', 51),
        'C1_S': (1, 'Fringe field coefficient C1', 52),
        'C2_S': (0, 'Fringe field coefficient C2', 53),
        'C3_S': (0, 'Fringe field coefficient C3', 54),
        'C4_S': (0, 'Fringe field coefficient C4', 55),
        'C5_S': (0, 'Fringe field coefficient C5', 56),
        'R1': (0 * _ureg.radian, 'Roll angle', 60),
        'XPAS': (0.1 * _ureg.centimeter, 'Integration step', 70),
        'KPOS': (1, 'Misalignment type', 80),
        'XCE': (0 * _ureg.centimeter, 'x offset', 81),
        'YCE': (0 * _ureg.centimeter, 'y offset', 82),
        'ALE': (0 * _ureg.radian, 'misalignment rotation', 83),
        'COLOR': ('#FF0000', 'Magnet color for plotting.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        if _cm(self.X_E) == 0 and _cm(self.R0) != 0 and self.LAM_E.magnitude != 0:
            self.X_E = 2 * self.R0
        if _cm(self.X_S) == 0 and _cm(self.R0) != 0 and self.LAM_S.magnitude != 0:
            self.X_S = 2 * self.R0

    def __str__(s):
        return f"""
            {super().__str__().rstrip()}
            {s.IL}
            {_cm(s.XL):.12e} {_cm(s.R0):.12e} {_ampere(s.IW1):.12e} {_ampere(s.IW2):.12e} {_ampere(s.IW3):.12e}
            {s.dIW1 :.12e} {s.dIW2 :.12e} {s.dIW3 :.12e} 
            {_cm(s.X_E):.12e} {_cm(s.LAM_E):.12e}
            {s.NCE} {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
            {_cm(s.X_S):.12e} {_cm(s.LAM_S):.12e}
            {s.NCS} {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
            {_radian(s.R1):.12e}
            {_cm(s.XPAS)}
            {s.KPOS} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {_radian(s.ALE):.12e}
            """


class Aimant(PolarMagnet):
    """Generation of dipole mid-plane 2-D map, polar frame.

    TODO
    """
    KEYWORD = 'AIMANT'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'NFACE': 2,
        'IC': 0,  # 1, 2: print field map
        'IL': 0,  # 1, 2: print field and coordinates on trajectores
        'IAMAX': 0,
        'IRMAX': 0,
        'B0': 0,
        'N': 0,
        'B': 0,
        'G': 0,
        'AT': 0,
        'ACENT': 0,
        'RM': 0,
        'RMIN': 0,
        'RMAX': 0,
        'LAM_E': 0,
        'XI_E': 0,
        'NCE': 0,
        'C0_E': 0,
        'C1_E': 0,
        'C2_E': 0,
        'C3_E': 0,
        'C4_E': 0,
        'C5_E': 0,
        'SHIFT_E': 0,
        'OMEGA_E': 0,
        'THETA_E': 0,
        'R1_E': 1e9,
        'U1_E': -1e9,
        'U2_E': 1e9,
        'R2_E': 1e9,
        'LAM_S': 0,
        'XI_S': 0,
        'NCS': 0,
        'C0_S': 0,
        'C1_S': 0,
        'C2_S': 0,
        'C3_S': 0,
        'C4_S': 0,
        'C5_S': 0,
        'SHIFT_S': 0,
        'OMEGA_S': 0,
        'THETA_S': 0,
        'R1_S': 1e9,
        'U1_S': -1e9,
        'U2_S': 1e9,
        'R2_S': 1e9,
        'LAM_L': 0,
        'XI_L': 0,
        'NCL': 0,
        'C0_L': 0,
        'C1_L': 0,
        'C2_L': 0,
        'C3_L': 0,
        'C4_L': 0,
        'C5_L': 0,
        'SHIFT_L': 0,
        'OMEGA_L': 0,
        'THETA_L': 0,
        'R1_L': 1e9,
        'U1_L': -1e9,
        'U2_L': 1e9,
        'R2_L': 1e9,
        'RM3': 0,
        'NBS': 0,
        'R0': 0,
        'DELTAB': 0,
        'THETA_0': 0,
        'IORDRE': 4,
        'XPAS': 0.1,
        'KPOS': 2,
        'RE': 0,
        'TE': 0,
        'RS': 0,
        'TS': 0,
        'DP': 0,
        'SHIM_R1': [],
        'SHIM_R2': [],
        'SHIM_THETA1': [],
        'SHIM_THETA2': [],
        'SHIM_LAMBDA': [],
        'SHIM_GAMMA': [],
        'SHIM_ALPHA': [],
        'SHIM_BETA': [],
        'SHIM_MU': [],
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
        commands (e.g. fit)."""

    def __str__(s):
        command = []
        if s.NFACE not in (2, 3):
            raise _ZgoubidooException(f"Error : Zgoubido does not support NFACE = {s.NFACE}")

        c = f"""
                {super().__str__().rstrip()}
                {s.NFACE} {s.IC} {s.IL}
                {s.IAMAX} {s.IRMAX}
                {s.B0:.12e} {s.N:.12e} {s.B:.12e} {s.G:.12e}
                {s.AT:.12e} {s.ACENT:.12e} {s.RM:.12e} {s.RMIN:.12e} {s.RMAX:.12e}
                {s.LAM_E:.12e} {s.XI_E:.12e}
                {s.NCE} {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e} {s.SHIFT_E:.12e}
                {s.OMEGA_E:.12e} {s.THETA_E:.12e} {s.R1_E:.12e} {s.U1_E:.12e} {s.U2_E:.12e} {s.R2_E:.12e}
                {s.LAM_S:.12e} {s.XI_S:.12e}
                {s.NCS} {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e} {s.SHIFT_S:.12e}
                {s.OMEGA_S:.12e} {s.THETA_S:.12e} {s.R1_S:.12e} {s.U1_S:.12e} {s.U2_S:.12e} {s.R2_S:.12e}
            """
        command.append(c)

        if s.NFACE == 3:
            c = f"""
                    {s.LAM_L:.12e} {s.XI_L:.12e}
                    {s.NCL} {s.C0_L:.12e} {s.C1_L:.12e} {s.C2_L:.12e} {s.C3_L:.12e} {s.C4_L:.12e} {s.C5_L:.12e} {s.SHIFT_L:.12e}
                    {s.OMEGA_L:.12e} {s.THETA_L:.12e} {s.R1_L:.12e} {s.U1_L:.12e} {s.U2_L:.12e} {s.R2_L:.12e} {s.RM3:.12e}
                """
            command.append(c)

        if s.NBS == 0:
            command.append(f"""
                {s.NBS}
                """)
        elif s.NBS == -2:
            c = f"""
                    {s.NBS}
                    {s.R0:.12e} {s.DELTAB:.12e}
                    """
            command.append(c)
        elif s.NBS == -1:
            c = f"""
                    {s.NBS}
                    {s.THETA_0:.12e} {s.DELTAB:.12e}
                    """
            command.append(c)
        elif s.NBS >= 1:
            command.append(f"""
                {s.NBS}""")

            shim_r1 = len(s.SHIM_R1)
            shim_r2 = len(s.SHIM_R2)
            shim_theta1 = len(s.SHIM_THETA1)
            shim_theta2 = len(s.SHIM_THETA2)
            shim_lambda = len(s.SHIM_LAMBDA)
            shim_gamma = len(s.SHIM_GAMMA)
            shim_alpha = len(s.SHIM_ALPHA)
            shim_beta = len(s.SHIM_BETA)
            shim_mu = len(s.SHIM_MU)
            if shim_r1 \
                    == shim_r2 \
                    == shim_theta1 \
                    == shim_theta2 \
                    == shim_lambda \
                    == shim_gamma \
                    == shim_alpha \
                    == shim_beta \
                    == shim_mu:
                for i, j, k, l in zip(s.SHIM_R1, s.SHIM_R2, s.SHIM_THETA1, s.SHIM_LAMBDA):
                    command.append(f"""
                        {i:.12e} {j:.12e} {k:.12e} {l:.12e}
                        """)

                for i, j, k, l in zip(s.GAMMA, s.ALPHA, s.MU, s.BETA):
                    command.append(f"""
                                       {i:.12e} {j:.12e} {k:.12e} {l:.12e}
                                       """)
            else:
                raise _ZgoubidooException('Error : The shim parameters lists must have the same lenghts')

        c = f"""
                {s.IORDRE}
                {s.XPAS:.12e}
                """
        command.append(c)

        if s.KPOS not in (1, 2):
            raise _ZgoubidooException("KPOS must be equal to 1 or 2.")

        if s.KPOS == 2:
            if s.RE == 0:
                s.RE = s.RM
            if s.RS == 0:
                s.RS = s.RM
            c = f"""
                    {s.KPOS}
                    {s.RE:.12e} {s.TE:.12e} {s.RS:.12e} {s.TS:.12e}
                    """
            command.append(c)
        elif s.KPOS == 1:
            c = f"""
                    {s.KPOS}
                    {s.DP:.12e}
                    """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Cyclotron(Magnet):
    r"""Spiral sector cyclotron

    .. rubric:: Zgoubi manual description

    ``CYCLOTRON` provides a model of a spiral sector dipole field [31, Appendix C, p. 149] [32]. The source code has
     been derived from ``FFAG-SPI``, thus there is many similarities in their capabilities and operation.
     The field along the particle’s trajectory is computed as the particle motion proceeds, by using the magnet’s
     geometrical boundaries: At any position (R,θ) along the particle trajectory (see Fig 17), the value of the
     vertical component of the mid-plane field is calculated using:

    .. math::

    B_Z (R, θ) = B_{norm} × F (R, θ) × R(R)


    • :math:`R(R)= B_0 + B_1 × R + B_2 × R^2 + B_3 × R^3 + B_4 × R^4`,
    • :math:`B_{norm}` is a normalization coefficient,
    • F(R, θ) is the fringe field coefficient, given by (after Enge’s fringe model):

    .. math ::

    F(R,θ) = F_{entr}(R,θ) × F_{exit}(R,θ) = \frac{1}{1 + exp(P_{entr}(d_{entr}))}×\frac{1}{1 + exp(P_{exit}(d_{exit}))}

    where

    .. math ::

    P(d) = C_0+ C_1 (\frac{d}{g})+ C_2 (\frac{d}{g})^2+ C_3 (\frac{d}{g})^3+ C_4 (\frac{d}{g})^4+ C_5 (\frac{d}{g})^5

    and d is the distance from the Effective Field Boundary (EFB) either at the entrance or at the exit of
    the magnet (:math:`d_{entr} and d_{exit} as shown in Fig 17)

    The EFBs are modelled by a logarithmic spiral for which the angle ξ is allowed to increase radially, namely:

    .. math ::

    r = r_0 × exp􏰇( \frac{θ+ω}{tan ξ(r)} 􏰈 (6.3.14)

    where :math:`ξ(r)=ξ_0 +ξ_1 ×r + ξ_2 × r^2 + ξ_3 × r^3`, θ is the azimuthal angle (origin θ=0) and ω is a parameter
    used to position the EFB with respect to the azimuthal position θ=0.
    In this model, the magnet gap is also allowed to vary: g is given as a function of the radius by:

    .. math ::

    g(r) = g_0 + g_1 × r + g_2 × r^2 (6.3.15)

    The field is then extrapolated off median plane by means of Taylor series: for that, the median plane antisymmetry
    is assumed and the Maxwell equations are accommodated.

    Note that ``CYCLOTRON`` allows the overlapping of 5 such dipole fields. This follows the method described in [46].
    In the case of a cyclotron machine, the isochronicity is a crucial point: Because the revolution time has to be
    constant (:math:`f_{rev} = \frac{qB}{2πγm_0}`), this implies that the radial dependence of the field must be
    proportional to γ, so that :math:`R(\bar{R}) ∝ γ(\bar{R})`, where R is the average radius of the orbit.
    Since :math:`f_{rev} = \frac{v}{C}, where C is the path length of the particle for one closed orbit, one obtains,
    with a good approximation, that :math:'R ∝ β`. Thus,

    .. math ::

    R(R) \approx \frac{1}{\sqrt{1-(\frac{R}{R_0})^2}}

    """
    KEYWORD = 'CYCLOTRON'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, 'Print field and coordinates along trajectories', 1),
        'N': (1, 'Number of dipoles in the FFAG n-tuple (maximum 5)', 2),
        'AT': (0 * _ureg.degree, 'Total angular extent of the N dipoles', 3),
        'RM': (0.0 * _ureg.centimeter, 'Reference radius: mean radius used for the positioning of field boundaries', 4),
        # For each magnet in the n-tuple
        'TYP': (1.0, 'sector type: spiral, radial, both'),
        'ACN': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Azimuth for dipole positioning', 5),
        'DRM': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter,
                'Reference radius offset of each dipole : RM_i  = RM + DRM', 6),
        'BN': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.kilogauss, "Field normalization coefficient"),
        'BI_0': ([0.0, 0.0, 0.0, 0.0, 0.0], "Field normalization coefficient"),
        'BI_1': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -1, "Field normalization coefficient"),
        'BI_2': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -2, "Field normalization coefficient"),
        'BI_3': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -3, "Field normalization coefficient"),
        'BI_4': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -4, "Field normalization coefficient"),
        'BI_5': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -5, "Field normalization coefficient"),
        'BI_6': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -6, "Field normalization coefficient"),
        'BI_7': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -7, "Field normalization coefficient"),
        'BI_8': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -8, "Field normalization coefficient"),
        'BI_9': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -9, "Field normalization coefficient"),
        'BI_10': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -10, "Field normalization coefficient"),
        'BI_11': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -11, "Field normalization coefficient"),
        'BI_12': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -12, "Field normalization coefficient"),
        'BI_13': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -13, "Field normalization coefficient"),
        'BI_14': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -14, "Field normalization coefficient"),
        'BI_15': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -15, "Field normalization coefficient"),
        'BI_16': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -16, "Field normalization coefficient"),
        'BI_17': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -17, "Field normalization coefficient"),
        'BI_18': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -18, "Field normalization coefficient"),
        'BI_19': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -19, "Field normalization coefficient"),
        'BI_20': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm ** -20, "Field normalization coefficient"),
        'G0_E': ([10.0, 10.0, 10.0, 10.0, 10.0] * _ureg.cm,
                 'Reference gaps for the entrance fringe fields of each dipole.', 9),
        'K_E': ([0, 0, 0, 0, 0], 'Fringe field parameter kappa', 10),
        'G10_E': ([0, 0, 0, 0, 0] * _ureg.cm, ''),
        'G11_E': ([0, 0, 0, 0, 0] * _ureg.cm ** -3, ''),
        'NCE': ([0, 0, 0, 0, 0], 'UNUSED', 11),
        'C0_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C0', 12),
        'C1_E': ([1, 1, 1, 1, 1], 'Fringe field coefficient C1', 13),
        'C2_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C2', 14),
        'C3_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C3', 15),
        'C4_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C4', 16),
        'C5_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C5', 17),
        'C6_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C6', 17),
        'OMEGA_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Azimuth of an EFB with respect to ACN', 19),
        'XI0_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Spiral angle coefficient XI_0', 20),
        'XI1_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree * _ureg.cm ** -1, 'Spiral angle coefficient XI_1', 20),
        'XI2_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree * _ureg.cm ** -2, 'Spiral angle coefficient XI_2', 20),
        'XI3_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree * _ureg.cm ** -3, 'Spiral angle coefficient XI_3', 20),
        'AEN': ([0.0, 0.0, 0.0, 0.0, 0.0], 'Coefficient a for entrance radial face equation', 20),
        'BEN': ([0.0, 0.0, 0.0, 0.0, 0.0], 'Coefficient b for entrance radial face equation', 20),
        'CEN': ([0.0, 0.0, 0.0, 0.0, 0.0], 'Coefficient c for entrance radial face equation', 20),
        'G0_S': ([10.0, 10.0, 10.0, 10.0, 10.0] * _ureg.cm,
                 'Reference gaps for the exit fringe fields of each dipole.', 9),
        'K_S': ([0, 0, 0, 0, 0], 'Fringe field parameter kappa', 10),
        'G10_S': ([0, 0, 0, 0, 0] * _ureg.cm, ''),
        'G11_S': ([0, 0, 0, 0, 0] * _ureg.cm ** -3, ''),
        'NCS': ([0, 0, 0, 0, 0], 'UNUSED', 11),
        'C0_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C0', 12),
        'C1_S': ([1, 1, 1, 1, 1], 'Fringe field coefficient C1', 13),
        'C2_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C2', 14),
        'C3_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C3', 15),
        'C4_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C4', 16),
        'C5_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C5', 17),
        'C6_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C6', 17),
        'OMEGA_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Azimuth of an EFB with respect to ACN', 19),
        'XI0_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Spiral angle coefficient XI_0', 20),
        'XI1_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree * _ureg.cm ** -1, 'Spiral angle coefficient XI_1', 20),
        'XI2_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree * _ureg.cm ** -2, 'Spiral angle coefficient XI_2', 20),
        'XI3_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree * _ureg.cm ** -3, 'Spiral angle coefficient XI_3', 20),
        'AEX': ([0.0, 0.0, 0.0, 0.0, 0.0], 'Coefficient a for entrance radial face equation', 20),
        'BEX': ([0.0, 0.0, 0.0, 0.0, 0.0], 'Coefficient b for entrance radial face equation', 20),
        'CEX': ([0.0, 0.0, 0.0, 0.0, 0.0], 'Coefficient c for entrance radial face equation', 20),
        'G0_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm,
                 'UNUSED Reference gaps for the lateral fringe fields of each dipole.', 41),
        'K_L': ([-1, -1, -1, -1, -1], 'UNUSED Fringe field parameter kappa', 42),
        'NCL': ([0, 0, 0, 0, 0], 'UNUSED', 43),
        'C0_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C0', 44),
        'C1_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C1', 45),
        'C2_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C2', 46),
        'C3_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C3', 47),
        'C4_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C4', 48),
        'C5_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C5', 49),
        'SHIFT_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'UNUSED  Shift of the EFB', 50),
        'OMEGA_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'UNUSED ', 51),
        'XI_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'UNUSED Entrance face wedge angle', 52),
        # General parameters
        # The fit index depends on the number of magnets in the FFAG_SPI N-tuple (+52 for each new magnet)
        'KIRD': (2,
                 'Analytical computation (KIRD = 0) or numerical interpolation (KIRD = 2,4, 25) of field derivatives',
                 57),
        'RESOL': (2, '', 58),
        'XPAS': (1.0 * _ureg.millimeter, 'Integration step', 59),
        'RE': (0.0 * _ureg.centimeter, '', 61),
        'TE': (0.0 * _ureg.radian, '', 62),
        'RS': (0.0 * _ureg.centimeter, '', 63),
        'TS': (0.0 * _ureg.radian, '', 64),
    }

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        for i in range(self.N):
            if _cm(self.RE) == 0:
                self.RE = self.RM
            if _cm(self.RS) == 0:
                self.RS = self.RM

    def __str__(s):
        command = []
        c = f"""
            {super().__str__().rstrip()}
            {s.IL}
            {s.N} {s.AT.m_as('degree'):.12e} {s.RM.m_as('cm'):.12e} {s.TYP}
            """
        command.append(c)

        for i in range(0, s.N):
            c = f"""
                {s.ACN[i].m_as('degree'):.12e} {s.DRM[i].m_as('cm'):.12e} {s.BN[i].m_as('kilogauss'):.12e} {s.BI_0[i]:.12e} 0.0 0.0 \
    {s.BI_1[i].m_as('cm**-1'):.12e} {s.BI_2[i].m_as('cm**-2'):.12e} {s.BI_3[i].m_as('cm**-3'):.12e} {s.BI_4[i].m_as('cm**-4'):.12e} {s.BI_5[i].m_as('cm**-5'):.12e} \
    {s.BI_6[i].m_as('cm**-6'):.12e} {s.BI_7[i].m_as('cm**-7'):.12e} {s.BI_8[i].m_as('cm**-8'):.12e} {s.BI_9[i].m_as('cm**-9'):.12e} {s.BI_10[i].m_as('cm**-10'):.12e} \
    {s.BI_11[i].m_as('cm**-11'):.12e} {s.BI_12[i].m_as('cm**-12'):.12e} {s.BI_13[i].m_as('cm**-13'):.12e} {s.BI_14[i].m_as('cm**-14'):.12e} {s.BI_15[i].m_as('cm**-15'):.12e} \
    {s.BI_16[i].m_as('cm**-16'):.12e} {s.BI_17[i].m_as('cm**-17'):.12e} {s.BI_18[i].m_as('cm**-18'):.12e} {s.BI_19[i].m_as('cm**-19'):.12e} {s.BI_20[i].m_as('cm**-20'):.12e}
                {s.G0_E[i].m_as('cm'):.12e} {s.K_E[i]:.12e} {s.G10_E[i].m_as('cm'):.12e} {s.G11_E[i].m_as('cm**-3'):.12e}
                {s.NCE[i]} {s.C0_E[i]:.12e} {s.C1_E[i]:.12e} {s.C2_E[i]:.12e} {s.C3_E[i]:.12e} {s.C4_E[i]:.12e} {s.C5_E[i]:.12e} {s.C6_E[i]:.12e} 0.0 0.0
                {s.OMEGA_E[i].m_as('degree'):.12e} {s.XI0_E[i].m_as('degree'):.12e} {s.XI1_E[i].m_as('degree/cm'):.12e} {s.XI2_E[i].m_as('degree/cm**2'):.12e} {s.XI3_E[i].m_as('degree/cm**3'):.12e} \
    {s.AEN[i]:.12e} {s.BEN[i]:.12e} {s.CEN[i]:.12e}  
                {s.G0_S[i].m_as('cm'):.12e} {s.K_S[i]:.12e} {s.G10_S[i].m_as('cm'):.12e} {s.G11_S[i].m_as('cm**-3'):.12e}
                {s.NCS[i]} {s.C0_S[i]:.12e} {s.C1_S[i]:.12e} {s.C2_S[i]:.12e} {s.C3_S[i]:.12e} {s.C4_S[i]:.12e} {s.C5_S[i]:.12e} {s.C6_S[i]:.12e} 0.0 0.0
                {s.OMEGA_S[i].m_as('degree'):.12e} {s.XI0_S[i].m_as('degree'):.12e} {s.XI1_S[i].m_as('degree/cm'):.12e} {s.XI2_S[i].m_as('degree/cm**2'):.12e} {s.XI3_S[i].m_as('degree/cm**3'):.12e} \
    {s.AEX[i]:.12e} {s.BEX[i]:.12e} {s.CEX[i]:.12e}
                {s.G0_L[i].m_as('cm'):.12e} {s.K_L[i]:.12e}
                {s.NCL[i]} {s.C0_L[i]:.12e} {s.C1_L[i]:.12e} {s.C2_L[i]:.12e} {s.C3_L[i]:.12e} {s.C4_L[i]:.12e} {s.C5_L[i]:.12e} {s.SHIFT_L[i].m_as('cm'):.12e}
                {s.OMEGA_L[i].m_as('degrees'):.12e} {s.XI_L[i].m_as('degrees'):.12e} {0.0} {0.0} {0.0} {0.0}
                """
            command.append(c)

        command.append(f"""
        {s.KIRD} {s.RESOL:.12e}
        {s.XPAS.m_as('cm'):.12e}
        """)

        c = f"""
        2
        {s.RE.m_as('cm'):.12e} {s.TE.m_as('radian'):.12e} {s.RS.m_as('cm'):.12e} {s.TS.m_as('radian'):.12e}
        """
        command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Bend(CartesianMagnet):
    r"""Bending magnet, Cartesian frame.

    .. note:: This is mostly a **sector bend** element defined in cartesian coordinates.

    .. rubric:: Zgoubi manual description

    ``BEND`` is one of several keywords available for the simulation of dipole magnets. It presents the interest of
    easy handling, and is well adapted for the simulation of synchrotron dipoles and such other regular dipoles as
    sector magnets with wedge angles.

    The field in ``BEND`` is defined in a Cartesian coordinate frame (unlike for instance ``DIPOLE``[S] that uses a
    polar frame). As a consequence, having particle coordinates at entrance or exit of the magnet referring to the
    curved main direction of motion may require using KPOS, in particular KPOS=3 (in a circular accelerator cell for
    instance, see section 7.9, p. 201).

    The dipole simulation accounts for the magnet geometrical length XL, for a possible skew angle (X-rotation, useful
    for obtaining vertical deviation magnet), and for the field B1 such that in absence of fringe field the  deviation
    θ satisfies :math:`XL = 2 \frac{BORO}{B1} sin(θ/2).

    Then follows the description of the entrance and exit EFBs and fringe fields. The wedge angles :math:`W_E`(entrance)
    and :math:`W_S` (exit) are defined with respect to the sector angle, with the signs as described in Fig. 12.
    Within a distance :math:`± X_E` :math:`(±X_S)` on both sides of the entrance (exit) EFB, the fringe field model is
    used (same as for ``QUADRUPO``, Fig. 35, p. 129) ; elsewhere, the field is supposed to be uniform.

    If :math:`λ_E` (resp. :math:`λ_S) is zero sharp edge field model is assumed at entrance (resp. exit) of the magnet
    and :math:`X_E` (resp. :math:`X_S`) is forced to zero. In this case, the wedge angle vertical first order focusing
    effect (if \vec{B1} is non zero) is simulated at magnet entrance and exit by a kick
    :math:`P_2 = P_1 − Z_1 tan(ε/ρ)` applied to each particle (:math:`P_1`, :math:`P_2` are the vertical angles
    upstream and downstream the EFB, :math:`Z1` the vertical particle position at the EFB, ρ the local horizontal
    bending radius and ε the wedge angle experienced by the particle ; ε depends on the horizontal angle T).

    Magnet (mis-)alignment is assured by KPOS. KPOS also allows some degrees of automatic alignment useful for periodic
    structures (section 7.9).

    *From matrice-style code modeling, to zgoubi :*
     Fig. 13 illustrates the conversion of matrix method style of data where the magnet is defined by its length and
     deviation angle (see MAD input below, using ’SBEND’), to zgoubi input data using ``BEND`` (in this particular case
     of an illustration of a rectangular magnet, ``MULTIPOL`` could be used, as well).

    *Negative bend, vertical bend, tricks :*
    Use ``YMY`` for the former, ``TRAROT`` with a ±π X-rotation for the latter. The two can be combined, so that a
    vertical negative bend can be represented by the sequence TRAROT[π], YMY, BEND[B>0], YMY, TRAROT[−π], with
    positionning methods for ``BEND`` as dis- cussed above (Fig. 13) still applying.
    """
    KEYWORD = 'BEND'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, "Print field and coordinates along trajectories", 1),
        'XL': (0.0 * _ureg.centimeter, "Magnet length (straight reference frame)", 10),
        'SK': (0.0 * _ureg.radian, "Skew angle", 11),
        'B1': (0.0 * _ureg.kilogauss, "Dipole field", 12),
        'X_E': (0.0 * _ureg.centimeter, "Integration zone extension (entrance face)"),
        'LAM_E': (0.0 * _ureg.centimeter, "Fringe field extension (entrance face)"),
        'W_E': (0.0 * _ureg.radian, "Wedge angle (entrance face)"),
        'C0_E': (0.0, 'Entrance fringe field coefficient C0'),
        'C1_E': (1.0, 'Entrance fringe field coefficient C1'),
        'C2_E': (0.0, 'Entrance fringe field coefficient C2'),
        'C3_E': (0.0, 'Entrance fringe field coefficient C3'),
        'C4_E': (0.0, 'Entrance fringe field coefficient C4'),
        'C5_E': (0.0, 'Entrance fringe field coefficient C5'),
        'X_S': (0.0 * _ureg.centimeter, "Integration zone extension (exit face)"),
        'LAM_S': (0.0 * _ureg.centimeter, "Fringe field extension (exit face)"),
        'W_S': (0.0 * _ureg.radian, "Wedge angle (exit face)"),
        'C0_S': (0.0, 'Exit fringe field coefficient C0'),
        'C1_S': (1.0, 'Exit fringe field coefficient C1'),
        'C2_S': (0.0, 'Exit fringe field coefficient C2'),
        'C3_S': (0.0, 'Exit fringe field coefficient C3'),
        'C4_S': (0.0, 'Exit fringe field coefficient C4'),
        'C5_S': (0.0, 'Exit fringe field coefficient C5'),
        'XPAS': (1.0 * _ureg.centimeter, "Integration step"),
        'KPOS': (2, "Alignment parameter"),
        'XCE': (0.0 * _ureg.centimeter, 'X shift'),
        'YCE': (0.0 * _ureg.centimeter, 'Y shift'),
        'ALE': (0.0 * _ureg.radian, 'Tilt'),
        'COLOR': '#4169E1',
        'LENGTH_IS_ARC_LENGTH': True,
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
        commands (e.g. fit)."""

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        if self.LAM_S.magnitude == 0:
            self.X_S = 0.0 * _ureg.cm
        if self.LAM_E.magnitude == 0:
            self.X_E = 0.0 * _ureg.cm

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {int(s.IL):d}
        {s.XL.to('cm').magnitude:.12e} {s.SK.to('radian').magnitude:.12e} {_kilogauss(s.B1):.12e}
        {s.X_E.to('cm').magnitude:.12e} {s.LAM_E.to('cm').magnitude:.12e} {s.W_E.to('radian').magnitude:.12e}
        6 {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
        {s.X_S.to('cm').magnitude:.12e} {s.LAM_S.to('cm').magnitude:.12e} {s.W_S.to('radian').magnitude:.12e}
        6 {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
        {_cm(s.XPAS):.12e}
        {int(s.KPOS):d} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {_radian(s.ALE):.12e}
        """


class Decapole(CartesianMagnet):
    r"""Decapole magnet.

    .. rubric:: Zgoubi manual description

    The meaning of parameters for ``DECAPOLE`` is the same as for ``QUADRUPO``.
    In fringe field regions the magnetic field :math:`\vec{B}(X, Y, Z)` and its derivatives up to fourth order are
    derived from the scalar potential expressed to the 5th order in Y and Z

    .. math::

        V (X, Y,Z) = G(X) (Y^4Z - 2Y^2Z^3 + \frac{Z^5}{5})

    with :math:`G0=\frac{B_0}{R_0^4}`
    The modelling of the fringe field form factor G(X) is described under ``QUADRUPO``, p. 128.
    Outside fringe field regions, or everywhere in sharp edge decapole (:math:`λ_E = λ_S = 0`) , :math:`\vec{B}(X, Y, Z)` in the
    magnet is given by

    .. math::

        \begin{align}
            B_X &= 0 \\
            B_Y &= 4G_0(Y^2 − Z^2)YZ \\
            B_Z &= G_0(Y^4 − 6Y^2Z^2 + Z^4)
        \end{align}
    """
    KEYWORD = 'DECAPOLE'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (2, "Print field and coordinates along trajectories", 1),
        'XL': (10.0 * _ureg.centimeter, "Magnet length (straight reference frame)", 10),
        'R0': (10.0 * _ureg.centimeter, 'Radius of the pole tips', 11),
        'B0': (0 * _ureg.kilogauss, 'Field at pole tips', 12),
        'X_E': (0 * _ureg.centimeter, 'Entrance face integration zone for the fringe field', 20),
        'LAM_E': (0 * _ureg.centimeter, 'Entrance face fringe field extent', 21),
        'NCE': (0, 'UNUSED', 30),
        'C0_E': (0, 'Fringe field coefficient C0', 31),
        'C1_E': (1, 'Fringe field coefficient C1', 32),
        'C2_E': (0, 'Fringe field coefficient C2', 33),
        'C3_E': (0, 'Fringe field coefficient C3', 34),
        'C4_E': (0, 'Fringe field coefficient C4', 35),
        'C5_E': (0, 'Fringe field coefficient C5', 36),
        'X_S': (0 * _ureg.centimeter, 'Exit face integration zone for the fringe field', 40),
        'LAM_S': (0 * _ureg.centimeter, 'Exit face fringe field extent', 41),
        'NCS': (0, 'UNUSED', 50),
        'C0_S': (0, 'Fringe field coefficient C0', 51),
        'C1_S': (1, 'Fringe field coefficient C1', 52),
        'C2_S': (0, 'Fringe field coefficient C2', 53),
        'C3_S': (0, 'Fringe field coefficient C3', 54),
        'C4_S': (0, 'Fringe field coefficient C4', 55),
        'C5_S': (0, 'Fringe field coefficient C5', 56),
        'XPAS': (0.1 * _ureg.centimeter, 'Integration step', 60),
        'KPOS': (1, 'Misalignment type', 70),
        'XCE': (0 * _ureg.centimeter, 'x offset', 71),
        'YCE': (0 * _ureg.centimeter, 'y offset', 72),
        'ALE': (0 * _ureg.radian, 'misalignment rotation', 73),
        'COLOR': ('#FF0000', 'Magnet color for plotting.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
        commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {int(self.IL):d}
        {_cm(self.XL):.12e} {_cm(self.R0):.12e} {_kilogauss(self.B0):.12e}
        {_cm(self.XE):.12e} {_cm(self.LAM_E):.12e}
        6 {self.C0_E:.12e} {self.C1_E:.12e} {self.C2_E:.12e} {self.C3_E:.12e} {self.C4_E:.12e} {self.C5_E:.12e}
        {_cm(self.XS):.12e} {_cm(self.LAM_S):.12e}
        6 {self.C0_S:.12e} {self.C1_S:.12e} {self.C2_S:.12e} {self.C3_S:.12e} {self.C4_S:.12e} {self.C5_S:.12e}
        {_cm(self.XPAS)}
        {int(self.KPOS):d} {_cm(self.XCE):.12e} {_cm(self.YCE):.12e} {_radian(self.ALE):.12e}
        """


class Dipole(PolarMagnet):
    r"""Dipole magnet, polar frame.

    .. rubric:: Zgoubi manual description

    ``DIPOLE`` provides a model of a dipole field, possibly with transverse field indices. The field along a particle
    trajectory is computed as the particle motion proceeds, straightforwardly from the dipole geometrical boundaries.
    Field simulation in ``DIPOLE`` is the same as used in ``DIPOLE-M`` and ``AIMANT`` for computing a field map;
    the essential difference in ``DIPOLE`` is in its skipping that intermediate stage of field map generation found in
    ``DIPOLE-M`` and ``AIMANT``.

    ``DIPOLE`` has a version, ``DIPOLES``, that allows overlapping of fringe fields in a configuration of neighboring
    magnets.

    The dimensioning of the magnet is defined by (Fig. 11, p. 82):

        - AT : total angular aperture
        - RM : mean radius used for the positioning of field boundaries

    The 2 or 3 effective field boundaries (EFB), from which the dipole field is drawn, are defined from geometric
    boundaries, the shape and position of which are determined by the following parameters:

        - ACENT: arbitrary inner angle, used for EFB’s positioning;
        - ω: azimuth of an EFB with respect to ACENT;
        - θ: angle of an EFB with respect to its azimuth (wedge angle) : radius of curvature of an EFB;
        - R1, R2 U1, U2: extent of the linear part of an EFB.

    The magnetic field is calculated in polar coordinates. At any position (R, θ) along the particle trajectory the
    value of the vertical component of the mid-plane field is calculated using

    .. math::

    B_Z(R,θ) = F(R,θ)* B_0 * (1 + N * \frac{R-RM}{RM} + B * (\frac{R-RM}{RM})**2 + G * (\frac{R-RM}{RM})**3 )

    where N, B and G are respectively the first, second and third order field indices and F(R,θ) is the fringe field
    coefficient (it determines the “flutter” in periodic structures).

    Calculation of the Fringe Field Coefficient

    With each EFB a realistic extent of the fringe field, λ (normally equal to the gap size), is associated and a
    fringe field coefficient F is calculated. In the following λ stands for either :math:`λ_E` (Entrance), :math:`λ_S`
    (Exit) or :math:`λ_L` (Lateral EFB).

    F is an exponential type fringe field (Fig. 12, p. 84) given by [34]

    .. math::

    F = \frac{1}{1+exp P(s)}

    wherein s is the distance to the EFB and depends on (R, θ), and

    .. math::

    P(s) = C_0+C_1􏰓(\frac{s}{λ})+ C_2􏰓(\frac{s}{λ})**2+ C_3􏰓(\frac{s}{λ})**3+ C_4􏰓(\frac{s}{λ})**4+ C_5(\frac{s}{λ})**5

    It is also possible to simulate a shift of the EFB, by giving a non zero value to the parameter shift.
    s is then changed to s−shift in the previous equation. This allows small variations of the magnetic length.

    Let :math:`F_E` (respectively :math:`F_S` , :math:`F_L`) be the fringe field coefficient attached to the entrance
    (respectively exit, lateral) EFB. At any position on a trajectory the resulting value of the fringe field
    coefficient (eq. 4.4.8) is

    .. math::

    F(R,θ) = F_E * F_S * F_L

    In particular, :math:`F_L ≡ 1` if no lateral EFB is requested.

    Calculation of the Mid-plane Field and Derivatives

    :math:`B_Z (R, θ)` in Eq. 4.4.8 is computed at the n × n nodes (n = 3 or 5 in practice) of a “flying” interpolation
    grid in the median plane centered on the projection :math:`m_0` of the actual particle position :math:`M_0` as
    schemed in Fig. 20. A polynomial interpolation is involved, of the form

    .. math::

    B_Z (R,θ) = A_{00} + A_{10}θ + A_{01}R + A_{20}θ**2 + A_{11}θR + A_{02}R**2

    that yields the requested derivatives, using

    .. math::

    A_{kl} = \frac{1}{k!l!} \frac{∂**{k+l}B_Z}{∂θ**k ∂r**l}

    Note that, the source code contains the explicit analytical expressions of the coefficients :math:`A_{kl}`
    solutions of the normal equations, so that the operation is not CPU time consuming.

    Extrapolation Off Median Plane

    From the vertical field \vec{B} and derivatives in the median plane, first a transformation from polar to Cartesian
    coordinates is performed, following eqs (1.4.9 or 1.4.10), then, extrapolation off median plane is performed by
    means of Taylor expansions, following the procedure described in section 1.3.3.

    .. rubric:: Zgoubidoo usage and example

    >>> m = Dipole()
    >>> m.fit()
    """
    KEYWORD = 'DIPOLE'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, 'Print field and coordinates along trajectories', 1),
        'AT': (0 * _ureg.degree, 'Total angular extent of the dipole (positive value in all cases)', 2),
        'RM': (0 * _ureg.centimeter, 'Reference radius', 3),
        'ACENT': (0 * _ureg.degree, 'Azimuth for positioning of EFBs', 4),
        'B0': (0 * _ureg.kilogauss, 'Reference field', 5),
        'N': (0, 'Field index (radial quadrupolar)', 6),
        'B': (0, 'Field index (radial sextupolar)', 7),
        'G': (0, 'Field index (radial octupolar)', 8),
        'LAM_E': (0 * _ureg.centimeter, 'Entrance fringe field extent (normally ≃ gap size)', 9),
        # XI_E: (0, 'UNUSED', 10)
        # NCE: (0, 'UNUSED', 11)
        'C0_E': (0, 'Fringe field coefficient C0', 12),
        'C1_E': (1, 'Fringe field coefficient C1', 13),
        'C2_E': (0, 'Fringe field coefficient C2', 14),
        'C3_E': (0, 'Fringe field coefficient C3', 15),
        'C4_E': (0, 'Fringe field coefficient C4', 16),
        'C5_E': (0, 'Fringe field coefficient C5', 17),
        'SHIFT_E': (0 * _ureg.centimeter, 'Shift of the EFB', 18),
        'OMEGA_E': (0 * _ureg.degree, 'Azimuth of entrance EFB with respect to ACENT', 19),
        'THETA_E': (0 * _ureg.degree, 'Entrance wedge angle of EFB', 20),
        'R1_E': (1e9 * _ureg.centimeter, 'Entrance EFB radius', 21),
        'U1_E': (-1e9 * _ureg.centimeter, 'Entrance EFB linear extent', 22),
        'U2_E': (1e9 * _ureg.centimeter, 'Entrance EFB linear extent', 23),
        'R2_E': (1e9 * _ureg.centimeter, 'Entrance EFB radius', 24),
        'LAM_S': (0 * _ureg.centimeter, 'Exit fringe field extent (normally ≃ gap size)', 25),
        # XI_S: (0, 'UNUSED', )
        # NCS: (0, 'UNUSED', ) #Check fit number
        'C0_S': (0, 'Fringe field coefficient C0', 26),
        'C1_S': (1, 'Fringe field coefficient C1', 27),
        'C2_S': (0, 'Fringe field coefficient C2', 28),
        'C3_S': (0, 'Fringe field coefficient C3', 29),
        'C4_S': (0, 'Fringe field coefficient C4', 30),
        'C5_S': (0, 'Fringe field coefficient C5', 31),
        'SHIFT_S': (0 * _ureg.centimeter, 'Shift of the EFB', 32),
        'OMEGA_S': (0 * _ureg.degree, 'Azimuth of exit EFB with respect to ACENT', 33),
        'THETA_S': (0 * _ureg.degree, 'Exit wedge angle of EFB', 34),
        'R1_S': (1e9 * _ureg.centimeter, 'Exit EFB radius', 35),
        'U1_S': (-1e9 * _ureg.centimeter, 'Exit EFB linear extent', 36),
        'U2_S': (1e9 * _ureg.centimeter, 'Exit EFB linear extent', 37),
        'R2_S': (1e9 * _ureg.centimeter, 'Exit EFB radius', 38),
        'LAM_L': (0.0 * _ureg.centimeter, 'Lateral fringe field extent (normally ≃ gap size)', 39),
        'XI_L': (0, 'Flag to activate/deactivate the lateral EFB (0 to deactivate)', 40),
        'C0_L': (0, 'Fringe field coefficient C0', 41),
        'C1_L': (1, 'Fringe field coefficient C1', 42),
        'C2_L': (0, 'Fringe field coefficient C2', 43),
        'C3_L': (0, 'Fringe field coefficient C3', 44),
        'C4_L': (0, 'Fringe field coefficient C4', 45),
        'C5_L': (0, 'Fringe field coefficient C5', 46),
        'SHIFT_L': (0 * _ureg.centimeter, 'Shift of the EFB', 47),
        'OMEGA_L': (0 * _ureg.degree, '', 48),
        'THETA_L': (0 * _ureg.degree, 'Lateral field boundary wedge angle', 49),
        'R1_L': (1e9 * _ureg.centimeter, 'Lateral EFB radius', 50),
        'U1_L': (1e9 * _ureg.centimeter, 'Lateral EFB linear extent', 51),
        'U2_L': (1e9 * _ureg.centimeter, 'Lateral EFB linear extent', 52),
        'R2_L': (1e9 * _ureg.centimeter, 'Lateral EFB radius', 53),
        'RM3': (1e9 * _ureg.centimeter, 'Reference radius of the lateral EFB', 54),
        'IORDRE': (2, '', 55),
        'RESOL': (10, '', 56),
        'XPAS': (1 * _ureg.millimeter, 'Integration step', 57),
        'KPOS': (2, 'Positionning of the map, normally 2', 58),
        'RE': (0 * _ureg.centimeter, 'Entrance reference radius', 64),
        'TE': (0 * _ureg.radian, 'Entrance reference angle', 65),
        'RS': (0 * _ureg.centimeter, 'Exit reference radius', 66),
        'TS': (0 * _ureg.radian, 'Exit reference angle', 67),
        'DP': (0.0, 'Reference relative momentum', 63),
        'COLOR': '#4169E1',
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        if _degree(self.OMEGA_E) == 0:
            self.OMEGA_E = self.AT / 2
        if _degree(self.OMEGA_S) == 0:
            self.OMEGA_S -= self.AT / 2
        if _degree(self.ACENT) == 0:
            self.ACENT = self.AT / 2
        if _cm(self.RE) == 0:
            self.RE = self.RM
        if _cm(self.RS) == 0:
            self.RS = self.RM

    def __str__(s):
        command = []
        c = f"""
        {super().__str__().rstrip()}
        {s.IL}
        {_degree(s.AT):.20e} {_cm(s.RM):.12e}
        {_degree(s.ACENT):.20e} {_kilogauss(s.B0):.12e} {s.N:.12e} {s.B:.12e} {s.G:.12e}
        {_cm(s.LAM_E):.12e} -1.0
        6 {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e} {_cm(s.SHIFT_E):.12e}
        {_degree(s.OMEGA_E):.20e} {_degree(s.THETA_E):.12e} {_cm(s.R1_E):.12e} {_cm(s.U1_E):.12e} {_cm(s.U2_E):.12e} {_cm(s.R2_E):.12e}
        {_cm(s.LAM_S):.12e} -1.0
        6 {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e} {_cm(s.SHIFT_S):.12e}
        {_degree(s.OMEGA_S):.20e} {_degree(s.THETA_S):.12e} {_cm(s.R1_S):.12e} {_cm(s.U1_S):.12e} {_cm(s.U2_S):.12e} {_cm(s.R2_S):.12e}
        {_cm(s.LAM_L):.12e} {s.XI_L}
        6 {s.C0_L:.12e} {s.C1_L:.12e} {s.C2_L:.12e} {s.C3_L:.12e} {s.C4_L:.12e} {s.C5_L:.12e} {_cm(s.SHIFT_L):.12e}
        {_degree(s.OMEGA_L):.12e} {_degree(s.THETA_L):.12e} {_cm(s.R1_L):.12e} {_cm(s.U1_L):.12e} {_cm(s.U2_L):.12e} {_cm(s.R2_L):.12e} {_cm(s.RM3):.12e}
        {s.IORDRE} {s.RESOL:.12e}
        {_cm(s.XPAS)}"""
        command.append(c)

        if s.KPOS not in (1, 2):
            raise _ZgoubidooException("KPOS must be equal to 1 or 2.")

        if s.KPOS == 2:
            if s.RE == 0:
                s.RE = s.RM
            if s.RS == 0:
                s.RS = s.RM
            c = f"""
        {s.KPOS}
        {_cm(s.RE):.12e} {_radian(s.TE):.12e} {_cm(s.RS):.12e} {_radian(s.TS):.12e}
                """
            command.append(c)
        elif s.KPOS == 1:
            c = f"""
        {s.KPOS}
        {s.DP:.12e} 0.0 0.0 0.0
                """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))

    def fit(self,
            kinematics: _Kinematics,
            particle: _ParticuleType = _Proton,
            entry_coordinates: _np.array = None,
            exit_coordinate: float = 0.0,
            method: _FitType = _Fit2,
            zgoubi: Optional[_Zgoubi] = None,
            debug=False):
        """

        Args:
            kinematics: the reference energy of the magnet
            particle: the particule type
            entry_coordinates: references 6D coordinates at the magnet entry
            exit_coordinate: the coordinate at the magnet exit
            method: the Zgoubi fitting command
            zgoubi: the `Zgoubi` instance used to launch the runs
            debug: verbose parent

        Returns:
            the `Dipole` itself (allows method chaining).
        """
        if entry_coordinates is None:
            entry_coordinates = _np.array([[0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]])

        z = zgoubi or _Zgoubi()
        zi = zgoubidoo.Input(f"FIT_{self.LABEL1}_MAGNET")
        zi += _Objet2('BUNCH', BORO=kinematics.brho).add(entry_coordinates)
        zi += particle()
        zi += _Marker('START')
        zi += self
        zi += _Marker('END')
        fit = method(PENALTY=1e-12,
                     PARAMS=[
                         _Fit.Parameter(line=zi, place=self.LABEL1, parameter=Dipole.B0_),
                     ],
                     CONSTRAINTS=[
                         _Fit.EqualityConstraint(
                             line=zi,
                             place='END',
                             variable=_Fit.FitCoordinates.Y,
                             value=exit_coordinate
                         ),
                     ]
                     ).generate_label('FIT_')
        zi += fit

        def cb(f):
            """Post execution callback."""
            r = f.result()
            if not fit.results[0][1].success:
                raise _ZgoubidooException(f"Unable to fit {self.__class__.__name__}.")
            if debug:
                print('\n'.join(r['result']))
            self.B0 = fit.results[0][1].results.at[1, 'final']
            self._fit = fit

        z(zi, identifier={'FITTING': self.LABEL1}, cb=cb)
        return self


class DipoleM(PolarMagnet):
    """TODO.

    .. rubric:: Zgoubi manual description

    """
    KEYWORD = 'DIPOLE-M'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'NFACE': 2,
        'IC': 0,  # 1, 2: print field map
        'IL': 0,  # 1, 2: print field and coordinates on trajectores
        'IAMAX': 0,
        'IRMAX': 0,
        'B0': 0 * _ureg.kilogauss,
        'N': 0,
        'B': 0,
        'G': 0,
        'AT': 0,
        'ACENT': 0,
        'RM': 0,
        'RMIN': 0,
        'RMAX': 0,
        'LAM_E': 0,
        'XI_E': 0,
        'NCE': 0,
        'C0_E': 0,
        'C1_E': 0,
        'C2_E': 0,
        'C3_E': 0,
        'C4_E': 0,
        'C5_E': 0,
        'SHIFT_E': 0,
        'OMEGA_E': 0,
        'THETA_E': 0,
        'R1_E': 1e9,
        'U1_E': -1e9,
        'U2_E': 1e9,
        'R2_E': 1e9,
        'LAM_S': 0,
        'XI_S': 0,
        'NCS': 0,
        'C0_S': 0,
        'C1_S': 0,
        'C2_S': 0,
        'C3_S': 0,
        'C4_S': 0,
        'C5_S': 0,
        'SHIFT_S': 0,
        'OMEGA_S': 0,
        'THETA_S': 0,
        'R1_S': 1e9,
        'U1_S': -1e9,
        'U2_S': 1e9,
        'R2_S': 1e9,
        'LAM_L': 0,
        'XI_L': 0,
        'NCL': 0,
        'C0_L': 0,
        'C1_L': 0,
        'C2_L': 0,
        'C3_L': 0,
        'C4_L': 0,
        'C5_L': 0,
        'SHIFT_L': 0,
        'OMEGA_L': 0,
        'THETA_L': 0,
        'R1_L': 1e9,
        'U1_L': -1e9,
        'U2_L': 1e9,
        'R2_L': 1e9,
        'RM3': 0,
        'NBS': 0,
        'R0': 0,
        'DELTAB': 0,
        'THETA_0': 0,
        'IORDRE': 4,
        'XPAS': 0.1,
        'KPOS': 2,
        'RE': 0,
        'TE': 0,
        'RS': 0,
        'TS': 0,
        'DP': 0,
        'SHIM_R1': [],
        'SHIM_R2': [],
        'SHIM_THETA1': [],
        'SHIM_THETA2': [],
        'SHIM_LAMBDA': [],
        'SHIM_GAMMA': [],
        'SHIM_ALPHA': [],
        'SHIM_BETA': [],
        'SHIM_MU': [],
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(s):
        command = []
        if s.NFACE not in (2, 3):
            raise _ZgoubidooException(f"Error : Zgoubido does not support NFACE = {s.NFACE}")

        c = f"""
            {super().__str__().rstrip()}
            {s.NFACE} {s.IC} {s.IL}
            {s.IAMAX} {s.IRMAX}
            {s.B0.to('kilogauss').magnitude:.12e} {s.N:.12e} {s.B:.12e} {s.G:.12e}
            {s.AT:.12e} {s.ACENT:.12e} {s.RM:.12e} {s.RMIN:.12e} {s.RMAX:.12e}
            {s.LAM_E:.12e} {s.XI_E:.12e}
            {s.NCE} {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e} {s.SHIFT_E:.12e}
            {s.OMEGA_E:.12e} {s.THETA_E:.12e} {s.R1_E:.12e} {s.U1_E:.12e} {s.U2_E:.12e} {s.R2_E:.12e}
            {s.LAM_S:.12e} {s.XI_S:.12e}
            {s.NCS} {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e} {s.SHIFT_S:.12e}
            {s.OMEGA_S:.12e} {s.THETA_S:.12e} {s.R1_S:.12e} {s.U1_S:.12e} {s.U2_S:.12e} {s.R2_S:.12e}
        """
        command.append(c)

        if s.NFACE == 3:
            c = f"""
                {s.LAM_L:.12e} {s.XI_L:.12e}
                {s.NCL} {s.C0_L:.12e} {s.C1_L:.12e} {s.C2_L:.12e} {s.C3_L:.12e} {s.C4_L:.12e} {s.C5_L:.12e} {s.SHIFT_L:.12e}
                {s.OMEGA_L:.12e} {s.THETA_L:.12e} {s.R1_L:.12e} {s.U1_L:.12e} {s.U2_L:.12e} {s.R2_L:.12e} {s.RM3:.12e}
            """
            command.append(c)

        if s.NBS == 0:
            command.append(f"""
            {s.NBS}
            """)
        elif s.NBS == -2:
            c = f"""
                {s.NBS}
                {s.R0:.12e} {s.DELTAB:.12e}
                """
            command.append(c)
        elif s.NBS == -1:
            c = f"""
                {s.NBS}
                {s.THETA_0:.12e} {s.DELTAB:.12e}
                """
            command.append(c)
        elif s.NBS >= 1:
            command.append(f"""
            {s.NBS}""")

            shim_r1 = len(s.SHIM_R1)
            shim_r2 = len(s.SHIM_R2)
            shim_theta1 = len(s.SHIM_THETA1)
            shim_theta2 = len(s.SHIM_THETA2)
            shim_lambda = len(s.SHIM_LAMBDA)
            shim_gamma = len(s.SHIM_GAMMA)
            shim_alpha = len(s.SHIM_ALPHA)
            shim_beta = len(s.SHIM_BETA)
            shim_mu = len(s.SHIM_MU)
            if shim_r1\
                    == shim_r2 \
                    == shim_theta1 \
                    == shim_theta2 \
                    == shim_lambda \
                    == shim_gamma \
                    == shim_alpha \
                    == shim_beta \
                    == shim_mu:
                for i, j, k, l in zip(s.SHIM_R1, s.SHIM_R2, s.SHIM_THETA1, s.SHIM_LAMBDA):
                    command.append(f"""
                    {i:.12e} {j:.12e} {k:.12e} {l:.12e}
                    """)

                for i, j, k, l in zip(s.GAMMA, s.ALPHA, s.MU, s.BETA):
                    command.append(f"""
                                   {i:.12e} {j:.12e} {k:.12e} {l:.12e}
                                   """)
            else:
                raise _ZgoubidooException('Error : The shim parameters lists must have the same lenghts')

        c = f"""
            {s.IORDRE}
            {s.XPAS:.12e}
            """
        command.append(c)

        if s.KPOS not in (1, 2):
            raise _ZgoubidooException("KPOS must be equal to 1 or 2.")

        if s.KPOS == 2:
            if s.RE == 0:
                s.RE = s.RM
            if s.RS == 0:
                s.RS = s.RM
            c = f"""
                {s.KPOS}
                {s.RE:.12e} {s.TE:.12e} {s.RS:.12e} {s.TS:.12e}
                """
            command.append(c)
        elif s.KPOS == 1:
            c = f"""
                {s.KPOS}
                {s.DP:.12e}
                """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Dipoles(PolarMultiMagnet):
    """Dipole magnet N-tuple, polar frame.

    .. rubric:: Zgoubi manual description

    TODO
    """
    KEYWORD = 'DIPOLES'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, 'Print field and coordinates along trajectories', 1),
        'N': (1, 'Number of magnets (maximum 5).', 2),
        'AT': (0.0 * _ureg.degree, 'Total angular extent of the N dipoles.', 3),
        'RM': (0.0 * _ureg.cm, 'Reference radius: mean radius used for the positioning of field boundaries', 4),
        'ACN': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Azimuth for dipole positioning', 5),
        'DRM': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter,
                'Offset for the reference radius of each magnet : RM_i  = RM +DELTA_RM', 6),
        'B0': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.kilogauss, 'Dipole fields of each magnets.', 7),
        'BI': ([[], [], [], [], []], 'Lists of field coefficients for each magnets.', 8),
        # à partir d'ici, on doit faire +ind pour tous les numéros de fit
        'G0_E': (
        [0.00000001, 0.0, 0.0, 0.0, 0.0] * _ureg.cm, 'Reference gaps for the entrance fringe fields of each magnets.',
        9),
        'K_E': ([0, 0, 0, 0, 0], 'Fringe field parameter kappa', 10),  # 11 c'est pour le NC
        'C0_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C0', 12),
        'C1_E': ([1, 1, 1, 1, 1], 'Fringe field coefficient C1', 13),
        'C2_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C2', 14),
        'C3_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C3', 15),
        'C4_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C4', 16),
        'C5_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C5', 17),
        'SHIFT_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'Shift of the EFB', 18),
        'OMEGA_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, '', 19),
        'THETA_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Entrance face wedge angle', 20),
        'R1_E': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'Entrance EFB radius', 21),
        'U1_E': ([-1e9, -1e9, -1e9, 1e9, 1e9] * _ureg.centimeter, 'Entrance EFB linear extent', 22),  ####-1e9 ?
        'U2_E': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'Entrance EFB linear extent', 23),
        'R2_E': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'Entrance EFB radius', 24),
        'G0_S': (
        [0.00000001, 0.0, 0.0, 0.0, 0.0] * _ureg.cm, 'Reference gaps for the exit fringe fields of each magnet.', 25),
        'K_S': ([0, 0, 0, 0, 0], 'Fringe field parameter kappa', 26),
        'C0_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C0', 28),  # 27 pour le NC
        'C1_S': ([1, 1, 1, 1, 1], 'Fringe field coefficient C1', 29),
        'C2_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C2', 30),
        'C3_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C3', 31),
        'C4_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C4', 32),
        'C5_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C5', 33),
        'SHIFT_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'Shift of the EFB', 34),
        'OMEGA_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, '', 35),
        'THETA_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Entrance face wedge angle', 36),
        'R1_S': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'Exit EFB radius', 37),
        'U1_S': ([-1e9, -1e9, -1e9, 1e9, 1e9] * _ureg.centimeter, 'Exit EFB linear extent', 38),  ####-1e9 ?
        'U2_S': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'Exit EFB linear extent', 39),
        'R2_S': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'Exit EFB radius', 40),
        'G0_L': (
        [0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm, 'UNUSED Reference gaps for the lateral fringe fields of each dipole.',
        41),
        'K_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field parameter kappa', 42),  ####POUR FIT : ne pas oublier NC unused
        'C0_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C0', 44),
        'C1_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C1', 45),
        'C2_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C2', 46),
        'C3_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C3', 47),
        'C4_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C4', 48),
        'C5_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C5', 49),
        'SHIFT_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'UNUSED  Shift of the EFB', 50),
        'OMEGA_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'UNUSED ', 51),
        'THETA_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'UNUSED Entrance face wedge angle', 52),
        'R1_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'UNUSED Lateral EFB radius', 53),
        'U1_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'UNUSED Lateral EFB linear extent', 54),
        'U2_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'UNUSED Lateral EFB linear extent', 55),
        'R2_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'UNUSED Lateral EFB radius', 56),
        'RM3': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'Unused.', 57),
        'KIRD': (
        2, 'Analytical computation (KIRD = 0) or numerical interpolation (KIRD = 2,4, 25) of field derivatives', 58),
        # 111 (pour chaque dipole supplémentaire, faire +53 pour le fit)
        'RESOL': (2, '', 59),
        'XPAS': (1.0 * _ureg.millimeter, 'Integration step', 60),
        'KPOS': (2, '', 61),
        'RE': (0.0 * _ureg.centimeter, '', 62),
        'TE': (0.0 * _ureg.radian, '', 63),
        'RS': (0.0 * _ureg.centimeter, '', 64),
        'TS': (0.0 * _ureg.radian, '', 65),
        'DP': (0.0, '', 62),
        'COLOR': '#4169E1',
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        for i in range(self.N):
            if _degree(self.OMEGA_E[i]) == 0:
                self.OMEGA_E[i] = self.AT / (2 * self.N) + i * self.AT / self.N
            if _degree(self.OMEGA_S[i]) == 0:
                self.OMEGA_S[i] -= (self.AT - self.AT / (2 * self.N) - i * self.AT / self.N)
            if _degree(self.ACN[i]) == 0:
                self.ACN[i] = self.AT / (2 * self.N) + i * self.AT / self.N
            if _cm(self.RE) == 0:
                self.RE = self.RM
            if _cm(self.RS) == 0:
                self.RS = self.RM

    def __str__(s):
        command = list()
        command.append(f"""
            {super().__str__().rstrip()}
            {s.IL}
            {s.N} {_degree(s.AT):.20e} {_cm(s.RM):.12e}
            """)

        for i in range(0, s.N):
            command.append(f"""
            {_degree(s.ACN[i]):.20e} {_cm(s.DRM[i]):.12e} {_kilogauss(s.B0[i]):.12e} {len(s.BI[i])} {' '.join(map(str, s.BI[i]))}
            {_cm(s.G0_E[i]):.12e} {s.K_E[i]:.12e}
            4 {s.C0_E[i]:.12e} {s.C1_E[i]:.12e} {s.C2_E[i]:.12e} {s.C3_E[i]:.12e} {s.C4_E[i]:.12e} {s.C5_E[i]:.12e} {_cm(s.SHIFT_E[i]):.12e}
            {_degree(s.OMEGA_E[i]):.20e} {_degree(s.THETA_E[i]):.12e} {_cm(s.R1_E[i]):.12e} {_cm(s.U1_E[i]):.12e} {_cm(s.U2_E[i]):.12e} {_cm(s.R2_E[i]):.12e}
            {_cm(s.G0_S[i]):.12e} {s.K_S[i]:.12e}
            4 {s.C0_S[i]:.12e} {s.C1_S[i]:.12e} {s.C2_S[i]:.12e} {s.C3_S[i]:.12e} {s.C4_S[i]:.12e} {s.C5_S[i]:.12e} {_cm(s.SHIFT_S[i]):.12e}
            {_degree(s.OMEGA_S[i]):.20e} {_degree(s.THETA_S[i]):.12e} {_cm(s.R1_S[i]):.12e} {_cm(s.U1_S[i]):.12e} {_cm(s.U2_S[i]):.12e} {_cm(s.R2_S[i]):.12e}
            {_cm(s.G0_L[i]):.12e} {s.K_L[i]:.12e}
            4 {s.C0_L[i]:.12e} {s.C1_L[i]:.12e} {s.C2_L[i]:.12e} {s.C3_L[i]:.12e} {s.C4_L[i]:.12e} {s.C5_L[i]:.12e} {_cm(s.SHIFT_L[i]):.12e}
            {_degree(s.OMEGA_L[i]):.20e} {_degree(s.THETA_L[i]):.12e} {_cm(s.R1_L[i]):.12e} {_cm(s.U1_L[i]):.12e} {_cm(s.U2_L[i]):.12e} {_cm(s.R2_L[i]):.12e} {_cm(s.RM3[i]):.12e}
            """)

        c = f"""
            {s.KIRD} {s.RESOL}
            {_cm(s.XPAS):.12e}
            {s.KPOS}
            """
        command.append(c)

        if s.KPOS not in (1, 2):
            raise _ZgoubidooException("KPOS must be equal to 1 or 2.")

        if s.KPOS == 2:
            if s.RE == 0:
                s.RE = s.RM
            if s.RS == 0:
                s.RS = s.RM
            c = f"""
            {_cm(s.RE):.12e} {_radian(s.TE):.12e} {_cm(s.RS):.12e} {_radian(s.TS):.12e}
                """
            command.append(c)

        elif s.KPOS == 1:
            c = f"""
            {s.DP:.12e}
                """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Dodecapole(CartesianMagnet):
    r"""Dodecapole magnet.

    .. rubric:: Zgoubi manual description

    The meaning of parameters for ``DODECAPO`` is the same as for ``QUADRUPO``.

    In fringe field regions the magnetic field :math:`\vec{B}(X, Y, Z)` and its derivatives up to fourth order are derived
    from the scalar potential approximated to the 6th order in Y and Z

    .. math::

        V(X,Y,Z) = G(X)(Y^4 − \frac{10}{3} Y^2 Z^2 + Z^4) YZ

    with :math:`G_0 = \frac{B_0}{R_0^5}`

    The modelling of the fringe field form factor G(X) is described under ``QUADRUPO``, p. 152.
    Outside fringe field regions, or everywhere in sharp edge dodecapole (:math:`λ_E = λ_S = 0`),
    :math:`\vec{B}(X, Y, Z)` in the magnet is given by

    .. math::

        \begin{align}
            B_X &= 0 \\
            B_Y &= G_0 (5 Y^4 − 10 Y^2 Z^2 + Z^4) Z \\
            B_Z &= G_0 (Y^4 − 10 Y^2 Z^2 + 5 Z^4) Y
        \end{align}
    """

    KEYWORD = 'DODECAPO'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, 'Print field and coordinates along trajectories', 1),
        'XL': (0.0 * _ureg.centimeter, 'Magnet length', 10),
        'R0': (10.0 * _ureg.centimeter, 'Radius of the pole tips', 11),
        'B0': (0.0 * _ureg.kilogauss, 'Field at pole tip', 12),
        'X_E': (0.0 * _ureg.centimeter, 'Entrance face integration zone extent for the fringe field', 20),
        'LAM_E': (0.0 * _ureg.centimeter, 'Entrance face fringe field extent (λ_E = 0 for sharp edge)', 21),
        # NCE: (0, 'UNUSED', 7)
        'C0_E': (0.0, 'Fringe field coefficient C0', 31),
        'C1_E': (1.0, 'Fringe field coefficient C1', 32),
        'C2_E': (0.0, 'Fringe field coefficient C2', 33),
        'C3_E': (0.0, 'Fringe field coefficient C3', 34),
        'C4_E': (0.0, 'Fringe field coefficient C4', 35),
        'C5_E': (0.0, 'Fringe field coefficient C5', 36),
        'X_S': (0.0 * _ureg.centimeter, 'Exit face integration zone extent for the fringe field', 40),
        'LAM_S': (0.0 * _ureg.centimeter, 'Exit face fringe field extent', 41),
        # NCS: (0, 'UNUSED', 7)
        'C0_S': (0.0, 'Fringe field coefficient C0', 31),
        'C1_S': (1.0, 'Fringe field coefficient C1', 32),
        'C2_S': (0.0, 'Fringe field coefficient C2', 33),
        'C3_S': (0.0, 'Fringe field coefficient C3', 34),
        'C4_S': (0.0, 'Fringe field coefficient C4', 35),
        'C5_S': (0.0, 'Fringe field coefficient C5', 36),
        'XPAS': (0.1 * _ureg.centimeter, 'Integration step', 60),
        'KPOS': (1, 'Alignment parameter: 1 (element aligned) or 2 (misaligned)', 70),
        'XCE': (0.0 * _ureg.centimeter, 'X shift', 71),
        'YCE': (0.0 * _ureg.centimeter, 'Y shift', 72),
        'ALE': (0.0 * _ureg.radian, 'Tilt', 73),
        'COLOR': ('green', 'Magnet color for plotting.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(s):
        return f"""
         {super().__str__().rstrip()}
         {s.IL}
         {_cm(s.XL):.12e} {_cm(s.R0):.12e} {_kilogauss(s.B0):.12e}
         {_cm(s.XE):.12e} {_cm(s.LAM_E):.12e}
         6 {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
         {_cm(s.XS):.12e} {_cm(s.LAM_S):.12e}
         6 {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
         {_cm(s.XPAS):.12e}
         {s.KPOS} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {_radian(s.ALE):.12e}
         """


class Drift(CartesianMagnet):
    r"""Field free drift space.

    .. rubric:: Zgoubi manual description

    ``DRIFT`` or ``ESL`` allow introduction of a drift space with length XL with positive or negative sign, anywhere in
    a structure. This is an exact transport: the associated equations of motion are (Fig. 24)

    .. math::

        \begin{align}
            Y_2 &= Y_1 +XL *tgT  \\
            Z_2 &= Z_1 + \frac{XL}{cosT}tgP \\
            SAR_2 &= SAR_1 + \frac{XL}{cosT *cosP}
        \end{align}

    whereas the velocity vector is left unchanged.

    The flag ’.plt’ can be added as a second LABEL following ``DRIFT`` keyword. It causes local coordinates to be logged
    to zgoubi.res or to zgoubi.plt (in the same manner as IL=1, or 2, respectively, does in the case optical elements).
    A drift can be split into pieces, using the ’split’ flag. This may be used for graphic purposes for instance:
    a sub-product of ’split’ is its allowing using the IL flag, so logging coordinates to either zgoubi.res or to
    zgoubi.plt (in the same manner as IL=1 or 2, respectively, does in optical elements, step by step).

    .. rubric:: Zgoubidoo usage and example

    >>> Drift(XL=10 * _ureg.cm)

    """
    KEYWORD = 'DRIFT'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, 'Print field and coordinates along trajectories'),
        'XL': (0 * _ureg.centimeter, 'Drift length'),
        'SPLIT': (True, 'Split the drift in multiple steps.'),
        'SPLITS': (10, 'If SPLITS > 1, the drift will be split in multiple steps.'),
        'COLOR': (None, 'Color used when plotting the element.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        if self.SPLIT:
            return f"""
        {super().__str__().rstrip()}
        {self.XL.m_as('cm'):.12e} split {self.SPLITS} {self.IL}
            """
        else:
            return f"""
        {super().__str__().rstrip()}
        {self.XL.m_as('cm'):.12e}
            """

    @property
    def entry_s(self) -> Optional[_ureg.Quantity]:
        """

        Returns:

        """
        if self.reference_trajectory is not None:
            r = self.reference_trajectory['S']
            return r.min() * _ureg.m
        else:
            return 0.0 * _ureg.m

    @classmethod
    def parse(cls, stream: str):
        """TODO"""
        template = """
        '{}' {label1:w}
        {XL_:.12e}
        """
        return _parse.parse(' '.join(template.split()), ' '.join(stream.split()))

    def adjust_tracks_variables(self, tracks: _pd.DataFrame):
        t = tracks[tracks.LABEL1 == self.LABEL1]
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'SREF'] = t['X'] + self.entry_sref.m_as('m')
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT'] = t['Y']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT0'] = t['Yo']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT'] = t['Z']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT0'] = t['Zo']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'BX'] = 0
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'BY'] = 0
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'BZ'] = 0
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'EX'] = 0
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'EY'] = 0
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'EZ'] = 0


class ESL(Drift):
    """Field free drift space ("espace libre")."""
    pass


class Emma(CartesianMagnet):
    """2-D Cartesian or cylindrical mesh field map for EMMA FFAG.

    TODO
    """
    KEYWORD = 'EMMA'
    """Keyword of the command used for the Zgoubi input data."""


class FFAG(PolarMultiMagnet):
    r"""FFAG magnet, N-tuple.

    .. rubric:: Zgoubi manual description

    ``FFAG`` works much like ``DIPOLES`` as to the field modelling, apart from the radial dependence of the field,
    :math:`B = B_0 (\frac{r}{r_0})^k`, so-called “scaling”. Note that ``DIPOLES`` does similar job by using a Taylor
    r-expansion of :math:`B_0(\frac{r}{r_0})^k`. The FFAG procedure allows overlapping of fringe fields of neighboring
    dipoles, thus simulating in some sort the field in a dipole N-tuple - as for instance in an FFAG doublet or triplet.
    A detailed application, with five dipoles, can be found in Ref. [44]. This is done in the way described below.

    The dimensioning of the magnet is defined by :

        - AT : total angular aperture
        - RM : mean radius used for the positioning of field boundaries

    For each one of the N = 1 to (maximum) 5 dipoles of the N-tuple, the two effective field boundaries
    (entrance and exit EFBs) from which the dipole field is drawn are defined from geometric boundaries,
    the shape and position of which are determined by the following parameters
    (in the same manner as in ``DIPOLE``, ``DIPOLE-M`` ) (see Fig. 11-A page 98, and Fig. 31):

        - :math:`ACN_i` : arbitrary inner angle, used for EFBs positioning
        - ω : azimuth of an EFB with respect to ACN
        - θ : angle of an EFB with respect to its azimuth (wedge angle)
        - R1, R2 : radius of curvature of an EFB
        - U1, U2 : extent of the linear part of an EFB

    *Calculation of the Field From a Single Dipole*

    The magnetic field is calculated in polar coordinates. At all (R, θ) in the median plane (z = 0),
    the magnetic field due a single one (index i) of the dipoles of a N-tuple FFAG magnet is written
    $$B_{Z_i}(R, θ) = B_{Z_{0,i}} F_i(R, θ) (R/RM)^{K_i}$$
    wherein :math:`B_{Z_{0,i}}` is a reference field, at reference radius :math:`RM_i`,
    whereas F(R,θ) is calculated as described below.


    *Calculation of* :math:`F_i(R, θ)`

    The fringe field coefficient :math:`F_i(R, θ)` associated with a dipole is computed as in the procedure ``DIPOLES``
    (eq. 6.4.16), including (rigorously if the interpolation method is used, see page 125, or to order zero
    if the analytic method is used, see page 125) radial dependence of the gap size
    $$g(R) = g_0 (RM/R)^κ (6.4.19) $$
    so to simulate the effect of gap shaping on :math:`B_{Z_i}(R,θ)|_R` field fall-off, over the all radial extent of a
    scaling FFAG dipole (with normally - but not necessarily in practice - κ ≈ Ki).

    *Calculation of the Field Resulting From All N Dipoles*

    For the rest, namely, calculation of the full field at particle position from the N dipoles, analytical calculation
    or numerical interpolation of the mid-plane field derivatives, extrapolation off median plane, etc.,
    things are performed exactly as in the case of the ``DIPOLES`` procedure (see page 125).

    *Sharp Edge*

    Sharp edge field fall-off at a field boundary can only be simulated if the following conditions are fulfilled :

        - Entrance (resp. exit) field boundary coincides with entrance (resp. exit) dipole limit (it means in particular
          see Fig. 11, :math:`ω^+ = ACENT` (resp. :math:`ω^- = −(AT − ACENT`)), together with θ = 0 at entrance
          (resp. exit) EFBs)

        - Analytical method for calculation of the mid-plane field derivatives is used.

    """

    KEYWORD = 'FFAG'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, 'Print field and coordinates along trajectories', 1),
        'N': (1, 'Number of dipoles in the FFAG N -tuple (maximum 5)', 2),
        'AT': (0.0 * _ureg.degree, 'Total angular extent of the N dipoles', 3),
        'RM': (0.0 * _ureg.centimeter, 'Reference radius: mean radius used for the positioning of field boundaries', 4),
        # For each magnet in the N-tuple
        'ACN': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Azimuth for dipole positioning', 5),
        'DRM': (
            [0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter,
            'Offset for the reference radius of each dipole RM_i  = RM + DRM', 6
        ),
        'BZ0': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.kilogauss, 'Field of each dipole', 7),
        'K': ([0.0, 0.0, 0.0, 0.0, 0.0], 'Field index for each dipole', 8),
        'G0_E': (
            [10.0, 10.0, 10.0, 10.0, 10.0] * _ureg.cm,
            'Reference gaps for the entrance fringe fields of each dipole.', 9
        ),
        'K_E': ([0, 0, 0, 0, 0], 'Fringe field parameter kappa', 10),
        'C0_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C0', 12),
        'C1_E': ([1, 1, 1, 1, 1], 'Fringe field coefficient C1', 13),
        'C2_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C2', 14),
        'C3_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C3', 15),
        'C4_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C4', 16),
        'C5_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C5', 16),
        'SHIFT_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'Shift of the EFB', 18),
        'OMEGA_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Azimuth of an EFB with respect to ACN', 19),
        'THETA_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Entrance face wedge angle', 20),
        'R1_E': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'Entrance EFB radius', 21),
        'U1_E': ([-1e9, -1e9, -1e9, -1e9, -1e9] * _ureg.centimeter, 'Entrance EFB linear extent', 22),
        'U2_E': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'Entrance EFB linear extent', 23),
        'R2_E': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'Entrance EFB radius', 24),
        'G0_S': (
            [10.0, 10.0, 10.0, 10.0, 10.0] * _ureg.cm,
            'Reference gaps for the exit fringe fields of each dipole.', 25
        ),
        'K_S': ([0, 0, 0, 0, 0], 'Fringe field parameter kappa', 26),
        'C0_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C0', 28),
        'C1_S': ([1, 1, 1, 1, 1], 'Fringe field coefficient C1', 29),
        'C2_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C2', 30),
        'C3_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C3', 31),
        'C4_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C4', 32),
        'C5_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C5', 33),
        'SHIFT_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'Shift of the EFB', 34),
        'OMEGA_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Azimuth of an EFB with respect to ACN', 35),
        'THETA_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Entrance face wedge angle', 36),
        'R1_S': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'Exit EFB radius', 37),
        'U1_S': ([-1e9, -1e9, -1e9, -1e9, -1e9] * _ureg.centimeter, 'Exit EFB linear extent', 38),
        'U2_S': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'Exit EFB linear extent', 39),
        'R2_S': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'Exit EFB radius', 40),
        'G0_L': (
            [0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm,
            'UNUSED Reference gaps for the lateral fringe fields of each dipole.', 41
        ),
        'K_L': ([-1, -1, -1, -1, -1], 'UNUSED Fringe field parameter kappa', 42),
        'C0_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C0', 44),
        'C1_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C1', 45),
        'C2_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C2', 46),
        'C3_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C3', 47),
        'C4_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C4', 48),
        'C5_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C5', 49),
        'SHIFT_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'UNUSED  Shift of the EFB', 50),
        'OMEGA_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'UNUSED ', 51),
        'THETA_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'UNUSED Entrance face wedge angle', 52),
        'R1_L': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'UNUSED Lateral EFB radius', 53),
        'U1_L': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'UNUSED Lateral EFB linear extent', 54),
        'U2_L': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'UNUSED Lateral EFB linear extent', 55),
        'R2_L': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'UNUSED Lateral EFB radius', 56),
        # General parameters
        # The fit index depends on the number of magnets in the FFAG N -tuple (+52 for each new magnet)
        'KIRD': (
            2, 'Analytical computation (KIRD = 0) or numerical interpolation (KIRD = 2,4, 25) of field derivatives', 57
        ),
        'RESOL': (2, '', 58),
        'XPAS': (1.0 * _ureg.millimeter, 'Integration step', 59),
        'KPOS': (2, '', 60),
        'RE': (0.0 * _ureg.centimeter, 'Radius of reference at entrance of the magnet', 61),
        'TE': (0.0 * _ureg.radian, 'Angle of reference at entrance of the magnet', 62),
        'RS': (0.0 * _ureg.centimeter, 'Radius of reference at exit of the magnet', 63),
        'TS': (0.0 * _ureg.radian, 'Angle of reference at exit of the magnet', 64),
        'DP': (0.0, 'Reference relative momentum', 61),
        'COLOR': '#4169E1',
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        for i in range(self.N):
            if _degree(self.ACN[i]) == 0:
                self.ACN[i] = self.AT / (2 * self.N) + i * self.AT / self.N

    def __str__(s):
        command = []
        c = f"""       
            {super().__str__().rstrip()}
            {s.IL}
            {s.N} {_degree(s.AT):.20e} {_cm(s.RM):.12e}
            """
        command.append(c)

        for i in range(0, s.N):
            c = f"""
            {_degree(s.ACN[i]):.20e} {_cm(s.DRM[i]):.12e} {_kilogauss(s.BZ0[i]):.12e} {s.K[i]:.12e}
            {_cm(s.G0_E[i]):.12e} {s.K_E[i]:.12e}
            6 {s.C0_E[i]:.12e} {s.C1_E[i]:.12e} {s.C2_E[i]:.12e} {s.C3_E[i]:.12e} {s.C4_E[i]:.12e} {s.C5_E[i]:.12e} {_cm(s.SHIFT_E[i]):.12e}
            {_degree(s.OMEGA_E[i]):.20e} {_degree(s.THETA_E[i]):.12e} {_cm(s.R1_E[i]):.12e} {_cm(s.U1_E[i]):.12e} {_cm(s.U2_E[i]):.12e} {_cm(s.R2_E[i]):.12e}
            {_cm(s.G0_S[i]):.12e} {s.K_S[i]:.12e}
            6 {s.C0_S[i]:.12e} {s.C1_S[i]:.12e} {s.C2_S[i]:.12e} {s.C3_S[i]:.12e} {s.C4_S[i]:.12e} {s.C5_S[i]:.12e} {_cm(s.SHIFT_S[i]):.12e}
            {_degree(s.OMEGA_S[i]):.20e} {_degree(s.THETA_S[i]):.12e} {_cm(s.R1_S[i]):.12e} {_cm(s.U1_S[i]):.12e} {_cm(s.U2_S[i]):.12e} {_cm(s.R2_S[i]):.12e}
            {_cm(s.G0_L[i]):.12e} {s.K_L[i]:.12e}
            6 {s.C0_L[i]:.12e} {s.C1_L[i]:.12e} {s.C2_L[i]:.12e} {s.C3_L[i]:.12e} {s.C4_L[i]:.12e} {s.C5_L[i]:.12e} {_cm(s.SHIFT_L[i]):.12e}
            {_degree(s.OMEGA_L[i]):.20e} {_degree(s.THETA_L[i]):.12e} {_cm(s.R1_L[i]):.12e} {_cm(s.U1_L[i]):.12e} {_cm(s.U2_L[i]):.12e} {_cm(s.R2_L[i]):.12e}
            """
            command.append(c)

        c = f"""
            {s.KIRD} {s.RESOL}
            {_cm(s.XPAS):.12e}
            {s.KPOS}
            """
        command.append(c)

        if s.KPOS not in (1, 2):
            raise _ZgoubidooException("KPOS must be equal to 1 or 2.")

        if s.KPOS == 2:
            if s.RE == 0:
                s.RE = s.RM
            if s.RS == 0:
                s.RS = s.RM
            c = f"""
            {_cm(s.RE):.12e} {_radian(s.TE):.12e} {_cm(s.RS):.12e} {_radian(s.TS):.12e}
                """
            command.append(c)

        elif s.KPOS == 1:
            c = f"""
            {s.DP:.12e}
                """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class FFAGSpirale(PolarMultiMagnet):
    r"""Spiral FFAG magnet, N-tuple.

    .. rubric:: Zgoubi manual description

    ``FFAG-SPI`` works much like ``FFAG`` as to the field modelling, with essentially a different axial dependence.
    The ``FFAG-SPI`` procedure allows overlapping of fringe fields of neighboring dipoles, thus simulating in some sort
    the field in a dipole N-tuple (similar to Fig. 31, page 137).
    This allows for instance accounting for fringe field effects, or clamps, as schemed in Fig. 32.

    The dimensioning of the magnet is defined by :

        - AT : total angular aperture
        - RM : mean radius used for the positioning of field boundaries

    For each one of the N = 1 to (maximum) 5 dipoles of the N-tuple, the two effective field boundaries
    (entrance and exit EFBs) from which the dipole field is drawn are defined from geometric boundaries,
    the shape and position of which are determined by the following parameters:

        - :math:`ACN_i` : arbitrary inner angle, used for EFBs positioning
        - ω : azimuth of an EFB with respect to ACN
        - ξ : spiral angle

    with :math:`ACN_i` and ω as defined in Fig. 32 (similar to what can be found in Figs. 31 and 11-A).

    *Calculation of the Field From a Single Dipole*

    The magnetic field is calculated in polar coordinates. At all (R, θ) in the median plane (Z = 0),
    the magnetic field due a single one (index i) of the dipoles of a N-tuple spiral FFAG magnet is written
    $$B_{Z_i}(R, θ) = B_{Z_{0,i}} F_i(R, θ) (R/RM )^{K_i}$$
    wherein :math:`B_{Z_{0,i}}` is a reference field, at reference radius :math:`RM_i`, whereas :math:`F(R,θ)` is
    calculated as described below.

    *Calculation of* :math:`F_i(R, θ)`

    The fringe field coefficient :math:`F_i(R, θ)` associated with a dipole is computed as in the procedure ``DIPOLES``
    (eq. 6.4.16), including radial dependence of the gap size :
    $$g(R) = g_0 (RM/R)^κ$$
    so to simulate the effect of gap shaping on :math:`B_{Z_i}(R,θ)|_R` field fall-off, over the all radial extent of
    the dipole (with normally - yet not necessarily in practice - κ ≈ Ki).


    *Calculation of the Full Field From All N Dipoles*

    For the rest, namely calculation of the full field at particle position, as resulting from the N dipoles,
    calculation of the mid-plane field derivatives, extrapolation off median plane, etc.,
    things are performed in the same manner as for the ``DIPOLES`` procedure (see page 125).
    """

    KEYWORD = 'FFAG-SPI'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, 'Print field and coordinates along trajectories', 1),
        'N': (1, 'Number of dipoles in the FFAG n-tuple (maximum 5)', 2),
        'AT': (0.0 * _ureg.degree, 'Total angular extent of the N dipoles', 3),
        'RM': (0.0 * _ureg.centimeter, 'Reference radius: mean radius used for the positioning of field boundaries', 4),
        # For each magnet in the n-tuple
        'ACN': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Azimuth for dipole positioning', 5),
        'DRM': (
            [0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter,
            'Reference radius offset of each dipole : RM_i  = RM + DRM', 6
        ),
        'BZ0': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.kilogauss, 'Field at the reference radius of each dipole', 7),
        'K': ([0.0, 0.0, 0.0, 0.0, 0.0], 'Field index for each dipole', 8),
        'G0_E': (
            [10.0, 10.0, 10.0, 10.0, 10.0] * _ureg.cm,
            'Reference gaps for the entrance fringe fields of each dipole.', 9
        ),
        'K_E': ([0, 0, 0, 0, 0], 'Fringe field parameter kappa', 10),
        'NCE': ([0, 0, 0, 0, 0], 'UNUSED', 11),
        'C0_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C0', 12),
        'C1_E': ([1, 1, 1, 1, 1], 'Fringe field coefficient C1', 13),
        'C2_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C2', 14),
        'C3_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C3', 15),
        'C4_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C4', 16),
        'C5_E': ([0, 0, 0, 0, 0], 'Fringe field coefficient C5', 17),
        'SHIFT_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'Shift of the EFB', 18),
        'OMEGA_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Azimuth of an EFB with respect to ACN', 19),
        'XI_E': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Spiral angle', 20),
        'G0_S': (
            [10.0, 10.0, 10.0, 10.0, 10.0] * _ureg.cm,
            'Reference gaps for the exit fringe fields of each dipole.', 25
        ),
        'K_S': ([0, 0, 0, 0, 0], 'Fringe field parameter kappa', 26),
        'NCS': ([0, 0, 0, 0, 0], 'UNUSED', 27),
        'C0_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C0', 28),
        'C1_S': ([1, 1, 1, 1, 1], 'Fringe field coefficient C1', 29),
        'C2_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C2', 30),
        'C3_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C3', 31),
        'C4_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C4', 32),
        'C5_S': ([0, 0, 0, 0, 0], 'Fringe field coefficient C5', 33),
        'SHIFT_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'Shift of the EFB', 34),
        'OMEGA_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Azimuth of an EFB with respect to ACN', 35),
        'XI_S': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'Spiral angle', 36),
        'G0_L': (
            [0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.cm,
            'UNUSED Reference gaps for the lateral fringe fields of each dipole.',41
        ),
        'K_L': ([-1, -1, -1, -1, -1], 'UNUSED Fringe field parameter kappa', 42),
        'NCL': ([0, 0, 0, 0, 0], 'UNUSED', 43),
        'C0_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C0', 44),
        'C1_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C1', 45),
        'C2_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C2', 46),
        'C3_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C3', 47),
        'C4_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C4', 48),
        'C5_L': ([0, 0, 0, 0, 0], 'UNUSED Fringe field coefficient C5', 49),
        'SHIFT_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.centimeter, 'UNUSED  Shift of the EFB', 50),
        'OMEGA_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'UNUSED ', 51),
        'THETA_L': ([0.0, 0.0, 0.0, 0.0, 0.0] * _ureg.degree, 'UNUSED Entrance face wedge angle', 52),
        'R1_L': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'UNUSED Lateral EFB radius', 53),
        'U1_L': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'UNUSED Lateral EFB linear extent', 54),
        'U2_L': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'UNUSED Lateral EFB linear extent', 55),
        'R2_L': ([1e9, 1e9, 1e9, 1e9, 1e9] * _ureg.centimeter, 'UNUSED Lateral EFB radius', 56),
        # General parameters
        # The fit index depends on the number of magnets in the FFAG_SPI N-tuple (+52 for each new magnet)
        'KIRD': (
            2, 'Analytical computation (KIRD = 0) or numerical interpolation (KIRD = 2,4, 25) of field derivatives', 57
        ),
        'RESOL': (2, '', 58),
        'XPAS': (1.0 * _ureg.millimeter, 'Integration step', 59),
        # 'KPOS': (2, '', 60), # KPOS = 2 for FFA-SPI
        'RE': (0.0 * _ureg.centimeter, '', 61),
        'TE': (0.0 * _ureg.radian, '', 62),
        'RS': (0.0 * _ureg.centimeter, '', 63),
        'TS': (0.0 * _ureg.radian, '', 64),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def adjust_tracks_variables(self, tracks: _pd.DataFrame):
        t = tracks[tracks.LABEL1 == self.LABEL1]
        radius = self.RM.m_as('m')
        angles = 100 * t['X'] + self.AT.m_as('radians') / 2
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ANGLE'] = angles
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'R'] = t['Y']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'R0'] = t['Yo']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'SREF'] = radius * angles + self.entry_sref.m_as('m')
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT'] = t['Y'] - radius
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT0'] = t['Yo'] - radius
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT'] = t['Z']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT0'] = t['Zo']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'X'] = t['Y'] * _np.sin(angles)
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'X0'] = t['Yo'] * _np.sin(angles)
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'Y'] = t['Y'] * _np.cos(angles) - radius
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'Y0'] = t['Yo'] * _np.cos(angles) - radius

    @property
    def reference_angles(self) -> List[_Q]:
        return [acn + self.AT / 2 for acn in self.ACN]

    @property
    def entrance_field_boundary_wedge_angle(self) -> List[_Q]:
        return _np.zeros(self.N)*_ureg.degrees

    @property
    def exit_field_boundary_wedge_angle(self) -> List[_Q]:
        return _np.zeros(self.N)*_ureg.degrees

    @property
    def entrance_spiral_angle(self) -> List[_Q]:
        return self.XI_E

    @property
    def exit_spiral_angle(self) -> List[_Q]:
        return self.XI_S

    @property
    def entrance_field_boundary_linear_extent_down(self) -> List[_Q]:
        return 500*_np.ones(self.N)*_ureg.cm

    @property
    def entrance_field_boundary_linear_extent_up(self) -> List[_Q]:
        return 500*_np.ones(self.N)*_ureg.cm

    @property
    def entrance_field_boundary_linear_radius_up(self) -> List[_Q]:
        return 500*_np.ones(self.N)*_ureg.cm

    @property
    def entrance_field_boundary_linear_radius_down(self) -> List[_Q]:
        return 500*_np.ones(self.N)*_ureg.cm

    @property
    def exit_field_boundary_linear_extent_down(self) -> List[_Q]:
        return 500*_np.ones(self.N)*_ureg.cm

    @property
    def exit_field_boundary_linear_extent_up(self) -> List[_Q]:
        return 500*_np.ones(self.N)*_ureg.cm

    @property
    def exit_field_boundary_linear_radius_up(self) -> List[_Q]:
        return 100*_np.ones(self.N)*_ureg.cm

    @property
    def exit_field_boundary_linear_radius_down(self) -> List[_Q]:
        return 500*_np.ones(self.N)*_ureg.cm

    def __str__(s):
        command = []
        c = f"""
            {super().__str__().rstrip()}
            {s.IL}
            {s.N} {s.AT.m_as('degree'):.12e} {s.RM.m_as('cm'):.12e}
            """
        command.append(c)

        for i in range(0, s.N):
            c = f"""
            {s.ACN[i].m_as('degree'):.12e} {s.DRM[i].m_as('cm'):.12e} {s.BZ0[i].m_as('kilogauss'):.12e} {s.K[i]:.12e}
            {s.G0_E[i].m_as('cm'):.12e} {s.K_E[i]:.12e}
            {s.NCE[i]} {s.C0_E[i]:.12e} {s.C1_E[i]:.12e} {s.C2_E[i]:.12e} {s.C3_E[i]:.12e} {s.C4_E[i]:.12e} {s.C5_E[i]:.12e} {s.SHIFT_E[i].m_as('cm'):.12e}
            {s.OMEGA_E[i].m_as('degree'):.12e} {s.XI_E[i].m_as('degree'):.12e} 0.0 0.0 0.0 0.0
            {s.G0_S[i].m_as('cm'):.12e} {s.K_S[i]:.12e}
            {s.NCS[i]} {s.C0_S[i]:.12e} {s.C1_S[i]:.12e} {s.C2_S[i]:.12e} {s.C3_S[i]:.12e} {s.C4_S[i]:.12e} {s.C5_S[i]:.12e} {s.SHIFT_S[i].m_as('cm'):.12e}
            {s.OMEGA_S[i].m_as('degree'):.12e} {s.XI_S[i].m_as('degree'):.12e} 0.0 0.0 0.0 0.0
            {_cm(s.G0_L[i]):.12e} {s.K_L[i]:.12e}
            {s.NCL[i]} {s.C0_L[i]:.12e} {s.C1_L[i]:.12e} {s.C2_L[i]:.12e} {s.C3_L[i]:.12e} {s.C4_L[i]:.12e} {s.C5_L[i]:.12e} {_cm(s.SHIFT_L[i]):.12e}
            {_degree(s.OMEGA_L[i]):.20e} {_degree(s.THETA_L[i]):.12e} {_cm(s.R1_L[i]):.12e} {_cm(s.U1_L[i]):.12e} {_cm(s.U2_L[i]):.12e} {_cm(s.R2_L[i]):.12e}
                """
            command.append(c)

        command.append(f"""
            {s.KIRD} {s.RESOL:.12e}
            {s.XPAS.m_as('cm'):.12e}
            """)

        c = f"""
            2
            {s.RE.m_as('cm'):.12e} {s.TE.m_as('radian'):.12e} {s.RS.m_as('cm'):.12e} {s.TS.m_as('radian'):.12e}
            """
        command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Halbach(CartesianMagnet):
    pass


class Multipole(CartesianMagnet):
    """Magnetic multipole.

    .. rubric:: Zgoubi manual description

    The simulation of multipolar magnetic field M⃗ by MULTIPOL proceeds by addition of the dipolar (B1),
    quadrupolar (B2), sextupolar (B3), etc., up to 20-polar (B10) components, and of their derivatives up to fourth
    order.

    The independent components B1, B2, B3, ..., B10 and their derivatives up to the fourth order are calculated as
    described in section 1.3.7.

    The entrance and exit fringe fields are treated separately. They are characterized by the integration zone XE at
    entrance and XS at exit, as for QUADRUPO, and by the extent λE at entrance, λS at exit. The fringe field extents
    for the dipole component are λE and λS. The fringe field for the quadrupolar (sextupolar, ..., 20-polar) component
    is given by a coefficient E2 (E3, ..., E10) at entrance, and S2 (S3, ..., S10) at exit, such that the extent is
    λE * E2 (λE * E3, ..., λE * E10) at entrance and λS * S2 (λS * S3, ..., λS * S10) at exit.

    If λE = 0 (λS = 0) the multipole lens is considered to have a sharp edge field at entrance (exit), and then,
    XE (XS) is forced to zero (for the mere purpose of saving computing time). If Ei = 0 (Si = 0) (i = 2, 10), the
    entrance (exit) fringe field for the multipole component i is considered as a sharp edge field. In sharp edge field
    model, the wedge angle vertical first order focusing effect (if B1 is non zero) is simulated at magnet entrance and
    exit by a kick P2 = P1 − Z1 tan(ε/ρ) applied to each particle (P1, P2 are the vertical angles upstream and
    downstream of the EFB, Z1 is the vertical particle position at the EFB, ρ the local horizontal bending radius and
    ε the wedge angle experienced by the particle ; ε depends on the horizontal angle T).

    Any multipole component Bi can be rotated independently by an angle RXi around the longitudinal X- axis, for the
    simulation of positioning defects, as well as skew lenses.

    Magnet (mis-)alignment is assured by KPOS. KPOS also allows some degrees of automatic alignment useful for periodic
    structures (section 4.6.7).
    """
    KEYWORD = 'MULTIPOL'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
            'IL': (0, 'Print field and coordinates along trajectories', 1),
            'XL': (0 * _ureg.cm, 'Magnet length', 2),
            'R0': (10.0 * _ureg.cm, 'Radius of the pole tips', 3),
            'B1': (0 * _ureg.kilogauss, 'Field at pole tip for dipolar component.', 4),
            'B2': (0 * _ureg.kilogauss, 'Field at pole tip for quadrupolar component.', 5),
            'B3': (0 * _ureg.kilogauss, 'Field at pole tip for sextupolar component.', 6),
            'B4': (0 * _ureg.kilogauss, 'Field at pole tip for octupolar component.', 7),
            'B5': (0 * _ureg.kilogauss, 'Field at pole tip for decapolar component.', 8),
            'B6': (0 * _ureg.kilogauss, 'Field at pole tip for dodecapolar component.', 9),
            'B7': (0 * _ureg.kilogauss, 'Field at pole tip for 14-polar component.', 10),
            'B8': (0 * _ureg.kilogauss, 'Field at pole tip for 16-polar component.', 11),
            'B9': (0 * _ureg.kilogauss, 'Field at pole tip for 18-polar component.', 12),
            'B10': (0 * _ureg.kilogauss, 'Field at pole tip for 20-polar component.', 13),
            'X_E': (0 * _ureg.cm, 'Entrance face integration zone for the fringe field.'),
            'LAM_E': (0 * _ureg.cm, 'Entrance face fringe field extent'),
            'E2': (1, 'Quadrupole entrance fringe field extent (E_2 * LAM_E).'),
            'E3': (1, 'Sextupolar entrance fringe field extent (E_3 * LAM_E).'),
            'E4': (1, 'Octupolar entrance fringe field extent (E_4 * LAM_E).'),
            'E5': (1, 'Decapolar entrance fringe field extent (E_5 * LAM_E).'),
            'E6': (1, 'Dodecapolar entrance fringe field extent (E_6 * LAM_E).'),
            'E7': (1, '14-polar entrance fringe field extent (E_7 * LAM_E).'),
            'E8': (1, '16-polar entrance fringe field extent (E_8 * LAM_E).'),
            'E9': (1, '18-polar entrance fringe field extent (E_9 * LAM_E).'),
            'E10': (1, '20-polar entrance fringe field extent (E_10 * LAM_E).'),
            'C0_E': (0, 'Zeroth-order Enge coefficient for entrance fringe field.'),
            'C1_E': (1, 'First-order Enge coefficient for entrance fringe field.'),
            'C2_E': (0, 'Second-order Enge coefficient for entrance fringe field.'),
            'C3_E': (0, 'Third-order Enge coefficient for entrance fringe field.'),
            'C4_E': (0, 'Fourth-order Enge coefficient for entrance fringe field.'),
            'C5_E': (0, 'Fifth-order Enge coefficient for entrance fringe field.'),
            'X_S': (0 * _ureg.cm, 'Exit face integration zone for the fringe field.'),
            'LAM_S': (0 * _ureg.cm, 'Exit face fringe field extent'),
            'S2': (1, 'Quadrupole exit fringe field extent (E_2 * LAM_S).'),
            'S3': (1, 'Sextupolar exit fringe field extent (E_3 * LAM_S).'),
            'S4': (1, 'Octupolar exit fringe field extent (E_4 * LAM_S).'),
            'S5': (1, 'Decapolar exit fringe field extent (E_5 * LAM_S).'),
            'S6': (1, 'Dodecapolar exit fringe field extent (E_6 * LAM_S).'),
            'S7': (1, '14-polar exit fringe field extent (E_7 * LAM_S).'),
            'S8': (1, '16-polar exit fringe field extent (E_8 * LAM_S).'),
            'S9': (1, '18-polar exit fringe field extent (E_9 * LAM_S).'),
            'S10': (1, '20-polar exit fringe field extent (E_10 * LAM_S).'),
            'C0_S': (0, 'Zeroth-order Enge coefficient for entrance fringe field.'),
            'C1_S': (1, 'First-order Enge coefficient for exit fringe field.'),
            'C2_S': (0, 'Second-order Enge coefficient for exit fringe field.'),
            'C3_S': (0, 'Third-order Enge coefficient for exit fringe field.'),
            'C4_S': (0, 'Fourth-order Enge coefficient for exit fringe field.'),
            'C5_S': (0, 'Fifth-order Enge coefficient for exit fringe field.'),
            'R1': (0 * _ureg.degree, 'Skew angle of the dipolar component'),
            'R2': (0 * _ureg.degree, 'Skew angle of the quadrupolar component'),
            'R3': (0 * _ureg.degree, 'Skew angle of the sextupolar component'),
            'R4': (0 * _ureg.degree, 'Skew angle of the octupolar component'),
            'R5': (0 * _ureg.degree, 'Skew angle of the decapolar component'),
            'R6': (0 * _ureg.degree, 'Skew angle of the dodecapolar component'),
            'R7': (0 * _ureg.degree, 'Skew angle of the 14-polar component'),
            'R8': (0 * _ureg.degree, 'Skew angle of the 16-polar component'),
            'R9': (0 * _ureg.degree, 'Skew angle of the 18-polar component'),
            'R10': (0 * _ureg.degree, 'Skew angle of the 20-polar component'),
            'XPAS': (1.0 * _ureg.cm, 'Integration step.'),
            'KPOS': (1, ''),
            'XCE': (0 * _ureg.cm, ''),
            'YCE': (0 * _ureg.cm, ''),
            'ALE': (0 * _ureg.radian, ''),
            'COLOR': ('green', 'Magnet color for plotting.'),

    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IL}
        {_cm(s.XL):.12e} {_cm(s.R0):.12e} {s.B1.m_as('kilogauss'):.12e} {s.B2.m_as('kilogauss'):.12e} {s.B3.m_as('kilogauss'):.12e} {s.B4.m_as('kilogauss'):.12e} {s.B5.m_as('kilogauss'):.12e} {s.B6.m_as('kilogauss'):.12e} {s.B7.m_as('kilogauss'):.12e} {s.B8.m_as('kilogauss'):.12e} {s.B9.m_as('kilogauss'):.12e} {s.B10.m_as('kilogauss'):.12e}
        {_cm(s.X_E):.12e} {_cm(s.LAM_E):.12e} {s.E2:.12e} {s.E3:.12e} {s.E4:.12e} {s.E5:.12e} {s.E6:.12e} {s.E7:.12e} {s.E8:.12e} {s.E9:.12e} {s.E10:.12e}
        6 {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
        {_cm(s.X_S):.12e} {_cm(s.LAM_S):.12e} {s.S2:.12e} {s.S3:.12e} {s.S4:.12e} {s.S5:.12e} {s.S6:.12e} {s.S7:.12e} {s.S8:.12e} {s.S9:.12e} {s.S10:.12e}
        6 {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
        {_radian(s.R1):.12e} {_radian(s.R2):.12e} {_radian(s.R3):.12e} {_radian(s.R4):.12e} {_radian(s.R5):.12e} {_radian(s.R6):.12e} {_radian(s.R7):.12e} {_radian(s.R8):.12e} {_radian(s.R9):.12e} {_radian(s.R10):.12e}
        {s.XPAS.m_as('cm')}
        {s.KPOS} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {_radian(s.ALE):.12e}
        """


Multipol = Multipole


class Octupole(CartesianMagnet):
    """Octupole magnet.

    TODO
    """
    KEYWORD = 'OCTUPOLE'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, 'Print field and coordinates along trajectories', 0),
        'XL': (0 * _ureg.centimeter, 'Magnet length', 10),
        'R0': (1.0 * _ureg.centimeter, 'Radius of the pole tips', 11),
        'B0': (0 * _ureg.kilogauss, 'Field at pole tips', 12),
        'X_E': (0 * _ureg.centimeter, 'Entrance face integration zone for the fringe field', 20),
        'LAM_E': (0 * _ureg.centimeter, 'Entrance face fringe field extent', 21),
        'C0_E': 0,
        'C1_E': 1,
        'C2_E': 0,
        'C3_E': 0,
        'C4_E': 0,
        'C5_E': 0,
        'X_S': (0 * _ureg.centimeter, 'Exit face integration zone for the fringe field'),
        'LAM_S': (0 * _ureg.centimeter, 'Exit face fringe field extent'),
        'C0_S': 0,
        'C1_S': 1,
        'C2_S': 0,
        'C3_S': 0,
        'C4_S': 0,
        'C5_S': 0,
        'XPAS': (0.1 * _ureg.centimeter, 'Integration step', 60),
        'KPOS': (1, 'Misalignment type', 70),
        'XCE': (0 * _ureg.centimeter, 'x offset', 71),
        'YCE': (0 * _ureg.centimeter, 'y offset', 72),
        'ALE': (0 * _ureg.radian, 'misalignment rotation', 73),
        'COLOR': ('#FF33E9', 'Magnet color for plotting.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        if _cm(self.X_E) == 0 and _cm(self.R0) != 0 and self.LAM_E.magnitude != 0:
            self.X_E = 2 * self.R0
        if _cm(self.X_S) == 0 and _cm(self.R0) != 0 and self.LAM_S.magnitude != 0:
            self.X_S = 2 * self.R0

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IL}
        {_cm(s.XL):.12e} {_cm(s.R0):.12e} {_kilogauss(s.B0):.12e}
        {_cm(s.X_E):.12e} {_cm(s.LAM_E):.12e}
        6 {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
        {_cm(s.X_S):.12e} {_cm(s.LAM_S):.12e}
        6 {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
        {_cm(s.XPAS)}
        {s.KPOS} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {_radian(s.ALE):.12e}
        """

    @property
    def gradient(self):
        """Octopolar gradient (field at pole tip divided by the bore radius."""
        return self.B0 / self.R0

    @gradient.setter
    def gradient(self, g):
        self.B0 = g * self.R0


class PS170(Magnet):
    """Simulation of a round shape dipole magnet.

    TODO

    Examples:
        >>> PS170('PS170', IL=2, XL=2 * _ureg.m, R0 = 1.5 * _ureg.m, B0 = 1 * _ureg.tesla)
    """
    KEYWORD = 'PS170'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, 'print field and coordinates along trajectories'),
        'XL': (1 * _ureg.m, 'Length of the element'),
        'R0': (1 * _ureg.m, ', radius of the circular dipole'),
        'B0': (0 * _ureg.tesla, 'field'),
        'XPAS': (1.0 * _ureg.mm, 'Integration step'),
        'KPOS': (0, ),
        'XCE': (0 * _ureg.cm, ''),
        'YCE': (0 * _ureg.cm, ''),
        'ALE': (0 * _ureg.degree, ''),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(self) -> str:
        if self.KPOS not in (0, 1, 2):
            raise _ZgoubidooException("KPOS must be in (0, 1, 2)")
        return f"""
        {super().__str__().rstrip()}
        {int(self.IL):d}
        {_cm(self.XL):.12e} {_cm(self.R0):.12e} {_kilogauss(self.B0):.12e}
        {_cm(self.XPAS):.12e}  
        {int(self.KPOS):d} {_cm(self.XCE):.12e} {_cm(self.YCE):.12e} {_radian(self.ALE):.12e}
        """


class Quadisex(CartesianMagnet):
    """Sharp edge magnetic multipoles.

    TODO
    """
    KEYWORD = 'QUADISEX'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': 0,
        'XL': 0,
        'R0': 0,
        'B0': 0,
        'N': 0,
        'EB1': 0,
        'EB2': 0,
        'EG1': 0,
        'EG2': 0,
        'XPAS': 0.1,
        'KPOS': 1,
        'XCE': 0,
        'YCE': 0,
        'ALE': 0,
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(s):
        command = []
        c = f"""
                {super().__str__().rstrip()}
                {s.IL}
                {s.XL:.12e} {s.R0:.12e} {s.B0:.12e}
                {s.N:.12e} {s.EB1:.12e} {s.EB2:.12e} {s.EG1:.12e} {s.EG2:.12e} 
                {s.XPAS:.12e}  
                """
        command.append(c)

        if s.KPOS not in (1, 2):
            raise _ZgoubidooException("KPOS must be equal to 1 or 2")

        if s.KPOS == 1:
            c = f"""
                {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
                """
            command.append(c)
        elif s.KPOS == 2:
            c = f"""
                {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
                """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Quadrupole(CartesianMagnet):
    """Quadrupole magnet.

    TODO
    """
    KEYWORD = 'QUADRUPO'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, 'Print field and coordinates along trajectories', 1),
        'XL': (0 * _ureg.centimeter, 'Magnet length', 10),
        'R0': (1.0 * _ureg.centimeter, 'Radius of the pole tips', 11),
        'B0': (0 * _ureg.kilogauss, 'Field at pole tips', 12),
        'X_E': (0 * _ureg.centimeter, 'Entrance face integration zone for the fringe field', 20),
        'LAM_E': (0 * _ureg.centimeter, 'Entrance face fringe field extent', 21),
        'C0_E': (0, 'Fringe field coefficient C0', 31),
        'C1_E': (1, 'Fringe field coefficient C1', 32),
        'C2_E': (0, 'Fringe field coefficient C2', 33),
        'C3_E': (0, 'Fringe field coefficient C3', 34),
        'C4_E': (0, 'Fringe field coefficient C4', 35),
        'C5_E': (0, 'Fringe field coefficient C5', 36),
        'X_S': (0 * _ureg.centimeter, 'Exit face integration zone for the fringe field', 40),
        'LAM_S': (0 * _ureg.centimeter, 'Exit face fringe field extent', 41),
        'C0_S': (0, 'Fringe field coefficient C0', 51),
        'C1_S': (1, 'Fringe field coefficient C1', 52),
        'C2_S': (0, 'Fringe field coefficient C2', 53),
        'C3_S': (0, 'Fringe field coefficient C3', 54),
        'C4_S': (0, 'Fringe field coefficient C4', 55),
        'C5_S': (0, 'Fringe field coefficient C5', 56),
        'XPAS': (0.1 * _ureg.centimeter, 'Integration step', 60),
        'KPOS': (1, 'Misalignment type', 70),
        'XCE': (0 * _ureg.centimeter, 'x offset', 71),
        'YCE': (0 * _ureg.centimeter, 'y offset', 72),
        'ALE': (0 * _ureg.radian, 'misalignment rotation', 73),
        'COLOR': ('#FF0000', 'Magnet color for plotting.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def post_init(self, **kwargs):
        """

        Args:
            **kwargs:

        Returns:

        """
        if _cm(self.X_E) == 0 and _cm(self.R0) != 0 and self.LAM_E.magnitude != 0:
            self.X_E = 2 * self.R0
        if _cm(self.X_S) == 0 and _cm(self.R0) != 0 and self.LAM_S.magnitude != 0:
            self.X_S = 2 * self.R0

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IL}
        {_cm(s.XL):.12e} {_cm(s.R0):.12e} {_kilogauss(s.B0):.12e}
        {_cm(s.X_E):.12e} {_cm(s.LAM_E):.12e}
        6 {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
        {_cm(s.X_S):.12e} {_cm(s.LAM_S):.12e}
        6 {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
        {_cm(s.XPAS)}
        {s.KPOS} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {_radian(s.ALE):.12e}
        """

    @property
    def gradient(self):
        """Quadrupolar gradient (field at pole tip divided by the bore radius."""
        return self.B0 / self.R0

    @gradient.setter
    def gradient(self, g):
        self.B0 = g * self.R0


class SexQuad(CartesianMagnet):
    """Sharp edge magnetic multipole.

    TODO
    """
    KEYWORD = 'SEXQUAD'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': 0,
        'XL': 0,
        'R0': 0,
        'N': 0,
        'EB1': 0,
        'EB2': 0,
        'EG1': 0,
        'EG2': 0,
        'XPAS': 0.1,
        'KPOS': 1,
        'XCE': 0,
        'YCE': 0,
        'ALE': 0,
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(s):
        command = []
        c = f"""
                    {super().__str__().rstrip()}
                    {s.IL}
                    {s.XL:.12e} {s.R0:.12e} {s.B0:.12e}
                    {s.N:.12e} {s.EB1:.12e} {s.EB2:.12e} {s.EG1:.12e} {s.EG2:.12e} 
                    {s.XPAS:.12e}  
                    """
        # Coefficients for the calculation of B.
        # if Y > 0 : B = EB1 and G = EG1;
        # if Y < 0: B = EB2 and G = EG2.
        command.append(c)

        if s.KPOS not in (1, 2):
            raise _ZgoubidooException("KPOS must be equal to 1 or 2")

        if s.KPOS == 1:  # XCE, YCE and ALE set to 0 and unused
            c = f"""
                    {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
                    """
            command.append(c)
        elif s.KPOS == 2:  # Elements are misaligned
            c = f"""
                    {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
                    """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Sextupole(CartesianMagnet):
    """Sextupole magnet.

    TODO
    """
    KEYWORD = 'SEXTUPOL'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, 'Print field and coordinates along trajectories', 1),
        'XL': (0 * _ureg.centimeter, 'Magnet length', 10),
        'R0': (1.0 * _ureg.centimeter, 'Radius of the pole tips', 11),
        'B0': (0 * _ureg.kilogauss, 'Field at pole tips', 12),
        'X_E': (0 * _ureg.centimeter, 'Entrance face integration zone for the fringe field', 20),
        'LAM_E': (0 * _ureg.centimeter, 'Entrance face fringe field extent', 21),
        'C0_E': 0,
        'C1_E': 1,
        'C2_E': 0,
        'C3_E': 0,
        'C4_E': 0,
        'C5_E': 0,
        'X_S': (0 * _ureg.centimeter, 'Exit face integration zone for the fringe field'),
        'LAM_S': (0 * _ureg.centimeter, 'Exit face fringe field extent'),
        'C0_S': 0,
        'C1_S': 1,
        'C2_S': 0,
        'C3_S': 0,
        'C4_S': 0,
        'C5_S': 0,
        'XPAS': (1.0 * _ureg.centimeter, 'Integration step', 60),
        'KPOS': (1, 'Misalignment type', 70),
        'XCE': (0 * _ureg.centimeter, 'x offset', 71),
        'YCE': (0 * _ureg.centimeter, 'y offset', 72),
        'ALE': 0 * _ureg.radian,
        'COLOR': ('#00FF00', 'Magnet color for plotting.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IL}
        {_cm(s.XL):.12e} {_cm(s.R0):.12e} {_kilogauss(s.B0):.12e}
        {_cm(s.X_E):.12e} {_cm(s.LAM_E):.12e}
        6 {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
        {_cm(s.X_S):.12e} {_cm(s.LAM_S):.12e}
        6 {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
        {_cm(s.XPAS)}
        {s.KPOS} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {_radian(s.ALE):.12e}
        """


class Solenoid(CartesianMagnet):
    """Solenoid.

    .. rubric:: Zgoubi manual description

    The solenoidal m􏰛agnet has an effective length XL, a mean radius R0 and an asymptotic field B0 = μ0 NI/XL,
    wherein BX is the longitudinal field component, and NI the number of Ampere-Turns.

    The distance of ray-tracing beyond the effective length XL, is XE at the entrance, and XS at the exit.
    """
    KEYWORD = 'SOLENOID'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, 'Print field and coordinates along trajectories'),
        'XL': (0 * _ureg.centimeter, 'Magnet length'),
        'R0': (1.0 * _ureg.centimeter, 'Radius'),
        'B0': (0 * _ureg.kilogauss, 'Asymptotic field'),
        'X_E': (0 * _ureg.centimeter, 'Entrance face integration zone for the fringe field'),
        'X_S': (0 * _ureg.centimeter, 'Exit face integration zone for the fringe field'),
        'MODL': ('', 'Methods for the computation of the field'),
        'XPAS': (0.1 * _ureg.centimeter, 'Integration step'),
        'KPOS': (1, 'Misalignment type'),
        'XCE': (0 * _ureg.centimeter, 'x offset'),
        'YCE': (0 * _ureg.centimeter, 'y offset'),
        'ALE': 0 * _ureg.radian,
        'COLOR': ('#808000', 'Magnet color for plotting.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IL}
        {_cm(s.XL):.12e} {_cm(s.R0):.12e} {_kilogauss(s.B0):.12e} {s.MODL}
        {_cm(s.XE):.12e} {_cm(s.XS):.12e}
        {_cm(s.XPAS)}
        {s.KPOS} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {_radian(s.ALE):.12e}
        """


class Undulator(Magnet):
    """Undulator magnet.

    TODO
    """
    KEYWORD = 'UNDULATOR'
    """Keyword of the command used for the Zgoubi input data."""


class Venus(Magnet):
    """Simulation of a rectangular shaped dipole magnet.

    TODO
    """
    KEYWORD = 'VENUS'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, ),
        'XL': (100 * _ureg.centimeter,),
        'YL': (100 * _ureg.centimeter,),
        'B0': (10 * _ureg.kilogauss,),
        'XPAS': (0.1 * _ureg.centimeter,),
        'KPOS': 1,
        'XCE': (0 * _ureg.centimeter,),
        'YCE': (0 * _ureg.centimeter,),
        'ALE': (0 * _ureg.radian,),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(self) -> str:
        if self.KPOS not in (0, 1, 2):
            raise _ZgoubidooException("KPOS must be in (0, 1, 2)")
        return f"""
        {super().__str__().rstrip()}
        {int(self.IL):d}
        {_cm(self.XL):.12e} {_cm(self.YL):.12e} {_kilogauss(self.B0):.12e}
        {_cm(self.XPAS):.12e}  
        {int(self.KPOS):d} {_cm(self.XCE):.12e} {_cm(self.YCE):.12e} {_radian(self.ALE):.12e}
        """
