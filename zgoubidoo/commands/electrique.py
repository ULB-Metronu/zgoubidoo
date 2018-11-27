"""Zgoubidoo's interfaces to purefly electric Zgoubi commands.

More details here.
"""
from .commands import Command as _Command


class Cavite(_Command):
    """Accelerating cavity."""
    KEYWORD = 'CAVITE'
    """Keyword of the command used for the Zgoubi input data."""


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
