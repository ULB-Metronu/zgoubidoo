"""

"""
import numpy as _np
import pandas as _pd

import zgoubidoo

from .. import Q_ as _Q
from ..commands.actions import Fit as _Fit
from ..commands.actions import FitType as _FitType
from ..commands.commands import Marker as _Marker
from ..commands.objet import Objet2 as _Objet2
from ..input import Input as _Input
from .coordinates import Coordinates


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
        >>> issubclass(BothPlanes, HorizontalPlane)
        True
        >>> issubclass(BothPlanes, VerticalPlane)
        True
        >>> issubclass(HorizontalPlane, HorizontalPlane)
        True
    """

    pass


def find_closed_orbit(
    self,
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
        name="CLOSED_ORBIT_FINDER",
        line=[
            self._particle,
            _Objet2("BUNCH", BORO=brho).add(guess.list),
        ]
        + self._sequence
        + [_Marker("__END__")],
    )
    fit = fit_method(
        "FIT_CO",
        PENALTY=tolerance,
        PARAMS=[
            fit_method.Parameter(line=zi, place="BUNCH", parameter=_Objet2.Y_, range=(-100, 500))
            if issubclass(plane, HorizontalPlane)
            else None,
            fit_method.Parameter(line=zi, place="BUNCH", parameter=_Objet2.T_, range=(-100, 500))
            if issubclass(plane, HorizontalPlane)
            else None,
            fit_method.Parameter(line=zi, place="BUNCH", parameter=_Objet2.Z_, range=(-100, 500))
            if issubclass(plane, VerticalPlane)
            else None,
            fit_method.Parameter(line=zi, place="BUNCH", parameter=_Objet2.P_, range=(-100, 500))
            if issubclass(plane, VerticalPlane)
            else None,
        ],
        CONSTRAINTS=[
            fit_method.DifferenceEqualityConstraint(zi, "__END__", fit_method.FitCoordinates.Y)
            if issubclass(plane, HorizontalPlane)
            else None,
            fit_method.DifferenceEqualityConstraint(zi, "__END__", fit_method.FitCoordinates.T)
            if issubclass(plane, HorizontalPlane)
            else None,
            fit_method.DifferenceEqualityConstraint(zi, "__END__", fit_method.FitCoordinates.Z)
            if issubclass(plane, VerticalPlane)
            else None,
            fit_method.DifferenceEqualityConstraint(zi, "__END__", fit_method.FitCoordinates.P)
            if issubclass(plane, VerticalPlane)
            else None,
        ],
    )
    zi.line.append(fit)
    zi.IL = 0
    self._last_run = self._z(zi())
    co = self._last_run.tracks.query("LABEL1 == '__END__'").iloc[-1][["Yo", "To", "Zo", "Po", "Do-1"]].values
    co1 = self._last_run.tracks.query("LABEL1 == '__END__'").iloc[-1][["Y-DY", "T", "Z", "P", "D-1"]].values
    assert _np.linalg.norm(co - co1) ** 2 < tolerance, f"Inconsistency detected during closed orbit search {co} {co1}."
    self._closed_orbit = co
    return self._closed_orbit


def track_closed_orbit(self, brho: _Q) -> _pd.DataFrame:
    """Track closed orbit.

    Args:
        brho: nominal magnetic rigidity of the physics
    """
    zi = zgoubidoo.Input(
        name=self.name,
        line=[
            self._particle,
            _Objet2("BUNCH", BORO=brho).add(
                [
                    [
                        100 * self._closed_orbit[0],
                        1000 * self._closed_orbit[1],
                        100 * self._closed_orbit[2],
                        1000 * self._closed_orbit[3],
                        0.0,
                        self._closed_orbit[4] + 1,
                        0.0,
                    ],
                ],
            ),
        ]
        + self._sequence,
    )
    zi.IL = 2
    self._last_run = self._z(zi())
    return self._last_run.tracks
