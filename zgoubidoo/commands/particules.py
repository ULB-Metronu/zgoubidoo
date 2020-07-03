"""Zgoubidoo's interfaces to Zgoubi commands related to particle types.

More details here. TODO
"""
import scipy.constants
from .commands import Command as _Command
from .commands import CommandType as _MetaCommand
from .. import ureg as _ureg


class ParticuleType(_MetaCommand):
    """
    TODO
    """
    def __str__(cls):
        return f"""
        '{cls.KEYWORD}' {cls.__name__.upper()}
        {cls.M.to('MeV_c2').magnitude:.12e} {cls.Q.to('coulomb').magnitude:.12e} {cls.G:.12e} {cls.tau:.12e} 0.0
        """


class Particule(_Command, metaclass=ParticuleType):
    """Particle characteristics."""
    KEYWORD = 'PARTICUL'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'M': (0 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (0 * _ureg.coulomb, 'Charge of the particle.'),
        'G': (0, 'Factor'),
        'tau': (0, 'Lifetime of the particle.'),
    }

    def __init__(self, label1='', label2='', *params, **kwargs):
        if len(label1) == 0:
            label1 = self.__class__.__name__.upper()
        super().__init__(label1, label2, Particule.PARAMETERS, self.PARAMETERS, *params, **kwargs)

    def __str__(self) -> str:
        return f"""
        {super().__str__().strip()}
        {self.M.m_as('MeV_c2'):.12e} {self.Q.m_as('coulomb'):.12e} {self.G:.12e} {self.tau:.12e} 0.0
        """

    @property
    def mass(self):
        """Mass of the particle."""
        return self.M

    @property
    def charge(self):
        """Charge of the particle."""
        return self.Q

    @property
    def lifetime(self):
        """Lifetime constant of the particle."""
        return self.tau

    @property
    def gyro(self):
        """Gyromagnetic factor of the particle."""
        return self.G


class NativeParticuleType(ParticuleType):
    """
    TODO
    """
    def __str__(cls):
        if cls.NATIVE:
            return f"""
        '{cls.KEYWORD}' {cls.__name__.upper()}
        {cls.__name__.upper()}
            """
        else:
            return super().__str__()


class NativeParticule(Particule, metaclass=NativeParticuleType):
    """
    TODO
    """
    PARAMETERS = {
        'NATIVE': (True, ''),
    }

    def __str__(self) -> str:
        if self.NATIVE:
            return f"""
        {_Command.__str__(self).strip()}
        {self.__class__.__name__.upper()}
            """
        else:
            return super().__str__()


