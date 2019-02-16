"""
TODO
"""
from typing import Optional, Dict
import os
import sys
import pandas as pd
import numpy as np
from .. import ureg as _ureg
from ..physics import Sequence as _Sequence
from ..commands import Dipole, Quadrupole, Sextupole, Octupole, Command, Marker, Drift, Bend
from ..kinematics import Kinematics
from ..commands import particules


def create_madx_marker(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> Command:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    return Marker(twiss_row.name[0:8])


def create_madx_drift(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> Command:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    return options.get('drift_command', Drift)(twiss_row.name[0:8], XL=twiss_row['L'] * _ureg.meter)


def create_madx_rbend(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> Command:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    return options.get('rbend_command', Bend)(twiss_row.name[0:8],
                                              XL=twiss_row['L'] * _ureg.meter,
                                              B0=kinematics.brho / (twiss_row['L'] / twiss_row['ANGLE'] * _ureg.meter),
                                              )


def create_madx_sbend(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> Command:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    radius = np.abs(twiss_row['L'] / twiss_row['ANGLE']) * _ureg.meter
    d = options.get('sbend_command', Dipole)(twiss_row.name[0:8],
                                             AT=np.abs(twiss_row['ANGLE']) * _ureg.radian,
                                             RM=radius,
                                             B0=kinematics.brho / radius,
                                             )
    return d


def create_madx_quadrupole(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> Command:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    return Quadrupole(twiss_row.name[0:8],
                      XL=twiss_row['L'] * _ureg.meter,
                      R0=options.get('R0', 10 * _ureg.cm),
                      B0=twiss_row['K1L'] / twiss_row['L'] * kinematics.brho_ * options.get('R0', 0.1) * _ureg.tesla,
                      )


def create_madx_sextupole(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> Command:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    return Sextupole(twiss_row.name[0:8], XL=twiss_row['L'] * _ureg.meter)


def create_madx_octupole(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> Command:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    return Octupole(twiss_row.name[0:8], XL=twiss_row['L'] * _ureg.meter)


def load_madx_twiss_headers(filename: str = 'twiss.outx', path: str = '.') -> pd.Series:
    """

    Args:
        filename:
        path:

    Returns:

    """
    return pd.read_csv(os.path.join(path, filename),
                       sep=r'\s+',
                       usecols=['KEY', 'VALUE'],
                       squeeze=True,
                       index_col=0,
                       names=['@', 'KEY', '_', 'VALUE'],
                       converters={'PC': float},
                       )[0:46]


def load_madx_twiss_table(filename: str = 'twiss.outx', path: str = '.') -> pd.DataFrame:
    """

    Args:
        filename:
        path:

    Returns:

    """
    headers = [
        'NAME',
        'KEYWORD',
        'S',
        'BETX', 'ALFX', 'MUX',
        'BETY', 'ALFY', 'MUY',
        'X', 'PX', 'Y', 'PY', 'T', 'PT',
        'DX', 'DPX', 'DY', 'DPY',
        'PHIX',
        'DMUX',
        'PHIY',
        'DMUY',
        'DDX',
        'DDPX',
        'DDY',
        'DDPY',
        'K1L', 'K2L', 'K3L', 'K4L', 'K5L', 'K6L',
        'K1SL', 'K2SL', 'K3SL', 'K4SL', 'K5SL', 'K6SL',
        'ENERGY',
        'L',
        'ANGLE',
        'HKICK', 'VKICK',
        'TILT',
        'E1', 'E2', 'H1', 'H2',
        'HGAP', 'FINT', 'FINTX',
        'KSI',
        'APERTYPE', 'APER_1', 'APER_2',
    ]
    _ = pd \
        .read_csv(os.path.join(path, filename),
                  skiprows=47,
                  sep=r'\s+',
                  index_col=False,
                  names=headers,
                  ) \
        .drop(0)
    _['L'] = _['L'].apply(float)
    _['ANGLE'] = _['ANGLE'].apply(float)
    _['K1L'] = _['K1L'].apply(float)
    return _


def from_madx_twiss(filename: str = 'twiss.outx',
                    path: str = '.',
                    options: Optional[dict] = None,
                    converters: Optional[dict] = None) -> _Sequence:
    """
    TODO
    Args:
        filename:
        path:
        options:
        converters:

    Returns:

    """
    madx_converters = {k.split('_')[2].upper(): getattr(sys.modules[__name__], k)
                       for k in globals().keys() if k.startswith('create_madx')}
    conversion_functions = {**madx_converters, **(converters or {})}
    options = options or {}
    twiss_headers = load_madx_twiss_headers(filename, path)
    p = getattr(particules, twiss_headers['PARTICLE'].capitalize())
    k = Kinematics(float(twiss_headers['PC']) * _ureg.GeV_c, particle=p)
    twiss_table = list(
                      load_madx_twiss_table(filename, path).set_index('NAME').apply(
                          lambda _: conversion_functions.get(_['KEYWORD'],
                                                             lambda _, __, ___: None
                                                             )(_, k, options.get(_['KEYWORD'], {})),
                          axis=1
                      ).values
    )
    return _Sequence(name=twiss_headers['NAME'],
                     sequence=twiss_table,
                     metadata=twiss_headers,
                     particle=p)
