from typing import NoReturn, Optional, Any
import uuid
from pint import UndefinedUnitError
from .patchable import Patchable
from .. import ureg, Q_
from ..frame import Frame
from ..units import _degree, _cm

ZGOUBI_LABEL_LENGTH: int = 10  # Used to be 8 on older versions


class ZgoubidoException(Exception):
    """Exception raised for errors in the Madx module."""

    def __init__(self, m):
        self.message = m


class MetaCommand(type):
    """
    Dark magic.
    Be careful.
    """
    def __new__(mcs, name, bases, dct):
        dct['__doc__'] = ''
        d = []
        if dct.get('PARAMETERS'):
            for k, v in dct.get('PARAMETERS').items():
                d.append(f"{k}: {v}")
            dct['__doc__'] = '\n'.join(d)
        return super().__new__(mcs, name, bases, dct)


class Command(metaclass=MetaCommand):
    """

    """

    KEYWORD: str = ''

    PARAMETERS = {
        'LABEL1': '',
        'LABEL2': '',
    }

    PROPERTIES = [
        '_attributes',
        '_output',
        '_entry',
        '_entry_patched',
        '_exit',
        '_exit_patched',
        '_center',
    ]

    def __init__(self, label1: str='', label2: str='', *params, **kwargs) -> NoReturn:
        self._output = list()
        self._attributes = {}
        for p in (Command.PARAMETERS, self.PARAMETERS,) + params + (
                {
                    'LABEL1': label1 or str(uuid.uuid4().hex)[:ZGOUBI_LABEL_LENGTH],
                    'LABEL2': label2
                },):
            self._attributes = dict(self._attributes, **p)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, a):
        if self._attributes.get(a) is None:
            return None
        if not isinstance(self._attributes[a], tuple):
            attr = self._attributes[a]
        else:
            attr = self._attributes[a][0]
        if attr is not '' and not isinstance(attr, Q_):
            try:
                _ = Q_(attr)
                if _.dimensionless:
                    return _.magnitude
                else:
                    return _
            except (TypeError, ValueError, UndefinedUnitError):
                return attr
        else:
            return attr

    def __setattr__(self, k, v: Any) -> NoReturn:
        if k in Command.PROPERTIES:
            self.__dict__[k] = v
        else:
            if k not in self._attributes.keys():
                raise ZgoubidoException(f"The parameter {k} is not part of the {self.__class__.__name__} definition.")
            else:
                try:
                    default = self._attributes[k][0]
                except (TypeError, IndexError):
                    default = self._attributes[k]
            try:
                if default is not None and ureg.Quantity(v).dimensionality != ureg.Quantity(default).dimensionality:
                    raise ZgoubidoException(f"Invalid dimension ({ureg.Quantity(v).dimensionality}"
                                            f" instead of {ureg.Quantity(default).dimensionality}) for parameter {k}.")
            except (ValueError, TypeError, UndefinedUnitError):
                pass
            self._attributes[k] = v

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"""
        '{self.KEYWORD}' {self.LABEL1} {self.LABEL2}
        """

    @property
    def plotable(self) -> bool:
        return False

    @property
    def output(self):
        """
        Provides the outputs associated with a command after each successive Zgoubi run.
        :return: the output, None if no output has been attached.
        """
        return self._output

    def attach_output(self, output: str) -> NoReturn:
        """
        Attach the ouput that an element generated during a Zgoubi run.
        :param output: the ouput from a Zgoubi run for the present element.
        :return: NoReturn
        """
        self._output.append(output)
        self.process_output(output)

    def process_output(self, output: str) -> Optional[bool]:
        pass


class AutoRef(Command):
    """Automatic transformation to a new reference frame."""
    KEYWORD = 'AUTOREF'

    PARAMETERS = {
        'I': (1, 'Mode (1, 2 or 3.'),
        'I1': (1, 'Particle number (only used if I = 3'),
        'I2': (1, 'Particle number (only used if I = 3'),
        'I3': (1, 'Particle number (only used if I = 3'),
    }

    def __str__(self) -> str:
        c = f"""
        {super().__str__().rstrip()}
        {self.I}
        """
        if self.I == 3:
            c += f"""
        {self.I1} {self.I2} {self.I3}
            """
        return c


