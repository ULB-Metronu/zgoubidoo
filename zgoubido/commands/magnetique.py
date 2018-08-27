from .commands import Command


class AGSMainMagnet(Command):
    """AGS main magnet."""
    KEYWORD = 'AGSMM'


class AGSQuadrupole(Command):
    """AGS quadrupole."""
    KEYWORD = 'AGSQUAD'


class Aimant(Command):
    """Generation of dipole mid-plane 2-D map, polar frame."""
    KEYWORD = 'AIMANT'


class Bend(Command):
    """Bending magnet, Cartesian frame."""
    KEYWORD = 'BEND'


class Decapole(Command):
    """Decapole magnet."""
    KEYWORD = 'DECAPOLE'


class Dipole(Command):
    """Dipole magnet, polar frame."""
    KEYWORD = 'DIPOLE'


class DipoleM(Command):
    """Generation of dipole mid-plane 2-D map, polar frame."""
    KEYWORD = 'DIPOLE-M'

    PARAMETERS = {
        'NFACE': 3,
        'IC': 1,
        'IL': 2,
        'IAMAX': 1,
        'IRMAX': 1,
        'B0': 1,
        'N': 1,
        'B': 1,
        'G': 1,
        'AT': 1,
        'ACENT': 1,
        'RM': 1,
        'RMIN': 1,
        'RMAX': 1,
        'entrance_fb_lambda': 1,
        'entrance_fb_xi': 1,
        'entrance_fb_NC': 1,
        'entrance_fb_C1': 1,
        'entrance_fb_C2': 1,
        'entrance_fb_C3': 1,
        'entrance_fb_C4': 1,
        'entrance_fb_C5': 1,
        'entrance_fb_shift': 1,
        'entrance_fb_omega': 1,
        'entrance_fb_theta': 1,
        'entrance_fb_R1': 1,
        'entrance_fb_U1': 1,
        'entrance_fb_U2': 1,
        'entrance_fb_R2': 1,
        'exit_fb_lambda': 1,
        'exit_fb_xi': 1,
        'exit_fb_NC': 1,
        'exit_fb_C1': 1,
        'exit_fb_C2': 1,
        'exit_fb_C3': 1,
        'exit_fb_C4': 1,
        'exit_fb_C5': 1,
        'exit_fb_shift': 1,
        'exit_fb_omega': 1,
        'exit_fb_theta': 1,
        'exit_fb_R1': 1,
        'exit_fb_U1': 1,
        'exit_fb_U2': 1,
        'exit_fb_R2': 1,
        'lateral_fb_lambda': 1,
        'lateral_fb_xi': 1,
        'lateral_fb_NC': 1,
        'lateral_fb_C1': 1,
        'lateral_fb_C2': 1,
        'lateral_fb_C3': 1,
        'lateral_fb_C4': 1,
        'lateral_fb_C5': 1,
        'lateral_fb_shift': 1,
        'lateral_fb_omega': 1,
        'lateral_fb_theta': 1,
        'lateral_fb_R1': 1,
        'lateral_fb_U1': 1,
        'lateral_fb_U2': 1,
        'lateral_fb_R2': 1,
        'RM3': 1,
        'NBS': 0,
        'IORDRE': 4,
        'XPAS': 0.1,
        'KPOS': 1,
        'RE': 1,
        'TE': 1,
        'RS': 1,
        'TS': 1,
        'DP': 1,
    }

    def __str__(s):
        c = f"""
        '{s.KEYWORD}' {s.LABEL1} {s.LABEL2}
        {s.NFACE} {s.IC} {s.IL}
        {s.IAMAX} {s.IRMAX}
        {s.B0} {s.N} {s.B} {s.G}
        {s.AT} {s.ACENT} {s.RM}
        {s.RMIN} {s.RMAX}
        {s.entrance_fb_lambda} {s.entrance_fb_xi}
        {s.entrance_fb_NC} {s.entrance_fb_C1} {s.entrance_fb_C2} {s.entrance_fb_C3} {s.entrance_fb_C4} {s.entrance_fb_C5} {s.entrance_fb_shift}
        {s.entrance_fb_omega} {s.entrance_fb_theta} {s.entrance_fb_R1} {s.entrance_fb_U1} {s.entrance_fb_U2} {s.entrance_fb_R2}
        {s.exit_fb_lambda} {s.exit_fb_xi}
        {s.exit_fb_NC} {s.exit_fb_C1} {s.exit_fb_C2} {s.exit_fb_C3} {s.exit_fb_C4} {s.exit_fb_C5} {s.exit_fb_shift}
        {s.exit_fb_omega} {s.exit_fb_theta} {s.exit_fb_R1} {s.exit_fb_U1} {s.exit_fb_U2} {s.exit_fb_R2}
        """
        if s.NFACE == 3:
            c += f"""
            {s.lateral_fb_lambda} {s.lateral_fb_xi}
            {s.lateral_fb_NC} {s.lateral_fb_C1} {s.lateral_fb_C2} {s.lateral_fb_C3} {s.lateral_fb_C4} {s.lateral_fb_C5} {s.lateral_fb_shift}
            {s.lateral_fb_omega} {s.lateral_fb_theta} {s.lateral_fb_R1} {s.lateral_fb_U1} {s.lateral_fb_U2} {s.lateral_fb_R2}
            """
        c += f"""
        {s.NBS}
        {s.IORDRE}
        {s.XPAS}
        {s.KPOS}
        {s.DP if s.KPOS == 1 else ''}
        """
        return c


