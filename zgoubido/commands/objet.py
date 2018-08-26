from .commands import Command


class Objet(Command):
    KEYWORD = 'OBJET'
    PARAMETERS = {
        'BORO': 1.0,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.BORO}
        {s.KOBJ}
        """

    def __init__(self, *params, **kwargs):
        super().__init__(Objet.PARAMETERS, self.PARAMETERS, *params, **kwargs)


class Objet1(Objet):
    pass


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
