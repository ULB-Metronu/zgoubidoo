"""Zgoubidoo's interfaces to electromagnetic Zgoubi commands.

More details here.
"""
from .. import ureg as _ureg
from .commands import Command as _Command


class WienFilter(_Command):
    """Wien filter.

    TODO
    """
    KEYWORD = 'WIENFILT'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IL': (2, 'Print field and coordinates along trajectories'),
        'XL': (0 * _ureg.centimeter, 'Element length'),
        'E': (1.0 * _ureg.volt / _ureg.meter, 'Electric field'),
        'B': (1.0 * _ureg.tesla, 'Magnetic field'),
        'HV': (0, 'Element inactive (HV = 0), horizontal (HV = 1) or vertical (HV = 2) separation'),
        'X_E': (0 * _ureg.centimeter, 'Entrance face integration zone for the fringe field'),
        'LAM_E_E': (0 * _ureg.centimeter, 'Entrance face electric fringe field extent'),
        'LAM_E_B': (0 * _ureg.centimeter, 'Entrance face magnetic fringe field extent'),
        'C0_E_E': 0,
        'C1_E_E': 1,
        'C2_E_E': 0,
        'C3_E_E': 0,
        'C4_E_E': 0,
        'C5_E_E': 0,
        'C0_E_B': 0,
        'C1_E_B': 1,
        'C2_E_B': 0,
        'C3_E_B': 0,
        'C4_E_B': 0,
        'C5_E_B': 0,
        'X_S': (0 * _ureg.centimeter, 'Exit face integration zone for the fringe field'),
        'LAM_S_E': (0 * _ureg.centimeter, 'Exit face electric fringe field extent'),
        'LAM_S_B': (0 * _ureg.centimeter, 'Exit face magnetic fringe field extent'),
        'C0_S_E': 0,
        'C1_S_E': 1,
        'C2_S_E': 0,
        'C3_S_E': 0,
        'C4_S_E': 0,
        'C5_S_E': 0,
        'C0_S_B': 0,
        'C1_S_B': 1,
        'C2_S_B': 0,
        'C3_S_B': 0,
        'C4_S_B': 0,
        'C5_S_B': 0,
        'XPAS': (0.1 * _ureg.centimeter, 'Integration step'),
        'KPOS': (1, 'Misalignment type'),
        'XCE': (0 * _ureg.centimeter, 'x offset'),
        'YCE': (0 * _ureg.centimeter, 'y offset'),
        'ALE': 0 * _ureg.radian,
        'COLOR': ('pink', 'Element color for plotting.'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IL}
        {s.XL.m_as('m'):.12e} {s.E.m_as('V/m'):.12e} {s.B.m_as('T'):.12e} {s.HV}
        {s.X_E.m_as('cm'):.12e} {s.LAM_E_E.m_as('cm'):.12e} {s.LAM_E_B.m_as('cm'):.12e}
        {s.C0_E_E:.12e} {s.C1_E_E:.12e} {s.C2_E_E:.12e} {s.C3_E_E:.12e} {s.C4_E_E:.12e} {s.C5_E_E:.12e}
        {s.C0_E_B:.12e} {s.C1_E_B:.12e} {s.C2_E_B:.12e} {s.C3_E_B:.12e} {s.C4_E_B:.12e} {s.C5_E_B:.12e}
        {s.X_S.m_as('cm'):.12e} {s.LAM_S_E.m_as('cm'):.12e} {s.LAM_S_B.m_as('cm'):.12e}
        {s.C0_S_E:.12e} {s.C1_S_E:.12e} {s.C2_S_E:.12e} {s.C3_S_E:.12e} {s.C4_S_E:.12e} {s.C5_S_E:.12e}
        {s.C0_S_B:.12e} {s.C1_S_B:.12e} {s.C2_S_B:.12e} {s.C3_S_B:.12e} {s.C4_S_B:.12e} {s.C5_S_B:.12e}
        {s.XPAS.m_as('cm')}
        {s.KPOS} {s.XCE.m_as('cm'):.12e} {s.YCE.m_as('cm'):.12e} {s.ALE.m_as('radian'):.12e}
        """
