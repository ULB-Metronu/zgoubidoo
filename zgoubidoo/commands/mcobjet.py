from .commands import Command as _Command


class MCObjet(_Command):
    """Monte-Carlo generation of a 6-D object."""

    PARAMETERS = {
        'BORO': 1.0,
        'IMAX': 1,
        'KY': 1,
    }


class MCObjet1(MCObjet):
    pass


class MCObjet2(MCObjet):
    pass


class MCObjet3(MCObjet):
    KEYWORD = 'MCOBJET3'

    PARAMETERS = {
        'KY': 2,
        'KT': 1,
        'KZ': 1,
        'KP': 1,
        'KX': 1,
        'KD': 1,
        'Y0': 1,
        'T0': 1.0,
        'Z0': 1.0,
        'P0': 1.0,
        'X0': 1.0,
        'D0': 1.0,
        'ALPHA_Y': 0.0,
        'BETA_Y': 1.0,
        'EMIT_Y': 1e-9,
        'N_CUTOFF_Y': 0,
        'N_CUTOFF2_Y': 0,
        'ALPHA_Z': 0.0,
        'BETA_Z': 1.0,
        'EMIT_Z': 1e-9,
        'N_CUTOFF_Z': 0,
        'N_CUTOFF2_Z': 0,
        'ALPHA_X': 0.0,
        'BETA_X': 1.0,
        'EMIT_X': 1e-9,
        'N_CUTOFF_X': 0,
        'N_CUTOFF2_X': 0,
        'I1': 1,
        'I2': 2,
        'I3': 3,
    }

    def __str__(s) -> str:
        return f"""
        '{s.KEYWORD}' {s.LABEL1} {s.LABEL2}
        3
        {s.KY} {s.KT} {s.KZ} {s.KP} {s.KX} {s.KD}
        {s.Y0} {s.T0} {s.Z0} {s.P0} {s.X0} {s.D0}
        {s.ALPHA_Y} {s.BETA_Y} {s.EMIT_Y} {s.N_CUTOFF_Y} {s.N_CUTOFF2_Y if s.N_CUTOFF_Y < 0 else ''}
        {s.ALPHA_Z} {s.BETA_Z} {s.EMIT_Z} {s.N_CUTOFF_Z} {s.N_CUTOFF2_Z if s.N_CUTOFF_Z < 0 else ''}
        {s.ALPHA_X} {s.BETA_X} {s.EMIT_X} {s.N_CUTOFF_X} {s.N_CUTOFF2_X if s.N_CUTOFF_X < 0 else ''}
        {s.I1} {s.I2} {s.I3}
    """
