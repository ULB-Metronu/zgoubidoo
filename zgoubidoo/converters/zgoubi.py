"""MAD-X converters.

Special methods prefixed with *to_zgoubi* are meant and understood to be conversion methods, to convert from a given
MAD command name.

Examples:
    TODO
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List
import numpy as _np
from .. import ureg as _ureg
from ..commands import Quadrupole, Sextupole, Octupole, Command, Marker, Drift, Bend, ChangeRef, Multipole, Cavite
if TYPE_CHECKING:
    from ..kinematics import Kinematics as _Kinematics
    from ..sequences import Element as _Element


def marker_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """
    Create a Marker command from the equivalent MAD-X marker keyword.

    Args:
        element:
        kinematics: kinematic quantities (used for field normalization)
        options: options for the creation of the command

    Returns:

    """
    return [options.get('command', Marker)().generate_label(prefix=element.name[0:8])]


def drift_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    return [options.get('command', Drift)(XL=element['L']).generate_label(prefix=element.name[0:8])]


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
    b = options.get('command', Bend)(element.name[0:8],
                                     XL=element['L'],
                                     B1=b1,
                                     KPOS=3,
                                     W_E=we * _np.sign(element['ANGLE']),
                                     W_S=ws * _np.sign(element['ANGLE']),
                                     )
    if element['TILT'] != 0:
        b.COLOR = 'goldenrod'
    if element['ANGLE'] < 0:
        return [
            ChangeRef(TRANSFORMATIONS=[['XR', -(-tilt + _np.pi * _ureg.radian)]]).generate_label(
                prefix=element.name + '_CRL'
            ),
            b,
            ChangeRef(TRANSFORMATIONS=[['XR', (-tilt + _np.pi * _ureg.radian)]]).generate_label(
                prefix=element.name + '_CRR'
            ),
        ]
    else:
        if _np.isnan(element['TILT']):
            return [
                b
            ]
        else:
            return [
                ChangeRef(TRANSFORMATIONS=[['XR', tilt]]).generate_label(
                    prefix=element.name + '_CRL'
                ),
                b,
                ChangeRef(TRANSFORMATIONS=[['XR', -tilt]]).generate_label(
                    prefix=element.name + '_CRR'
                ),
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
    if element.get('K1') is None and element.get('K1L') is None:
        gradient = 0 / _ureg.m**2
    elif element.get('K1L') is not None:
        gradient = element['K1L'] / element['L']
    elif element.get('K1') is not None:
        gradient = element['K1']
    else:
        raise KeyError("K1 and K1L cannot be defined at the same time.")
    return [Quadrupole(element.name[0:8],
                       XL=element['L'],
                       R0=bore_radius,
                       B0=gradient * kinematics.brho * bore_radius,
                       XE=0 * _ureg.cm,
                       LAM_E=0 * _ureg.cm,
                       XS=0 * _ureg.cm,
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
    return [Sextupole(element.name[0:8], XL=element['L'] * _ureg.meter)]


def octupole_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    return [Octupole(element.name[0:8], XL=element['L'] * _ureg.meter)]


def twcavity_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    cavity = Cavite(
        IOPT=10,
        XL=1 * _ureg.m,
        FREQ=element['FREQ'] * _ureg.MHz,
        V=element['VOLT'] * _ureg.MV * _np.sign(kinematics.brho),
        PHI_S=(element['LAG'] + _np.pi / 2) * _ureg.radian,
    ).generate_label(prefix=element.name[0:8])
    return [
        Drift(XL=1 * _ureg.mm),
        cavity,
    ]
