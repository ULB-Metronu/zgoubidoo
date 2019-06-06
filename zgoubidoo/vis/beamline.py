"""Beamline visualization module.

This module provides high-level functions for the rendering of beamlines (Zgoubi `Input`s).
"""
from __future__ import annotations
from .zgoubiplot import ZgoubiPlot
import zgoubidoo


def beamline(line: zgoubidoo.Input,
             artist: ZgoubiPlot,
             tracks=None,
             tracks_color: str = 'b',
             with_elements: bool = True,
             with_apertures: bool = False,
             with_tracks: bool = True,
             ) -> None:
    """
    Use a `ZgoubiPlot` artist to perform the rendering of the beamline with elements and tracks.

    The `Input` must be surveyed first so that all the placements are taken into account for the plotting.

    Args:
        line: the beamline to be rendered
        artist: the artist for the rendering
        tracks: the tracks dataset
        tracks_color: color for the rendering of the tracks
        with_elements: plot the beamline elements
        with_apertures:
        with_tracks: plot the beam tracks
    """
    line = line[zgoubidoo.commands.Patchable][zgoubidoo.commands.Plotable].line
    if getattr(artist, 'tracks_color'):
        artist.tracks_color = tracks_color
    for e in line:
        if with_elements:
            e.plot(artist=artist, apertures=with_apertures)
        if not with_elements and with_apertures:
            e.plot(artist=artist, apertures=True)
        if tracks is not None and with_tracks:
            e.plot_tracks(artist=artist, tracks=tracks.query(f"LABEL1 == '{e.LABEL1}'"))


def cartouche(line: zgoubidoo.Input,
              artist: ZgoubiPlot,
              ) -> None:
    """
    Use a `ZgoubiPlot` artist to display the beamline at the top of other plots; similarly to the MAD-X plots.

    TODO note about the use of S or X coordinate

    Args:
        line: the beamline to be rendered
        artist: the artist (ZgoubiPlot) for the rendering
    """
    line = line[zgoubidoo.commands.Patchable][zgoubidoo.commands.Plotable].line
    for e in line:
        try:
            e.plot_cartouche(s_location=e.entry.s, artist=artist)
        except AttributeError:
            e.plot_cartouche(s_location=e.entry.x, artist=artist)
