"""MAD-X loaders and converters.

Special methods prefixed with *create_madx* are meant and understood to be conversion methods, to convert from a given
MAD command name.

Examples:
    >>> fodo = zgoubidoo.loaders.from_madx_twiss(
    filename='twiss.outx',
    path='/Users/chernals/Downloads',
    options={'DRIFT': {'command': FakeDrift}})
    >>> zi = zgoubidoo.Input(line=[
    Objet5(BORO=fodo.kinematics.brho),
    fodo.particle,
    ] + fodo.sequence)
    >>> zi.XPAS = 1 * _.cm
"""
from typing import Optional, Dict, List
import sys
import pandas as pd
import numpy as np
import itertools
from .. import ureg as _ureg
from ..sequence import Sequence as _Sequence
from ..commands import Dipole, Quadrupole, Sextupole, Octupole, Command, Marker, Drift, Bend, Ymy, ChangeRef, Multipole
from ..kinematics import Kinematics
from ..commands import particules
from ..units import _m
from ..output.madx import load_madx_twiss_headers, load_madx_twiss_table


def create_madx_marker(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> List[Command]:
    """
    Create a Marker command from the equivalent MAD-X marker keyword.

    Args:
        twiss_row:
        kinematics: kinematic quantities (used for field normalization)
        options: options for the creation of the command

    Returns:

    """
    return [options.get('command', Marker)().generate_label(prefix=twiss_row.name[0:8])]


def create_madx_drift(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    return [options.get('command', Drift)(XL=twiss_row['L'] * _ureg.meter).generate_label(prefix=twiss_row.name[0:8])]


def create_madx_rbend(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    return [options.get('command', Bend)(twiss_row.name[0:8],
                                         XL=twiss_row['L'] * _ureg.meter,
                                         B0=kinematics.brho / (twiss_row['L'] / twiss_row['ANGLE'] * _ureg.meter),
                                         )]


def create_madx_sbend_with_multipole(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    bore_radius = options.get('R0', 10 * _ureg.cm)
    return [
        Multipole(
            XL=twiss_row['L'] * _ureg.meter,
            R0=bore_radius,
            B1=kinematics.brho / (twiss_row['L'] / twiss_row['ANGLE'] * _ureg.m),
            B2=twiss_row['K1L'] / twiss_row['L'] * kinematics.brho_ * _m(bore_radius) * _ureg.tesla,
            R1=twiss_row['TILT'] * _ureg.radian,
            R2=twiss_row['TILT'] * _ureg.radian,
            KPOS=3,  # MAD-X convention
        ).generate_label(prefix=twiss_row.name[0:8]),
    ]


def create_madx_sbend(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    if options.get('command', Dipole) is Multipole:
        return create_madx_sbend_with_multipole(twiss_row, kinematics, options)
    else:
        radius = np.abs(twiss_row['L'] / twiss_row['ANGLE']) * _ureg.meter
        b0 = kinematics.brho / radius
        d = Dipole(AT=np.abs(twiss_row['ANGLE']) * _ureg.radian,
                   RM=radius,
                   B0=b0,
                   THETA_E=-twiss_row['E1'] * _ureg.radian,
                   THETA_S=-twiss_row['E2'] * _ureg.radian,
                   ).generate_label(prefix=twiss_row.name[0:8])
        if twiss_row['ANGLE'] < 0:
            return [
                ChangeRef(TRANSFORMATIONS=[['XR', float(twiss_row['TILT']) * _ureg.radian]]),
                Ymy(),
                d,
                Ymy(),
                ChangeRef(TRANSFORMATIONS=[['XR', -float(twiss_row['TILT']) * _ureg.radian]]),
            ]
        else:
            return [
                ChangeRef(TRANSFORMATIONS=[['XR', float(twiss_row['TILT']) * _ureg.radian]]),
                d,
                ChangeRef(TRANSFORMATIONS=[['XR', -float(twiss_row['TILT']) * _ureg.radian]]),
            ]


def create_madx_quadrupole(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """

    bore_radius = options.get('R0', 10 * _ureg.cm)
    return [Quadrupole(XL=twiss_row['L'] * _ureg.meter,
                       R0=bore_radius,
                       B0=twiss_row['K1L'] / twiss_row['L'] * kinematics.brho_* _m(bore_radius) * _ureg.tesla,
                       ).generate_label(prefix=twiss_row.name[0:8])
            ]


def create_madx_sextupole(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    return [Sextupole(twiss_row.name[0:8], XL=twiss_row['L'] * _ureg.meter)]


def create_madx_octupole(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    return [Octupole(twiss_row.name[0:8], XL=twiss_row['L'] * _ureg.meter)]


def from_madx_twiss(filename: str = 'twiss.outx',
                    path: str = '.',
                    columns: List = None,
                    options: Optional[dict] = None,
                    converters: Optional[dict] = None) -> _Sequence:
    """
    TODO
    Args:
        filename: name of the Twiss table file
        path: path to the Twiss table file
        columns: the list of columns in the Twiss file
        options:
        converters:

    Returns:

    """
    madx_converters = {k.split('_')[2].upper(): getattr(sys.modules[__name__], k)
                       for k in globals().keys() if k.startswith('create_madx')}
    conversion_functions = {**madx_converters, **(converters or {})}
    options = options or {}
    twiss_headers = load_madx_twiss_headers(filename, path)
    twiss_table = load_madx_twiss_table(filename, path, columns)
    p = getattr(particules, twiss_headers['PARTICLE'].capitalize())
    k = Kinematics(float(twiss_headers['PC']) * _ureg.GeV_c, particle=p)
    converted_table: list = list(
        twiss_table.apply(
            lambda _: conversion_functions.get(_['KEYWORD'], lambda _, __, ___: None)
            (_, k, options.get(_['KEYWORD'], {})),
            axis=1
        ).values
    )
    return _Sequence(name=twiss_headers['NAME'],
                     sequence=list(itertools.chain.from_iterable(converted_table)),
                     metadata=twiss_headers,
                     particle=p,
                     table=twiss_table,
                     )
