from .commands import Command


class Drift(Command):
    KEYWORD = 'DRIFT'
    PARAMETERS = {
        'XL': 0.0
    }

    def __str__(s):
        return f"""
        '{s.KEYWORD}' {s.LABEL1} {s.LABEL2}
        {s.XL}
        """


class DipoleM(Command):
    KEYWORD = 'DIPOLEM'
    PARAMETERS = {

    }


class Quadrupo(Command):
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


class AGSMainMagnet(Command):
    """AGS main magnet."""
    KEYWORD = 'AGSMM'


class AGSQuadrupole(Command):
    """AGS quadrupole."""
    KEYWORD = 'AGSQUAD'


class Aimant(Command):
    """Generation of dipole mid-plane 2-D map, polar frame."""
    KEYWORD = 'AIMANT'


class AutoRef(Command):
    """Automatic transformation to a new reference frame."""
    KEYWORD = 'AUTOREF'


class BeamBeam(Command):
    """Beam-beam lens."""
    KEYWORD = 'BEAMBEAM'


class Bend(Command):
    """Bending magnet, Cartesian frame."""
    KEYWORD = 'BEND'


class Binary(Command):
    """BINARY/FORMATTED data converter."""
    KEYWORD = 'BINARY'


class Brevol(Command):
    """1-D uniform mesh magnetic field map."""
    KEYWORD = 'BREVOL'


class Cartemes(Command):
    """"2-D Cartesian uniform mesh magnetic field map."""
    KEYWORD = 'CARTEMES'


class Cavite(Command):
    """Accelerating cavity."""
    KEYWORD = 'CAVITE'


# Alias
Cavity = Cavite


class Chambre(Command):
    """Long transverse aperture limitation."""
    KEYWORD = 'CHAMBR'


# Aliases
Chamber = Chambre
Chambr = Chambre


class ChangeRef(Command):
    """Transformation to a new reference frame."""
    KEYWORD = 'CHANGREF'


# Alias
ChangRef = ChangeRef


class Cible(Command):
    """Generate a secondary beam following target interaction."""
    KEYWORD = 'CIBLE'


# Alias
Target = Cible


class Collimateur(Command):
    """Collimator."""
    KEYWORD = 'COLLIMA'

# Alias
Collimator = Collimateur


class Decopole(Command):
    """Decapole magnet."""
    KEYWORD = 'DECAPOLE'


class Dipole(Command):
    """Dipole magnet, polar frame."""
    KEYWORD = 'DIPOLE'


class DipoleM(Command):
    """Generation of dipole mid-plane 2-D map, polar frame."""
    KEYWORD = 'DIPOLE-M'


class Dipoles(Command):
    """Dipole magnet N-tuple, polarframe."""
    KEYWORD = 'DIPOLES'


class Dodecapole(Command):
    """Dodecapole magnet."""
    KEYWORD = 'DODECAPO'


class Drift(Command):
    """Field free drift space."""
    KEYWORD = 'DRIFT'


class EBMult(Command):
    """Electro-magnetic multipole."""
    KEYWORD = 'EBMULT'


# Aliases
EBMultipole = EBMult


class EL2Tub(Command):
    """Two-tube electrostatic lens."""
    KEYWORD = 'EL2TUB'


class ELMir(Command):
    """Electrostatic N-electrode mirror/lens,straight slits."""
    KEYWORD = 'ELMIR'


class ELMirCircular(Command):
    """Electrostatic N-electrode mirror/lens, circular slits."""
    KEYWORD = 'ELMIRC'


class ELMulti(Command):
    """Electric multipole."""
    KEYWORD = 'ELMULT'