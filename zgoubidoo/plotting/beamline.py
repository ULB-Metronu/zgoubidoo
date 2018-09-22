from .zgoubiplot import ZgoubiPlot


def plot(beamline=None, tracks=None, artist: ZgoubiPlot=None, with_elements: bool=True) -> None:
    line = beamline['Patchable'].line
    artist.reference_frame = line[0].entry
    for e in line:
        if not e.plotable:
            continue
        if with_elements:
            e.plot(artist=artist)
        if tracks is not None:
            e.plot_tracks(artist=artist, tracks=tracks.query(f"LABEL1 == '{e.LABEL1}'"))
