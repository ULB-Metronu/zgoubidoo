"""Zgoubi converters.

Special methods suffixed with *to_zgoubi* are meant and understood to be conversion methods, to convert from a given
command name.

Loaders and converters for a variety of formats (MAD-X, etc.).

The `converters` module is a collection of

- **converters**: convert 'commands' to Zgoubidoo commands (e.g. read a MAD-X drift and convert it to Zgoubidoo).

This module is meant to be extensible to handle a wide variety of formats. To allow for maximal flexibility and to
encourage the development of converters even for exotic cases, no specific configuration is in place: we favor convention.
The MAD-X converters and converters are to be considered as typical examples and conventions that other modules should
follow.

Examples:
    TODO
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List
import numpy as _np
from zgoubidoo import ureg as _ureg
from zgoubidoo.commands import Quadrupole, Sextupole, Octupole, Command, Marker, Drift, Bend, ChangeRef, Multipole, \
    Cavite, Dipole
from zgoubidoo.constants import ZGOUBI_LABEL_LENGTH as _ZGOUBI_LABEL_LENGTH
if TYPE_CHECKING:
    from georges_core import Kinematics as _Kinematics
    from georges_core.sequences import Element as _Element


def marker_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """
    Create a Marker command from the equivalent MAD-X marker keyword.

    Args:
        element:
        kinematics: kinematic quantities (used for field normalization)
        options: options for the creation of the command

    Returns:

    """
    return [options.get('command', Marker)().generate_label(prefix=element.name)]


def drift_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    return [options.get('command', Drift)(element.name, XL=element['L'])]


def rbend_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    bore_radius = options.get('R0', 10 * _ureg.cm)
    m = Multipole(
        XL=element['L'] * _ureg.meter,
        R0=bore_radius,
        B1=kinematics.brho / (element['L'] / element['ANGLE'] * _ureg.m),
        B2=element['K1L'] / element['L'] * kinematics.brho_ * bore_radius.m_as('m') * _ureg.tesla,
        R1=element['TILT'] * _ureg.radian,
        R2=element['TILT'] * _ureg.radian,
        KPOS=3,
    ).generate_label(prefix=element.name)

    return [
        m
    ]


def sbend_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    if element['ANGLE'] == 0.0:  # Avoid division by zero
        b1 = 0 * _ureg.tesla
    else:
        b1 = kinematics.brho / (element['L'] / _np.abs(element['ANGLE']))
    if _np.isnan(element['E1']):
        we = 0.0 * _ureg.radian
    else:
        we = element['E1']
    if _np.isnan(element['E2']):
        ws = 0.0 * _ureg.radian
    else:
        ws = element['E2']
    if _np.isnan(element['TILT']):
        tilt = 0.0 * _ureg.radian
    else:
        tilt = element['TILT']
    if options.get('command', Bend) == Bend:
        b = Bend(element.name[0:_ZGOUBI_LABEL_LENGTH],
                 XL=element['L'],
                 B1=b1,
                 KPOS=3,
                 W_E=we * _np.sign(element['ANGLE']),
                 W_S=ws * _np.sign(element['ANGLE']),
                 KINEMATICS=kinematics,
                 LENGTH_IS_ARC_LENGTH=options.get('LENGTH_IS_ARC_LENGTH', True)
                 )

    elif options.get('command') == Dipole:
        b = Dipole(element.name[0:_ZGOUBI_LABEL_LENGTH],
                   RM=_np.abs(element.L/element.ANGLE),
                   AT=_np.abs(element.ANGLE),
                   B0=b1,
                   )
    if element['TILT'] != 0:
        b.COLOR = 'goldenrod'
    if element['ANGLE'] < 0:
        return [
            ChangeRef(element.name + '_CRL', TRANSFORMATIONS=[['XR', -(-tilt + _np.pi * _ureg.radian)]]),
            b,
            ChangeRef(element.name + '_CRR', TRANSFORMATIONS=[['XR', (-tilt + _np.pi * _ureg.radian)]]),
        ]
    else:
        if _np.isnan(element['TILT']) or element['TILT'] == 0:
            return [
                b
            ]
        else:
            return [
                ChangeRef(element.name + '_CRL', TRANSFORMATIONS=[['XR', tilt]]),
                b,
                ChangeRef(element.name + '_CRR', TRANSFORMATIONS=[['XR', -tilt]]),
            ]


def quadrupole_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    bore_radius = options.get('R0', 10 * _ureg.cm)
    if element.get('K1') is None and element.get('K1L') is None and element.get('K1BRHO') is None:
        gradient = 0 / _ureg.m ** 2
    elif element.get('K1L') is not None:
        gradient = element['K1L'] / element['L']
    elif element.get('K1') is not None:
        gradient = element['K1'] / _ureg.m ** 2
    elif element.get('K1BRHO') is not None:
        gradient = element['K1BRHO'] / kinematics.brho
    else:
        raise KeyError("K1, K1L or K1BHRHO cannot be defined at the same time.")
    return [Quadrupole(element.name[0:_ZGOUBI_LABEL_LENGTH],
                       XL=element['L'],
                       R0=bore_radius,
                       B0=gradient * kinematics.brho * bore_radius,
                       X_E=0 * _ureg.cm,
                       LAM_E=0 * _ureg.cm,
                       X_S=0 * _ureg.cm,
                       LAM_S=0 * _ureg.cm,
                       ),
            ]


def sextupole_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    return [Sextupole(element.name[0:_ZGOUBI_LABEL_LENGTH], XL=element['L'] * _ureg.meter)]


def octupole_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    return [Octupole(element.name[0:_ZGOUBI_LABEL_LENGTH], XL=element['L'] * _ureg.meter)]


def twcavity_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    cavity = Cavite(
        element.name[0:_ZGOUBI_LABEL_LENGTH],
        IOPT=10,
        XL=1 * _ureg.m,
        FREQ=element['FREQ'] * _ureg.MHz,
        V=element['VOLT'] * _ureg.MV * _np.sign(kinematics.brho),
        PHI_S=(element['LAG'] + _np.pi / 2) * _ureg.radian,
    )
    return [
        Drift(XL=1 * _ureg.mm),
        cavity,
    ]
