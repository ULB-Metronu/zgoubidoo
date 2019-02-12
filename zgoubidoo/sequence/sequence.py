"""High-level interface for Zgoubi using sequences and beams.

"""
from __future__ import annotations
from typing import Optional, List
import copy
import pandas as _pd
from ..commands.particules import Proton as _Proton
from .. commands.particules import ParticuleType as _ParticuleType
from ..commands.commands import Command as _Command
from ..physics import Kinematics as _Kinematics
from .. import ureg as _ureg
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
                 metadata: Optional[_pd.Series] = None,
                 kinematics: Optional[_Kinematics] = None,
                 particle: _ParticuleType = _Proton,
                 periods: int = 1,
                 ):
        """

        Args:
            name: the name of the sequence
            sequence: the list of commands composing the sequence
            metadata:
            kinematics:
            particle: the main particle type
            periods: the number of repetitions (for periodic sequences)
        """
        self._name = name
        if metadata is not None:
            self._metadata: _pd.Series = metadata
        else:
            self._metadata = _pd.Series()
        self._kinematics: Optional[_Kinematics] = kinematics
        try:
            self._kinematics = self._kinematics or _Kinematics(float(self._metadata['PC']) * _ureg.GeV_c)
        except KeyError:
            pass
        try:
            self._kinematics = self._kinematics or _Kinematics(float(self._metadata['ENERGY']) * _ureg.GeV)
        except KeyError:
            pass
        try:
            self._kinematics = self._kinematics or _Kinematics(float(self._metadata['GAMMA']))
        except KeyError:
            pass
        if self._kinematics is None:
            raise ValueError("Unable to infer kinematics data for the sequence.")
        self._sequence: List[_Command] = sequence or []
        if periods > 1:
            self.repeat_sequence(periods)
        self._particle = particle()
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

    @property
    def metadata(self) -> _pd.Series:
        """Provide the metadata associated with the sequence."""
        return self._metadata

    @property
    def kinematics(self) -> _Kinematics:
        """Provide the kinematics data associated with the sequence."""
        return self._kinematics

    @property
    def zgoubi(self) -> zgoubidoo.Zgoubi:
        """Provide the Zgoubi instance associated with the sequence."""
        return self._z

    @property
    def particle(self) -> _ParticuleType:
        """Provide the particle type associated with the sequence."""
        return self._particle

    def validate(self) -> bool:
        """
        Verify the validity of the sequence based on a set of rules.

        Returns:
            true if the sequence is valid.

        Raises:
            ZgoubidooSequenceException in case the sequence is not valid.
        """
        if len(list(filter(lambda _: isinstance(_, zgoubidoo.commands.Particule), self.sequence))) > 0:
            raise ZgoubidooSequenceException("A valid sequence should not contain any Particule.")

        if len(list(filter(lambda _: isinstance(_, zgoubidoo.commands.Objet), self.sequence))) > 0:
            raise ZgoubidooSequenceException("A valid sequence should not contain any Objet.")

        if len(list(filter(lambda _: isinstance(_, zgoubidoo.commands.Fit), self.sequence))) > 0:
            raise ZgoubidooSequenceException("A valid sequence should not contain a Fit command.")

        return True

    def repeat_sequence(self, periods: int = 1):
        """
        Repeat the sequence, assuming a periodic sequence.

        Args:
            periods: the number of periodic repetitions of the sequence
        """
        self._sequence = [copy.copy(e) for e in periods * self.sequence]
