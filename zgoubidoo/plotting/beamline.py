import numpy as np
from ..input import Input
from .. import ureg
from ..commands import CartesianMagnet, PolarMagnet


def plot_beamline(beamline=None, tracks=None, artist=None, with_elements=True, reference=None):
    if beamline is None or not isinstance(beamline, Input):
        raise Exception("'line' must be a Zgoubi input object.")
    if artist is None:
        raise Exception("Unable to plot if no artist is provided.")

    ref = reference or [0.0 * ureg.centimeter, 0.0 * ureg.centimeter, 0.0 * ureg.degree]
    tracks_x = np.array(ref[0])
    tracks_y = np.array(ref[1])
    for e in beamline.line:
        print(e.KEYWORD)
        if not e.patchable:
            continue
        if with_elements:
            e.PLACEMENT = ref
            print(ref)
            print(e.center)
            e.plot(artist=artist)
            if e.KEYWORD == 'YMY':
                print('ok')
        if tracks is not None:
            t = tracks.query(f"LABEL1 == '{e.LABEL1}'")
            if isinstance(e, CartesianMagnet) and t.size > 0:
                x = t['X'].values
                y = t['Y-DY'].values
                s = np.sin((ref[2] + e.rotation).to('radian').magnitude)
                c = np.cos((ref[2] + e.rotation).to('radian').magnitude)
                xx = c * x - s * y
                yy = s * x + c * y
                tracks_x = np.append(tracks_x, (ref[0] + e.entry[0]).to('cm').magnitude + xx)
                tracks_y = np.append(tracks_y, (ref[1] + e.entry[1]).to('cm').magnitude + yy)
        artist.plot(e.entry[0], e.entry[1], 'gs', ms=4)
        artist.plot(e.sortie[0], e.sortie[1], 'ks', ms=4)
        # artist.plot(tracks_x, tracks_y, 'b-', ms=1)
        ref[0] = e.sortie[0]
        ref[1] = e.sortie[1]
        ref[2] = e.sortie[2]
