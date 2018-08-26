from .commands import Command


class Particul(Command):
    KEYWORD = 'PARTICUL'
    PARAMETERS = {
        'M': 0,
        'Q': 0,
        'G': 0,
        'tau': 0,
        'X': 0,
    }

    def __init__(self, *params, **kwargs):
        super().__init__(Particul.PARAMETERS, self.PARAMETERS, *params, **kwargs)

    def __str__(s):
        return f"""
        '{s.KEYWORD}'
        {s.M} {s.Q} {s.G} {s.tau} {s.X}
        """


class Electron(Particul):
    PARAMETERS = {
        'M': 0.51099892e6,
        'Q': -1.60217653e-19,
        'G': (2.0023193043622 - 2) / 2,
    }


class Positron(Particul):
    PARAMETERS = {
        'M': 0.51099892e6,
        'Q': 1.60217653e-19,
        'G': (2.0023193043622 - 2) / 2,
    }


class Proton(Particul):
    PARAMETERS = {
        'M': 938.27203e6,
        'Q': 1.602176487e-19,
        'G': (5.585694701 - 2) / 2,
    }


class AntiProton(Particul):
    PARAMETERS = {
        'M': 938.27203e6,
        'Q': -1.602176487e-19,
        'G': (5.585694701 - 2) / 2,
    }
