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
import os
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

MADX_TWISS_TABLE_HEADER_ROWS = 47
"""MAD-X Twiss table header rows (lines to be skipped when reading the table's content."""

MADX_TWISS_HEADERS = [
    'NAME',
    'KEYWORD',
    'S',
    'BETX', 'ALFX', 'MUX',
    'BETY', 'ALFY', 'MUY',
    'X', 'PX', 'Y', 'PY', 'T', 'PT',
    'DX', 'DPX', 'DY', 'DPY',
    'WX',
    'PHIX',
    'DMUX',
    'WY',
    'PHIY',
    'DMUY',
    'DDX', 'DDPX',
    'DDY', 'DDPY',
    'R11', 'R12', 'R21', 'R22',
    'ENERGY',
    'L',
    'ANGLE',
    'K0L', 'K0SL',
    'K1L', 'K1SL',
    'K2L', 'K2SL',
    'K3L', 'K3SL',
    'K4L', 'K4SL',
    'K5L', 'K5SL',
    'K6L', 'K6SL',
    'K7L', 'K7SL',
    'K8L', 'K8SL',
    'K9L', 'K9SL',
    'K10L', 'K10SL',
    'K11L', 'K11SL',
    'K12L', 'K12SL',
    'K13L', 'K13SL',
    'K14L', 'K14SL',
    'K15L', 'K15SL',
    'K16L', 'K16SL',
    'K17L', 'K17SL',
    'K18L', 'K18SL',
    'K19L', 'K19SL',
    'K20L', 'K20SL',
    'KSI',
    'HKICK', 'VKICK',
    'TILT',
    'E1', 'E2',
    'H1', 'H2',
    'HGAP',
    'FINT',
    'FINTX',
    'VOLT',
    'LAG',
    'FREQ',
    'HARMON',
    'SLOT_ID',
    'ASSEMBLY_ID',
    'MECH_SEP',
    'V_POS',
    'LRAD',
    'PARENT',
    'RE11', 'RE12', 'RE13', 'RE14', 'RE15', 'RE16',
    'RE21', 'RE22', 'RE23', 'RE24', 'RE25', 'RE26',
    'RE31', 'RE32', 'RE33', 'RE34', 'RE35', 'RE36',
    'RE41', 'RE42', 'RE43', 'RE44', 'RE45', 'RE46',
    'RE51', 'RE52', 'RE53', 'RE54', 'RE55', 'RE56',
    'RE61', 'RE62', 'RE63', 'RE64', 'RE65', 'RE66',
    'KMAX',
    'KMIN',
    'CALIB',
    'POLARITY',
    'ALFA',
    'BETA11', 'BETA12', 'BETA13',
    'BETA21', 'BETA22', 'BETA23',
    'BETA31', 'BETA32', 'BETA33',
    'ALFA11', 'ALFA12', 'ALFA13',
    'ALFA21', 'ALFA22', 'ALFA23',
    'ALFA31', 'ALFA32', 'ALFA33',
    'GAMA11', 'GAMA12', 'GAMA13',
    'GAMA21', 'GAMA22', 'GAMA23',
    'GAMA31', 'GAMA32', 'GAMA33',
    'BETA11P', 'BETA12P', 'BETA13P',
    'BETA21P', 'BETA22P', 'BETA23P',
    'BETA31P', 'BETA32P', 'BETA33P',
    'ALFA11P', 'ALFA12P', 'ALFA13P',
    'ALFA21P', 'ALFA22P', 'ALFA23P',
    'ALFA31P', 'ALFA32P', 'ALFA33P',
    'GAMA11P', 'GAMA12P', 'GAMA13P',
    'GAMA21P', 'GAMA22P', 'GAMA23P',
    'GAMA31P', 'GAMA32P', 'GAMA33P',
    'DISP1', 'DISP2', 'DISP3', 'DISP4',
    'DISP1P', 'DISP2P', 'DISP3P', 'DISP4P',
    'DISP1P2', 'DISP2P2', 'DISP3P2', 'DISP4P2',
    'DISP1P3', 'DISP2P3', 'DISP3P3', 'DISP4P3',
    'MU1', 'MU2', 'MU3',
    'SIG11', 'SIG12', 'SIG13', 'SIG14', 'SIG15', 'SIG16',
    'SIG21', 'SIG22', 'SIG23', 'SIG24', 'SIG25', 'SIG26',
    'SIG31', 'SIG32', 'SIG33', 'SIG34', 'SIG35', 'SIG36',
    'SIG41', 'SIG42', 'SIG43', 'SIG44', 'SIG45', 'SIG46',
    'SIG51', 'SIG52', 'SIG53', 'SIG54', 'SIG55', 'SIG56',
    'SIG61', 'SIG62', 'SIG63', 'SIG64', 'SIG65', 'SIG66',
    'N1',
]
"""MAD-X Twiss headers (by default, when all columns are selected)."""


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


def load_madx_twiss_headers(filename: str = 'twiss.outx', path: str = '.') -> pd.Series:
    """

    Args:
        filename: name of the Twiss table file
        path: path to the Twiss table file

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


def load_madx_twiss_table(filename: str = 'twiss.outx', path: str = '.', columns: List = None) -> pd.DataFrame:
    """

    Args:
        filename: name of the Twiss table file
        path: path to the Twiss table file
        columns: the list of columns in the Twiss file

    Returns:
        A DataFrame representing the Twiss table.
    """
    columns = columns or MADX_TWISS_HEADERS
    _: pd.DataFrame = pd \
        .read_csv(os.path.join(path, filename),
                  skiprows=MADX_TWISS_TABLE_HEADER_ROWS,
                  sep=r'\s+',
                  index_col=False,
                  names=columns,
                  ) \
        .drop(0)
    for c in _.columns:
        try:
            _[c] = _[c].apply(float)
        except ValueError:
            pass
    return _.set_index('NAME')


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
