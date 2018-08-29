class ZgoubidoException(Exception):
    """Exception raised for errors in the Madx module."""

    def __init__(self, m):
        self.message = m


class Command:
    PARAMETERS = {
        'LABEL1': '',
        'LABEL2': '',
    }

    def __init__(self, label1='', label2='', *params, **kwargs):
        self._attributes = {}
        for p in (Command.PARAMETERS, self.PARAMETERS,) + params + ({'LABEL1': label1, 'LABEL2': label2},):
            self._attributes = dict(self._attributes, **p)
        self._attributes = dict(self._attributes, **kwargs)

    def __getattr__(self, a):
        return self._attributes[a]

    def __setattr__(self, a, v):
        if a == '_attributes':
            self.__dict__[a] = v
        else:
            self._attributes[a] = v

    def __repr__(s):
        return str(s)

    def __str__(s):
        return f"""
        '{s.KEYWORD}' {s.LABEL1} {s.LABEL2}
        """

    def plot(self, ax):
        return ax


class AutoRef(Command):
    """Automatic transformation to a new reference frame."""
    KEYWORD = 'AUTOREF'


class BeamBeam(Command):
    """Beam-beam lens."""
    KEYWORD = 'BEAMBEAM'


class Binary(Command):
    """BINARY/FORMATTED data converter."""
    KEYWORD = 'BINARY'


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


class Collimateur(Command):
    """Collimator."""
    KEYWORD = 'COLLIMA'


# Alias
Collimator = Collimateur


class Cible(Command):
    """Generate a secondary beam following target interaction."""
    KEYWORD = 'CIBLE'


class End(Command):
    """End of input data list."""
    KEYWORD = 'END'


class ESL(Command):
    """??? Field free drift space."""
    KEYWORD = 'ESL'


class Faisceau(Command):
    """Print particle coordinates."""
    KEYWORD = 'FAISCEAU'


class Faiscnl(Command):
    """Store particle coordinates in file FNAME."""

    KEYWORD = 'FAISCNL'
    PARAMETERS = {
        'FNAME': 'zgoubi.fai',
        'B_FNAME': 'b_zgoubi.fai',
        'binary': False,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.B_FNAME if s.binary else s.FNAME}
        """


class FaiStore(Command):
    """Store coordinates every IP other pass at labeled elements."""
    KEYWORD = 'FAISTORE'


class Fin(Command):
    """End of input data list."""
    KEYWORD = 'FIN'


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

    class Marker(Command):
        """Marker."""
        KEYWORD = 'MARKER'

    class Matrix(Command):
        """Calculation of transfer coefficients, periodic parameters."""
        KEYWORD = 'MATRIX'

    class MCDesintegration(Command):
        """Monte-Carlo simulation of in-flight decay."""
        KEYWORD = 'MCDESINT'


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


class Rebelote(Command):
    """’Do it again’."""
    KEYWORD = 'REBELOTE'

    PARAMETERS = {
        'NPASS': 1,
        'KWRIT': 0.0,
        'K': 99,
    }

    def __str__(s):
        return f"""
        {super().__str__()}
        {s.NPASS} {s.KWRIT} {s.K}
        """


class Reset(Command):
    """Reset counters and flags."""
    KEYWORD = 'RESET'


class Scaling(Command):
    """Power supplies and R.F. function generator."""
    KEYWORD = 'SCALING'


class Separa(Command):
    """Wien Filter - analytical simulation."""
    KEYWORD = 'SEPARA'


class SynchrotronRadiationLosses(Command):
    """Synchrotron radiation loss."""
    KEYWORD = 'SRLOSS'


class SynchrotronRadiationPrint(Command):
    """Print SR loss statistics."""
    KEYWORD = 'SRPRNT'


class SynchrotronRadiation(Command):
    """Synchrotron radiation spectral-angular densities."""
    KEYWORD = 'SYNRAD'


class Target(Command):
    """Generate a secondary beam following target interaction."""
    KEYWORD = 'TARGET'


class TransferMatrix(Command):
    """Transfer matrix."""
    KEYWORD = 'TRANSMAT'


class TranslationRotation(Command):
    """Translation-Rotation of the reference frame."""
    KEYWORD = 'TRAROT'


class Twiss(Command):
    """Calculation of periodic optical parameters."""
    KEYWORD = 'TWISS'


class WienFilter(Command):
    """Wien filter."""
    KEYWORD = 'WIENFILT'


class Ymy(Command):
    """Reverse signs of Y and Z reference axes."""
    KEYWORD = 'YMY'

    def __str__(s):
        return f"""
        '{s.KEYWORD}' {s.LABEL1} {s.LABEL2}
    """