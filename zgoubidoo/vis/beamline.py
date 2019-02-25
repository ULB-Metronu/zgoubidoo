"""Beamline visualization module.

This module provides high-level functions for the rendering of beamlines (Zgoubi `Input`s).
"""
from __future__ import annotations
from typing import Optional
from .zgoubiplot import ZgoubiPlot
import zgoubidoo
from zgoubidoo import ureg as _ureg


def beamline(line: zgoubidoo.Input,
             artist: ZgoubiPlot,
             tracks=None,
             tracks_color: str = 'b',
             with_elements: bool = True,
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
        with_tracks: plot the beam tracks
    """
    line = line[zgoubidoo.commands.Patchable][zgoubidoo.commands.Plotable].line
    if getattr(artist, 'tracks_color'):
        artist.tracks_color = tracks_color
    for e in line:
        if with_elements:
            e.plot(artist=artist)
        if tracks is not None and with_tracks:
            e.plot_tracks(artist=artist, tracks=tracks.query(f"LABEL1 == '{e.LABEL1}'"))


def cartouche(line: zgoubidoo.Input,
              artist: ZgoubiPlot,
              ) -> None:
    """

    Args:
        line:
        artist:

    Returns:

    """
    line = line[zgoubidoo.commands.Patchable][zgoubidoo.commands.Plotable].line
    s = 0 * _ureg.cm
    for e in line:
        e.plot_cartouche(s_location=s, artist=artist)
        s += e.length
