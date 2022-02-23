import numpy as np
import sympy as sp
from itertools import product

from zgoubidoo.commands import ToscaCartesian2D
from zgoubidoo.fieldmaps import CartesianFieldMap
from zgoubidoo import ureg as _ureg


def test_cartesian_fieldmap():
    x, y, z = sp.symbols('x:z')

    ge = sp.symbols('ge')
    gs = sp.symbols('gs')

    CE = sp.IndexedBase('CE')
    CS = sp.IndexedBase('CS')

    Bz0 = sp.symbols('BZ0')

    i = sp.symbols('i', integer=True)
    d_e = sp.symbols('d_e')
    d_s = sp.symbols('d_s')
    xe = sp.symbols('xe')
    xs = sp.symbols('xs')
    xl = sp.symbols('xl')

    we = 0 * _ureg.degrees
    ws = 0 * _ureg.degrees
    FE = 1 / (1 + sp.exp(sp.Sum(CE[i] * (d_e / ge) ** i, (i, 0, 5))))
    FS = 1 / (1 + sp.exp(sp.Sum(CS[i] * (d_s / gs) ** i, (i, 0, 5))))

    B_x = 0
    B_y = 0
    B_z = Bz0 * FE * FS

    # Define values for free parameters
    parameters_map = {ge: 4,
                      gs: 4,
                      CE[0]: 0,
                      CE[1]: 1,
                      CE[2]: 0,
                      CE[3]: 0,
                      CE[4]: 0,
                      CE[5]: 0,
                      CS[0]: 0,
                      CS[1]: 1,
                      CS[2]: 0,
                      CS[3]: 0,
                      CS[4]: 0,
                      CS[5]: 0,
                      d_e: (-(x - xe + y * np.tan(-we.m_as('radians')))) * np.cos(
                          we.m_as('radians')),
                      d_s: ((x - xl) - xe + y * np.tan(ws.m_as('radians'))) * np.cos(
                          ws.m_as('radians'))
                      }
    B_z = B_z.doit().subs(parameters_map)

    magnet_field = 0.5 * _ureg.T
    magnet_length = 0.3 * _ureg.m
    magnet_xe = 0 * _ureg.cm
    magnet_xs = 0 * _ureg.cm

    B_z = B_z.subs({Bz0: magnet_field.m_as('kG'),
                    xl: magnet_length.m_as('cm'),
                    xe: magnet_xe.m_as('cm'),
                    xs: magnet_xs.m_as('cm')})

    magnet_magnetic_length = magnet_length + magnet_xe + magnet_xs
    x_val = np.linspace(0, magnet_magnetic_length.m_as('cm'), 201)
    y_val = np.linspace(-5, 5, 101)
    z_val = [0]

    mesh = np.array(list(product(x_val, y_val, z_val)))

    fm = CartesianFieldMap.generate_from_cartesian_expression(bx_expression=B_x,
                                                              by_expression=B_y,
                                                              bz_expression=B_z,
                                                              mesh=mesh)

    fmap = fm(label1='a',
              path=None,
              filename='test',
              binary=False,
              load_map=True, MOD2=0, generator=ToscaCartesian2D)

    assert magnet_magnetic_length == fmap.length
