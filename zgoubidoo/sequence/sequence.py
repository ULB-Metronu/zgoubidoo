"""High-level sequence module.

"""
from typing import Optional, List, Union, Iterable
from dataclasses import dataclass
import numpy as _np
from ..input import Input
from ..commands.particules import Proton, ParticuleType
from ..commands.commands import CommandType, Command, Fit2, Marker, FitType
from ..commands.objet import Objet2
from .. import ureg as _ureg
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
    t: float = 0
    z: float = 0
    p: float = 0
    x: float = 0
    d: float = 1
    iex: int = 1

    def __getitem__(self, item: int):
        return getattr(self, list(self.__dataclass_fields__.keys())[item])

    @property
    def array(self) -> _np.array:
        """Convert to a numpy array."""
        return _np.array(self.list)

    @property
    def list(self) -> list:
        """Convert to a flat list."""
        return list(self.__dict__.values())


class Sequence:
    """Sequence.

    """

    def __init__(self,
                 sequence: Optional[List[Command]] = None,
                 particle: Optional[ParticuleType] = Proton,
                 ):
        """

        Args:
            sequence:
            particle:
        """
        self._sequence: List[Command] = sequence
        self._particle = particle()
        self._closed_orbit = None
        self._z: zgoubidoo.Zgoubi = zgoubidoo.Zgoubi()

    def __getitem__(self, item: Union[slice,
                                      int,
                                      float,
                                      str,
                                      CommandType,
                                      type,
                                      Iterable[Union[CommandType, type, str]]]) -> Union[
            zgoubidoo.commands.Command, Input]:
        """

        Args:
            item:

        Returns:

        """
        return self._sequence[item]

    def is_valid(self) -> bool:
        """

        Returns:

        Raises:

        """
        if len(self[zgoubidoo.commands.Particule]) > 0:
            raise ZgoubidooSequenceException("A valid sequence should not contain any Particule")

        if len(self[zgoubidoo.commands.Objet]) > 0:
            raise ZgoubidooSequenceException("A valid sequence should not contain any Objet")

        return True

    def find_closed_orbit(self,
                          guess: Coordinates = Coordinates(),
                          tolerance: float = 1e-10,
                          fit_method: FitType = Fit2,
                          ):
        """

        Args:
            guess: initial closed orbit guess
            tolerance: tolerance for the termination of the fit method
            fit_method: a Zgoubi Fit command

        Returns:
            the closed orbit
        """
        zi = Input(
            name='CLOSED_ORBIT_FINDER',
            line=[
                     self._particle,
                     Objet2('BUNCH', BORO=2149 * _ureg.kilogauss * _ureg.cm).add(guess.list)
                 ] + self._sequence + [Marker('__END__')]
        )
        fit = fit_method(
            'FIT_CO',
            PENALTY=tolerance,
            PARAMS=[
                fit_method.Parameter(line=zi, place='BUNCH', parameter=Objet2.Y),
                fit_method.Parameter(line=zi, place='BUNCH', parameter=Objet2.T),
                #fit_method.Parameter(line=zi, place='BUNCH', parameter=Objet2.Z),
                #fit_method.Parameter(line=zi, place='BUNCH', parameter=Objet2.P),
            ],
            CONSTRAINTS=[
                fit_method.DifferenceEqualityConstraint(zi, '__END__', fit_method.Coordinates.Y),
                fit_method.DifferenceEqualityConstraint(zi, '__END__', fit_method.Coordinates.T),
                #fit_method.DifferenceEqualityConstraint(zi, '__END__', fit_method.Coordinates.Z),
                #fit_method.DifferenceEqualityConstraint(zi, '__END__', fit_method.Coordinates.P),
            ]
        )
        zi.line.append(fit)
        zi.IL = 0
        self.out = self._z(zi())
        co = self.out.tracks.query("LABEL1 == '__END__'").iloc[-1][['Yo', 'To', 'Zo', 'Po', 'Do-1']].values
        co1 = self.out.tracks.query("LABEL1 == '__END__'").iloc[-1][['Y-DY', 'T', 'Z', 'P', 'D-1']].values
        assert ((co - co1)**2 < tolerance).all(), f"Inconsistency detected during closed orbit search {co} {co1}."
        self._closed_orbit = co
        return self._closed_orbit

    def track_closed_orbit(self):
        """Track closed orbit"""
        zi = zgoubidoo.Input(
            name='TEST',
            line=[
                     self._particle,
                     Objet2('BUNCH', BORO=2149 * _.kilogauss * _.cm).add([[100 * self._closed_orbit[0],
                                                                           1000 * self._closed_orbit[1],
                                                                           100 * self._closed_orbit[2],
                                                                           1000 * self._closed_orbit[3],
                                                                           0.0,
                                                                           self._closed_orbit[4] + 1,
                                                                           0.0]])
                 ] + self._sequence
        )
        zi.IL = 2
        out = self._z(zi)
        return out.tracks

    def twiss(self):
        """

        Returns:

        """
        pass






