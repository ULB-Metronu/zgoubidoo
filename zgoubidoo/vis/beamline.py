from __future__ import annotations
from .zgoubiplot import ZgoubiPlot
from .. import commands
import zgoubidoo


def plot(beamline: zgoubidoo.Input, tracks=None, artist: ZgoubiPlot=None, with_elements: bool=True) -> None:
    """

    Args:
        beamline:
        tracks:
        artist:
        with_elements:

    Returns:

    """
    line = beamline[commands.Patchable][commands.Plotable].line
    for e in line:
        if with_elements:
            e.plot(artist=artist)
        if tracks is not None:
            e.plot_tracks(artist=artist, tracks=tracks.query(f"LABEL1 == '{e.LABEL1}'"))
