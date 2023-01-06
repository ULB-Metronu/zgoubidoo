import numpy as _np

import zgoubidoo
from zgoubidoo.commands import ChangeRef, Drift, Electron, Faisceau, Objet2, Quadrupole

_ = zgoubidoo.ureg

cells = 42
angle = 360 / cells * _.degree
d_offset = -34.048 * _.mm
f_offset = -7.514 * _.mm

# Lengths
ld = 210 * _.mm
sd = 50 * _.mm
fq = 58.782 * _.mm
dq = 75.699 * _.mm

# Quadrupole radii
fr = 37 * _.mm
dr = 53 * _.mm

# Fields
fb = -6.695 * fr * _.T / _.cm
db = 4.704 * dr * _.T / _.cm

rigidity = zgoubidoo.Kinematics(1 * _.GeV, particle=zgoubidoo.commands.Electron)
objet = Objet2("BUNCH", BORO=rigidity.brho)
objet.add(_np.array([[0.456, -38.1, 0.0, 0.0, 0.0, 1.0, 1.0]]))
emma = zgoubidoo.Input(
    name="EMMA",
    line=[
        objet,
        Electron(),
        Drift("ld1", XL=ld / 2),
        ChangeRef(TRANSFORMATIONS=[("ZR", angle), ("YS", d_offset)]),
        Quadrupole("defoc", XL=dq, R0=dr, B0=db, XPAS=10 * _.mm, KPOS=1),
        ChangeRef(TRANSFORMATIONS=[("YS", -d_offset)]),
        Drift("sd", XL=sd),
        ChangeRef(TRANSFORMATIONS=[("YS", f_offset)]),
        Quadrupole("foc", XL=fq, R0=fr, B0=fb, XPAS=10 * _.mm, KPOS=1),
        ChangeRef(TRANSFORMATIONS=[("YS", -f_offset)]),
        Drift("ld2", XL=ld / 2),
        # Rebelote(K=99, NPASS=10),
        Faisceau(),
    ],
)
emma.WIDTH = 10 * _.cm
emma.IL = 2
z = zgoubidoo.Zgoubi()
r = z(emma).collect()
zgoubidoo.survey(
    beamline=emma,
    reference_frame=zgoubidoo.Frame(),
    with_reference_trajectory=True,
    reference_kinematics=rigidity,
)
artist = zgoubidoo.vis.ZgoubidooPlotlyArtist()
artist.plot_beamline(beamline=emma)
artist.scatter(x=r.tracks_global["XG"], y=r.tracks_global["YG"])
z.cleanup()
