"""Zgoubidoo's interfaces to purefly electric Zgoubi commands.

More details here.
"""
from .. import ureg as _ureg
from .commands import Command as _Command
from .plotable import Plotable as _Plotable
from .patchable import Patchable as _Patchable


class Cavite(_Command, _Patchable, _Plotable):
    """Accelerating cavity."""
    KEYWORD = 'CAVITE'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IOPT': (0, "Model."),
        'FREQ': (0.0 * _ureg.Hz, "RF frequency"),
        'V': (0.0 * _ureg.volt, "RF voltage"),
        'PHI_S': (0.0 * _ureg.radian, "Phase"),
        'XL': (0.0 * _ureg.cm, "Cavity length"),
        'CHAMBERS': ('+1', "Use Chambers' model."),
        'COLOR': 'yellow',
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
        commands (e.g. fit)."""

    def __str__(s):
        return f"""
            {super().__str__().rstrip()}
            {int(s.IOPT):d}   PRINT
            {s.XL.m_as('m'):.12e} {s.FREQ.to('Hz').magnitude:.12e}
            {s.V.m_as('volt'):.12e} {s.PHI_S.m_as('radian'):.12e} {s.CHAMBERS}
            """


# Alias
Cavity = Cavite


class EBMult(_Command):
    """Electro-magnetic multipole."""
    KEYWORD = 'EBMULT'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (0, ""),
        'XL': (),
        'R0': (),
        'E1': (),
        'E2': (),
        'E3': (),
        'E4': (),
        'E5': (),
        'E6': (),
        'E7': (),
        'E8': (),
        'E9': (),
        'E10': (),
    }


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
