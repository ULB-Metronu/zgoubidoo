"""
TODO
"""
import os
import pandas as pd
from .. import ureg as _ureg
from ..input import Input as _Input
from ..commands import *

MADX_ELEMENTS = {
    'MARKER': lambda r: Marker(r.name[0:8]),
    'DRIFT': lambda r: Drift(r.name[0:8], XL=float(r['L']) * _ureg.meter),
    'SBEND': lambda r: Dipole(r.name[0:8], AT=float(r['ANGLE']) * _ureg.degree),
    'QUADRUPOLE': lambda r: Quadrupole(r.name[0:8], XL=float(r['L']) * _ureg.meter),
    'SEXTUPOLE': lambda r: Sextupole(r.name[0:8], XL=float(r['L']) * _ureg.meter),
}


def load_madx_twiss_headers(filename: str, path: str = '.') -> pd.Series:
    """

    Args:
        filename:
        path:

    Returns:

    """
    return pd.Series()


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
    return pd\
        .read_csv(os.path.join(path, filename), skiprows=47, sep=r'\s+', index_col=False, names=headers) \
        .drop(0)


def from_madx_twiss(filename: str, path: str = '.') -> _Input:
    """

    Args:
        filename:
        path:

    Returns:

    """
    return _Input(name='TEST',
                  line=list(
                      load_madx_twiss(filename, path).set_index('NAME').apply(
                          lambda _: MADX_ELEMENTS[r['KEYWORD']](_),
                          axis=1
                      ).values
                  )
                  )
