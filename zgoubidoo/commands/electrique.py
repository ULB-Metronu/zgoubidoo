"""Zgoubidoo's interfaces to purefly electric Zgoubi commands.

More details here.
"""
from .commands import Command as _Command


class Cavite(_Command):
    """Accelerating cavity."""


# Alias
Cavity = Cavite


class EBMult(_Command):
    """Electro-magnetic multipole."""
    KEYWORD = 'EBMULT'


# Aliases
EBMultipole = EBMult


class EL2Tub(_Command):
    """Two-tube electrostatic lens."""
    KEYWORD = 'EL2TUB'


class ELMir(_Command):
    """Electrostatic N-electrode mirror/lens,straight slits."""
    KEYWORD = 'ELMIR'


class ELMirCircular(_Command):
    """Electrostatic N-electrode mirror/lens, circular slits."""
    KEYWORD = 'ELMIRC'


class ELMulti(_Command):
    """Electric multipole."""
    KEYWORD = 'ELMULT'


class ELRevol(_Command):
    """1-D uniform mesh electric field map."""


class Unipot(_Command):
    """Unipotential cylindrical electrostatic lens."""
