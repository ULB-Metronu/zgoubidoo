class Command:
    PARAMETERS = {
        'LABEL1': '',
        'LABEL2': '',
    }

    def __init__(self, label1='', label2='', *params, **kwargs):
        self._attributes = {}
        for p in (Command.PARAMETERS, self.PARAMETERS,) + params + ({'LABEL1': label1, 'LABEL2': label2},):
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
        return f"'{s.KEYWORD}' {s.LABEL1} {s.LABEL2}"


class Faiscnl(Command):
    KEYWORD = 'FAISCNL'
    PARAMETERS = {
        'FNAME': 'zgoubi.fai',
        'B_FNAME': 'b_zgoubi.fai',
        'binary': False,
    }

    def __str__(s):
        return f"""
        {super().__str__()}
        {s.B_FNAME if s.binary else s.FNAME}
        """


class End(Command):
    """End of input data list."""
    KEYWORD = 'END'


class Fin(Command):
    """End of input data list."""
    KEYWORD = 'FIN'


class Rebelote(Command):
    """’Do it again’."""
    KEYWORD = 'REBELOTE'

    PARAMETERS = {
        'NPASS': 1,
        'KWRIT': 0.0,
        'K': 99,
    }

    def __str__(s):
        return f"""
        {super().__str__()}
        {s.NPASS} {s.KWRIT} {s.K}
        """


class Reset(Command):
    """Reset counters and flags."""
    KEYWORD = 'RESET'