class Dipoles(Command):
    """Dipole magnet N-tuple, polarframe."""
    KEYWORD = 'DIPOLES'


class Dodecapole(Command):
    """Dodecapole magnet."""
    KEYWORD = 'DODECAPO'


class Drift(Command):
    """Field free drift space."""
    KEYWORD = 'DRIFT'

    PARAMETERS = {
        'XL': 0.0
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.XL}
        """


class Emma(Command):
    """2-D Cartesian or cylindrical mesh field map for EMMA FFAG."""
    KEYWORD = 'EMMA'


class FFAG(Command):
    """FFAG magnet, N-tuple."""
    KEYWORD = 'FFAG'


class FFAGSpirale(Command):
    """Spiral FFAG magnet, N-tuple."""
    KEYWORD = 'FFAG-SPI'


class Multipole(Command):
    """Magnetic multipole."""
    KEYWORD = 'MULTIPOL'


class Octupole(Command):
    """Octupole magnet."""
    KEYWORD = 'OCTUPOLE'


class PS170(Command):
    """Simulation of a round shape dipole magnet."""
    KEYWORD = 'PS170'


class Quadisex(Command):
    """Sharp edge magnetic multipoles."""
    KEYWORD = 'QUADISEX'


class Quadrupole(Command):
    """Quadrupole magnet."""
    KEYWORD = 'QUADRUPO'

    PARAMETERS = {
        'IL': 2,
        'XL': 0,
        'R0': 0,
        'B0': 0,
        'XE': 0,
        'LAM_E': 0,
        'NCE': 0,
        'NCS': 0,
        'C0': 0,
        'C1': 0,
        'C2': 0,
        'C3': 0,
        'C4': 0,
        'C5': 0,
        'XS': 0,
        'LAM_S': 0,
        'XPAS': 0.1,
        'KPOS': 0,
        'XCE': 0,
        'YCE': 0,
        'ALE': 0,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IL}
        {s.XL:.12e} {s.R0:.12e} {s.B0:.12e}
        {s.XE:.12e} {s.LAM_E:.12e}
        {s.NCE} {s.C0:.12e} {s.C1:.12e} {s.C2:.12e} {s.C3:.12e} {s.C4:.12e} {s.C5:.12e}
        {s.XS:.12e} {s.LAM_S:.12e}
        {s.NCS} {s.C0:.12e} {s.C1:.12e} {s.C2:.12e} {s.C3:.12e} {s.C4:.12e} {s.C5:.12e}
        {s.XPAS}
        {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
        """


class SexQuad(Command):
    """Sharp edge magnetic multipole."""
    KEYWORD = 'SEXQUAD'


class Sextupole(Command):
    """Sextupole magnet."""
    KEYWORD = 'SEXTUPOL'


class Solenoid(Command):
    """Solenoid."""
    KEYWORD = 'SOLENOID'


class Undulator(Command):
    """Undulator magnet."""
    KEYWORD = 'UNDULATOR'


class Venus(Command):
    """Simulation of a rectangular shape dipole magnet."""
    KEYWORD = 'VENUS'
