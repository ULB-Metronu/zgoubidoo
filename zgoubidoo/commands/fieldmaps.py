"""Zgoubidoo's interfaces to field map tracking commands.

More details here.
"""
from .commands import Command as _Command
from .. import ureg as _ureg
from ..units import _cm, _radian


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
    """Read magnetic field data from POISSON output.

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


class Tosca(_Command):
    """2-D and 3-D Cartesian or cylindrical mesh field map.

    .. rubric:: Zgoubi manual description

    TOSCA is dedicated to the reading and treatment of 2-D or 3-D Cartesian or cylindrical mesh field maps as delivered
    by the TOSCA magnet computer code standard output.

    A pair of flags, MOD, MOD2, determine whether Cartesian or Z-axis cylindrical mesh is used, and the nature of the
    field map data set.

    The total number of field data files to be read is determined by the MOD flag (see below) and by the parameter IZ
    that appears in the data list following the keyword. Each of these files contains the field components
    BX,BY,BZonan(X,Y)mesh.IZ=1fora2-Dmap,andinthiscaseBXandBY are assumed zero all over the map7.

    For a 3-D map with mid-plane symmetry, described with a set of 2-D maps at various Z, then MOD=0 and IZ ≥ 2, and
    thus, the first data file whose name follows in the data list is supposed to contain the median plane field
    (assuming Z = 0 and BX = BY = 0), while the remaining IZ − 1 file(s) contain the IZ − 1 additional planes in
    increasing Z order.

    For arbitrary 3-D maps, no symmetry assumed, then MOD=1 and the total number of maps (whose names follow in the
    data list) is IZ, such that map number [IZ/2] + 1 is the Z = 0 elevation one.

    The field map data file has to be be filled with a format that fits the FORTRAN reading sequence.

    IX (JY , KZ) is the number of longitudinal (transverse horizontal, vertical) nodes of the 3-D uniform mesh.
    For letting zgoubi know that these are binary files, FNAME must begin with ‘B ’ or ‘b ’. In addition to the
    MOD=1, 2 cases above, one can have MOD=12 and in that case a single file contains the all 3-D field map.
    See table below and the FORTRAN subroutine fmapw.f and its entries FMAPR, FMAPR2, for more details, in particular
    the formatting of the field map data file(s).

    The field B = (BX , BY , BZ ) is normalized by means of BNORM in a similar way as in CARTEMES.
    As well the coordinates X and Y (and Z in the case of a 3-D field map) are normalized by the X-[, Y-, Z-]NORM
    coefficient (useful to convert to centimeters, the working units in zgoubi).

    At each step of the trajectory of a particle inside the map, the field and its derivatives are calculated

        - in the case of 2-D map, by means of a second or fourth order polynomial interpolation, depending
            on IORDRE (IORDRE = 2, 25 or 4), as for CARTEMES,
        - in the case of 3-D map, by means of a second order polynomial interpolation with a 3 × 3 × 3-point
            parallelepipedic grid, as described in section 1.4.4.

    Entrance and/or exit integration boundaries between which the trajectories are integrated in the field may be
    defined, in the same way as in CARTEMES.

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
        'A': (1,),
        'B': (1,),
        'C': (1,),
        'IORDRE': (25, 'Degree of interpolation polynomial.'),
        'XPAS': (1 * _ureg.mm, 'Integration step.'),
        'KPOS': (2, "Alignment parameter"),
        'XCE': (0,),
        'YCE': (0,),
        'ALE': (0,),
        'RE': (0,),
        'TE': (0,),
        'RS': (0,),
        'TS': (0,),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
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
        {s.KPOS:d} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
        """
