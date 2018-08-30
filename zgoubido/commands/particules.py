from .commands import Command


class Particule(Command):
    """Particle characteristics."""
    KEYWORD = 'PARTICUL'
    PARAMETERS = {
        'M': 0,
        'Q': 0,
        'G': 0,
        'tau': 0,
    }

    def __init__(self, label1='', label2='', *params, **kwargs):
        super().__init__(label1, label2, Particule.PARAMETERS, self.PARAMETERS, *params, **kwargs)

    def __str__(s):
        return f"""
        {super().__str__().strip()}
        {s.M:.12e} {s.Q:.12e} {s.G:.12e} {s.tau:.12e} 0.0
        """


class Electron(Particule):
    """An electron particle."""
    PARAMETERS = {
        'M': 0.51099892,
        'Q': -1.60217653e-19,
        'G': (-2.0023193043622 - 2) / 2,
    }


class Positron(Particule):
    """A positron particle."""
    PARAMETERS = {
        'M': 0.51099892,
        'Q': 1.60217653e-19,
        'G': (-2.0023193043622 - 2) / 2,
    }


class Muon(Particule):
    """A muon particle."""
    PARAMETERS = {
        'M': 105.6583745,
        'Q': -1.60217653e-19,
        'G': (-2.0023318418 - 2) / 2,
        'tau': 2.197029e-6,
    }


class AntiMuon(Particule):
    """An anti-muon particle."""
    PARAMETERS = {
        'M': 105.6583745,
        'Q': 1.60217653e-19,
        'G': (-2.0023318418 - 2) / 2,
        'tau': 2.197029e-6,
    }


class ImmortalMuon(AntiMuon):
    """A muon particle (no decay)."""
    PARAMETERS = dict(AntiMuon.PARAMETERS, **{
        'tau': 0.0,
    })


class ImmortalAntiMuon(Muon):
    """An anti-muon particle (no decay)."""
    PARAMETERS = dict(Muon.PARAMETERS, **{
        'tau': 0.0,
    })


class Pion(Particule):
    """A pion particle."""
    PARAMETERS = {
        'M': 139.57018,
        'Q': 1.60217653e-19,
        'G': 0,
        'tau': 2.6033e-8,
    }


class Proton(Particule):
    """A proton particle."""
    PARAMETERS = {
        'M': 938.27203,
        'Q': 1.602176487e-19,
        'G': (5.585694701 - 2) / 2,
    }


class AntiProton(Particule):
    """An anti-proton particle."""
    PARAMETERS = {
        'M': 938.27203,
        'Q': -1.602176487e-19,
        'G': (5.585694701 - 2) / 2,
    }
