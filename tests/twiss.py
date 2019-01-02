import zgoubidoo
from zgoubidoo.commands import FakeDrift, Quadrupole, Proton, Objet5

_ = zgoubidoo.ureg

qf = Quadrupole(
    XL=50 * _.cm,
    B0=0.01 * _.tesla,
    XPAS=10 * _.cm,
)

qd = Quadrupole(
    XL=50 * _.cm,
    B0=-0.01 * _.tesla,
    XPAS=10 * _.cm,
)

particule = Proton()
objet = Objet5('BUNCH', BORO=2149 * _.kilogauss * _.cm)

fodo = zgoubidoo.Input(name='FODO', line=[
    objet,
    particule,
    qf,
    FakeDrift(XL=1 * _.m, XPAS=100 * _.cm),
    qd,
    FakeDrift(XL=1 * _.m, XPAS=100 * _.cm),
])

z = zgoubidoo.Zgoubi()

out = z(fodo())
zgoubidoo.survey(fodo)

r = zgoubidoo.twiss.compute_transfer_matrix(fodo, out.tracks)
twiss = zgoubidoo.twiss.compute_twiss(r)
