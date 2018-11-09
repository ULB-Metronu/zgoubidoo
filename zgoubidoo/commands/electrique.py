"""Zgoubidoo's interfaces to purefly electric Zgoubi commands.

More details here.
"""
from .commands import Command


class Cavite(Command):
    """Accelerating cavity."""
    KEYWORD = 'CAVITE'


# Alias
Cavity = Cavite


class EBMult(Command):
    """Electro-magnetic multipole."""
    KEYWORD = 'EBMULT'


# Aliases
EBMultipole = EBMult


class EL2Tub(Command):
    """Two-tube electrostatic lens."""
    KEYWORD = 'EL2TUB'


class ELMir(Command):
    """Electrostatic N-electrode mirror/lens,straight slits."""
    KEYWORD = 'ELMIR'


class ELMirCircular(Command):
    """Electrostatic N-electrode mirror/lens, circular slits."""
    KEYWORD = 'ELMIRC'


class ELMulti(Command):
    """Electric multipole."""
    KEYWORD = 'ELMULT'


class ELRevol(Command):
    """1-D uniform mesh electric field map."""
    KEYWORD = 'ELREVOL'


class Unipot(Command):
    """Unipotential cylindrical electrostatic lens."""
    KEYWORD = 'UNIPOT'
