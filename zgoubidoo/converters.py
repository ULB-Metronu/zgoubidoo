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
import logging
from typing import TYPE_CHECKING, Dict, List, Union
import numpy as _np
from zgoubidoo import ureg as _ureg
from zgoubidoo.commands import Quadrupole, Sextupole, Octupole, Command, Marker, Drift, Bend, ChangeRef, Multipole, \
    Cavite, Dipole, Solenoid, ChangRef
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
    # if option generate prefix, etc .generate_label(prefix=element.name)
    return [options.get('command', Marker)(element.name)]


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
    element['K1L'] = element['K1'] * element['L']
    m = Multipole(LABEL1=element.name[0:_ZGOUBI_LABEL_LENGTH],
                  XL=element['L'],
                  R0=bore_radius,
                  B1=kinematics.brho / (element['L'] / element['ANGLE']),
                  R1=element['TILT'] * _ureg.radian,
                  R2=element['TILT'] * _ureg.radian,
                  KPOS=3)

    return [m]


def sbend_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    if element.get('ANGLE') == 0.0 and element.get('B') is not None:
        h = element['B'] / kinematics.brho
        element['ANGLE'] = element['L'] * h
    if element['ANGLE'] == 0.0:  # Avoid division by zero
        b1 = 0 * _ureg.tesla
    else:
        b1 = kinematics.brho / (element['L'] / _np.abs(element['ANGLE']))
    if _np.isnan(element['E1']):
        we = 0.0 * _ureg.degrees
    else:
        we = element['E1'].to('degrees')
    if _np.isnan(element['E2']):
        ws = 0.0 * _ureg.degrees
    else:
        ws = element['E2'].to('degrees')
    if _np.isnan(element['TILT']):
        tilt = 0.0 * _ureg.radian
    else:
        tilt = element['TILT']
    if options.get('command', Bend) == Bend:
        b = Bend(element.name[0:_ZGOUBI_LABEL_LENGTH],
                 XL=element['L'],
                 B1=b1,
                 KPOS=3,
                 W_E=we * _np.sign(element['ANGLE'].magnitude),
                 W_S=ws * _np.sign(element['ANGLE'].magnitude),
                 KINEMATICS=kinematics,
                 LENGTH_IS_ARC_LENGTH=options.get('LENGTH_IS_ARC_LENGTH', True)
                 )

    elif options.get('command') == Dipole:
        if element.K1 is not None and not _np.isnan(element.K1):
            field_index = (_np.abs(
                element.L / element.ANGLE).to('m') ** 2 * getattr(element, 'K1', 0.0 * _ureg.m ** -2)
                           ).magnitude
        elif element.N is not None and not _np.isnan(element.N):
            field_index = element.N
        else:
            field_index = 0

        if element.K2 is not None and not _np.isnan(element.K1):
            field_index_B = (_np.abs(
                element.L / 2 * element.ANGLE).to('m') ** 3 * getattr(element, 'K2', 0.0 * _ureg.m ** -3)
                             ).magnitude
        elif element.B is not None and not _np.isnan(element.B):
            field_index_B = element.B
        else:
            field_index_B = 0

        b = Dipole(element.name[0:_ZGOUBI_LABEL_LENGTH],
                   RM=_np.abs(element.L / element.ANGLE).to('meter'),
                   AT=_np.abs(element.ANGLE).to('degrees'),
                   THETA_E=we * _np.sign(element['ANGLE'].magnitude),
                   LAM_E=0 * _ureg.cm,  # Default value
                   THETA_S=-ws * _np.sign(element['ANGLE'].magnitude),
                   LAM_S=0 * _ureg.cm,
                   B0=b1,
                   N=field_index,
                   B=field_index_B
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
    if element['L'] == 0 * _ureg.m:
        raise ValueError("Quadrupole length cannot be zero.")
    if element.get('B1') is not None and element.get('R') is not None and not _np.isnan(element['B1']) \
            and not _np.isnan(element['R']):
        b_field = element['B1']
        bore_radius = element['R']
    else:
        bore_radius = options.get('R0', 10 * _ureg.cm)
        if element.get('K1') is None and element.get('K1L') is None and element.get('K1BRHO') is None and element.get(
                'K1S') is None and element.get('K1SL') is None:
            gradient = 0 / _ureg.m ** 2
        elif element.get('K1') is not None and element.get('K1L') is not None:
            if element['K1'] == 0:
                gradient = element['K1L'] / element['L']
            elif element['K1L'] == 0:
                gradient = element['K1'] / _ureg.m ** 2 if isinstance(element['K1'], float) else element['K1']
            else:
                # TODO Clean converters
                if element['K1L'] / element['L'] == element['K1']:
                    gradient = element['K1']
                else:
                    raise KeyError("K1 and K1L cannot be non zero at the same time.")
        elif element.get('K1L') is not None and element.get('K1SL') is not None:
            if element.get('K1SL') == 0:
                gradient = element['K1L'] / element['L']
            if element.get('K1L') == 0:
                gradient = element['K1SL'] / element['L']
                changeref_in = ChangRef("changeref_in", TRANSFORMATIONS=[('XR', -45 * _ureg.degree)])
                changeref_out = ChangRef("changeref_out", TRANSFORMATIONS=[('XR', 45 * _ureg.degree)])
        elif element.get('K1') is not None:
            gradient = element['K1'] / _ureg.m ** 2 if isinstance(element['K1'], float) else element['K1']
        elif element.get('K1BRHO') is not None:
            gradient = element['K1BRHO'] / kinematics.brho
        elif element.get('K1S') is not None:
            gradient = element['K1S'] / _ureg.m ** 2 if isinstance(element['K1S'], float) else element['K1S']
            changeref_in = ChangRef("changeref_in", TRANSFORMATIONS=[('XR', -45 * _ureg.degree)])
            changeref_out = ChangRef("changeref_out", TRANSFORMATIONS=[('XR', 45 * _ureg.degree)])
        else:
            raise KeyError("K1, K1L or K1BHRHO cannot be defined at the same time.")
        b_field = gradient * kinematics.brho * bore_radius

    if b_field == 0:
        logging.warning("Quadrupole field is 0. Your input file may be wrong.")
    quad = Quadrupole(element.name[0:_ZGOUBI_LABEL_LENGTH],
                      XL=element['L'],
                      R0=bore_radius,
                      B0=b_field,
                      X_E=0 * _ureg.cm,
                      LAM_E=0 * _ureg.cm,
                      X_S=0 * _ureg.cm,
                      LAM_S=0 * _ureg.cm,
                      )

    if element.get('K1S') is not None or element.get('K1SL') is not None and element.get('K1SL') != 0:
        return [
            changeref_in,
            quad,
            changeref_out
        ]
    else:
        return [
            quad
        ]


def solenoid_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    if element['L'] == 0 * _ureg.m:
        raise ValueError("Solenoïde length cannot be zero.")  # to check
    if element.get('B0') is not None and element.get('R') is not None and not _np.isnan(element['B0']) \
            and not _np.isnan(element['R']):
        b_field = element['B0']
        bore_radius = element['R']
    else:
        bore_radius = options.get('R0', 1 * _ureg.m)
        if element.get('KS') is None and element.get('KSI') is None:
            gradient = 0 / _ureg.m ** 2
        elif element.get('KSI') is not None:
            gradient = element['KSI'] / element['L']
        b_field = gradient * kinematics.brho

    return [Solenoid(element.name[0:_ZGOUBI_LABEL_LENGTH],
                     XL=element['L'],
                     R0=bore_radius,
                     B0=b_field,
                     X_E=0 * _ureg.cm,
                     X_S=0 * _ureg.cm,
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

    if element['L'] == 0 * _ureg.m:
        raise ValueError("Sextupole length cannot be zero.")
    if element.get('B1') is not None and element.get('R') is not None and not _np.isnan(element['B1']) \
            and not _np.isnan(element['R']):
        b_field = element['B1']
        bore_radius = element['R']
    else:
        bore_radius = options.get('R0', 10 * _ureg.cm)
        if element.get('K2') is None and element.get('K2L') is None and element.get('K2BRHO') is None and element.get(
                'K2S') is None and element.get('K2SL') is None:
            gradient = 0 / _ureg.m ** 2
        elif element.get('K2') is not None and element.get('K2L') is not None:
            if element['K2'] == 0:
                gradient = element['K2L'] / element['L']
            elif element['K2L'] == 0:
                gradient = element['K2'] / _ureg.m ** 2 if isinstance(element['K2'], float) else element['K2']
            else:
                gradient = element['K2L'] / element['L']
                # raise KeyError("K2 and K2L cannot be non zero at the same time.")
        elif element.get('K2L') is not None and element.get('K1SL') is not None:
            if element.get('K2SL') == 0:
                gradient = element['K2L'] / element['L']
            if element.get('K2L') == 0:
                gradient = element['K2SL'] / element['L']
                changeref_in = ChangRef("changeref_in", TRANSFORMATIONS=[('XR', -45 * _ureg.degree)])
                changeref_out = ChangRef("changeref_out", TRANSFORMATIONS=[('XR', 45 * _ureg.degree)])
        elif element.get('K2') is not None:
            gradient = element['K2'] / _ureg.m ** 3 if isinstance(element['K2'], float) else element['K2']
        elif element.get('K2BRHO') is not None:
            gradient = element['K2BRHO'] / kinematics.brho
        elif element.get('K2S') is not None:
            gradient = element['K2S'] / _ureg.m ** 3 if isinstance(element['K1S'], float) else element['K2S']
            changeref_in = ChangRef("changeref_in", TRANSFORMATIONS=[('XR', -45 * _ureg.degree)])
            changeref_out = ChangRef("changeref_out", TRANSFORMATIONS=[('XR', 45 * _ureg.degree)])
        else:
            raise KeyError("K2, K2L or K1BHRHO cannot be defined at the same time.")
        b_field = (gradient * kinematics.brho * bore_radius ** 2) / 2

    return [Sextupole(element.name[0:_ZGOUBI_LABEL_LENGTH],
                      XL=element['L'],
                      R0=bore_radius,
                      B0=b_field,
                      X_E=0 * _ureg.cm,
                      LAM_E=0 * _ureg.cm,
                      X_S=0 * _ureg.cm,
                      LAM_S=0 * _ureg.cm,
                      )]


def octupole_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    if element['L'] == 0 * _ureg.m:
        raise ValueError("Octupole length cannot be zero.")
    if element.get('B1') is not None and element.get('R') is not None and not _np.isnan(element['B1']) \
            and not _np.isnan(element['R']):
        b_field = element['B1']
        bore_radius = element['R']
    else:
        bore_radius = options.get('R0', 10 * _ureg.cm)
        if element.get('K3') is None and element.get('K3L') is None and element.get('K3BRHO') is None and element.get(
                'K3S') is None and element.get('K3SL') is None:
            gradient = 0 / _ureg.m ** 2
        elif element.get('K3') is not None and element.get('K3L') is not None:
            if element['K3'] == 0:
                gradient = element['K3L'] / element['L']
            elif element['K3L'] == 0:
                gradient = element['K3'] / _ureg.m ** 2 if isinstance(element['K3'], float) else element['K3']
            else:
                gradient = element['K3L'] / element['L']
                # raise KeyError("K3 and K3L cannot be non zero at the same time.")
        elif element.get('K3L') is not None and element.get('K3SL') is not None:
            if element.get('K3SL') == 0:
                gradient = element['K3L'] / element['L']
            if element.get('K3L') == 0:
                gradient = element['K3SL'] / element['L']
                changeref_in = ChangRef("changeref_in", TRANSFORMATIONS=[('XR', -45 * _ureg.degree)])
                changeref_out = ChangRef("changeref_out", TRANSFORMATIONS=[('XR', 45 * _ureg.degree)])
        elif element.get('K3') is not None:
            gradient = element['K3'] / _ureg.m ** 3 if isinstance(element['K3'], float) else element['K3']
        elif element.get('K3BRHO') is not None:
            gradient = element['K3BRHO'] / kinematics.brho
        elif element.get('K3S') is not None:
            gradient = element['K3S'] / _ureg.m ** 3 if isinstance(element['K3S'], float) else element['K3S']
            changeref_in = ChangRef("changeref_in", TRANSFORMATIONS=[('XR', -45 * _ureg.degree)])
            changeref_out = ChangRef("changeref_out", TRANSFORMATIONS=[('XR', 45 * _ureg.degree)])
        else:
            raise KeyError("K3, K3L or K3BHRHO cannot be defined at the same time.")
        b_field = (gradient * kinematics.brho * bore_radius ** 3) / _np.math.factorial(3)

    return [Octupole(element.name[0:_ZGOUBI_LABEL_LENGTH],
                     XL=element['L'],
                     R0=bore_radius,
                     B0=b_field,
                     X_E=0 * _ureg.cm,
                     LAM_E=0 * _ureg.cm,
                     X_S=0 * _ureg.cm,
                     LAM_S=0 * _ureg.cm,
                     )]


def multipole_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """

    multipole_length = element['L']
    k0 = element.get('K0L', 0) / multipole_length
    k1 = element.get('K1L', 0 * _ureg.m ** -1) / multipole_length
    k2 = element.get('K2L', 0 * _ureg.m ** -2) / multipole_length
    k3 = element.get('K3L', 0 * _ureg.m ** -3) / multipole_length
    k4 = element.get('K4L', 0 * _ureg.m ** -4) / multipole_length

    bore_radius = options.get('R0', 10.0 * _ureg.cm)

    b1_field = k0 * kinematics.brho
    b2_field = k1 * kinematics.brho * bore_radius
    b3_field = (k2 * kinematics.brho * bore_radius ** 2) / _np.math.factorial(2)
    b4_field = (k3 * kinematics.brho * bore_radius ** 3) / _np.math.factorial(3)
    b5_field = (k4 * kinematics.brho * bore_radius ** 4) / _np.math.factorial(4)

    return [Multipole(element.name[0:_ZGOUBI_LABEL_LENGTH],
                      XL=multipole_length,
                      R0=bore_radius,
                      B1=b1_field,
                      B2=b2_field,
                      B3=b3_field,
                      B4=b4_field,
                      B5=b5_field,
                      X_E=0 * _ureg.cm,
                      LAM_E=0 * _ureg.cm,
                      X_S=0 * _ureg.cm,
                      LAM_S=0 * _ureg.cm,
                      )]
    # TODO take into account the changeRef if K1S
    # if element.get('K1S') is not None or element.get('K1SL') is not None and element.get('K1SL') != 0:
    #     return [
    #         changeref_in,
    #         quad,
    #         changeref_out
    #     ]
    # else:
    #     return [
    #         quad
    #     ]


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
        V=element['VOLT'] * _ureg.MV * _np.sign(kinematics.brho.magnitude),
        PHI_S=(element['LAG'] + _np.pi / 2) * _ureg.radian,
    )
    return [
        Drift(XL=1 * _ureg.mm),
        cavity,
    ]


def changeref_to_zgoubi(element: _Element, kinematics: _Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        element:
        kinematics:
        options:

    Returns:

    """
    print(element)
    srotation = ChangeRef(
        element.name[0:_ZGOUBI_LABEL_LENGTH],
        TRANSFORMATIONS=[("XR", 180 * _ureg.degrees)]
    )
    return [
        srotation
    ]
