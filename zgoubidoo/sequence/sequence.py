"""High-level sequence.

"""
from typing import Optional, List
import copy
from ..input import Input as _Input
from ..commands.particules import Proton as _Proton
from .. commands.particules import ParticuleType as _ParticuleType
from ..commands.commands import Command as _Command
import zgoubidoo

__all__ = ['ZgoubidooSequenceException', 'Sequence']


class ZgoubidooSequenceException(Exception):
    """Exception raised for errors when using zgoubidoo.Sequence"""

    def __init__(self, m):
        self.message = m


class Sequence:
    """Sequence.

    """
    def __init__(self,
                 name: str = 'SEQUENCE',
                 sequence: Optional[List[_Command]] = None,
                 particle: _ParticuleType = _Proton,
                 periods: int = 1,
                 ):
        """

        Args:
            name: the name of the sequence
            sequence: the list of commands composing the sequence
            particle: the main particle type
            periods: the number of repetitions (for periodic sequences)
        """
        self._name = name
        self._sequence: List[_Command] = sequence or []
        if periods > 1:
            self.repeat_sequence(periods)
        self._particle = particle()
        self._closed_orbit = None
        self._z: zgoubidoo.Zgoubi = zgoubidoo.Zgoubi()
        self.validate()

    @property
    def name(self) -> str:
        """Provide the name of the sequence."""
        return self._name

    @property
    def sequence(self) -> List[_Command]:
        """Provide the sequence of elements."""
        return self._sequence

    def validate(self) -> bool:
        """
        Verify the validity of the sequence based on a set of rules.

        Returns:
            true if the sequence is valid.

        Raises:
            ZgoubidooSequenceException in case the sequence is not valid.
        """
        if len(self[zgoubidoo.commands.Particule]) > 0:
            raise ZgoubidooSequenceException("A valid sequence should not contain any Particule.")

        if len(self[zgoubidoo.commands.Objet]) > 0:
            raise ZgoubidooSequenceException("A valid sequence should not contain any Objet.")

        if len(self[zgoubidoo.commands.Fit]) > 0:
            raise ZgoubidooSequenceException("A valid sequence should not contain a Fit command.")

        return True

    def repeat_sequence(self, periods: int = 1):
        """
        Repeat the sequence, assuming a periodic sequence.

        Args:
            periods: the number of periodic repetitions of the sequence
        """
        self._sequence = [copy.copy(e) for e in periods * self.sequence]
        self._input = _Input(name=self.name, line=self.sequence).survey()
