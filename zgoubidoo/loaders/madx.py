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
import numpy as _np
import pandas as pd
import itertools
from .. import ureg as _ureg
from ..sequence import Sequence as _Sequence
from ..commands import Quadrupole, Sextupole, Octupole, Command, Marker, Drift, Bend, ChangeRef, Multipole, Cavite
from ..kinematics import Kinematics
from ..commands import particules
from ..units import _m
from ..output.madx import load_madx_twiss_headers, load_madx_twiss_table, get_twiss_values


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
    bore_radius = options.get('R0', 10 * _ureg.cm)
    m = Multipole(
        XL=twiss_row['L'] * _ureg.meter,
        R0=bore_radius,
        B1=kinematics.brho / (twiss_row['L'] / twiss_row['ANGLE'] * _ureg.m),
        B2=twiss_row['K1L'] / twiss_row['L'] * kinematics.brho_ * bore_radius.m_as('m') * _ureg.tesla,
        R1=twiss_row['TILT'] * _ureg.radian,
        R2=twiss_row['TILT'] * _ureg.radian,
        KPOS=3,
    ).generate_label(prefix=twiss_row.name)

    return [
        m
    ]


def create_madx_sbend(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    if twiss_row['ANGLE'] == 0.0:  # Avoid division by zero
        b1 = 0 * _ureg.tesla
    else:
        b1 = kinematics.brho / (twiss_row['L'] / _np.abs(twiss_row['ANGLE']) * _ureg.meter)
    b = options.get('command', Bend)(twiss_row.name[0:8],
                                     XL=twiss_row['L'] * _ureg.meter,
                                     B1=b1,
                                     KPOS=3,
                                     W_E=twiss_row['E1'] * _ureg.radian * _np.sign(twiss_row['ANGLE']),
                                     W_S=twiss_row['E2'] * _ureg.radian * _np.sign(twiss_row['ANGLE']),
                                     )
    if twiss_row['TILT'] != 0:
        b.COLOR = 'orange'
    if twiss_row['ANGLE'] < 0:
        return [
            ChangeRef(TRANSFORMATIONS=[['XR', -(-twiss_row['TILT'] + _np.pi) * _ureg.radian]]).generate_label(
                prefix=twiss_row.name + '_CRL'
            ),
            b,
            ChangeRef(TRANSFORMATIONS=[['XR', (-twiss_row['TILT'] + _np.pi) * _ureg.radian]]).generate_label(
                prefix=twiss_row.name + '_CRR'
            ),
        ]
    else:
        return [
            ChangeRef(TRANSFORMATIONS=[['XR', twiss_row['TILT'] * _ureg.radian]]).generate_label(
                prefix=twiss_row.name + '_CRL'
            ),
            b,
            ChangeRef(TRANSFORMATIONS=[['XR', -twiss_row['TILT'] * _ureg.radian]]).generate_label(
                prefix=twiss_row.name + '_CRR'
            ),
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
    return [Quadrupole(twiss_row.name[0:8],
                       XL=twiss_row['L'] * _ureg.meter,
                       R0=bore_radius,
                       B0=twiss_row['K1L'] / twiss_row['L'] * kinematics.brho_ * _m(bore_radius) * _ureg.tesla,
                       XE=0 * _ureg.cm,
                       LAM_E=0 * _ureg.cm,
                       XS=0 * _ureg.cm,
                       LAM_S=0 * _ureg.cm,
                       ).generate_label(prefix=twiss_row.name[0:8]),
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


def create_madx_twcavity(twiss_row: pd.Series, kinematics: Kinematics, options: Dict) -> List[Command]:
    """

    Args:
        twiss_row:
        kinematics:
        options:

    Returns:

    """
    cavity = Cavite(
        IOPT=10,
        XL=1 * _ureg.m,
        FREQ=twiss_row['FREQ'] * _ureg.MHz,
        V=twiss_row['VOLT'] * _ureg.MV * _np.sign(kinematics.brho),
        PHI_S=(twiss_row['LAG'] + _np.pi / 2) * _ureg.radian,
    ).generate_label(prefix=twiss_row.name[0:8])
    return [
        Drift(XL=1 * _ureg.mm),
        cavity,
    ]


def from_madx_twiss(filename: str = 'twiss.outx',
                    path: str = '.',
                    columns: List = None,
                    options: Optional[dict] = None,
                    converters: Optional[dict] = None,
                    elements_database: Optional[dict] = None,
                    from_element: str = None,
                    to_element: str = None,) -> _Sequence:
    """
    TODO
    Args:
        filename: name of the Twiss table file
        path: path to the Twiss table file
        columns: the list of columns in the Twiss file
        options:
        converters:
        elements_database:
        from_element:
        to_element:

    Returns:

    Examples:
        >>> lhec = zgoubidoo.from_madx_twiss(filename='lhec.outx', path='.')
    """
    madx_converters = {k.split('_')[2].upper(): getattr(sys.modules[__name__], k)
                       for k in globals().keys() if k.startswith('create_madx')}
    conversion_functions = {**madx_converters, **(converters or {})}
    elements_database = elements_database or {}
    options = options or {}
    twiss_headers = load_madx_twiss_headers(filename, path)
    twiss_table = load_madx_twiss_table(filename, path, columns).loc[from_element:to_element]
    particle_name = twiss_headers['PARTICLE'].capitalize()
    p = getattr(particules, particle_name if particle_name != 'Default' else 'Proton')
    k = Kinematics(float(twiss_headers['PC']) * _ureg.GeV_c, particle=p)
    converted_table: list = list(
        twiss_table.apply(
            lambda _: elements_database.get(_.name,
                                            conversion_functions.get(_['KEYWORD'], lambda _, __, ___: None)
                                            (_, k, options.get(_['KEYWORD'], {}))
                                            ),
            axis=1
        ).values
    )
    return _Sequence(name=twiss_headers['NAME'],
                     sequence=list(itertools.chain.from_iterable(converted_table)),
                     metadata=twiss_headers,
                     particle=p,
                     table=twiss_table,
                     initial_twiss=get_twiss_values(twiss_table),
                     )
