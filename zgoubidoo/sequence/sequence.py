"""High-level sequence module.

"""
from typing import Optional, List, Union, Iterable
from dataclasses import dataclass
import copy
import numpy as _np
from ..input import Input as _Input
from ..commands.particules import Proton as _Proton
from .. commands.particules import ParticuleType as _ParticuleType
from ..commands.commands import CommandType as _CommandType
from ..commands.commands import Command as _Command
from ..commands.commands import Fit as _Fit
from ..commands.commands import FitType as _FitType
from ..commands.commands import Marker as _Marker
from ..commands.objet import Objet2 as _Objet2
from .. import _Q
from ..zgoubi import ZgoubiRun as _ZgoubiRun
import zgoubidoo


class ZgoubidooSequenceException(Exception):
    """Exception raised for errors when using zgoubidoo.Sequence"""

    def __init__(self, m):
        self.message = m


@dataclass
class Coordinates:
    """Particle coordinates in 6D phase space.

    Follows Zgoubi's convention.

    Examples:
        >>> c = Coordinates()
        >>> c.y
        0.0
        >>> c = Coordinates(1.0, 1.0, 0.0, 0.0, 0.0, 0.0)
        >>> c.t
        1.0
    """
    y: float = 0
    """Horizontal plane coordinate."""
    t: float = 0
    """Horizontal plane angle."""
    z: float = 0
    """Vertical plane coordinate"""
    p: float = 0
    """Vertical plane angle."""
    x: float = 0
    """Longitudinal coordinate."""
    d: float = 1
    """Off-momentum offset"""
    iex: int = 1
    """Particle alive status."""

    def __getitem__(self, item: int):
        return getattr(self, list(self.__dataclass_fields__.keys())[item])

    @property
    def array(self) -> _np.array:
        """Provides a numpy array."""
        return _np.array(self.list)

    @property
    def list(self) -> list:
        """Provides a flat list."""
        return list(self.__dict__.values())


