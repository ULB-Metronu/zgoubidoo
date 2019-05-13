"""TODO"""
from ..commands import Command as _Command
from ..commands import CommandType as _CommandType


class MadCommandType(_CommandType):
    """
    Dark magic.
    Be careful.

    TODO
    """
    pass


class MadCommand(_Command, metaclass=MadCommandType):
    """MAD Command.

    """
    def __str__(self) -> str:
        """
        Provides the string representation of the command in the MAD-X input format.

        Returns:
            The string representation.

        """
        return f"{self.KEYWORD};"


class Beam(MadCommand):
    """
        'beam': "BEAM, PARTICLE={{{{PARTICLE}}}}, "
            "PC={{{{PC/1000.0}}}}, "
            "EX={{{{ EMITX or '1e-9' }}}}, "
            "EY={{{{ EMITY or '1e-9' }}}};",
    """
    KEYWORD = 'BEAM'
    pass


class Call(MadCommand):
    """
    TODO
    """
    KEYWORD = ' CALL'

    def __str__(self) -> str:
        return f"{self.KEYWORD}, FILE={self.FILE};"


class Option(MadCommand):
    """
    TODO
    """
    KEYWORD = 'OPTION'


class Use(MadCommand):
    """
    TODO
    """
    KEYWORD = 'USE'

    def __str__(self) -> str:
        return f"{self.KEYWORD}, SEQUENCE={self.SEQUENCE};"


class SaveBeta(MadCommand):
    """
    TODO
    """
    KEYWORD = 'SAVEBETA'

    def __str__(self) -> str:
        return f"{self.KEYWORD}, LABEL={self.LABEL}, PLACE={self.PLACE};"


class Show(MadCommand):
    """
    TODO
    """
    KEYWORD = 'SHOW'

    def __str__(self) -> str:
        return f"{self.KEYWORD}, {self.WHAT};"


class Survey(MadCommand):
    """
    TODO
    """
    KEYWORD = 'SURVEY'

    def __str__(self) -> str:
        return f"{self.KEYWORD}, FILE={self.FILE};"


class Stop(MadCommand):
    """Magnetic multipole.
    """
    KEYWORD = 'STOP'
    """Keyword of the command used for the Zgoubi input data."""


class Twiss(MadCommand):
    """
    TODO
    """
    pass


class MakeThin(MadCommand):
    """
    TODO
    """
    pass


class Track(MadCommand):
    """
    TODO
    """
    pass


class PTCCreateUniverse(MadCommand):
    """
    TODO
    """
    pass


class PTCCreateLayout(MadCommand):
    """
    TODO
    """
    pass


class PTCSetSwitch(MadCommand):
    """
    TODO
    """
    pass


class PTCEnd(MadCommand):
    """
    TODO
    """
    pass
