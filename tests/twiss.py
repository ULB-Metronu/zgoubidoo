import zgoubidoo
from zgoubidoo.commands import FakeDrift, Quadrupole, Proton, Objet5, Matrix

_ = zgoubidoo.ureg

qf = Quadrupole(XL=50 * _.cm)
qf.B0 = 0.01 * _.tesla
qf.XPAS = 10 * _.cm
qd = Quadrupole(XL=50 * _.cm)
qd.B0 = -0.01 * _.tesla
qd.XPAS = 10 * _.cm

particule = Proton()
objet = Objet5('BUNCH', BORO=2149 * _.kilogauss * _.cm)

fodo = zgoubidoo.Input(name='FODO', line=[
    objet,
    particule,
    qf,
    FakeDrift(XL=1 * _.m, XPAS=100 * _.cm),
    qd,
    FakeDrift(XL=1 * _.m, XPAS=100 * _.cm),
    Matrix()
])

z = zgoubidoo.Zgoubi()

out = z(fodo())
zgoubidoo.survey(fodo)

m = out.matrix.iloc[-1]['CMUY']
b = out.matrix.iloc[-1]['BETA11']
r = zgoubidoo.twiss.compute_transfer_matrix(fodo, out.tracks)
x = (r.iloc[-1]['R11']+r.iloc[-1]['R22'])/2
import math
mu = math.acos(x)
beta = r.iloc[-1]['R12'] / math.sin(mu)
#twiss = zgoubidoo.twiss.compute_twiss(r, zgoubidoo.read_matrix_file().iloc[-1])
