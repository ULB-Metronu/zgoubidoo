"""
Commands controlling Zgoubi's control flow, geometry, tracking options, etc.

TODO
"""
from __future__ import annotations
from typing import NoReturn, Optional, Any, Tuple, Dict, List
import uuid
import pandas as _pd
from pint import UndefinedUnitError as _UndefinedUnitError
from .patchable import Patchable as _Patchable
from .. import ureg as _ureg
from .. import _Q
from ..frame import Frame as _Frame
from ..units import _radian, _degree, _m, _cm
import zgoubidoo

ZGOUBI_LABEL_LENGTH: int = 10
"""Maximum length for the Zgoubi command labels. Used to be 8 on older versions."""


class ZgoubidooException(Exception):
    """Exception raised for errors in the Zgoubidoo commands module."""

    def __init__(self, m):
        self.message = m


class MetaCommand(type):
    """
    Dark magic.
    Be careful.

    TODO
    """
    def __new__(mcs, name: str, bases: Tuple[type, ...], dct: Dict[str, Any]):
        # Insert a default initializer (constructor) in case one is not present
        if '__init__' not in dct:
            def default_init(self, label1: str = '', label2: str = '', *params, **kwargs):
                """Default initializer for all Commands."""
                bases[0].__init__(self, label1, label2, dct.get('PARAMETERS', {}), *params, **kwargs)
                if 'post_init' in dct:
                    dct['post_init'](self, **kwargs)
            dct['__init__'] = default_init

        # Collect all post_init arguments
        if '_POST_INIT' not in dct:
            dct['_POST_INIT'] = {}
        if 'post_init' in dct and len(bases) > 0:
            dct['_POST_INIT'] = [*getattr(bases[0], '_POST_INIT', {}), *dct['post_init'].__code__.co_varnames]

        # Add a default keyword
        if 'KEYWORD' not in dct:
            for b in bases:
                if getattr(b, 'KEYWORD', None):
                    dct['KEYWORD'] = b.KEYWORD
                    break

        # Add comment to all PARAMETERS entry
        for k, v in dct.get('PARAMETERS', {}).items():
            if not isinstance(v, (tuple, list)):
                dct['PARAMETERS'][k] = (v, )
                if isinstance(getattr(bases[0], 'PARAMETERS', {}).get(k), (tuple, list)):
                    if len(getattr(bases[0], 'PARAMETERS', {}).get(k)) > 1:
                        dct['PARAMETERS'][k] = (*dct['PARAMETERS'][k], getattr(bases[0], 'PARAMETERS', {}).get(k)[1])
                    if len(getattr(bases[0], 'PARAMETERS', {}).get(k)) > 2:
                        dct['PARAMETERS'][k] = (*dct['PARAMETERS'][k], getattr(bases[0], 'PARAMETERS', {}).get(k)[2])

        # Add PARAMETERS from the base class
        try:
            dct['PARAMETERS'] = {**getattr(bases[0], 'PARAMETERS', {}), **dct.get('PARAMETERS', {})}
        except IndexError:
            pass

        return super().__new__(mcs, name, bases, dct)

    def __init__(cls, name: str, bases: Tuple[type, ...], dct: Dict[str, Any]):
        super().__init__(name, bases, dct)
        if cls.__doc__ is not None:
            cls.__doc__ = cls.__doc__.rstrip()
            cls.__doc__ += """
            
    .. rubric:: Command attributes
    
    Attributes:
            """
            for k, v in cls.PARAMETERS.items():
                if isinstance(v, tuple) and len(v) >= 2:
                    cls.__doc__ += f"""
        {k}='{v[0]}' ({type(v[0]).__name__}): {v[1]}
            """


