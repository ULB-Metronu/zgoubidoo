"""Zgoubidoo's interfaces to field map tracking commands.

More details here.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Mapping, Union
import numpy as _np
import pandas as _pd
from .commands import Command as _Command
from .actions import Action as _Action
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
    """Parameters of the command, with their default value, their description and optinally an index used by other 
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


class Tosca(_CartesianMagnet):
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
        'IC': (2, 'Print the map.'),
        'IL': (2, 'Print field and coordinates along trajectories.'),
        'BNORM': (1.0, 'Field normalization coefficient.'),
        'XN': (1.0, 'X coordinate normalization coefficient.'),
        'YN': (1.0, 'Y coordinate normalization coefficient.'),
        'ZN': (1.0, 'Z coordinate normalization coefficient.'),
        'TITL': ('FIELDMAP', 'Title.'),
        'IX': (1, 'Number of nodes of the mesh in the X direction.'),
        'IY': (1, 'Number of nodes of the mesh in the Y direction.'),
        'IZ': (1, 'Number of nodes of the mesh in the Z direction.'),
        'MOD': (0, 'Format reading mode.'),
        'MOD2': (0, 'Format reading sub-mode.'),
        'FNAME': ('TOSCA', 'File names.'),
        'ID': (0, 'Integration boundary.'),
        'A': (1.0,),
        'B': (1.0,),
        'C': (1.0,),
        'IORDRE': (25, 'Degree of interpolation polynomial.'),
        'XPAS': (1.0 * _ureg.mm, 'Integration step.'),
        'KPOS': (2, 'Alignment parameter: 1 (element aligned) or 2 (misaligned) ; If polar mesh : KPOS=2'),
        'XCE': (0.0 * _ureg.cm, 'X shift'),
        'YCE': (0.0 * _ureg.cm, 'Y shift'),
        'ALE': (0.0 * _ureg.radian, 'Tilt'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
        commands (e.g. fit)."""

    def __str__(s) -> str:
        return f"""
        {super().__str__().rstrip()}
        {s.IC:d} {s.IL:d}
        {s.BNORM:.12e} {s.XN:.12e} {s.YN:.12e} {s.ZN:.12e}
        {s.TITL}
        {s.IX:d} {s.IY:d} {s.IZ:d} {s.MOD:d}.{s.MOD2:d}
        {s.FNAME}
        {s.ID:d} {s.A:.12e} {s.B:.12e} {s.C:.12e}
        {s.IORDRE:d}
        {_cm(s.XPAS):.12e}
        {s.KPOS:d} {s.XCE.m_as('cm'):.12e} {s.YCE.m_as('cm'):.12e} {s.ALE.m_as('radian'):.12e}
        """

    def adjust_tracks_variables(self, tracks: _pd.DataFrame):
        super().adjust_tracks_variables(tracks)
        t = tracks[tracks.LABEL1 == self.LABEL1]
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'SREF'] = t['X'] - t['X'].min() + self.entry_s.m_as('m')
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'X'] = t['X'] - t['X'].min()

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

    def plotly(self):
        """

        Returns:

        """
        if self.MOD == 1 and self.IZ >= 3:
            fname = self.FNAME.split('\n')[int(self.IZ/2)].strip(' ')
        else:
            fname = self.FNAME

        fieldmap = _pd.read_csv(fname, skiprows=8, names=['Y', 'Z', 'X', 'BY', 'BZ', 'BX'], sep=r'\s+')
#        fieldmap['X'] = fieldmap['X'] + self.length.m_as('cm') / 2
        fieldmap['X'] = fieldmap['X'] + abs(fieldmap['X'].min())
        fieldmap['Z_ABS'] = fieldmap['Z'].apply(_np.abs)
        fieldmap = fieldmap[fieldmap['Z'] == fieldmap['Z_ABS'].min()]

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
            colorscale='Greys',
        )

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
        return self._length

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
                self._entry_patched.translate_x(self.x_offset)
                self._entry_patched.translate_y(self.y_offset)
                self._entry_patched.rotate_z(self.rotation)
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


class ToscaPolar(_PolarMagnet):
    r"""2-D and 3-D Cylindrical mesh field map (MOD>=20).

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
        'RM': (0 * _ureg.cm, ''),
        'IC': (2, 'Print the map.'),
        'IL': (2, 'Print field and coordinates along trajectories.'),
        'BNORM': (1.0, 'Field normalization coefficient.'),
        'XN': (1.0, 'X coordinate normalization coefficient.'),
        'YN': (1.0, 'Y coordinate normalization coefficient.'),
        'ZN': (1.0, 'Z coordinate normalization coefficient.'),
        'TITL': ('FIELDMAP', 'Title.'),
        'IX': (1, 'Number of nodes of the mesh in the X direction.'),
        'IY': (1, 'Number of nodes of the mesh in the Y direction.'),
        'IZ': (1, 'Number of nodes of the mesh in the Z direction.'),
        'MOD': (0, 'Format reading mode.'),
        'MOD2': (0, 'Format reading sub-mode.'),
        'FNAME': ('TOSCA', 'File names.'),
        'ID': (0, 'Integration boundary.'),
        'A': (1.0,),
        'B': (1.0,),
        'C': (1.0,),
        'IORDRE': (25, 'Degree of interpolation polynomial.'),
        'XPAS': (1.0 * _ureg.mm, 'Integration step.'),
        'KPOS': (2, 'Positioning of the map, normally 2 for polar mesh'),
        'RE': (0.0 * _ureg.cm, 'Reference radius at entrance of the map'),
        'TE': (0.0 * _ureg.radian, 'Reference angle at entrance of the map'),
        'RS': (0.0 * _ureg.cm, 'Reference radius at exit of the map'),
        'TS': (0.0 * _ureg.radian, 'Reference angle at exit of the map'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
        commands (e.g. fit)."""

    def __str__(s) -> str:
        return f"""
        {super().__str__().rstrip()}
        {s.IC:d} {s.IL:d}
        {s.BNORM:.12e} {s.XN:.12e} {s.YN:.12e} {s.ZN:.12e}
        {s.TITL}
        {s.IX:d} {s.IY:d} {s.IZ:d} {s.MOD:d}.{s.MOD2:d}
        {s.FNAME}
        {s.ID:d} {s.A:.12e} {s.B:.12e} {s.C:.12e}
        {s.IORDRE:d}
        {_cm(s.XPAS):.12e}
        {s.KPOS:d} 
        {s.RE.m_as('cm'):.12e} {s.TE.m_as('radian'):.12e} {s.RS.m_as('cm'):.12e} {s.TS.m_as('radian'):.12e}
        """

    def adjust_tracks_variables(self, tracks: _pd.DataFrame):
        t = tracks[tracks.LABEL1 == self.LABEL1]
        radius = self.RM.m_as('m')
        angles = 100 * t['X'] - 100 * t['X'][0]
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ANGLE'] = angles
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'R'] = t['Y']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'R0'] = t['Yo']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'SREF'] = radius * angles + self.entry_s.m_as('m')
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT'] = t['Y'] - radius
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT0'] = t['Yo'] - radius
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT'] = t['Z']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT0'] = t['Zo']
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'X'] = t['Y'] * _np.sin(angles)
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'X0'] = t['Yo'] * _np.sin(angles)
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'Y'] = t['Y'] * _np.cos(angles) - radius
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'Y0'] = t['Yo'] * _np.cos(angles) - radius

    def plotly(self):
        """

        Returns:

        """
        fieldmap = _pd.read_csv(self.FNAME, skiprows=8, names=['Y', 'Z', 'X', 'BY', 'BZ', 'BX'], sep=r'\s+')

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


