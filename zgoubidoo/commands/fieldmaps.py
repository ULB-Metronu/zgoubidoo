from .commands import Command as _Command
from .. import ureg as _ureg
from ..units import _cm, _radian


class Brevol(_Command):
    """1-D uniform mesh magnetic field map."""


class CartesianMesh(_Command):
    """"2-D Cartesian uniform mesh magnetic field map."""
    KEYWORD = 'CARTEMES'
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
    """2-D Cartesian uniform mesh field map - arbitrary magnetic field."""


class Map2DElectric(_Command):
    """2-D Cartesian uniform mesh field map - arbitrary electric field."""
    KEYWORD = 'MAP2D-E'


class Poisson(_Command):
    """Read magnetic field data from POISSON output."""


class PolarMesh(_Command):
    """2-D polar mesh magnetic field map."""
    KEYWORD = 'POLARMES'


class Tosca(_Command):
    """2-D and 3-D Cartesian or cylindrical mesh field map."""
    PARAMETERS = {
        'IC': (),
        'IL': (),
        'BNORM': (),
        'XN': (),
        'YN': (),
        'ZN': (),
        'TITL': (),
        'IX': (),
        'IY': (),
        'IZ': (),
        'MOD': (),
        'MOD2': (),
        'FNAME': (),
        'ID': (),
        'A': (),
        'B': (),
        'C': (),
        'IORDRE': (),
        'XPAS': (),
        'KPOS': (),
        'XCE': (),
        'YCE': (),
        'ALE': (),
        'RE': (),
        'TE': (),
        'RS': (),
        'TS': (),
    }

    def __str__(self) -> str:
        pass