class Command(metaclass=MetaCommand):
    """Test test test.

    More info on this wonderful class.
    TODO
    """
    KEYWORD: str = ''
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS: dict = {
        'LABEL1': ('', 'Primary label for the Zgoubi command (default: auto-generated hash).'),
        'LABEL2': ('', 'Secondary label for the Zgoubi command.'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __init__(self, label1: str='', label2: str='', *params, **kwargs):
        """
        TODO
        Args:
            label1:
            label2:
            *params:
            **kwargs:
        """
        self._output = list()
        self._results = None
        self._attributes = {}
        for d in (Command.PARAMETERS, ) + params + (
                {
                    'LABEL1': (label1 or str(uuid.uuid4().hex)[:ZGOUBI_LABEL_LENGTH], ''),
                    'LABEL2': (label2, )
                },):
            self._attributes = dict(self._attributes, **{k: v[0] for k, v in d.items()})
        for k, v in kwargs.items():
            if k not in self._POST_INIT:
                setattr(self, k, v)
        Command.post_init(self, **kwargs)

    def post_init(self, **kwargs) -> NoReturn:
        """
        TODO
        Args:
            **kwargs: all arguments from the initializer (constructor) are passed to ``post_init`` as keyword arguments.

        Examples:
            >>> xxx

        """
        pass

    def __getattr__(self, a: str) -> Any:
        """
        TODO
        Args:
            a:

        Returns:

        """
        if self._attributes.get(a) is None:
            return None
        attr = self._attributes[a]
        if not isinstance(attr, str) and not isinstance(attr, _Q):
            try:
                _ = _Q(attr)
                if _.dimensionless:
                    return _.magnitude
                else:
                    return _
            except (TypeError, ValueError, _UndefinedUnitError):
                return attr
        else:
            return attr

    def __setattr__(self, k: str, v: Any) -> NoReturn:
        """
        TODO
        Args:
            k:
            v:

        Returns:

        """
        if k.startswith('_'):
            super().__setattr__(k, v)
        else:
            if k not in self._attributes.keys():
                raise ZgoubidooException(f"The parameter {k} is not part of the {self.__class__.__name__} definition.")
            else:
                try:
                    default = self.PARAMETERS[k][0]
                except (TypeError, IndexError):
                    default = self.PARAMETERS[k]
            try:
                dimension = v.dimensionality
            except AttributeError:
                dimension = _ureg.Quantity(1).dimensionality
            try:
                if default is not None and dimension != _ureg.Quantity(default).dimensionality:
                    raise ZgoubidooException(f"Invalid dimension ({dimension} "
                                             f"instead of {_ureg.Quantity(default).dimensionality}) "
                                             f"for parameter {k}={v}."
                                             )
            except (ValueError, TypeError, _UndefinedUnitError):
                pass
            self._attributes[k] = v

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        """
        Provides the string representation of the command in the Zgoubi input file format.

        Returns:
            The string representation.

        Examples:
            >>> c = Command('my_label_1', 'my_label_2')
            >>> print(c)
        """
        return f"""
        '{self.KEYWORD}' {self.LABEL1} {self.LABEL2}
        """

    @property
    def attributes(self) -> Dict[str, _ureg.Quantity]:
        """All attributes.

        Provides a dictionary with all attributes for the command.

        Returns: dictionnary with all attributes.

        """
        return self._attributes

    @property
    def defaults(self) -> Dict[str, _ureg.Quantity]:
        """Default attributes.

        Provides a dictionary with all attributes that have been assigned a default value.

        Returns: dictionary with all default attributes.
        """
        return {k: v for k, v in self._attributes.items() if v == self.PARAMETERS.get(k)[0]}

    @property
    def nondefaults(self) -> Dict[str, _ureg.Quantity]:
        """Non default attributes.

        Provides a dictionary with all attributes that have been assigned a non default value.

        Returns: dictionary with all non default attributes.
        """
        return {k: v for k, v in self._attributes.items() if v != self.PARAMETERS.get(k)[0]}

    @property
    def output(self) -> List[str]:
        """
        Provides the outputs associated with a command after each successive Zgoubi run.

        Returns:
            the output, None if no output has been previously attached.
        """
        return self._output

    @property
    def results(self):
        """
        Provides the outputs associated with a command after each successive Zgoubi run.

        Returns:
            the output, None if no output has been previously attached.
        """
        return self._results.set_index('variable_id')

    def attach_output(self, output: str, zgoubi_input: zgoubidoo.Input) -> NoReturn:
        """
        Attach the ouput that an command has generated during a Zgoubi run.

        Args:
            output: the output from a Zgoubi run to be attached to the command.
            zgoubi_input: xxxx.
        """
        self._output.append(output)
        self.process_output(output, zgoubi_input)

    def process_output(self, output: str, zgoubi_input: zgoubidoo.Input) -> Optional[bool]:
        """
        
        Args:
            output:
            zgoubi_input:

        Returns:

        """
        pass


class AutoRef(Command):
    """Automatic transformation to a new reference frame.

    TODO
    """
    KEYWORD = 'AUTOREF'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'I': (1, 'Mode (1, 2 or 3).'),
        'I1': (1, 'Particle number (only used if I = 3)'),
        'I2': (1, 'Particle number (only used if I = 3)'),
        'I3': (1, 'Particle number (only used if I = 3)'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

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
    """Beam-beam lens.

    TODO
    """
    KEYWORD = 'BEAMBEAM'
    """Keyword of the command used for the Zgoubi input data."""


class Binary(Command):
    """BINARY/FORMATTED data converter.

    TODO
    """
    KEYWORD = 'BINARY'
    """Keyword of the command used for the Zgoubi input data."""


class Chambre(Command):
    """Long transverse aperture limitation."""
    KEYWORD = 'CHAMBR'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IA': (0, '0 (element inactive), 1 ((re)definition of the aperture), 2 (stop testing and reset counters,'
                  'print information on stopped particles'),
        'IFORM': (1, '1 (rectangular aperture), 2 (elliptical aperture)'),
        'J': (0, '0 (default) or 1'),
        'C1': (100 * _ureg.cm, 'If J=0, Y opening, if J=1, inner Y opening'),
        'C2': (100 * _ureg.cm, 'If J=0, Z opening, if J=1, outer Y opening'),
        'C3': (0 * _ureg.cm, 'If J=0, Y center, if J=1, inner Z opening'),
        'C4': (0 * _ureg.cm, 'If J=0, Z center, if J=1, outer Z opening'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""


# Aliases
Chamber = Chambre
Chambr = Chambre


class ChangRef(Command, _Patchable):
    """Transformation to a new reference frame.

    Supports only Zgoubi "new style" ChangeRef. To recover the "old style", do XS, YS, ZR.
    TODO
    """
    KEYWORD = 'CHANGREF'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'TRANSFORMATIONS': []
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        c = f"""
        {super().__str__().rstrip()}
        """
        for t in self.TRANSFORMATIONS:
            if t[1].dimensionality == _ureg.cm.dimensionality:
                c += f"{t[0]} {_cm(t[1])} "
            elif t[1].dimensionality == _ureg.radian.dimensionality:
                c += f"{t[0]} {_degree(t[1])} "
            else:
                raise ZgoubidooException("Incorrect dimensionality in CHANGEREF.")
        return c

    @property
    def entry_patched(self) -> _Frame:
        """

        Returns:

        """
        if self._entry_patched is None:
            self._entry_patched = _Frame(self.entry)
            for t in self.TRANSFORMATIONS:
                if len(t) > 2:
                    raise Exception("Invalid transformation.")
                if t[0].endswith('S'):
                    self._entry_patched.translate_axis(t[0][0], t[1])
                elif t[0].endswith('R'):
                    self._entry_patched.rotate_axis(t[0][0], t[1])
        return self._entry_patched


# Alias
ChangeRef = ChangRef


class Collimateur(Command):
    """Collimator.

    TODO
    """
    KEYWORD = 'COLLIMA'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IA': (2, 'Element active or not (0 - inactive, 1 - active, 2 - active and prints information.'),
        'IFORM': (1, 'Aperture shape.'),
        'J': (0, 'Description of the aperture coordinates system.'),
        'C1': (0 * _ureg.cm, 'Half opening (Y).'),
        'C2': (0 * _ureg.cm, 'Half opening (Z).'),
        'C3': (0 * _ureg.cm, 'Center of the aperture (Y).'),
        'C4': (0 * _ureg.cm, 'Center of the aperture (Z).'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.IA}
        {self.IFORM}.{self.J} {self.C1} {self.C2} {self.C3} {self.C4}
        """


# Alias
Collimator = Collimateur


class Cible(Command):
    """Generate a secondary beam following target interaction.

    TODO
    """
    KEYWORD = 'CIBLE'
    """Keyword of the command used for the Zgoubi input data."""


class End(Command):
    """End of input data list.

    The end of a problem, or of a set of several problems stacked in the data file, should be stated by means of the
    keywords FIN or END.

    Any information following these keywords will be ignored.

    In some cases, these keywords may cause some information to be printed in zgoubi.res, for instance when the keyword
    PICKUPS is used.
    """
    KEYWORD = 'END'
    """Keyword of the command used for the Zgoubi input data."""


class ESL(Command):
    """??? Field free drift space."""


class Faisceau(Command):
    """Print particle coordinates.

    TODO
    """
    KEYWORD = 'FAISCEAU'
    """Keyword of the command used for the Zgoubi input data."""


class Faiscnl(Command):
    """Store particle coordinates in file FNAME.

    TODO
    """
    KEYWORD = 'FAISCNL'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'FNAME': 'zgoubi.fai',
        'B_FNAME': 'b_zgoubi.fai',
        'binary': False,
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.B_FNAME if self.binary else self.FNAME}
        """


class FaiStore(Command):
    """Store coordinates every IP other pass at labeled elements.

    TODO
    """
    KEYWORD = 'FAISTORE'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'FNAME': 'zgoubi.fai',
        'IP': 1,
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.FNAME}
        {self.IP}
        """


class Fin(Command):
    """End of input data list.

    The end of a problem, or of a set of several problems stacked in the data file, should be stated by means of the
    keywords FIN or END.

    Any information following these keywords will be ignored.

    In some cases, these keywords may cause some information to be printed in zgoubi.res, for instance when the keyword
    PICKUPS is used.
    """
    KEYWORD = 'FIN'
    """Keyword of the command used for the Zgoubi input data."""


class Fit(Command):
    """Fitting procedure.

    TODO
    """
    KEYWORD = 'FIT'
    """Keyword of the command used for the Zgoubi input data."""

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
                    'NP': 0
                }
            ], 'Constraints'),
        'PENALTY': (1.0e-8, 'Penalty'),
        'ITERATIONS': (10000, 'Iterations'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        command = list()
        command.append(super().__str__().rstrip())
        command.append(f"""
        {len(self.PARAMS)}
        """)
        for p in self.PARAMS:
            if isinstance(p['IP'], (list, tuple)):
                ip = p['IP'][2]
            else:
                ip = p['IP']
            if isinstance(p['DV'], (list, tuple)):
                command.append(f"""
        {p['IR']} {ip} {p['XC']} [{p['DV'][0]}, {p['DV'][1]}]
        """)
            else:
                command.append(f"""
        {p['IR']} {ip} {p['XC']} {p['DV']}
        """)
        command.append(f"""
        {len(self.CONSTRAINTS)} {self.PENALTY:.12e} {self.ITERATIONS}
        """)
        for c in self.CONSTRAINTS:
            command.append(f"""
        {c['IC']} {c['I']} {c['J']} {c['IR']} {c['V']} {c['WV']} {c['NP']}
        """)
        return ''.join(map(lambda x: x.rstrip(), command))

    def process_output(self, output: str, zgoubi_input: zgoubidoo.Input) -> Optional[bool]:
        """

        Args:
            output:
            zgoubi_input:

        Returns:

        """
        def find_parameter_by_id(command: int, parameter: int) -> str:
            """

            Args:
                command:
                parameter:

            Returns:

            """
            k = None
            for k, v in zgoubi_input[command - 1].__class__.PARAMETERS.items():
                if v is None:
                    continue
                try:
                    if v[2] == parameter:
                        break
                except (TypeError, IndexError):
                    continue
            return k

        def find_dimension_by_id(command: int, parameter: int):
            """

            Args:
                command:
                parameter:

            Returns:

            """
            for k, v in zgoubi_input[command - 1].__class__.PARAMETERS.items():
                if v is None:
                    continue
                try:
                    if v[2] == parameter:
                        break
                except (TypeError, IndexError):
                    continue
            return zgoubidoo._Q(v[0]).units

        grab: bool = False
        data: list = []
        for l in self.output:
            if l.strip().startswith('LMNT'):
                grab = True
                continue
            if l.strip().startswith('STATUS OF'):
                grab = False
            if grab:
                values = l.split()
                d = {
                        'element_id': int(values[0]),
                        'variable_id': int(values[1]),
                        'parameter_id': int(values[2]),
                        'parameter': find_parameter_by_id(int(values[0]), int(values[2])),
                        'min': float(values[3]),
                        'initial': float(values[4]),
                        'final': float(values[5]) * find_dimension_by_id(int(values[0]), int(values[2])),
                        'max': float(values[6]),
                        'stepsize': float(values[7]),
                }
                if len(values) >= 9:
                    d['name'] = values[8]
                    d['label1'] = values[9]
                    d['label2'] = values[10]
                data.append(d)
        self._results = _pd.DataFrame(data)
        return True


class Fit2(Fit):
    """Fitting procedure.

    TODO
    """
    KEYWORD = 'FIT2'
    """Keyword of the command used for the Zgoubi input data."""


class Focale(Command):
    """Particle coordinates and horizontal beam size at distance XL.

    TODO
    """
    KEYWORD = 'FOCALE'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'XL': (0.0 * _ureg.centimeter, 'Distance from the location of the keyword.'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {_cm(self.XL)}
        """


class FocaleZ(Command):
    """Particle coordinates and vertical beam size at distance XL.

    TODO
    """
    KEYWORD = 'FOCALEZ'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'XL': (0.0 * _ureg.centimeter, 'Distance from the location of the keyword.'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {_cm(self.XL)}
        """


class GasScattering(Command):
    """Gas scattering.

    Modification of particle momentum and velocity vector, performed at each integration step, under the effect of
    scattering by residual gas.
    **Implementation is to be completed in Zgoubi**.
    """
    KEYWORD = 'GASCAT'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'KGA': 0,
        'AI': 0.0,
        'DEN': 0.0,
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.KGA}
        {self.AI} {self.DEN}
        """


class GetFitVal(Command):
    """Get values of variables as saved from former FIT[2] run.

    This keyword allows reading, from a file whose name needs be specified, parameter values to be assigned to optical
    elements in zgoubi.dat.
    That file is expected to contain a copy-paste of the data under the FIT[2] procedure as displayed in zgoubi.res,
    normally under the form.

    # STATUS OF CONSTRAINTS
    # TYPE  I   J  LMNT#     DESIRED       WEIGHT         REACHED         KI2     *  Parameter(s)
    #   3   1   2   127   0.0000000E+00  1.0000E+00    1.0068088E-08   6.0335E-01 *  0 :
    #   3   1   3   127   0.0000000E+00  1.0000E+00    7.0101405E-09   2.9250E-01 *  0 :
    #   3   1   4   127   0.0000000E+00  1.0000E+00    2.9184383E-10   5.0696E-04 *  0 :
    #   3   1   5   127   0.0000000E+00  1.0000E+00    3.1142381E-10   5.7727E-04 *  0 :
    #   3   1   2   436   0.0000000E+00  1.0000E+00    3.8438378E-09   8.7944E-02 *  0 :
    #   3   1   3   436   0.0000000E+00  1.0000E+00    1.5773011E-09   1.4808E-02 *  0 :
    #   3   1   4   436   0.0000000E+00  1.0000E+00    2.2081272E-10   2.9022E-04 *  0 :
    #   3   1   5   436   0.0000000E+00  1.0000E+00    5.7930552E-11   1.9975E-05 *  0 :
    #   Function  called   1859 times
    # Xi2 =    1.68006E-16   Busy...

    A ’#’ at the beginning of a line means it is commented, thus it will not be taken into account. However a copy-paste
    from zgoubi.res (which is the case in the present example) would not not need any commenting.
    Since some of the FIT[2] variables may belong in [MC]OBJET, GETFITVAL may appear right before [MC]OBJET in zgoubi.dat,
    to allow for its updating.

    """
    KEYWORD = 'GETFITVAL'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'FNAME': 'zgoubi.res',
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.FNAME}
        """


class Histo(Command):
    """1-Dhistogram"""
    KEYWORD = 'HISTO'
    """Keyword of the command used for the Zgoubi input data."""


class Image(Command):
    """Localization and size of horizontal waist."""
    KEYWORD = 'IMAGE'
    """Keyword of the command used for the Zgoubi input data."""


class Images(Command):
    """Localization and size of horizontal waists."""
    KEYWORD = 'IMAGES'
    """Keyword of the command used for the Zgoubi input data."""


class ImageZ(Command):
    """Localization and size of vertical waist."""
    KEYWORD = 'IMAGEZ'
    """Keyword of the command used for the Zgoubi input data."""


class ImagesZ(Command):
    """Localization and size of vertical waists."""
    KEYWORD = 'IMAGESZ'
    """Keyword of the command used for the Zgoubi input data."""


class Marker(Command):
    """Marker."""
    KEYWORD = 'MARKER'
    """Keyword of the command used for the Zgoubi input data."""

    def __init__(self, label1='', label2='', *params, with_plt=True, **kwargs):
        super().__init__(label1, label2, self.PARAMETERS, *params, **kwargs)
        self.LABEL2 = '.plt' if with_plt else ''


class Matrix(Command):
    """Calculation of transfer coefficients, periodic parameters."""
    KEYWORD = 'MATRIX'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IORD': 1,
        'IFOC': (11, 'If IFOC=11, periodic parameters (single pass)'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.IORD} {self.IFOC} PRINT
        """


class MCDesintegration(Command):
    """Monte-Carlo simulation of in-flight decay."""
    KEYWORD = 'MCDESINT'
    """Keyword of the command used for the Zgoubi input data."""


class Optics(Command):
    """Write out optical functions.

    OPTICS normally appears next to object definition, it normally works in conjunction with element label(s).
    OPTICS causes the transport and write out, in zgoubi.res, of the 6×6 beam matrix, following options KOPT and
    ’label ’, below.

    IF KOPT=0 : Off
    IF KOPT=1 : Will transport the optical functions with initial values as specified in OBJET, option KOBJ=5.01.

    *Note*: The initial values in OBJET[KOBJ=5.01] may be the periodic ones, as obtained, for instance, from a first
    run using MATRIX[IFOC=11].

    A second argument, ’label ’, allows

        - if label = all : printing out, into zgoubi.res, after all keywords of the zgoubi.dat structure,
        - otherwise, printing out at all keyword featuring LABEL ≡ label as a first label (see section 4.6.5,
          page 162, regarding the labelling of keywords).

    A third argument, IMP=1, will cause saving of the transported beta functions into file zgoubi.OPTICS.out.
    """
    KEYWORD = 'OPTICS'
    """Keyword of the command used for the Zgoubi input data."""


class Ordre(Command):
    """Taylor expansions order."""
    KEYWORD = 'ORDRE'
    """Keyword of the command used for the Zgoubi input data."""


class Pickups(Command):
    """Beam centroid path; closed orbit."""
    KEYWORD = 'PICKUPS'
    """Keyword of the command used for the Zgoubi input data."""


class PlotData(Command):
    """Intermediate output for the PLOTDATA graphic software."""
    KEYWORD = 'PLOTDATA'
    """Keyword of the command used for the Zgoubi input data."""


class Rebelote(Command):
    """’Do it again’."""

    KEYWORD = 'REBELOTE'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'NPASS': 1,
        'KWRIT': 1.1,
        'K': 99,
        'N': None,
        'LABL1': None,
        'LABL2': None,
        'NPRM': 1,
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__()}
        {self.NPASS} {self.KWRIT} {self.K}.{self.N or ''} {self.LABL1 or ''} {self.LABL2 or ''}
        """


class Reset(Command):
    """Reset counters and flags.

    .. rubric:: Zgoubi manual description

    Piling up problems in zgoubi input data file is allowed, with normally no particular precaution, except that each
    new problem must begin with a new object definition (using MCOBJET, OBJET). Nevertheless, when calling upon certain
    keywords, then, flags, counters or other integrating procedures may be involved. It may therefore be necessary to
    reset them. This is the purpose of RESET which normally appears right before the object definition and causes each
    problem to be treated as a new and independent one.

    The keywords or procedures of concern and the effect of RESET are the following:

        - **CHAMBR**: number of stopped particles reset to 0 ; CHAMBR option switched off
        - **COLLIMA**: number of stopped particles reset to 0
        - **HISTO**: histograms are emptied
        - **INTEG**: number of particles out of field map boundaries reset to 0
        - **MCDESINT**: decay in flight option switched off, counter reset
        - **PICKUPS**: pick-up signal calculation switched off
        - **SCALING**: scaling functions disabled
        - **SPNTRK**: spin tracking option switched off

    .. rubric:: Zgoubidoo usage and example

    >>> Reset()
    """
    KEYWORD = 'RESET'
    """Keyword of the command used for the Zgoubi input data."""


class Scaling(Command):
    """Power supplies and R.F. function generator."""
    KEYWORD = 'SCALING'
    """Keyword of the command used for the Zgoubi input data."""


class Separa(Command):
    """Wien Filter - analytical simulation."""
    KEYWORD = 'SEPARA'
    """Keyword of the command used for the Zgoubi input data."""


class SynchrotronRadiationLosses(Command):
    """Synchrotron radiation loss.

    The keyword SRLOSS allows activating or stopping (option KSR = 1, 0 respectively) stepwise tracking of energy loss
    by stochastic emission of photons in magnetic fields, following the method described in section 3.1.

    It can be chosen to allow radiation in the sole dipole fields, or in all types of fields regardless of their
    multipole composition. It can also be chosen to allow for the radiation induced transverse kick.

    SRLOSS must be preceded by PARTICUL for defining mass and charge values as they enter in the defini- tion of SR
    parameters.

    Statistics on SR parameters are computed and updated while tracking, the results of which can be obtained by means
    of the keyword SRPRNT.
    """
    KEYWORD = 'SRLOSS'
    """Keyword of the command used for the Zgoubi input data."""


class SynchrotronRadiationPrint(Command):
    """Print SR loss statistics."""
    KEYWORD = 'SRPRNT'
    """Keyword of the command used for the Zgoubi input data."""


class SynchrotronRadiation(Command):
    """Synchrotron radiation spectral-angular densities."""
    KEYWORD = 'SYNRAD'
    """Keyword of the command used for the Zgoubi input data."""


class Target(Command):
    """Generate a secondary beam following target interaction."""
    KEYWORD = 'TARGET'
    """Keyword of the command used for the Zgoubi input data."""


class TransferMatrix(Command):
    """Transfer matrix."""
    KEYWORD = 'TRANSMAT'
    """Keyword of the command used for the Zgoubi input data."""


class TranslationRotation(Command):
    """Translation-Rotation of the reference frame."""
    KEYWORD = 'TRAROT'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'TX': (0 * _ureg.m, 'X axis translation'),
        'TY': (0 * _ureg.m, 'Y axis translation'),
        'TZ': (0 * _ureg.m, 'Z axis translation'),
        'RX': (0 * _ureg.degree, 'X axis rotation'),
        'RY': (0 * _ureg.degree, 'Y axis rotation'),
        'RZ': (0 * _ureg.degree, 'Z axis rotation'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        s = self
        return f"""
        {super().__str__().rstrip()}
        {_m(s.TX):.12e} {_m(s.TY):.12e} {_m(s.TZ):.12e} {_radian(s.RX):.12e} {_radian(s.RY):.12e} {_radian(s.RZ):.12e}
        """


class Twiss(Command):
    """Calculation of periodic optical parameters."""
    KEYWORD = 'TWISS'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'KTW': 1,
        'FACD': 1.0,
        'FACA': (0.0, 'Unused'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.KTW} {self.FACD:.12e} {self.FACA:.12e}
        """


class WienFilter(Command):
    """Wien filter.

    TODO
    """
    KEYWORD = 'WIENFILT'
    """Keyword of the command used for the Zgoubi input data."""


class Ymy(Command, _Patchable):
    """Reverse signs of Y and Z reference axes, equivalent to a 180 degree rotation around the X axis.

    TODO
    """
    KEYWORD = 'YMY'
    """Keyword of the command used for the Zgoubi input data."""

    @property
    def entry_patched(self) -> _Frame:
        """

        Returns:

        """
        if self._entry_patched is None:
            self._entry_patched = _Frame(self.entry)
            self._entry_patched.rotate_x(180 * _ureg.degree)
        return self._entry_patched
