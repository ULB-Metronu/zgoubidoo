import zgoubidoo
from zgoubidoo.commands import Quadrupole

zi = zgoubidoo.Input(name='TEST-INPUT')

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

zi += qf
zi += qd

zi.line
