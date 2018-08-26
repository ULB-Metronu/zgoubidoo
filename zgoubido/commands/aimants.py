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


class CartesianMesh(Command):
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


class ELRevol(Command):
    """1-D uniform mesh electric field map."""
    KEYWORD = 'ELREVOL'


class Emma(Command):
    """2-D Cartesian or cylindrical mesh field map for EMMA FFAG."""
    KEYWORD = 'EMMA'


class ESL(Command):
    """??? Field free drift space."""
    KEYWORD = 'ESL'


class Faisceau(Command):
    """Print particle coordinates."""
    KEYWORD = 'FAISCEAU'


class Faiscnl(Command):
    """Store particle coordinates in file FNAME."""
    KEYWORD = 'FAISCNL'


class FaiStore(Command):
    """Store coordinates every IP other pass at labeled elements."""
    KEYWORD = 'FAISTORE'


class FFAG(Command):
    """FFAG magnet, N-tuple."""
    KEYWORD = 'FFAG'


class FFAGSpirale(Command):
    """Spiral FFAG magnet, N-tuple."""
    KEYWORD = 'FFAG-SPI'


class Fit(Command):
    """Fitting procedure."""
    KEYWORD = 'FIT'


class Fit2(Command):
    """Fitting procedure."""
    KEYWORD = 'FIT2'


class Focale(Command):
    """Particle coordinates and horizontal beam size at distance XL."""
    KEYWORD = 'FOCALE'


class FocaleZ(Command):
    """Particle coordinates and vertical beam size at distance XL."""
    KEYWORD = 'FOCALEZ'


class GasScattering(Command):
    """Gas scattering."""
    KEYWORD = 'GASCAT'


class GetFitVal(Command):
    """Get values of variables as saved from former FIT[2] run."""
    KEYWORD = 'GETFITVAL'


class Histo(Command):
    """1-Dhistogram"""
    KEYWORD = 'HISTO'


class Image(Command):
    """Localization and size of horizontal waist."""
    KEYWORD = 'IMAGE'


class Images(Command):
    """Localization and size of horizontal waists."""
    KEYWORD = 'IMAGES'


class ImageZ(Command):
    """Localization and size of vertical waist."""
    KEYWORD = 'IMAGEZ'


class ImagesZ(Command):
    """Localization and size of vertical waists."""
    KEYWORD = 'IMAGESZ'


class Map2D(Command):
    """2-D Cartesian uniform mesh field map - arbitrary magnetic field."""
    KEYWORD = 'MAP2D'


class Map2DElectric(Command):
    """2-D Cartesian uniform mesh field map - arbitrary electric field."""
    KEYWORD = 'MAP2D-E'


class Marker(Command):
    """Marker."""
    KEYWORD = 'MARKER'


class Matrix(Command):
    """Calculation of transfer coefficients, periodic parameters."""
    KEYWORD = 'MATRIX'


class MCDesintegration(Command):
    """Monte-Carlo simulation of in-flight decay."""
    KEYWORD = 'MCDESINT'


class Multipole(Command):
    """Magnetic multipole."""
    KEYWORD = 'MULTIPOL'


class Octupole(Command):
    """Octupole magnet."""
    KEYWORD = 'OCTUPOLE'


class Optics(Command):
    """Write out optical functions."""
    KEYWORD = 'OPTICS'


class Ordre(Command):
    """Taylor expansions order."""
    KEYWORD = 'ORDRE'


class Pickups(Command):
    """Beam centroid path; closed orbit."""
    KEYWORD = 'PICKUPS'


class PlotData(Command):
    """Intermediate output for the PLOTDATA graphic software."""
    KEYWORD = 'PLOTDATA'


class Poisson(Command):
    """Read magnetic field data from POISSON output."""
    KEYWORD = 'POISSON'


class PolarMesh(Command):
    """2-D polar mesh magnetic field map."""
    KEYWORD = 'POLARMES'


class PS170(Command):
    """Simulation of a round shape dipole magnet."""
    KEYWORD = 'PS170'


class Quadisex(Command):
    """Sharp edge magnetic multipoles."""
    KEYWORD = 'QUADISEX'


class