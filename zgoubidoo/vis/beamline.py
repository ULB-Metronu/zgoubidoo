from .zgoubiplot import ZgoubiPlot
from .. import commands


def plot(beamline=None, tracks=None, artist: ZgoubiPlot=None, with_elements: bool=True) -> None:
    line = beamline[commands.Patchable][commands.Plotable].line
    for e in line:
        if with_elements:
            e.plot(artist=artist)
        if tracks is not None:
            e.plot_tracks(artist=artist, tracks=tracks.query(f"LABEL1 == '{e.LABEL1}'"))
