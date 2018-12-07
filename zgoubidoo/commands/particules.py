"""Zgoubidoo's interfaces to Zgoubi commands related to particle types.

More details here.
"""
from .commands import Command as _Command
from .. import ureg as _ureg


class Particule(_Command):
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
        if issubclass(self.__class__, Particule) and len(label1) == 0:
            label1 = self.__class__.__name__.upper()
        super().__init__(label1, label2, Particule.PARAMETERS, self.PARAMETERS, *params, **kwargs)

    def __str__(s) -> str:
        return f"""
        {super().__str__().strip()}
        {s.M.to('MeV_c2').magnitude:.12e} {s.Q.to('coulomb').magnitude:.12e} {s.G:.12e} {s.tau:.12e} 0.0
        """

    @property
    def mass(self):
        return self.M

    @property
    def charge(self):
        return self.Q

    @property
    def lifetime(self):
        return self.tau


class Electron(Particule):
    """An electron particle."""
    PARAMETERS = {
        'M': (0.51099892 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (-1.60217653e-19 * _ureg.coulomb, 'Charge of the particle.'),
        'G': (-2.0023193043622 - 2) / 2,
    }


class Positron(Particule):
    """A positron particle."""
    PARAMETERS = {
        'M': (0.51099892 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (1.60217653e-19 * _ureg.coulomb, 'Charge of the particle.'),
        'G': (-2.0023193043622 - 2) / 2,
    }


class Muon(Particule):
    """A muon particle."""
    PARAMETERS = {
        'M': (105.6583745 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (-1.60217653e-1 * _ureg.coulomb, 'Charge of the particle.'),
        'G': (-2.0023318418 - 2) / 2,
        'tau': 2.197029e-6,
    }


class AntiMuon(Particule):
    """An anti-muon particle."""
    PARAMETERS = {
        'M': (105.6583745 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (1.60217653e-19 * _ureg.coulomb, 'Charge of the particle.'),
        'G': (-2.0023318418 - 2) / 2,
        'tau': 2.197029e-6,
    }


class ImmortalMuon(AntiMuon):
    """A muon particle (no decay)."""
    PARAMETERS = dict(AntiMuon.PARAMETERS, **{
        'tau': (0.0, 'Half-life of the particle.'),
    })


class ImmortalAntiMuon(Muon):
    """An anti-muon particle (no decay)."""
    PARAMETERS = dict(Muon.PARAMETERS, **{
        'tau': (0.0, 'Half-life of the particle.'),
    })


class Pion(Particule):
    """A pion particle."""
    PARAMETERS = {
        'M': (139.57018 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (1.60217653e-19 * _ureg.coulomb, 'Charge of the particle.'),
        'G': 0,
        'tau': (2.6033e-8, 'Half-life of the particle.'),
    }


class Proton(Particule):
    """A proton particle."""
    PARAMETERS = {
        'M': (938.27203 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (1.602176487e-19 * _ureg.coulomb, 'Charge of the particle.'),
        'G': (5.585694701 - 2) / 2,
    }


class AntiProton(Particule):
    """An anti-proton particle."""
    PARAMETERS = {
        'M': (938.27203 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (-1.602176487e-19 * _ureg.coulomb, 'Charge of the particle.'),
        'G': (5.585694701 - 2) / 2,
    }


class HeliumIon(Particule):
    """A fully stripped Helium ion"""
    PARAMETERS = {
        'M': 1,
        'Q': 1,
        'G': 1,
    }


class CarbonIon(Particule):
    """A fully stripped Carbon ion"""
    PARAMETERS = {
        'M': 1,
        'Q': 1,
        'G': 1,
    }


class LeadIon(Particule):
    """A fully stripped Lead ion"""
    PARAMETERS = {
        'M': 1,
        'Q': 1,
        'G': 1,
    }


class SulfurIon(Particule):
    """A fully stripped Sulfur ion"""
    PARAMETERS = {
        'M': 1,
        'Q': 1,
        'G': 1,
    }
