"""High-level interface for Zgoubi using sequences and beams.

"""
from __future__ import annotations
from typing import Optional, List, Union, Iterable, Tuple, Any
import itertools
import copy
import pandas as _pd
from .commands.commands import ZgoubidooException as _ZgoubidooException
from .commands.particules import Proton as _Proton
from .commands.particules import ParticuleType as _ParticuleType
from .commands.commands import CommandType as _CommandType
from .commands.commands import Command as _Command
from .kinematics import Kinematics as _Kinematics
from zgoubidoo import ureg as _ureg
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
                 table: Optional[_pd.DataFrame] = None,
                 initial_twiss: Optional[_pd.Series] = None,
                 periods: int = 1,
                 ):
        """

        Args:
            name: the name of the physics
            sequence: the list of commands composing the physics
            metadata:
            kinematics:
            particle: the main particle type
            table:
            periods: the number of repetitions (for periodic sequences)
        """
        self._name = name
        self._table = table
        if initial_twiss is not None:
            self._initial_twiss: _pd.Series = initial_twiss
        else:
            self._initial_twiss: _pd.Series = _pd.Series()
        if metadata is not None:
            self._metadata: _pd.Series = metadata
        else:
            self._metadata = _pd.Series()
        self._kinematics: Optional[_Kinematics] = kinematics
        try:
            self._kinematics = self._kinematics or _Kinematics(float(self._metadata['PC']) * _ureg.GeV_c,
                                                               particle=particle)
        except KeyError:
            pass
        try:
            self._kinematics = self._kinematics or _Kinematics(float(self._metadata['ENERGY']) * _ureg.GeV,
                                                               particle=particle)
        except KeyError:
            pass
        try:
            self._kinematics = self._kinematics or _Kinematics(float(self._metadata['GAMMA']),
                                                               particle=particle)
        except KeyError:
            pass
        self._sequence: List[_Command] = sequence or []
        if periods > 1:
            self.repeat_sequence(periods)
        self._particle = particle()
        self._z: zgoubidoo.Zgoubi = zgoubidoo.Zgoubi()
        if self.validate():
            for _ in self._sequence:
                try:
                    _.KINEMATICS = self.kinematics
                except _ZgoubidooException:
                    pass

    @property
    def name(self) -> str:
        """Provide the name of the physics."""
        return self._name

    @property
    def sequence(self) -> List[_Command]:
        """Provide the physics of elements."""
        return self._sequence

    @property
    def table(self) -> _pd.DataFrame:
        """Provide the associated table."""
        return self._table

    @property
    def metadata(self) -> _pd.Series:
        """Provide the metadata associated with the physics."""
        return self._metadata

    @property
    def initial_twiss(self) -> _pd.Series:
        """Provide the associated initial Twiss values"""
        return self._initial_twiss

    @property
    def kinematics(self) -> _Kinematics:
        """Provide the kinematics data associated with the physics."""
        return self._kinematics

    @property
    def zgoubi(self) -> zgoubidoo.Zgoubi:
        """Provide the Zgoubi instance associated with the physics."""
        return self._z

    @property
    def particle(self) -> _ParticuleType:
        """Provide the particle type associated with the physics."""
        return self._particle

    def validate(self) -> bool:
        """
        Verify the validity of the physics based on a set of rules.

        Returns:
            true if the physics is valid.

        Raises:
            ZgoubidooSequenceException in case the physics is not valid.
        """
        if len(list(filter(lambda _: isinstance(_, zgoubidoo.commands.Particule), self.sequence))) > 0:
            raise ZgoubidooSequenceException("A valid physics should not contain any Particule.")

        if len(list(filter(lambda _: isinstance(_, zgoubidoo.commands.Objet), self.sequence))) > 0:
            raise ZgoubidooSequenceException("A valid physics should not contain any Objet.")

        if len(list(filter(lambda _: isinstance(_, zgoubidoo.commands.Fit), self.sequence))) > 0:
            raise ZgoubidooSequenceException("A valid physics should not contain a Fit command.")

        return True

    def repeat(self, periods: int = 2):
        """
        Repeat the physics, assuming a periodic physics.

        Args:
            periods: the number of periodic repetitions of the physics
        """
        self._sequence = [copy.copy(e) for e in periods * self.sequence]

    def reverse(self):
        """

        Returns:

        """
        self._sequence = copy.copy(self._sequence)[::-1]

    def __len__(self) -> int:
        """Length of the sequence.

        Returns:
            the number of elements in the sequence.

        """
        return len(self._sequence)

    def __iadd__(self, command: _Command) -> Sequence:
        """Append a command at the end of the input sequence.

        Args:
            command: the command to be appended.

        Returns:
            the input sequence (in-place operation).

        """
        self._sequence.append(command)
        return self

    def __isub__(self, other: Union[str, _Command]) -> Sequence:
        """Remove a command from the input sequence.

        Args:
            other: the `Command` to be removed or the LABEL1 of the command to be removed as a string.

        Returns:
            the `Input` itself (in-place operation).
        """
        if isinstance(other, str):
            self._sequence = [c for c in self._sequence if c.LABEL1 != other]
        else:
            self._sequence = [c for c in self._sequence if c != other]
        return self

    def __getitem__(self,
                    items: Union[slice,
                                 int,
                                 float,
                                 str,
                                 _CommandType,
                                 type,
                                 Iterable[Union[_CommandType, type, str]]]
                    ) -> Union[_Command, List[_Command]]:
        """Multi-purpose dictionnary-like elements access and filtering.

        A triple interafce is provided:

            - **numerical index**: provides the element from its numeric index (starting at 0, looked-up in the `line`
              property of the input (the returned object is a `Command`);

            - **slicing**: provides a powerful slicing feature, using either object slice or string slice (or a mix of
              both); see example below (the returned object is a copy of the sliced input);

            - **element access**: returns a filtered input containing only the given elements. The elements are given
              either in the form of a list of strings (or a single string), representing the class name of the element or
              in the form of a list of classes (or a single class).

        Args:
            items: index based accessor, slice or elements types for filtering access (see above).

        Returns:

                - with numerical index returns the object located at that position (an instance of a `Command`);
                - with slicing returns a copy of the input, with the slicing applied (an instance of a `Input`);
                - with element access returns a filtering copy of the input (an instance of a `Input`).

        """
        # Behave like element access
        if isinstance(items, (int, float)):
            return self._sequence[int(items)]

        # Behave like slicing
        if isinstance(items, slice):
            start = items.start
            end = items.stop
            if isinstance(items.start, (zgoubidoo.commands.Command, str)):
                start = self.index(items.start) - 1
            if isinstance(items.stop, (zgoubidoo.commands.Command, str)):
                end = self.index(items.stop)
            slicing = slice(start, end, items.step)
            return self._sequence[slicing]

        else:
            # Behave like a filtering
            if not isinstance(items, (tuple, list)):
                items = (items,)
            l, i = self._filter(items)
            return l

    def __getattr__(self, item: str) -> _Command:
        """

        Args:
            item:

        Returns:

        """
        for e in self._sequence:
            if e.LABEL1 == item:
                return e
        raise AttributeError

    def __setattr__(self, key: str, value: Any):  # -> NoReturn
        """

        Args:
            key:
            value:

        Returns:

        """
        if key.startswith('_'):
            self.__dict__[key] = value
        else:
            for e in self._line:
                if getattr(e, key) is not None:
                    setattr(e, key, value)

    def __contains__(self, items: Union[str, _CommandType, Tuple[Union[str, _CommandType]]]) -> int:
        """

        Args:
            items:

        Returns:

        """
        if not isinstance(items, tuple):
            items = (items,)
        l, i = self._filter(items)
        return len(l)

    def _filter(self, items: Union[str, _CommandType, Tuple[Union[str, _CommandType]]]) -> tuple:
        """

        Args:
            items:

        Returns:

        """
        try:
            items = tuple(map(lambda x: getattr(zgoubidoo.commands, x) if isinstance(x, str) else x, items))
        except AttributeError:
            return list(), tuple()
        return list(filter(
            lambda x: itertools.reduce(lambda u, v: u or v, [isinstance(x, i) for i in items]),
            self._line
        )), items
