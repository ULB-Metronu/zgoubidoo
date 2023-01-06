"""Vertical FFA generator."""

import copy
from itertools import product

import numpy as _np
import pandas as _pd

from ..units import _Q
from ..units import _ureg as _ureg
from . import CartesianFieldMap


def compute_xi_range_with_edge_angle(tau, d_y, ymax, d_z, zmin, IZ, y_range):
    d_xi = tau * d_y
    n_factor = round(d_z / d_xi)
    if n_factor == 0:
        n_factor = 1
    d_xi = d_z / n_factor
    d_y = d_xi / tau
    xi_supp = tau * ymax.m_as("m")
    n_xi_supp = round(xi_supp / d_xi + 0.5)

    IXI = IZ * n_factor + n_xi_supp
    xi_min = zmin.to("m") - n_xi_supp * d_xi * _ureg.m
    IY = round(y_range / d_y + 0.5)
    return d_xi, d_y, IXI, xi_min, n_factor, n_xi_supp, IY


def compute_xi_range_without_edge_angle(d_z, IZ, zmin, IY_approx):
    d_xi = d_z
    IXI = IZ
    xi_min = zmin.to("m")
    n_factor = 1
    n_xi_supp = 0
    IY = IY_approx
    return d_xi, IXI, xi_min, n_factor, n_xi_supp, IY


def compute_range_and_steps(
    xmin: _Q,
    xmax: _Q,
    ymin: _Q,
    ymax: _Q,
    zmin: _Q,
    zmax: _Q,
    IX,
    IY_approx,
    IZ,
    tau,
):
    xi_max = zmax
    x_range = (xmax - xmin).m_as("m")
    y_range = (ymax - ymin).m_as("m")
    z_range = (zmax - zmin).m_as("m")

    d_z = z_range / IZ
    d_y = y_range / IY_approx
    d_x = x_range / IX

    if tau != 0.0:
        d_xi, d_y, IXI, xi_min, n_factor, n_xi_supp, IY = compute_xi_range_with_edge_angle(
            tau,
            d_y,
            ymax,
            d_z,
            zmin,
            IZ,
            y_range,
        )

    else:
        d_xi, IXI, xi_min, n_factor, n_xi_supp, IY = compute_xi_range_without_edge_angle(d_z, IZ, zmin, IY_approx)

    return xi_min, xi_max, IXI, d_xi, d_x, n_xi_supp, n_factor, d_y, IY


def compute_A_matrix(n, k, tau):
    a = _np.zeros(((n + 1) + 1, (2 * n + 2) + 1))
    a[0, 0] = 1 / k

    for i in range(_np.shape(a)[0] - 1):
        for j in range(2 * (i + 1) + 1):
            if j == 0:
                a[i + 1, j] = -(k**2) * a[i, j]
            if j == 1:
                a[i + 1, j] = -(k**2) * a[i, j] + 2 * k * tau * a[i, j - 1]
            else:
                a[i + 1, j] = -(k**2) * a[i, j] + 2 * k * tau * a[i, j - 1] - (1 + tau**2) * a[i, j - 2]
    return a


def compute_T_matrix(n_prime):
    t = _np.zeros((n_prime + 1, (n_prime + 1) + 1))
    t[0, 1] = 1
    for i in range(_np.shape(t)[0] - 1):
        for j in range(0, i + 3):
            if j == 0:
                t[i + 1, j] = (j + 1) * t[i, j + 1]
            elif j == i + 2:
                t[i + 1, j] = -(j - 1) * t[i, j - 1]
            else:
                t[i + 1, j] = (j + 1) * t[i, j + 1] - (j - 1) * t[i, j - 1]
    return t


def compute_tanh_multiple_orders(l, L, IXI, d_xi, xi_min, n_prime):
    tan = _np.zeros(((n_prime + 1) + 1, IXI + 1))
    for j in range(_np.shape(tan)[0]):
        for xixi in range(IXI + 1):
            xi = xi_min.to("m").magnitude + xixi * d_xi
            t_1j = (_np.tanh(xi / l)) ** j
            t_2j = (_np.tanh((xi - L) / l)) ** j
            tan[j, xixi] = t_1j - t_2j
    return tan


def compute_fringe_field_function_derivatives(gap, Lmag, n_prime, IXI, d_xi, xi_min):
    l = gap.to("m").magnitude
    L = Lmag.to("m").magnitude
    t = compute_T_matrix(n_prime)
    tan = compute_tanh_multiple_orders(l, L, IXI, d_xi, xi_min, n_prime)

    scaling = _np.zeros((n_prime + 1, 1))
    for nn in range(n_prime + 1):
        scaling[nn, :] = 1 / (2 * l**nn)
    f_nprime = t.dot(tan)
    f_nprime = scaling * f_nprime
    return f_nprime


def compute_g_h_matrix(n, a, f_nprime):
    g = a[:, 0 : 2 * n + 1].dot(f_nprime[0 : 2 * n + 1, :])
    h = a[:, 0 : 2 * n + 1].dot(f_nprime[1 : 2 * n + 2, :])
    return g, h


def compute_field_in_initial_plane(d_x, IX, n, xmin, g, h, B0, k, tau):
    # B DANS LE PLAN XI_Z pour Y=0

    X = _np.zeros((IX + 1, n + 1))
    X_prime = _np.zeros((IX + 1, n + 1))

    for xx in range(IX + 1):
        x = xmin.to("m").magnitude + xx * d_x
        for nn in range(n + 1):
            X[xx, nn] = x ** (2 * nn + 1) / _np.math.factorial(2 * nn + 1)
            X_prime[xx, nn] = x ** (2 * nn) / _np.math.factorial(2 * nn)

    BX = B0 * X.dot(g[1:, :])
    BY = B0 * X_prime.dot(k * g[0 : n + 1, :] - tau * h[0 : n + 1, :])
    BZ = B0 * X_prime.dot(h[0 : n + 1, :])
    B = _np.dstack((BX, BY, BZ))
    return B