class Electron(NativeParticule):
    """An electron particle."""
    PARAMETERS = {
        'M': (scipy.constants.electron_mass * _ureg.kg, 'Mass of the particle.'),
        'Q': (-scipy.constants.elementary_charge * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((scipy.constants.physical_constants['electron g factor'][0] - 2) / 2, 'G factor'),
    }


class Positron(NativeParticule):
    """A positron particle."""
    PARAMETERS = {
        'M': (scipy.constants.electron_mass * _ureg.kg, 'Mass of the particle.'),
        'Q': (scipy.constants.elementary_charge * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((scipy.constants.physical_constants['electron g factor'][0] - 2) / 2, 'G factor'),
    }


class Muon(Particule):
    """A muon particle."""
    PARAMETERS = {
        'M': (scipy.constants.physical_constants['muon mass'][0] * _ureg(scipy.constants.physical_constants['muon mass'][1]), 'Mass of the particle.'),
        'Q': (-scipy.constants.elementary_charge * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((scipy.constants.physical_constants['muon g factor'][0] - 2) / 2, 'G factor'),
        'tau': (2.197029e-6 * _ureg.s, 'Lifetime'),
    }


class AntiMuon(Particule):
    """An anti-muon particle."""
    PARAMETERS = {
        'M': (scipy.constants.physical_constants['muon mass'][0] * _ureg.kg, 'Mass of the particle.'),
        'Q': (scipy.constants.elementary_charge * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((scipy.constants.physical_constants['muon g factor'][0] - 2) / 2, 'G factor'),
        'tau': (2.197029e-6 * _ureg.s, 'Lifetime'),
    }


class ImmortalMuon(Muon):
    """A muon particle (no decay)."""
    PARAMETERS = {
        'tau': (0.0 * _ureg.s, 'Half-life of the particle.'),
    }


class ImmortalAntiMuon(AntiMuon):
    """An anti-muon particle (no decay)."""
    PARAMETERS = {
        'tau': (0.0 * _ureg.s, 'Half-life of the particle.'),
    }


class Pion(Particule):
    """A pion particle."""
    PARAMETERS = {
        'M': (139.57018 * _ureg.MeV_c2, 'Mass of the particle.'),
        'tau': (2.6033e-8 * _ureg.s, 'Half-life of the particle.'),
    }


class PositivePion(Pion):
    """A pion particle."""
    PARAMETERS = {
        'Q': (scipy.constants.elementary_charge * _ureg.coulomb, 'Charge of the particle.'),
    }


class NegativePion(Pion):
    """A pion particle."""
    PARAMETERS = {
        'Q': (-scipy.constants.elementary_charge * _ureg.coulomb, 'Charge of the particle.'),
    }


class Proton(NativeParticule):
    """A proton particle."""
    PARAMETERS = {
        'M': (scipy.constants.proton_mass * _ureg.kg, 'Mass of the particle.'),
        'Q': (scipy.constants.elementary_charge * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((scipy.constants.physical_constants['proton g factor'][0] - 2) / 2, ),
    }


class AntiProton(Particule):
    """An anti-proton particle."""
    PARAMETERS = {
        'M': (scipy.constants.proton_mass * _ureg.kg, 'Mass of the particle.'),
        'Q': (-scipy.constants.elementary_charge * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((scipy.constants.physical_constants['proton g factor'][0] - 2) / 2, 'G factor'),
    }


class HMinus(Particule):
    """An H- ion."""
    PARAMETERS = {
        'M': (scipy.constants.proton_mass * _ureg.kg, 'Mass of the particle.'),
        'Q': (-scipy.constants.elementary_charge * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((scipy.constants.physical_constants['proton g factor'][0] - 2) / 2, 'G factor'),
    }


class Ion(Particule):
    """Base class for ion particles."""
    pass


class HeliumIon(Ion):
    """A fully stripped Helium ion"""
    PARAMETERS = {
        'M': (scipy.constants.physical_constants['helion mass'][0]*_ureg.kg, 'Mass of the particle'),
        'Q': (2 * scipy.constants.elementary_charge * _ureg.coulomb, 'Charge of the particle'),
        'G': (scipy.constants.physical_constants['helion g factor'][0], 'G factor'),
    }


Helion = HeliumIon


class CarbonIon(Ion):
    """A fully stripped Carbon ion"""
    PARAMETERS = {
        'M': (1, ''),
        'Q': (1, ''),
        'G': (1, ''),
    }


class OxygenIon(Ion):
    """A fully stripped Oxygen ion"""
    PARAMETERS = {
        'M': (1, ''),
        'Q': (1, ''),
        'G': (1, ''),
    }


class LeadIon(Ion):
    """A fully stripped Lead ion"""
    PARAMETERS = {
        'M': (1, ''),
        'Q': (1, ''),
        'G': (1, ''),
    }


class SulfurIon(Ion):
    """A fully stripped Sulfur ion"""
    PARAMETERS = {
        'M': (1, ''),
        'Q': (1, ''),
        'G': (1, ''),
    }


class XenonIon(Ion):
    """A fully stripped Sulfur ion"""
    PARAMETERS = {
        'M': (1, ''),
        'Q': (1, ''),
        'G': (1, ''),
    }

