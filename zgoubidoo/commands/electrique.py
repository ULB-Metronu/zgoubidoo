"""Zgoubidoo's interfaces to purefly electric Zgoubi commands.

More details here.
"""
from .. import ureg as _ureg
from .commands import Command as _Command
from .plotable import Plotable as _Plotable
from .patchable import Patchable as _Patchable
from ..vis.zgoubiplot import ZgoubiPlot as _ZgoubiPlot


class Cavite(_Command, _Patchable, _Plotable):
    """Accelerating cavity."""
    KEYWORD = 'CAVITE'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IOPT': (0, ""),
        'FREQ': (0.0 * _ureg.Hz, ""),
        'V': (0.0 * _ureg.volt, ""),
        'PHI_S': (0.0 * _ureg.radian, ""),
        'COLOR': 'yellow',
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
        commands (e.g. fit)."""

    def __str__(s):
        return f"""
            {super().__str__().rstrip()}
            {int(s.IOPT):d}.1
            0.0 {s.FREQ.to('Hz').magnitude:.12e}
            {s.V.m_as('volt'):.12e} {s.PHI_S.m_as('radian'):.12e}
            """

    def plot_cartouche(self, s_location, artist: _ZgoubiPlot):
        """

        Args:
            s_location:
            artist:

        Returns:

        """
        getattr(artist,
                f"cartouche_{self.__class__.__name__.lower()}"
                )(s_location, self)


# Alias
Cavity = Cavite


class EBMult(_Command):
    """Electro-magnetic multipole."""
    KEYWORD = 'EBMULT'
    """Keyword of the command used for the Zgoubi input data."""


# Aliases
EBMultipole = EBMult


class EL2Tub(_Command):
    """Two-tube electrostatic lens."""
    KEYWORD = 'EL2TUB'
    """Keyword of the command used for the Zgoubi input data."""


class ELMir(_Command):
    """Electrostatic N-electrode mirror/lens,straight slits."""
    KEYWORD = 'ELMIR'
    """Keyword of the command used for the Zgoubi input data."""


class ELMirCircular(_Command):
    """Electrostatic N-electrode mirror/lens, circular slits."""
    KEYWORD = 'ELMIRC'
    """Keyword of the command used for the Zgoubi input data."""


class ELMulti(_Command):
    """Electric multipole."""
    KEYWORD = 'ELMULT'
    """Keyword of the command used for the Zgoubi input data."""


class ELRevol(_Command):
    """1-D uniform mesh electric field map."""
    KEYWORD = 'ELREVOL'
    """Keyword of the command used for the Zgoubi input data."""


class Unipot(_Command):
    """Unipotential cylindrical electrostatic lens."""
    KEYWORD = 'UNIPOT'
    """Keyword of the command used for the Zgoubi input data."""