class Sequence:
    """Sequence.

    """

    class PlaneType(type):
        """A type system for plane classes."""
        pass

    class HorizontalPlane(metaclass=PlaneType):
        """A type to represent the horizontal plane."""
        pass

    class VerticalPlane(metaclass=PlaneType):
        """A type to represent the vertical plane."""
        pass

    class BothPlanes(HorizontalPlane, VerticalPlane):
        """A type to represent both planes, horizontal and vertical.

        Examples:
            >>> issubclass(Sequence.BothPlanes, Sequence.HorizontalPlane)
            True
            >>> issubclass(Sequence.BothPlanes, Sequence.VerticalPlane)
            True
            >>> issubclass(Sequence.HorizontalPlane, Sequence.HorizontalPlane)
        """
        pass

    def __init__(self,
                 name: str = '',
                 sequence: Optional[List[_Command]] = None,
                 particle: Optional[_ParticuleType] = _Proton,
                 periods: int = 1,
                 ):
        """

        Args:
            name: the name of the sequence
            sequence:
            particle:
            periods:
        """
        self._name = name
        self._sequence: List[_Command] = sequence
        self._input: _Input = _Input(name=self.name, line=self.sequence)
        if periods > 1:
            self.repeat_sequence(periods)
        self._particle = particle()
        self._closed_orbit = None
        self._z: zgoubidoo.Zgoubi = zgoubidoo.Zgoubi()
        self._last_run: Optional[_ZgoubiRun] = None
        self.validate()

    def __getitem__(self, item: Union[slice,
                                      int,
                                      float,
                                      str,
                                      _CommandType,
                                      type,
                                      Iterable[Union[_CommandType, type, str]]]) -> Union[
            zgoubidoo.commands.Command, _Input]:
        """

        Args:
            item:

        Returns:

        """
        return self.input[item]

    @property
    def name(self) -> str:
        """Provide the name of the sequence."""
        return self._name

    @property
    def sequence(self) -> List[_Command]:
        """Provide the sequence of elements."""
        return self._sequence

    @property
    def input(self) -> _Input:
        """Provide the sequence of elements wrapped in a Zgoubi Input."""
        return self._input

    @property
    def last_run(self) -> _ZgoubiRun:
        """Provide the result of the last Zgoubi run."""
        return self._last_run

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

        Args:
            periods: the number of periodic repetitions of the sequence

        Returns:

        """
        self._sequence = [copy.copy(e) for e in periods * self.sequence]
        self._input = Input(name=self.name, line=self.sequence).survey()

    def find_closed_orbit(self,
                          brho: _Q,
                          dpp: float = 0.0,
                          guess: Coordinates = Coordinates(),
                          tolerance: float = 1e-10,
                          fit_method: _FitType = _Fit,
                          plane: PlaneType = HorizontalPlane,
                          ):
        """

        Args:
            brho: nominal magnetic rigidity of the sequence
            dpp: momentum offset for off-momentum closed orbit computation
            guess: initial closed orbit guess
            tolerance: tolerance for the termination of the fit method
            fit_method: a Zgoubi Fit command
            plane: the plane(s) for which the search has to be performed

        Returns:
            the closed orbit
        """
        guess.d += dpp
        zi = _Input(
            name='CLOSED_ORBIT_FINDER',
            line=[
                     self._particle,
                     _Objet2('BUNCH', BORO=brho).add(guess.list)
                 ] + self._sequence + [_Marker('__END__')]
        )
        fit = fit_method(
            'FIT_CO',
            PENALTY=tolerance,
            PARAMS=[
                fit_method.Parameter(line=zi, place='BUNCH', parameter=_Objet2.Y_, range=(-100, 500))
                if issubclass(plane, Sequence.HorizontalPlane) else None,
                fit_method.Parameter(line=zi, place='BUNCH', parameter=_Objet2.T_, range=(-100, 500))
                if issubclass(plane, Sequence.HorizontalPlane) else None,
                fit_method.Parameter(line=zi, place='BUNCH', parameter=_Objet2.Z_, range=(-100, 500))
                if issubclass(plane, Sequence.VerticalPlane) else None,
                fit_method.Parameter(line=zi, place='BUNCH', parameter=_Objet2.P_, range=(-100, 500))
                if issubclass(plane, Sequence.VerticalPlane) else None,
            ],
            CONSTRAINTS=[
                fit_method.DifferenceEqualityConstraint(zi, '__END__', fit_method.FitCoordinates.Y)
                if issubclass(plane, Sequence.HorizontalPlane) else None,
                fit_method.DifferenceEqualityConstraint(zi, '__END__', fit_method.FitCoordinates.T)
                if issubclass(plane, Sequence.HorizontalPlane) else None,
                fit_method.DifferenceEqualityConstraint(zi, '__END__', fit_method.FitCoordinates.Z)
                if issubclass(plane, Sequence.VerticalPlane) else None,
                fit_method.DifferenceEqualityConstraint(zi, '__END__', fit_method.FitCoordinates.P)
                if issubclass(plane, Sequence.VerticalPlane) else None,
            ]
        )
        zi.line.append(fit)
        zi.IL = 0
        self._last_run = self._z(zi())
        co = self._last_run.tracks.query("LABEL1 == '__END__'").iloc[-1][['Yo', 'To', 'Zo', 'Po', 'Do-1']].values
        co1 = self._last_run.tracks.query("LABEL1 == '__END__'").iloc[-1][['Y-DY', 'T', 'Z', 'P', 'D-1']].values
        assert _np.linalg.norm(co-co1)**2 < tolerance, f"Inconsistency detected during closed orbit search {co} {co1}."
        self._closed_orbit = co
        return self._closed_orbit

    def track_closed_orbit(self, brho: _Q):
        """Track closed orbit.

        Args:
            brho: nominal magnetic rigidity of the sequence
        """
        zi = zgoubidoo.Input(
            name=self.name,
            line=[
                     self._particle,
                     _Objet2('BUNCH', BORO=brho).add([[100 * self._closed_orbit[0],
                                                      1000 * self._closed_orbit[1],
                                                      100 * self._closed_orbit[2],
                                                      1000 * self._closed_orbit[3],
                                                      0.0,
                                                      self._closed_orbit[4] + 1,
                                                      0.0]])
                 ] + self._sequence
        )
        zi.IL = 2
        self._last_run = self._z(zi())
        return self._last_run.tracks

    def twiss(self):
        """

        Returns:

        """
        pass






