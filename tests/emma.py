import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import zgoubidoo
from zgoubidoo.commands import Objet2, Electron, FakeDrift, ChangeRef, Quadrupole, Rebelote, Faisceau
_ = zgoubidoo.ureg

cells = 42
angle = 360/cells * _.degree
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
fb = -6.695 * fr * _.tesla / _.cm
db = 4.704 * dr * _.tesla / _.cm

rigidity = zgoubidoo.physics.Kinematics(10 * _.MeV, particle=zgoubidoo.commands.Electron)
objet = Objet2('BUNCH', BORO=rigidity.brho)
objet.add([0.456, -38.1, 0.0, 0.0, 0.0, 1.0, 1.0])
emma = zgoubidoo.Input(name='EMMA', line=[
    objet,
    Electron(),
    FakeDrift('ld1', XL=ld/2),
    ChangeRef(TRANSFORMATIONS=[('ZR', angle), ('YS', d_offset)]),
    Quadrupole('defoc', XL=dq, R0=dr, B0=db, XPAS=10*_.mm, KPOS=1),
    ChangeRef(TRANSFORMATIONS=[('YS', -d_offset)]),
    FakeDrift('sd', XL=sd),
    ChangeRef(TRANSFORMATIONS=[('YS', f_offset)]),
    Quadrupole('foc', XL=fq, R0=fr, B0=fb, XPAS=10*_.mm, KPOS=1),
    ChangeRef(TRANSFORMATIONS=[('YS', -f_offset)]),
    FakeDrift('ld2', XL=ld/2),
    #Rebelote(K=99, NPASS=10),
    Faisceau()
])
emma.WIDTH = 10 * _.cm
emma.IL = 2
z = zgoubidoo.Zgoubi()
r = z(emma).collect()
zgoubidoo.survey(emma)
artist = zgoubidoo.vis.ZgoubiMpl()
zgoubidoo.vis.beamline(beamline=emma, tracks=r.tracks, artist=artist)
artist.ax.set_aspect('equal', 'datalim')
artist.figure.show()
