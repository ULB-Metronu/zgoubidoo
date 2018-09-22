from .zgoubiplot import ZgoubiPlot


def plot(beamline=None, tracks=None, artist: ZgoubiPlot=None, with_elements: bool=True) -> None:
    #tracks_x = np.array(ref[0])
    #tracks_y = np.array(ref[1])
    for e in beamline['Patchable'].line:
        if not e.plotable:
            continue
        if with_elements:
            e.plot(artist=artist)
        # if tracks is not None:
        #     t = tracks.query(f"LABEL1 == '{e.LABEL1}'")
        #     if isinstance(e, CartesianMagnet) and t.size > 0:
        #         x = t['X'].values
        #         y = t['Y-DY'].values
        #         s = np.sin((ref[2] + e.rotation).to('radian').magnitude)
        #         c = np.cos((ref[2] + e.rotation).to('radian').magnitude)
        #         xx = c * x - s * y
        #         yy = s * x + c * y
        #         tracks_x = np.append(tracks_x, (ref[0] + e.entry[0]).to('cm').magnitude + xx)
        #         tracks_y = np.append(tracks_y, (ref[1] + e.entry[1]).to('cm').magnitude + yy)
        # artist.plot(tracks_x, tracks_y, 'b-', ms=1)

