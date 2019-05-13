from ... import ureg as _ureg
from ..commands import Command as _Command
from ..commands import CommandType as _CommandType


class MadElementCommandType(_CommandType):
    """
    Dark magic.
    Be careful.

    TODO
    """
    pass


class MadElementCommand(_Command, metaclass=MadElementCommandType):
    """MAD Command.

    """
    def __str__(self) -> str:
        """
        Provides the string representation of the command in the MAD-X input format.

        Returns:
            The string representation.

        """
        cmd = f"{self.LABEL1}: {self.KEYWORD}, "
        for p in self.attributes.keys():
            if p is not 'LABEL1':
                cmd += f"{p}={getattr(self, p)}, " if getattr(self, p) else ''
        cmd = cmd.rstrip(', ')
        cmd += ';'
        return cmd


class Drift(MadElementCommand):
    """
    A drift space.

    The straight reference system for a drift space is a Cartesian coordinate system.
    """
    KEYWORD = 'DRIFT'
    """Keyword of the command used for the MAD-X input data."""

    PARAMETERS = {
        'L': (0 * _ureg.m, 'The drift length (Default: 0 m).'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
        commands (e.g. fit)."""


class Marker(MadElementCommand):
    """
    The simplest element which can occur in a beam line is a MARKER. It has zero length and has no effect on the beam,
    but it allows one to identify a position in the beam line, for example to apply a matching constraint.
    """
    KEYWORD = 'MARKER'
    """Keyword of the command used for the MAD-X input data."""
