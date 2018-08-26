class Command:
    PARAMETERS = {
        'VALID': True,
        'LABEL2': '',
    }

    def __init__(self, *params, **kwargs):
        name = params[0] if (len(params) > 0 and isinstance(params[0], str)) else ''
        self._attributes = {
            'LABEL1': name,
        }
        for p in (Command.PARAMETERS, self.PARAMETERS,) + (
        params[1] if (len(params) > 1 and isinstance(params[0], str)) else params):
            self._attributes = dict(self._attributes, **p)
        self._attributes = dict(self._attributes, **kwargs)

    def __getattr__(self, a):
        return self._attributes[a]

    def __setattr__(self, a, v):
        if a == '_attributes':
            self.__dict__[a] = v
        else:
            self._attributes[a] = v

    def __repr__(s):
        return str(s)

    def __str__(s):
        return f"""
        '{s.KEYWORD}' {s.LABEL1} {s.LABEL2}
        """


class Faiscnl(Command):
    KEYWORD = 'FAISCNL'
    PARAMETERS = {
        'FNAME': 'zgoubi.fai',
        'B_FNAME': 'b_zgoubi.fai',
        'binary': False,
    }

    def __str__(s):
        return f"""
        '{s.KEYWORD}' {s.LABEL1} {s.LABEL2}
        {s.B_FNAME if s.binary else s.FNAME}
        """


class End(Command):
    KEYWORD = 'END'


class Rebelote(Command):
    KEYWORD = 'REBELOTE'
    PARAMETERS = {
        'NPASS': 1,
        'KWRIT': 0.0,
        'K': 99,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.NPASS} {s.KWRIT} {s.K}
        """


