from .commands import Command


class Particule(Command):
    KEYWORD = 'PARTICUL'
    PARAMETERS = {
        'M': 0,
        'Q': 0,
        'G': 0,
        'tau': 0,
        'X': 0,
    }

    def __init__(self, name='', *params, **kwargs):
        super().__init__(name, Particule.PARAMETERS, self.PARAMETERS, *params, **kwargs)

    def __str__(s):
        return f"""
        {super().__str__()}
        {s.M} {s.Q} {s.G} {s.tau} {s.X}
        """


class Electron(Particule):
    PARAMETERS = {
        'M': 0.51099892,
        'Q': -1.60217653e-19,
        'G': (-2.0023193043622 - 2) / 2,
    }


class Positron(Particule):
    PARAMETERS = {
        'M': 0.51099892,
        'Q': 1.60217653e-19,
        'G': (-2.0023193043622 - 2) / 2,
    }


class Muon(Particule):
    PARAMETERS = {
        'M': 105.6583745,
        'Q': -1.60217653e-19,
        'G': (-2.0023318418 - 2) / 2,
        'tau': 2.197029e-6,
    }


class AntiMuon(Particule):
    PARAMETERS = {
        'M': 105.6583745,
        'Q': 1.60217653e-19,
        'G': (-2.0023318418 - 2) / 2,
        'tau': 2.197029e-6,
    }


class Proton(Particule):
    PARAMETERS = {
        'M': 938.27203,
        'Q': 1.602176487e-19,
        'G': (5.585694701 - 2) / 2,
    }


class AntiProton(Particule):
    PARAMETERS = {
        'M': 938.27203,
        'Q': -1.602176487e-19,
        'G': (5.585694701 - 2) / 2,
    }