class BeamBeam(Command):
    """Beam-beam lens."""
    KEYWORD = 'BEAMBEAM'


class Binary(Command):
    """BINARY/FORMATTED data converter."""
    KEYWORD = 'BINARY'


class Chambre(Command):
    """Long transverse aperture limitation."""
    KEYWORD = 'CHAMBR'

    PARAMETERS = {
        'IA': (0, '0 (element inactive), 1 ((re)definition of the aperture), 2 (stop testing and reset counters,'
                  'print information on stopped particles'),
        'IFORM': (1, '1 (rectangular aperture), 2 (elliptical aperture)'),
        'J': (0, '0 (default) or 1'),
        'C1': (100 * ureg.cm, 'If J=0, Y opening, if J=1, inner Y opening'),
        'C2': (100 * ureg.cm, 'If J=0, Z opening, if J=1, outer Y opening'),
        'C3': (0 * ureg.cm, 'If J=0, Y center, if J=1, inner Z opening'),
        'C4': (0 * ureg.cm, 'If J=0, Z center, if J=1, outer Z opening'),
    }


# Aliases
Chamber = Chambre
Chambr = Chambre


class ChangeRef(Command, Patchable):
    """Transformation to a new reference frame.

    Supports only Zgoubi "new style" ChangeRef. To recover the "old style", do XS, YS, ZR.
    """
    KEYWORD = 'CHANGREF'
    PARAMETERS = {
        'TRANSFORMATIONS': []
    }

    def __str__(s):
        c =  f"""
        {super().__str__().rstrip()}
        """
        for t in s.TRANSFORMATIONS:
            if t[1].dimensionality == ureg.cm.dimensionality:
                c += f"{t[0]} {_cm(t[1])} "
            elif t[1].dimensionality == ureg.radian.dimensionality:
                c += f"{t[0]} {_degree(t[1])} "
            else:
                raise ZgoubidoException("Incorrect dimensionality in CHANGEREF.")
        return c

    @property
    def entry_patched(self) -> Frame:
        if self._entry_patched is None:
            self._entry_patched = Frame(self.entry)
            for t in self.TRANSFORMATIONS:
                if len(t) > 2:
                    raise Exception("Invalid transformation.")
                if t[0].endswith('S'):
                    self._entry_patched.translate_axis(t[0][0], t[1])
                elif t[0].endswith('R'):
                    self._entry_patched.rotate_axis(t[0][0], t[1])
        return self._entry_patched


# Alias
ChangRef = ChangeRef


class Collimateur(Command):
    """Collimator."""
    KEYWORD = 'COLLIMA'
    PARAMETERS = {
        'IA': (2, 'Element active or not (0 - inactive, 1 - active, 2 - active and prints information.'),
        'IFORM': (1, 'Aperture shape.'),
        'J': (0, 'Description of the aperture coordinates system.'),
        'C1': (0 * ureg.cm, 'Half opening (Y).'),
        'C2': (0 * ureg.cm, 'Half opening (Z).'),
        'C3': (0 * ureg.cm, 'Center of the aperture (Y).'),
        'C4': (0 * ureg.cm, 'Center of the aperture (Z).'),
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IA}
        {s.IFORM}.{s.J} {s.C1} {s.C2} {s.C3} {s.C4}
        """


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

    PARAMETERS = {
        'FNAME': 'zgoubi.fai',
        'IP': 1,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.FNAME}
        {s.IP}
        """


class Fin(Command):
    """End of input data list."""
    KEYWORD = 'FIN'


