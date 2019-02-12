"""
TODO
"""
from typing import Optional
import os
import pandas as pd
import numpy as np
from .. import ureg as _ureg
from ..input import Input as _Input
from ..commands import *
from ..physics import Kinematics

MADX_ELEMENTS = {
    'MARKER': lambda r, _, __: Marker(r.name[0:8]),
    'DRIFT': lambda r, _, __: Drift(r.name[0:8], XL=r['L'] * _ureg.meter),
    'SBEND': lambda r, k, o: Dipole(r.name[0:8],
                                    AT=np.abs(r['ANGLE'] * _ureg.radian),
                                    RM=np.abs(r['L'] / r['ANGLE'] * _ureg.meter),
                                    B0=k.brho / (r['L'] / r['ANGLE'] * _ureg.meter),
                                    ),
    'QUADRUPOLE': lambda r, k, o: Quadrupole(r.name[0:8],
                                             XL=r['L'] * _ureg.meter,
                                             R0=o.get('R0', 10 * _ureg.cm),
                                             B0=r['K1L'] / r['L'] * k.brho_ * o.get('R0', 10) * _ureg.tesla,
                                             ),
    'SEXTUPOLE': lambda r, k, o: Sextupole(r.name[0:8], XL=r['L'] * _ureg.meter),
}


def load_madx_twiss_headers(filename: str, path: str = '.') -> pd.Series:
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


def load_madx_twiss_table(filename: str, path: str = '.') -> pd.DataFrame:
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


def from_madx_twiss(filename: str,
                    path: str = '.',
                    options: Optional[dict] = None,
                    converters: Optional[dict] = None) -> _Input:
    """

    Args:
        filename:
        path:
        options:
        converters:

    Returns:

    """
    conversion_functions = {**MADX_ELEMENTS, **(converters or {})}
    options = options or {}
    twiss_headers = load_madx_twiss_headers(filename, path)
    k = Kinematics(float(twiss_headers['PC']) * _ureg.GeV_c)
    return _Input(name=twiss_headers['NAME'],
                  line=list(
                      load_madx_twiss_table(filename, path).set_index('NAME').apply(
                          lambda _: conversion_functions[_['KEYWORD']](_, k, options.get(_['KEYWORD'], {})),
                          axis=1
                      ).values
                  )
                  )
