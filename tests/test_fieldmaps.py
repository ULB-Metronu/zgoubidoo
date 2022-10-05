import pytest
import numpy as np
import sympy as sp
from itertools import product

import zgoubidoo
from zgoubidoo.commands import Bend, ToscaCartesian2D, Objet2, Drift
from zgoubidoo.fieldmaps import CartesianFieldMap
from zgoubidoo import ureg as _ureg

kin = zgoubidoo.Kinematics(140 * _ureg.MeV)
B1 = (kin.brho / (1 * _ureg.m)) / 50
g_val = 0.15 * _ureg.m

XL = 1 * _ureg.m
WE = 50 * _ureg.degrees
WS = 50 * _ureg.degrees

C0 = 0.1455
C1 = 2.2670
C2 = -0.6395
C3 = 1.1558
C4 = 0
C5 = 0

XE = 2 * g_val
XS = 2 * g_val


def get_zgoubi_rend():
    return Bend('B1',
                XL=XL,
                B1=B1,
                KINEMATICS=kin,
                LAM_E=g_val,
                LAM_S=g_val,
                W_E=WE,
                W_S=WS,
                X_E=XE,
                X_S=XS,
                C0_E=C0,
                C1_E=C1,
                C2_E=C2,
                C3_E=C3,
                C4_E=C4,
                C5_E=C5,
                C0_S=C0,
                C1_S=C1,
                C2_S=C2,
                C3_S=C3,
                C4_S=C4,
                C5_S=C5,
                LENGTH_IS_ARC_LENGTH=False)


def get_zgoubi_fieldmap():
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

    FE = 1 / (1 + sp.exp(sp.Sum(CE[i] * (d_e / ge) ** i, (i, 0, 5))))
    FS = 1 / (1 + sp.exp(sp.Sum(CS[i] * (d_s / gs) ** i, (i, 0, 5))))

    B_x = 0
    B_y = 0
    B_z = Bz0 * FE * FS

    parameters_map = {ge: g_val.m_as('cm'),
                      gs: g_val.m_as('cm'),
                      CE[0]: C0,
                      CE[1]: C1,
                      CE[2]: C2,
                      CE[3]: C3,
                      CE[4]: C4,
                      CE[5]: C5,
                      CS[0]: C0,
                      CS[1]: C1,
                      CS[2]: C2,
                      CS[3]: C3,
                      CS[4]: C4,
                      CS[5]: C5,
                      d_e: (-(x - xe + y * np.tan(-WE.m_as('radians')))) * np.cos(WE.m_as('radians')),
                      d_s: ((x - xl) - xe + y * np.tan(WS.m_as('radians'))) * np.cos(WS.m_as('radians')),
                      Bz0: B1.m_as('kG'),
                      xe: XE.m_as('cm'),
                      xs: XS.m_as('cm'),
                      xl: XL.m_as('cm'),
                      }
    B_z = B_z.doit().subs(parameters_map)

    magnet_magnetic_length = XL + XE + XS
    x_val = np.linspace(0, magnet_magnetic_length.m_as('cm'), 201)
    y_val = np.linspace(-5, 5, 101)
    z_val = [0]

    mesh = np.array(list(product(x_val, y_val, z_val)))

    fm = CartesianFieldMap.generate_from_cartesian_expression(bx_expression=B_x,
                                                              by_expression=B_y,
                                                              bz_expression=B_z,
                                                              mesh=mesh)

    fmap = fm(label1='FMAP',
              path=None,
              filename='test',
              binary=False,
              load_map=True, MOD2=0, generator=ToscaCartesian2D)

    return fmap


@pytest.mark.parametrize("beam", [([0, 0, 0, 0, 1.0]),
                                  ([1, 0, 0, 0, 1.0]),
                                  ([0, 1, 0, 0, 1.0]),
                                  ([0, 0, 0, 1, 1.0]),
                                  ([0, 0, 0, 0, 1.1])])
def test_cartesian_fieldmap(beam):
    ref_beam = Objet2('BUNCH', BORO=kin.brho)
    ref_beam.add(np.array([beam]))

    # Get the rbend from Zgoubi
    zi_rbend = zgoubidoo.Input(name='REND', line=[ref_beam,
                                                  get_zgoubi_rend()
                                                  ])
    zi_rbend.XPAS = 1 * _ureg.mm
    zi_rbend.IL = 2
    zi_rbend.survey(with_reference_trajectory=True, reference_kinematics=kin)
    zr_rbend = zgoubidoo.Zgoubi()(zi_rbend).collect()

    # Get the rbend from fieldMaps
    fmap = get_zgoubi_fieldmap()
    zi_map = zgoubidoo.Input(name='MAP', line=[ref_beam,
                                               Drift('A', XL=-XE),
                                               fmap,
                                               Drift('B', XL=-XS),
                                               ])
    zi_map.XPAS = 1 * _ureg.mm
    zi_map.survey(reference_frame=zgoubidoo.Frame(), with_reference_trajectory=True, reference_kinematics=kin)
    zi_map.IL = 2
    zr_map = zgoubidoo.Zgoubi()(zi_map).collect()

    assert XL + XE + XS == fmap.length

    tracks_frenet_rbend = zr_rbend.tracks_frenet
    tracks_frenet_map = zr_map.tracks_frenet.query("LABEL1 == 'FMAP'")
    tracks_frenet_map['SREF'] += XE.m_as('m')

    # Interpolate wanted quantities
    yt_map = np.interp(tracks_frenet_rbend['SREF'].values, tracks_frenet_map['SREF'].values,
                       tracks_frenet_map['YT'].values)

    t_map = np.interp(tracks_frenet_rbend['SREF'].values, tracks_frenet_map['SREF'].values,
                      tracks_frenet_map['T'].values)

    bz_map = np.interp(tracks_frenet_rbend['SREF'].values, tracks_frenet_map['SREF'].values,
                       tracks_frenet_map['BZ'].values)

    np.testing.assert_allclose(yt_map, tracks_frenet_rbend["YT"].values, atol=1e-4)
    np.testing.assert_allclose(t_map, tracks_frenet_rbend["T"].values, atol=1e-4)
    np.testing.assert_allclose(bz_map, tracks_frenet_rbend["BZ"].values, atol=1e-2)