class Fit(Command):
    """Fitting procedure."""
    KEYWORD = 'FIT'

    PARAMETERS = {
        'PARAMS': (
            [
                {
                    'IR': 1,
                    'IP': 1,
                    'XC': 0,
                    'DV': 1.0
                }
            ], 'Physical parameters to be varied'),
        'CONSTRAINTS': (
            [
                {
                    'IC': 1,
                    'I': 1,
                    'J': 1,
                    'IR': 1,
                    'V': 1,
                    'WV': 1,
                    'NP': 1
                }
            ], 'Constraints'),
        'PENALTY': (1.0e-14, 'Penalty'),
        'ITERATIONS': (1000, 'Iterations'),
    }

    def __str__(s):
        command = list()
        command.append(super().__str__().rstrip())
        command.append(f"""
        {len(s.PARAMS)}
        """)
        for p in s.PARAMS:
            command.append(f"""
        {p['IR']} {p['IP']} {p['XC']} [-30.0,30.0]
        """)
        command.append(f"""
        {len(s.CONSTRAINTS)} {s.PENALTY:.12e} {s.ITERATIONS}
        """)
        for c in s.CONSTRAINTS:
            command.append(f"""
        {c['IC']} {c['I']} {c['J']} {c['IR']} {c['V']} {c['WV']} {c['NP']}
        """)
        return ''.join(map(lambda x: x.rstrip(), command))


class Fit2(Fit):
    """Fitting procedure."""
    KEYWORD = 'FIT2'


class Focale(Command):
    """Particle coordinates and horizontal beam size at distance XL."""
    KEYWORD = 'FOCALE'

    PARAMETERS = {
        'XL': (0.0 * ureg.centimeter, 'Distance from the location of the keyword.'),
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.XL.to('cm').magnitude}
        """


class FocaleZ(Command):
    """Particle coordinates and vertical beam size at distance XL."""
    KEYWORD = 'FOCALEZ'

    PARAMETERS = {
        'XL': (0.0 * ureg.centimeter, 'Distance from the location of the keyword.'),
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.XL.to('cm').magnitude}
        """


class GasScattering(Command):
    """Gas scattering."""
    KEYWORD = 'GASCAT'

    PARAMETERS = {
        'KGA': 0,
        'AI': 0.0,
        'DEN': 0.0,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.KGA}
        {s.AI} {s.DEN}
        """


class GetFitVal(Command):
    """Get values of variables as saved from former FIT[2] run."""
    KEYWORD = 'GETFITVAL'

    PARAMETERS = {
        'FNAME': 'zgoubi.res',
    }

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.FNAME}
        """


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

    def __init__(self, label1='', label2='', *params, with_plt=True, **kwargs):
        super().__init__(label1, label2, self.PARAMETERS, *params, **kwargs)
        self.LABEL2 = '.plt' if with_plt else ''


class Matrix(Command):
    """Calculation of transfer coefficients, periodic parameters."""
    KEYWORD = 'MATRIX'

    PARAMETERS = {
        'IORD': 1,
        'IFOC': (11, 'If IFOC=11, periodic parameters (single pass)'),
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IORD} {s.IFOC} PRINT
        """


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
        'KWRIT': 1.1,
        'K': 99,
        'N': None,
        'LABL1': None,
        'LABL2': None,
        'NPRM': 1,
    }

    def __str__(s):
        return f"""
        {super().__str__()}
        {s.NPASS} {s.KWRIT} {s.K}.{s.N or ''} {s.LABL1 or ''} {s.LABL2 or ''}
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

    PARAMETERS = {
        'KTW': 1,
        'FACD': 1.0,
        'FACA': (0.0, 'Unused'),
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.KTW} {s.FACD:.12e} {s.FACA:.12e}
        """


class WienFilter(Command):
    """Wien filter."""
    KEYWORD = 'WIENFILT'


class Ymy(Command, Patchable):
    """Reverse signs of Y and Z reference axes."""
    KEYWORD = 'YMY'

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        """

    @property
    def entry_patched(self) -> Frame:
        if self._entry_patched is None:
            self._entry_patched = Frame(self.entry)
            self._entry_patched.rotate_x(180 * ureg.degree)
        return self._entry_patched
