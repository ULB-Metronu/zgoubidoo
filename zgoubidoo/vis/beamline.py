from __future__ import annotations
from .zgoubiplot import ZgoubiPlot
import zgoubidoo


def beamline(beamline: zgoubidoo.Input,
             tracks=None,
             tracks_color: str = 'b',
             artist: ZgoubiPlot = None,
             with_elements: bool = True
             ) -> None:
    """

    Args:
        beamline:
        tracks:
        artist:
        with_elements:

    Returns:

    """
    line = beamline[zgoubidoo.commands.Patchable][zgoubidoo.commands.Plotable].line
    for e in line:
        if with_elements:
            e.plot(artist=artist)
        if tracks is not None:
            e.plot_tracks(artist=artist, tracks=tracks.query(f"LABEL1 == '{e.LABEL1}'"))
