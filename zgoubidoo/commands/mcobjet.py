"""Zgoubidoo's interfaces to Monte-Carlo object definition commands.

More details here.
"""
from .commands import Command as _Command
from .objet import ObjetType as _ObjetType
from .. import ureg as _ureg


class MCObjet(_Command, metaclass=_ObjetType):
    """Monte-Carlo generation of a 6-D object."""
    KEYWORD = 'MCOBJET'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'BORO': (1.0 * _ureg.tesla * _ureg.m, 'Reference rigidity'),
        'IMAX': (1, 'Number of particles to be generated'),
        'KY': (2, '1 - Uniform, 2 - Gaussian, 3 - Parabolic'),
        'KT': (2, '1 - Uniform, 2 - Gaussian, 3 - Parabolic'),
        'KZ': (2, '1 - Uniform, 2 - Gaussian, 3 - Parabolic'),
        'KP': (2, '1 - Uniform, 2 - Gaussian, 3 - Parabolic'),
        'KX': (2, '1 - Uniform, 2 - Gaussian, 3 - Parabolic'),
        'KD': (1, '1 - Uniform, 2 - Exponential, 3 - Kinematic'),
        'Y0': (0 * _ureg.cm, 'Mean value'),
        'T0': (0 * _ureg.rad, 'Mean value'),
        'Z0': (0 * _ureg.cm, 'Mean value'),
        'P0': (0 * _ureg.rad, 'Mean value'),
        'X0': (0 * _ureg.cm, 'Mean value'),
        'D0': (1, 'Mean value'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
        commands (e.g. fit)."""


class MCObjet1(MCObjet):
    """

    """
    pass


class MCObjet2(MCObjet):
    """

    """
    pass


class MCObjet3(MCObjet):
    """Monte-Carlo generation of a 6-D object.

    """
    PARAMETERS = {
        'ALPHA_Y': (0.0, 'Horizontal (Y) alpha function'),
        'BETA_Y': (1.0 * _ureg.m, 'Horizontal (Y) beta function'),
        'EMIT_Y': (1e-9 * _ureg.m * _ureg.radian, 'Horizontal (Y) normalized emittance'),
        'D_Y': (0.0 * _ureg.m, 'Horizontal (Y) dispersion'),
        'D_YP': (0.0, 'Horizontal (Y) dispersion prime'),
        'N_CUTOFF_Y': (10, 'Cut-off value for the horizontal distribution'),
        'N_CUTOFF2_Y': (0, 'Secondary cut-off value for the horizontal distribution'),
        'ALPHA_Z': (0.0, 'Vertical (Z) alpha function'),
        'BETA_Z': (1.0 * _ureg.m, 'Vertical (Z) beta function'),
        'EMIT_Z': (1e-9 * _ureg.m * _ureg.radian, 'Vertical (Z) normalized emittance'),
        'D_Z': (0.0 * _ureg.m, 'Vertical (Z) dispersion'),
        'D_ZP': (0.0, 'Vertical (Z) dispersion prime'),
        'N_CUTOFF_Z': (10, 'Cut-off value for the vertical distribution'),
        'N_CUTOFF2_Z': (0, 'Secondary cut-off value for the vertical distribution'),
        'ALPHA_X': (0.0, 'Longitudinal (X) alpha function'),
        'BETA_X': (1.0 * _ureg.m, 'Longitudinal (X) beta function'),
        'EMIT_X': (1e-9 * _ureg.m * _ureg.radian, 'Longitudinal (X) normalized emittance'),
        'N_CUTOFF_X': (10, 'Cut-off value for the longitudinal distribution'),
        'N_CUTOFF2_X': (0, 'Secondary cut-off value for the longitudinal distribution'),
        'I1': (1, 'Random sequence seed'),
        'I2': (2, 'Random sequence seed'),
        'I3': (3, 'Random sequence seed'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
        commands (e.g. fit)."""

    def __str__(s) -> str:
        return f"""
        '{s.KEYWORD}' {s.LABEL1} {s.LABEL2}
        {s.BORO.m_as('kilogauss cm'):.12e}
        3
        {int(s.IMAX):d}
        {s.KY} {s.KT} {s.KZ} {s.KP} {s.KX} {s.KD}
        {s.Y0.m_as('cm'):.12e} {s.T0.m_as('radian'):.12e} {s.Z0.m_as("cm"):.12e} {s.P0.m_as('radian'):.12e} {s.X0.m_as('cm'):.12e} {s.D0:.12e}
        {s.ALPHA_Y:.12e} {s.BETA_Y.m_as('m'):.12e} {s.EMIT_Y.m_as('m radian'):.12e} {s.N_CUTOFF_Y} {s.N_CUTOFF2_Y if s.N_CUTOFF_Y < 0 else ''} {s.D_Y.m_as('m'):.12e} {s.D_YP:.12e}
        {s.ALPHA_Z:.12e} {s.BETA_Z.m_as('m'):.12e} {s.EMIT_Z.m_as('m radian'):.12e} {s.N_CUTOFF_Z} {s.N_CUTOFF2_Z if s.N_CUTOFF_Z < 0 else ''} {s.D_Z.m_as('m'):.12e} {s.D_ZP:.12e}
        {s.ALPHA_X:.12e} {s.BETA_X.m_as('m'):.12e} {s.EMIT_X.m_as('m radian'):.12e} {s.N_CUTOFF_X} {s.N_CUTOFF2_X if s.N_CUTOFF_X < 0 else ''}
        {s.I1} {s.I2} {s.I3}
    """