def compute_total_fieldmap(B, tau, k, IY, ymin, d_y, n_xi_supp, IXI, n_factor):
    B_fieldmap = []

    if tau != 0.0:
        for yy in range(IY + 1):
            y = ymin.to("m").magnitude + yy * d_y
            B_XXI = copy.deepcopy(B[:, n_xi_supp - yy : IXI + 1 - yy, :])
            B_XXI = _np.exp(k * y) * B_XXI
            B_XZ = copy.deepcopy(B_XXI[:, ::n_factor, :])
            B_fieldmap.append(B_XZ)
    else:
        for yy in range(IY + 1):
            y = ymin.to("m").magnitude + yy * d_y
            B_XXI = copy.deepcopy(B[:, : IXI + 1, :])
            B_XXI = _np.exp(k * y) * B_XXI
            B_XZ = copy.deepcopy(B_XXI[:, ::n_factor, :])
            B_fieldmap.append(B_XZ)

    B_fieldmap = _np.array(B_fieldmap)
    return B_fieldmap


def generate_vFFA_fieldmap(
    B0: _Q,
    k: _Q,
    tau: int,
    Lmag: _Q,
    gap: _Q,
    xmin: _Q,
    xmax: _Q,
    ymin: _Q,
    ymax: _Q,
    z_ff_1: _Q,
    z_ff_2: _Q,
    n: int,
    IX: int,
    IY_approx: int,
    IZ: int,
):
    k, B0 = k.m_as("1/m"), B0.to("kilogauss")
    xmin, xmax, ymin, ymax, z_ff_1, z_ff_2 = (
        xmin.to("m"),
        xmax.to("m"),
        ymin.to("m"),
        ymax.to("m"),
        z_ff_1.to(
            "m",
        ),
        z_ff_2.to("m"),
    )
    Lmag, gap = Lmag.to("m"), gap.to("m")
    zmin = -z_ff_1
    zmax = Lmag + z_ff_2

    xi_min, xi_max, IXI, d_xi, d_x, n_xi_supp, n_factor, d_y, IY = compute_range_and_steps(
        xmin,
        xmax,
        ymin,
        ymax,
        zmin,
        zmax,
        IX,
        IY_approx,
        IZ,
        tau,
    )

    a = compute_A_matrix(n, k, tau)
    n_prime = 2 * n + 2
    f_nprime = compute_fringe_field_function_derivatives(gap, Lmag, n_prime, IXI, d_xi, xi_min)
    g, h = compute_g_h_matrix(n, a, f_nprime)
    B = compute_field_in_initial_plane(d_x, IX, n, xmin, g, h, B0, k, tau)
    B_fieldmap = compute_total_fieldmap(B, tau, k, IY, ymin, d_y, n_xi_supp, IXI, n_factor)

    B_fieldmap_reshaped = B_fieldmap.reshape((IY + 1) * (IX + 1) * (IZ + 1), 3)

    x_val = _np.linspace(xmin.m_as("cm"), xmax.m_as("cm"), IX + 1)
    y_val = _np.linspace(ymin.m_as("cm"), ymax.m_as("cm"), IY + 1)
    z_val = _np.linspace((zmin + z_ff_1).m_as("cm"), (zmax + z_ff_1).m_as("cm"), IZ + 1)
    mesh = _np.array(list(product(y_val, x_val, z_val)))

    fieldmap = _pd.DataFrame(
        {
            "Y": mesh[:, 1],
            "Z": mesh[:, 0],
            "X": mesh[:, 2],
            "BY": B_fieldmap_reshaped[:, 0],
            "BZ": B_fieldmap_reshaped[:, 1],
            "BX": B_fieldmap_reshaped[:, 2],
        },
    )

    return fieldmap


class VFFAFieldMap(CartesianFieldMap):
    def __init__(self, field_map: _pd.DataFrame):
        super().__init__(field_map)

    @classmethod
    def generate(
        cls,
        B0,
        k,
        tau,
        Lmag,
        gap,
        xmin,
        xmax,
        ymin,
        ymax,
        z_ff_1,
        z_ff_2,
        n,
        IX,
        IY_approx,
        IZ,
    ):
        """
        Method to generate a vFFA field map, with tanh fringe field and possible edge angle

        Args:
            B0: Reference magnetic field
            k: Field index
            tau: Tangent of the edge angle
            Lmag: Length of the magnet
            gap: Fringe length
            xmin: Horizontal extent of the field map
            xmax : Horizontal extent of the field map
            ymin: Vertical extent of the field map
            ymax: Vertical extent of the field map
            z_ff_1: Additional length before the magnet for the longitudinal extent of the field map
            z_ff_2: Additional length after the magnet for the longitudinal extent of the field map
            n: Order of the expansion
            IX: Number of nodes of the mesh - X direction
            IY_approx: Number of nodes of the mesh - Y direction
            IZ: Number of nodes of the mesh - Z direction

        Returns:
            A vFFA FieldMap.
        """
        return cls(
            field_map=generate_vFFA_fieldmap(
                B0,
                k,
                tau,
                Lmag,
                gap,
                xmin,
                xmax,
                ymin,
                ymax,
                z_ff_1,
                z_ff_2,
                n,
                IX,
                IY_approx,
                IZ,
            ),
        )
