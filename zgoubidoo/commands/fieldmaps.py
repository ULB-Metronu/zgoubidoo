"""Zgoubidoo's interfaces to field map tracking commands.

More details here.
"""
from __future__ import annotations
import os
from typing import TYPE_CHECKING, Optional, List, Mapping, Union
from abc import abstractmethod
import numpy as _np
import pandas as _pd
from scipy.io import FortranFile, FortranEOFError
from .commands import Command as _Command
from .actions import Action as _Action
from .magnetique import Magnet as _Magnet
from .magnetique import CartesianMagnet as _CartesianMagnet
from .magnetique import PolarMagnet as _PolarMagnet
from .. import ureg as _ureg
from .. import Q_ as _Q
from ..units import _cm, _radian
from ..zgoubi import Zgoubi as _Zgoubi
from ..zgoubi import ZgoubiException as _ZgoubiException
import zgoubidoo
import plotly.graph_objects as _go
from georges_core.frame import Frame as _Frame

if TYPE_CHECKING:
    from ..input import Input as _Input


class Brevol(_Command):
    """1-D uniform mesh magnetic field map.

    TODO
    """
    KEYWORD = 'BREVOL'
    """Keyword of the command used for the Zgoubi input data."""


class CartesianMesh(_Command):
    """2-D Cartesian uniform mesh magnetic field map.

    TODO
    """
    KEYWORD = 'CARTEMES'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IC': (2, 'Print the map'),
        'IL': (2, 'Print field and coordinates along trajectories'),
        'BNORM': (1.0, 'Field normalization coefficient'),
        'XN': (1.0, 'X coordinate normalization coefficient'),
        'YN': (1.0, 'Y coordinate normalization coefficient'),
        'TITL': ("CARTEMES_FIELD_MAP", "Title. Start with 'FLIP' to get field map X-flipped"),
        'IX': (1, 'Number of longitudinal nodes of the map'),
        'JY': (1, 'Number of transverse nodes of the map'),
        'FNAME': ("field_map.map", 'File name'),
        'ID': (0, 'Integration boundary'),
        'A': (0.0,),
        'B': (0.0,),
        'C': (0.0,),
        'AP': ([0.0]),
        'BP': ([0.0]),
        'CP': ([0.0]),
        'IORDRE': (25, 'Degree of interpolation polynomial'),
        'XPAS': (1 * _ureg.cm, 'Integration step'),
        'KPOS': (1, 'Alignment'),
        'XCE': (0 * _ureg.cm, 'Misalignment X shift'),
        'YCE': (0 * _ureg.cm, 'Misalignment Y shift'),
        'ALE': (0 * _ureg.radian, 'Misalignment tilt'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(s) -> str:
        return f"""
        {super().__str__().rstrip()}
        {s.IC} {s.IL}
        {s.BNORM} {s.XN} {s.YN}
        {s.TITL}
        {s.IX} {s.JY}
        {s.FNAME}
        {s.ID} {s.A} {s.B} {s.C}
        {s.IORDRE}
        {_cm(s.XPAS)}
        {s.KPOS} {_cm(s.XCE)} {_cm(s.YCE)} {_radian(s.ALE)}
        """


class Map2D(_Command):
    """2-D Cartesian uniform mesh field map - arbitrary magnetic field.

    TODO
    """
    KEYWORD = 'MAP2D'
    """Keyword of the command used for the Zgoubi input data."""


class Map2DElectric(_Command):
    """2-D Cartesian uniform mesh field map - arbitrary electric field.

    TODO
    """
    KEYWORD = 'MAP2D-E'
    """Keyword of the command used for the Zgoubi input data."""


class Poisson(_Command):
    """Read magnetic field data from POISSON parent.

    TODO
    """
    KEYWORD = 'POISSON'
    """Keyword of the command used for the Zgoubi input data."""


class PolarMesh(_Command):
    """2-D polar mesh magnetic field map.

    TODO
    """
    KEYWORD = 'POLARMES'
    """Keyword of the command used for the Zgoubi input data."""


class Tosca(_Magnet):
    r"""2-D and 3-D Cartesian mesh field map (MOD<20).

    .. rubric:: Zgoubi manual description

    ``TOSCA`` is dedicated to the reading and treatment of 2-D or 3-D Cartesian or cylindrical mesh field maps as
    delivered by the TOSCA magnet computer code standard parent.

    A pair of flags, MOD, MOD2, determine whether Cartesian or Z-axis cylindrical mesh is used, and the nature of the
    field map data set.

    The total number of field data files to be read is determined by the MOD flag (see below) and by the parameter IZ
    that appears in the data list following the keyword. Each of these files contains the field components
    :math:`B_X`, :math:`B_Y`, :math:`B_Z` on an (X,Y) mesh. IZ=1 for a 2-D map, and in this case :math:`B_X` and
    :math:`B_Y` are assumed zero all over the map.

    For a 3-D map with mid-plane symmetry, described with a set of 2-D maps at various Z, then MOD=0 and IZ ≥ 2, and
    thus, the first data file whose name follows in the data list is supposed to contain the median plane field
    (assuming Z = 0 and :math:`B_X = B_Y = 0`), while the remaining IZ − 1 file(s) contain the IZ − 1 additional planes
    in increasing Z order.

    For arbitrary 3-D maps, no symmetry assumed, then MOD=1 and the total number of maps (whose names follow in the
    data list) is IZ, such that map number [IZ/2] + 1 is the Z = 0 elevation one.

    The field map data file has to be be filled with a format that fits the FORTRAN reading sequence.

    IX (JY , KZ) is the number of longitudinal (transverse horizontal, vertical) nodes of the 3-D uniform mesh.
    For letting zgoubi know that these are binary files, FNAME must begin with ‘B ’ or ‘b ’. In addition to the
    MOD=1, 2 cases above, one can have MOD=12 and in that case a single file contains the all 3-D field map.
    See table below and the FORTRAN subroutine fmapw.f and its entries FMAPR, FMAPR2, for more details, in particular
    the formatting of the field map data file(s).

    The field :math:`\vec{B}` = (BX , BY , BZ ) is normalized by means of BNORM in a similar way as in ``CARTEMES``.
    As well the coordinates X and Y (and Z in the case of a 3-D field map) are normalized by the X-[, Y-, Z-]NORM
    coefficient (useful to convert to centimeters, the working units in zgoubi).

    At each step of the trajectory of a particle inside the map, the field and its derivatives are calculated:

        - In the case of 2-D map, by means of a second or fourth order polynomial interpolation, depending
          on IORDRE (IORDRE = 2, 25 or 4), as for ``CARTEMES``,

        - In the case of 3-D map, by means of a second order polynomial interpolation with a 3 × 3 × 3-point
          parallelepipedic grid, as described in section 1.4.4.

    Entrance and/or exit integration boundaries between which the trajectories are integrated in the field may be
    defined, in the same way as in ``CARTEMES``.

    A 'TITL' (a line of comments) is part of the arguments of the keyword ``TOSCA``. It allows introducing options,
    for instance :

        - Including 'HEADER n' allows specifying the number of header lines (''n' non-data lines) at the top of the
          field map file.

        - Including ‘FLIP’ in TITL causes the field map to be X-flipped,

        - Including ‘ZroBXY’ forces :math:`B_X = B_Y = 0` at all Z=0 nodes of the field map mesh
          (only applies with MOD=15 and MOD =24).

    .. rubric:: Zgoubidoo usage and example

    """
    KEYWORD = 'TOSCA'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IC': (0, 'Print the map.'),
        'IL': (2, 'Print field and coordinates along trajectories.'),
        'BNORM': (1.0, 'Field normalization coefficient.'),
        'XN': (1.0, 'X coordinate normalization coefficient.'),
        'YN': (1.0, 'Y coordinate normalization coefficient.'),
        'ZN': (1.0, 'Z coordinate normalization coefficient.'),
        'TITL': ('FIELDMAP', 'Title.'),
        'IX': (0, 'Number of nodes of the mesh in the X direction.'),
        'IY': (0, 'Number of nodes of the mesh in the Y direction.'),
        'IZ': (1, 'Number of nodes of the mesh in the Z direction.'),
        'MOD': (0, 'Format reading mode.'),
        'MOD2': (0, 'Format reading sub-mode.'),
        'A1': (None, 'Field normalisation factors.'),
        'A2': (None, 'Field normalisation factors.'),
        'A3': (None, 'Field normalisation factors.'),
        'A4': (None, 'Field normalisation factors.'),
        'FILES': (['tosca.table'], 'File names.'),
        'ID': (0, 'Integration boundary.'),
        'A': (1.0,),
        'B': (1.0,),
        'C': (1.0,),
        'IORDRE': (25, 'Degree of interpolation polynomial.'),
        'XPAS': (1.0 * _ureg.cm, 'Integration step.'),
        'KPOS': (2, 'Alignment parameter: 1 (element aligned) or 2 (misaligned) ; If polar mesh : KPOS=2'),
        'COLOR': ('#808080', 'Magnet color for plotting.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
        commands (e.g. fit)."""

    @abstractmethod
    def __str__(self) -> str:
        commands = []
        c = f"""
        {super().__str__().rstrip()}
        {self.IC:d} {self.IL:d}
        {self.BNORM:.12e} {self.XN:.12e} {self.YN:.12e} {self.ZN:.12e}
        {self.TITL}
        {self.IX:d} {self.IY:d} {self.IZ:d} {self.MOD:d}.{self.MOD2:d} {self.A1 or ''} {self.A2 or ''} {self.A3 or ''} {self.A4 or ''}
        """
        commands.append(c)
        commands.append('\n'.join(self.FILES))
        c = f"""
        {self.ID:d} {self.A:.12e} {self.B:.12e} {self.C:.12e}
        {self.IORDRE:d}
        {self.XPAS.m_as('cm'):.12e}
        """
        commands.append(c)

        return ''.join(commands).rstrip()

    def load(self, zgoubi: Optional[_Zgoubi] = None):
        z = zgoubi or _Zgoubi()
        zi = zgoubidoo.Input(f"TOSCA_{self.LABEL1}")
        zi += self

        def cb(f):
            """Post execution callback."""
            if not self.results[0][1].success:
                raise _ZgoubiException(f"Unable to load field map for keyword {self.__class__.__name__}.")
            self._length = self.results[0][1].results.iloc[-1]['LENGTH'] * _ureg.cm

        z(zi, identifier={'TOSCA_LOAD': self.LABEL1}, cb=cb)
        z.wait()
        return self

    @property
    def length(self) -> _Q:
        """

        Returns:

        """
        if self._length is None:
            raise _ZgoubiException("The field map must be loaded (use `.load()`) to determine the optical length.")
        return self._length

    @property
    def optical_ref_length(self) -> _Q:
        return self.length

    def load_map(self, file: str = None) -> _pd.DataFrame:
        # Check if the file is a binary
        if os.path.basename(file).startswith("b_"):  # This is a binary file
            f = FortranFile(file, 'r')
            field = _np.array([])
            while f:
                try:
                    field = _np.append(field, f.read_reals(float))
                except FortranEOFError:
                    break
            fm = _pd.DataFrame(field.reshape(-1, 6),
                               columns=['Y', 'Z', 'X', 'BY', 'BZ', 'BX'])
            # fm = _pd.DataFrame(data=_np.fromfile(file).reshape(-1, 6),
            #                    columns=['Y', 'Z', 'X', 'BY', 'BZ', 'BX'])
        else:
            fm = _pd.read_csv(file, skiprows=int(self.TITL.split(' ')[1]), names=['Y', 'Z', 'X', 'BY', 'BZ', 'BX'],
                              sep=r'\s+')

        return fm

    def plotly(self):
        """

        Returns:

        """
        if self.MOD == 1 and self.IZ >= 3:
            file = self.FILES[int(self.IZ / 2)]
        else:
            file = self.FILES[0]

        fieldmap = self.load_map(file=file)

        #        fieldmap['X'] = fieldmap['X'] + self.length.m_as('cm') / 2
        fieldmap['X'] = fieldmap['X'] + abs(fieldmap['X'].min())
        fieldmap['Z_ABS'] = fieldmap['Z'].apply(_np.abs)
        fieldmap = fieldmap[fieldmap['Z_ABS'] == fieldmap['Z_ABS'].min()]

        rotation_matrix = _np.linalg.inv(self.entry_patched.get_rotation_matrix())
        origin = self.entry_patched.origin

        u = _np.dot(fieldmap[['X', 'Y', 'Z']].values, rotation_matrix)
        fieldmap['XG'] = (u[:, 0] + origin[0].m_as('cm')) / 100
        fieldmap['YG'] = (u[:, 1] + origin[1].m_as('cm')) / 100
        fieldmap['ZG'] = (u[:, 2] + origin[2].m_as('cm')) / 100
        return _go.Histogram2d(
            histfunc='avg',
            nbinsx=100,
            nbinsy=100,
            x=fieldmap['XG'],
            y=fieldmap['YG'],
            z=fieldmap['BZ'],
            zsmooth='best',
            opacity=1.0,
            colorscale='RdYlBu',
        )


class ToscaCartesian(Tosca, _CartesianMagnet):
    PARAMETERS = {
        'XCE': (0.0 * _ureg.cm, 'X shift'),
        'YCE': (0.0 * _ureg.cm, 'Y shift'),
        'ALE': (0.0 * _ureg.radian, 'Tilt'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other
        commands (e.g. fit)."""

    @abstractmethod
    def post_init(self, length=None, **kwargs):
        assert self.MOD < 20, "The value of the variable 'MOD' is incompatible with a cartesian mesh."
        if length is not None:
            self._length = length

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.KPOS:d} {self.XCE.m_as('cm'):.12e} {self.YCE.m_as('cm'):.12e} {self.ALE.m_as('radian'):.12e}
        """

    def process_output(self, output: List[str],
                       parameters: Mapping[str, Union[_Q, float]],
                       zgoubi_input: _Input
                       ) -> bool:
        """

        Args:
            output:
            parameters:
            zgoubi_input:

        Returns:

        """
        length: float = 0.0
        for line in output:
            if line.strip().startswith("Length of element,  XL ="):
                length = float(line.split()[5])
                break
        self._results.append(
            (
                parameters,
                _Action.CommandResult(success=True, results=_pd.DataFrame([{'LENGTH': length}]))
            )
        )
        return True

    def adjust_tracks_variables(self, tracks: _pd.DataFrame):
        super().adjust_tracks_variables(tracks)
        t = tracks[tracks.LABEL1 == self.LABEL1]
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'SREF'] = t['X'] - t['X'].min() + self.entry_s.m_as('m')
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'X'] = t['X'] - t['X'].min()

    @property
    def entry_patched(self) -> Optional[_Frame]:
        """

        Returns:

        """
        if self._entry_patched is None:
            self._entry_patched = self.entry.__class__(self.entry)
            if self.KPOS in (0, 1, 2):
                self._entry_patched.translate_x(self.x_offset)
                self._entry_patched.translate_y(self.y_offset)
                self._entry_patched.rotate_z(-self.rotation)
        return self._entry_patched

    @property
    def exit(self) -> Optional[_Frame]:
        """

        Returns:

        """
        if self._exit is None:
            self._exit = self.entry_patched.__class__(self.entry_patched)
            self._exit.translate_x(self.length)
        return self._exit

    @property
    def exit_patched(self) -> Optional[_Frame]:
        """

        Returns:

        """
        if self._exit_patched is None:
            if self.KPOS is None or self.KPOS == 1:
                self._exit_patched = self.exit.__class__(self.exit)
            elif self.KPOS == 0 or self.KPOS == 2:
                self._exit_patched = self.entry.__class__(self.entry)
                self._exit_patched.translate_x(self.length)
        return self._exit_patched


class ToscaCartesian2D(ToscaCartesian):
    PARAMETERS = {
        'MOD': (0, 'Format reading mode.'),
        'MOD2': (1, 'Format reading sub-mode.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
        commands (e.g. fit)."""

    def post_init(self, infer_and_check_meshes: bool = True, **kwargs):
        assert self.MOD in (0, 1, 3, 15), "The value of the variable 'MOD' is incompatible with a 2D cartesian mesh " \
                                          "with mid-plane antisymmetry assumed."


class ToscaCartesian3D(ToscaCartesian):
    PARAMETERS = {
        'MOD': (12, 'Format reading mode.'),
        'MOD2': (1, 'Format reading sub-mode.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
        commands (e.g. fit)."""

    def post_init(self, infer_and_check_meshes: bool = True, **kwargs):
        assert self.MOD in (1, 12, 15, 16), "The value of the variable 'MOD' is incompatible with a 3D cartesian " \
                                            "mesh with no symmetry assumed."
        if len(self.FILES) > 1 and self.MOD in (1, 12):
            self.MOD = 1
            self.MOD2 = 0
            self.IZ = len(self.FILES)
            if infer_and_check_meshes:
                for f in self.FILES:
                    df = self.load(f)
                    assert df['Z'].nunique() == 1
                    if self.IX != 0:
                        assert self.IX == df['X'].nunique()
                    else:
                        self.IX = df['X'].nunique()
                    if self.IY != 0:
                        assert self.IY == df['Y'].nunique()
                    else:
                        self.IY = df['Y'].nunique()


class ToscaCartesian3DAntisymetric(ToscaCartesian):
    PARAMETERS = {
        'MOD': (12, 'Format reading mode.'),
        'MOD2': (0, 'Format reading sub-mode.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
        commands (e.g. fit)."""

    def post_init(self, **kwargs):
        assert self.MOD in (0, 12), "The value of the variable 'MOD' is incompatible with a 3D cartesian mesh with " \
                                    "no symmetry assumed."


class ToscaPolar(Tosca, _PolarMagnet):
    PARAMETERS = {
        'RM': (0.0 * _ureg.cm, 'Reference radius'),
        'RE': (0.0 * _ureg.cm, 'X shift'),
        'TE': (0.0 * _ureg.radian, 'Y shift'),
        'RS': (0.0 * _ureg.cm, 'Tilt'),
        'TS': (0.0 * _ureg.radian, 'Tilt'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
        commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.KPOS:d}
        {self.RE.m_as('cm'):.12e} {self.TE.m_as('radian'):.12e} {self.RS.m_as('cm'):.12e} {self.TS.m_as('radian'):.12e}
        """

    def process_output(self, output: List[str],
                       parameters: Mapping[str, Union[_Q, float]],
                       zgoubi_input: _Input
                       ) -> bool:
        """

        Args:
            output:
            parameters:
            zgoubi_input:

        Returns:

        """
        radius = 0.0 * _ureg.m
        angle = 0.0 * _ureg.radians
        for line in output:
            if line.strip().startswith("Field map limits, angle :  min, max, max-min (rad) :"):
                angle = float(line.split()[-1]) * _ureg.rad
            if line.strip().startswith("Integration step : "):
                radius = float(line.replace(')', ' ').split()[-1]) * _ureg.cm  # For Zgoubi output
                break
        length = (radius * angle).m_as('cm')
        self._results.append(
            (
                parameters,
                _Action.CommandResult(success=True, results=_pd.DataFrame([{'LENGTH': length}]))
            )
        )
        return True

    def post_init(self, reference_radius: float = 0.0 * _ureg.cm, **kwargs):
        assert self.MOD >= 20, "The value of the variable 'MOD' is incompatible with a polar mesh."

    def adjust_tracks_variables(self, tracks: _pd.DataFrame):
        t = tracks[tracks.LABEL1 == self.LABEL1]
        angles = 100 * t['X'] - 100 * t['X'][0]
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ANGLE'] = angles
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'R'] = t['Y']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'R0'] = t['Yo']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'SREF'] = self.radius.m_as('m') * angles + self.entry_s.m_as('m')
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT'] = t['Y'] - self.radius.m_as('m')
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT0'] = t['Yo'] - self.radius.m_as('m')
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT'] = t['Z']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT0'] = t['Zo']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'X'] = t['Y'] * _np.sin(angles)
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'X0'] = t['Yo'] * _np.sin(angles)
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'Y'] = t['Y'] * _np.cos(angles) - self.radius.m_as('m')
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'Y0'] = t['Yo'] * _np.cos(angles) - self.radius.m_as('m')

    def plotly(self):
        """

        Returns:

        """
        FNAME = self.FILES[0]
        fieldmap = _pd.read_csv(FNAME, skiprows=8, names=['Y', 'Z', 'X', 'BY', 'BZ', 'BX'], sep=r'\s+')

        rotation_matrix = _np.linalg.inv(self.entry_patched.get_rotation_matrix())
        origin = self.entry_patched.origin

        u = _np.dot(fieldmap[['X', 'Y', 'Z']].values, rotation_matrix)
        fieldmap['XG'] = (u[:, 0] + origin[0].m_as('cm')) / 100
        fieldmap['YG'] = (u[:, 1] + origin[1].m_as('cm')) / 100
        fieldmap['ZG'] = (u[:, 2] + origin[2].m_as('cm')) / 100

        return _go.Histogram2d(
            histfunc='avg',
            nbinsx=100,
            nbinsy=100,
            x=fieldmap['XG'],
            y=fieldmap['YG'],
            z=fieldmap['BZ'],
            opacity=1.0,
            colorscale='Jet',
        )


class vFFA(ToscaCartesian3D):
    PARAMETERS = {
        'B0': (0 * _ureg.kilogauss, 'Reference magnetic field'),
        'k': (0 / _ureg.m, 'Field index'),
        'tau': (0.0, 'Tangent of the edge angle'),
        'lmag': (0.0 * _ureg.m, 'Length of the magnet'),
        'gap': (0.0 * _ureg.m, 'Fringe length'),
        'xmin': (0.0 * _ureg.m, 'Horizontal extent of the field map'),
        'xmax': (0.0 * _ureg.m, 'Horizontal extent of the field map'),
        'ymin': (0.0 * _ureg.m, 'Vertical extent of the field map'),
        'ymax': (0.0 * _ureg.m, 'Vertical extent of the field map'),
        'z_ff_1': (0.0 * _ureg.m, 'Additional length before the magnet for the longitudinal extent of the field map'),
        'z_ff_2': (0.0 * _ureg.m, 'Additional length after the magnet for the longitudinal extent of the field map'),
        'n': (0.0, 'Order of the expansion'),
        'IX': (0.0, 'Number of nodes of the mesh - X direction'),
        'IY': (0.0, 'Number of nodes of the mesh - Y direction'),
        'IZ': (0.0, 'Number of nodes of the mesh - Z direction'),
        'path': ('.', '.'),
        'fieldmap': (None, '...')
    }

    def post_init(self, **kwargs):
        if self.fieldmap is None:
            self.vFFA_map = zgoubidoo.fieldmaps.VFFAFieldMap.generate(self.B0, self.k, self.tau, self.lmag,
                                                                      self.gap, self.xmin, self.xmax,
                                                                      self.ymin, self.ymax, self.z_ff_1,
                                                                      self.z_ff_2, self.n, self.IX,
                                                                      self.IY_approx, self.IZ)

            self.vFFA_map.write(path=self.path, filename='tosca.table', binary=True)
            self.FILES = [self.vFFA_map.file]

        else:
            self.vFFA_map = zgoubidoo.fieldmaps.VFFAFieldMap.load(self.fieldmap)
            self.FILES = [self.fieldmap]

        self.TITL = "HEADER 0"
        self.IX = self.vFFA_map.mesh_sampling_x[1]
        self.IY = self.vFFA_map.mesh_sampling_y[1]
        self.IZ = self.vFFA_map.mesh_sampling_z[1]
