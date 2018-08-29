from .commands import Command


class Objet(Command):
    """Generation of an object."""
    KEYWORD = 'OBJET'

    PARAMETERS = {
        'BORO': 1.0,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.BORO:.12e}
        {s.KOBJ}
        """

    def __init__(self, label1='', label2='', *params, **kwargs):
        super().__init__(label1, label2, Objet.PARAMETERS, self.PARAMETERS, *params, **kwargs)


class Objet1(Objet):
    PARAMETERS = {
        'KOBJ': 1,
        'IY': 1,
        'IT': 1,
        'IZ': 1,
        'IP': 1,
        'IX': 1,
        'ID': 1,
        'PY': 0.1,
        'PT': 1.0,
        'PZ': 0.1,
        'PP': 1.0,
        'PX': 0.1,
        'PD': 0.1,
        'YR': 0.0,
        'TR': 0.0,
        'ZR': 0.0,
        'PR': 0.0,
        'XR': 0.0,
        'DR': 1.0,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IY} {s.IT} {s.IZ} {s.IP} {s.IX} {s.ID}
        {s.PY} {s.PT} {s.PZ} {s.PP} {s.PX} {s.PD}
        {s.YR} {s.TR} {s.ZR} {s.PR} {s.XR} {s.DR}
        """


class Objet2(Objet):
    PARAMETERS = {
        'KOBJ': 2,
        'IMAX': 1,
        'IDMAX': 1,
        'Y': [0.0],
        'T': [0.0],
        'Z': [0.0],
        'P': [0.0],
        'X': [0.0],
        'D': [0.0],
        'LET': 1.0,
        'IEX': 1,
    }

    def __str__(s):
        c = f"""
        {super().__str__().rstrip()}
        {s.IMAX} {s.IDMAX}
        """
        for p in zip(s.Y, s.T, s.Z, s.P, s.X, s.D):
            c += f"{p[0]} {p[1]} {p[2]} {p[3]} {p[4]} {p[5]}"
        c += f"{s.IEX}\n"
        return c


class Objet3(Objet):
    pass


class Objet4(Objet):
    pass


class Objet5(Objet):
    pass


class Objet6(Objet):
    pass


class Objet7(Objet):
    pass


class Objet8(Objet):
    pass


class ObjetA(Command):
    """Object from Monte-Carlo simulation of decay reaction."""
    KEYWORD = 'OBJETA'
