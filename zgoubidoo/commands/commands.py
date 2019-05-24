"""
Commands controlling Zgoubi's control flow, geometry, tracking options, etc.

TODO
"""
from __future__ import annotations
from typing import Any, Tuple, Dict, Mapping, List, Union, Iterable
import uuid
import numpy as _np
import pandas as _pd
import parse as _parse
from pint import UndefinedUnitError as _UndefinedUnitError
from .patchable import Patchable as _Patchable
from .. import ureg as _ureg
from .. import _Q
from ..frame import Frame as _Frame
from ..units import _radian, _degree, _m, _cm
from ..utils import fortran_float
import zgoubidoo

ZGOUBI_LABEL_LENGTH: int = 10
"""Maximum length for the Zgoubi command labels. Used to be 8 on older versions."""


class ZgoubidooException(Exception):
    """Exception raised for errors in the Zgoubidoo commands module."""

    def __init__(self, m):
        self.message = m


class CommandType(type):
    """
    Dark magic.
    Be careful.

    TODO
    """
    def __new__(mcs, name: str, bases: Tuple[CommandType, type, ...], dct: Dict[str, Any]):
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

    def __getattr__(cls, key: str):
        try:
            if key.endswith('_'):
                return cls.PARAMETERS[key.rstrip('_')][2]
            else:
                return cls.PARAMETERS[key][0]
        except KeyError:
            raise AttributeError(key)

    def __getitem__(cls, item: str):
        try:
            return cls.PARAMETERS[item]
        except KeyError:
            raise AttributeError(item)

    def __contains__(cls, item) -> bool:
        return item in cls.PARAMETERS


class Command(metaclass=CommandType):
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

    class CommandResult:
        """TODO"""
        def __init__(self, success: bool, results: _pd.DataFrame):
            self._success: bool = success
            self._results: _pd.DataFrame = results

        @property
        def success(self) -> bool:
            """TODO"""
            return self._success

        @property
        def results(self) -> _pd.DataFrame:
            """TODO"""
            return self._results

    def __init__(self, label1: str = '', label2: str = '', *params, **kwargs):
        """
        TODO
        Args:
            label1:
            label2:
            *params:
            **kwargs:
        """
        self._output: List[Tuple[Mapping[str, Union[_Q, float]], List[str]]] = list()
        self._results: List[Tuple[Mapping[str, Union[_Q, float]], Command.CommandResult]] = list()
        self._attributes = {}
        for d in (Command.PARAMETERS, ) + params:
            self._attributes = dict(self._attributes, **{k: v[0] for k, v in d.items()})
        for k, v in kwargs.items():
            if k not in self._POST_INIT:
                setattr(self, k, v)
        if label1:
            if len(label1) > ZGOUBI_LABEL_LENGTH:
                raise ZgoubidooException(f"LABEL1 '{label1}' for element {self.KEYWORD} is too long.")
            self._attributes['LABEL1'] = label1
        if label2:
            if len(label2) > ZGOUBI_LABEL_LENGTH:
                raise ZgoubidooException(f"LABEL2 '{label2}' for element {label1} ({self.KEYWORD}) is too long.")
            self._attributes['LABEL2'] = label2
        if not self._attributes['LABEL1']:
            self.generate_label()
        Command.post_init(self, **kwargs)

    def generate_label(self, prefix: str = ''):
        """

        Args:
            prefix:

        Returns:

        """
        self._attributes['LABEL1'] = '_'.join(filter(None, [
            prefix,
            str(uuid.uuid4().hex)
        ]))[:ZGOUBI_LABEL_LENGTH]
        return self

    def post_init(self, **kwargs):  # -> NoReturn:
        """
        TODO
        Args:
            **kwargs: all arguments from the initializer (constructor) are passed to ``post_init`` as keyword arguments.

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
            try:
                return super().__getattribute__(a)
            except AttributeError:
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

    def __setattr__(self, k: str, v: Any):
        """
        Custom attribute setter; all non-protected (starting with a '_') attributes in upper-case are considered
        parameters of the `Command`. As such, the method will verify that they are indeed part of the command
        definition, if not an exception is raised. For valid attributes, their dimensionality is verified against the
        command definition (the dimension of the parameter's default value).

        It is also possible to use unit inference by appending an underscore to the attributes' name. In that
        case the unit of the default value is implicitely used. This is useful in case it is known that the parameter's
        numerical value is expressed in Zgoubi's default units set.

        Examples:
            >>> c = Command()
            >>> c.LABEL1 = 'FOOBAR'

        Args:
            k: a string representing the attribute
            v: the attribute's value to be set

        Raises:
            A ZgoubidooException is raised in case the parameter is not part of the class definition or if it has
            invalid dimension.
        """
        if k.startswith('_') or not k.isupper():
            super().__setattr__(k, v)
        else:
            k_ = k.rstrip('_')
            if k_ not in self._attributes.keys():
                raise ZgoubidooException(f"The parameter {k_} is not part of the {self.__class__.__name__} definition.")

            default = self._retrieve_default_parameter_value(k_)
            if isinstance(v, (int, float)) and k.endswith('_'):
                v = _ureg.Quantity(v, _ureg.Quantity(default).units)
            try:
                dimension = v.dimensionality
            except AttributeError:
                dimension = _ureg.Quantity(1).dimensionality  # No dimension
            try:
                if default is not None and dimension != _ureg.Quantity(default).dimensionality:
                    raise ZgoubidooException(f"Invalid dimension ({dimension} "
                                             f"instead of {_ureg.Quantity(default).dimensionality}) "
                                             f"for parameter {k_}={v}."
                                             )
            except (ValueError, TypeError, _UndefinedUnitError):
                pass
            self._attributes[k_] = v

    def _retrieve_default_parameter_value(self, k: str) -> Any:
        """
        Retrieve the default value of a given parameter as defined in the Command definition (class hierarchy).

        Args:
            k: the parameter for which the default value is requested.

        Returns:
            the default value of the Command's parameter 'k'.
        """
        try:
            return self.PARAMETERS[k][0]
        except (TypeError, IndexError):
            return self.PARAMETERS[k]

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        """
        Provides the string representation of the command in the Zgoubi input file format.

        Returns:
            The string representation.

        Examples:
            >>> c = Command('my_label_1', 'my_label_2')
            >>> str(c)
        """
        return f"""
        '{self.KEYWORD}' {self.LABEL1} {self.LABEL2}
        """

    def __copy__(self):
        """Object (instance) copy operation."""
        label1 = f"{self.LABEL1}_COPY"
        if len(label1) > ZGOUBI_LABEL_LENGTH:
            label1 = str(uuid.uuid4().hex)[:ZGOUBI_LABEL_LENGTH]
        return self.__class__(label1=label1, label2=self.LABEL2, **self.attributes)

    def __deepcopy__(self, *args):
        """Object (instance) deep copy operation."""
        return self.__copy__()

    def __eq__(self, other):
        """Comparison based on string representation in the Zgoubi format."""
        return str(self) == str(other)

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
    def output(self) -> List[Tuple[Mapping[str, Union[_Q, float]], List[str]]]:
        """
        Provides the outputs associated with a command after each successive Zgoubi run.

        Returns:
            the output, None if no output has been previously attached.
        """
        return self._output

    @property
    def results(self) -> List[Tuple[Mapping[str, Union[_Q, float]], _pd.DataFrame]]:
        """
        Provides the results of a Zgoubi command in the form of a Pandas DataFrame.

        Returns:
            the results, None if not available, a DataFrame otherwise.
        """
        return self._results

    def clean_output_and_results(self):
        """
        Clears the output attached to the command.

        Returns:
            the command itself (for method chaining, etc.)
        """
        self._output = list()
        self._results = list()
        return self

    def attach_output(self,
                      outputs: List[str],
                      parameters: Mapping[str, Union[_Q, float]],
                      zgoubi_input: zgoubidoo.Input,
                      ):  # -> NoReturn:
        """
        Attach the ouput that an command has generated during a Zgoubi run.

        Args:
            outputs: the outputs from a Zgoubi run to be attached to the command.
            parameters: TODO
            zgoubi_input: the Input sequence (required for output processing).
        """
        self._output.append((parameters, outputs))
        self.process_output(outputs, parameters, zgoubi_input)

    def process_output(self, output: List[str],
                       parameters: Mapping[str, Union[_Q, float]],
                       zgoubi_input: zgoubidoo.Input
                       ) -> bool:
        """
        
        Args:
            output: the output from a Zgoubi run to be processed by the command.
            parameters: TODO
            zgoubi_input: the Input sequence (required and some cases by the command output processor).

        Returns:
            a flag indicating if the processing is valid.
        """
        return True

    @classmethod
    def build(cls, stream: str, debug: bool = False) -> Command:
        """

        Args:
            stream:
            debug:

        Returns:

        """
        if debug:
            print("-----------------")
            print(stream)
            print(f"----------------- {cls.__name__} detected")
        return cls(**cls.parse(stream).named)

    @classmethod
    def parse(cls, stream: str):
        """

        Args:
            stream:

        Returns:

        """
        return _parse.search("'{}' {label1:w}", ' '.join(stream.split()))


class Fake(Command):
    """Fake command for Zgoubi input.

    This command can be used to add an arbitrary input command in a Zgoubi input sequence. The `INPUT` parameter is
    formatted before being printed, and uses the OPTIONS command attributes list for that purpose (see examples below).
    
    Examples:
        >>> c = Fake('FAKE1', INPUT="'COMMAND_NAME' {LABEL1} 1.0 2.0 3.0")
        >>> str(c)
    """
    PARAMETERS = {
        'INPUT': ('', 'Input string.'),
        'OPTIONS': {},
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return self.INPUT.format(**self.OPTIONS)


class AutoRef(Command):
    """Automatic transformation to a new reference frame.

    .. rubric:: Zgoubi manual description

    AUTOREF positions the new reference frame following 3 options:

    - If I = 1, AUTOREF is equivalent to CHANGREF[XCE = 0,Y CE = Y (1),ALE = T(1)] so that the new reference frame is at the exit of the last element, with particle 1 at the origin with its horizontal angle set to T = 0.
    - If I = 2, it is equivalent to CHANGREF[XW,Y W,T(1)] so that the new reference frame is at the position (X W, Y W ) of the waist (calculated automatically in the same way as for IMAGE) of the three rays number 1, 4 and 5 (compatible for instance with OBJET, KOBJ = 5, 6, together with the use of MATRIX) while T(1), the horizontal angle of particle number I1, is set to zero.
    - If I = 3, it is equivalent to CHANGREF[XW,Y W,T(I1)] so that the new reference frame is at the position (X W, Y W ) of the waist (calculated automatically in the same way as for IMAGE) of the three rays number I1, I2 and I3 specified as data, while T(I1) is set to zero.
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
    """Long transverse aperture limitation.

    .. rubric:: Zgoubi manual description

    CHAMBR causes the identification, counting and stopping of particles that reach the transverse limits of the vacuum
    chamber. The chamber can be either rectangular (IFORM = 1) or elliptic (IFORM = 2). The chamber is centered at YC,
    ZC and has transverse dimensions ±Y L and ±ZL such that any particle will be stopped if its coordinates Y, Z
    satisfy.

    The conditions introduced with CHAMBR are valid along the optical structure until the next occurrence of the
    keyword CHAMBR. Then, if IL = 1 the aperture is possibly modified by introducing new values of YC, ZC, Y L and ZL,
    or, if IL = 2 the chamber ends and information is printed concerning those particles that have been stopped.

    The testing is done in optical elements at each integration step, between the EFB’s. For instance, in QUADRUPO
    there will be no testing from −XE to 0 and from XL to XL + XS, but only from 0 to XL ; in DIPOLE, there is no
    testing as long as the ENTRANCE EFB is not reached, and testing is stopped as soon as the EXIT or LATERAL EFB’s
    are passed.

    In optical elements defined in polar coordinates, Y stands for the radial coordinate (e.g., DIPOLE, see Figs. 3C,
    p. 27, and 11, p. 82). Thus, centering CHAMBR at Y C = RM simulates a chamber curved with radius RM, and having a
    radial acceptance RM ± YL. In DRIFT, the testing is done at the beginning and at the end, and only for positive
    drifts. There is no testing in CHANGREF.

    When a particle is stopped, its index IEX (see OBJET and section 4.6.10) is set to the value -4, and its actual
    path length is stored in the array SORT for possible further use.
    """
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

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.IA}
        {self.IFORM}.{self.J} {_cm(self.C1)} {_cm(self.C2)} {_cm(self.C3)} {_cm(self.C4)}
        """


# Aliases
Chamber = Chambre
Chambr = Chambre


class ChangRef(Command, _Patchable):
    """Transformation to a new reference frame.

    Supports only Zgoubi "new style" ChangeRef. To recover the "old style", do XS, YS, ZR.

    ::note: `ChangRef` supports the `Patchable` interface and the transformations will thus be taken into account when
    surveying the line.

    .. rubric:: Zgoubi manual description

    TODO
    """
    KEYWORD = 'CHANGREF'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'TRANSFORMATIONS': ([], 'List of transformations for new style ChangeRef'),
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
    def length(self) -> _Q:
        """

        Returns:

        """
        return _np.linalg.norm((self.exit_patched._get_origin() - self.entry._get_origin())) * _ureg.cm

    @property
    def exit_patched(self) -> _Frame:
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

    .. rubric:: Zgoubi manual description

    COLLIMA acts as a mathematical aperture of zero length. It causes the identification, counting and stop- ping of
    particles that reach the aperture limits.

    """
    KEYWORD = 'COLLIMA'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IA': (2, 'Element active or not (0 - inactive, 1 - active, 2 - active and prints information.'),
        'IFORM': (1, 'Aperture shape (1 - rectangular, 2 - elliptic (other options, see documentation).'),
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
        {self.IFORM}.{self.J} {_cm(self.C1)} {_cm(self.C2)} {_cm(self.C3)} {_cm(self.C4)}
        """


# Aliases
Collima = Collimateur
Collimator = Collimateur


class Cible(Command):
    """Generate a secondary beam following target interaction.

    TODO
    """
    KEYWORD = 'CIBLE'
    """Keyword of the command used for the Zgoubi input data."""


class End(Command):
    """End of input data list.

    .. rubric:: Zgoubi manual description

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
    """Print coordinates.

    .. rubric:: Zgoubi manual description

    Print particle coordinates at the location where the keyword is introduced in the structure.
    """
    KEYWORD = 'FAISCEAU'
    """Keyword of the command used for the Zgoubi input data."""


class Faiscnl(Command):
    """Store coordinates in file.

    .. rubric:: Zgoubi manual description

    Store particle coordinates in file FNAME.
    """
    KEYWORD = 'FAISCNL'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'FNAME': 'zgoubi.fai',
        'B_FNAME': 'b_zgoubi.fai',
        'binary': (False, 'Binary storage format.'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.B_FNAME if self.binary else self.FNAME}
        """


class FaiStore(Command):
    """Store coordinates at labeled elements.

    .. rubric:: Zgoubi manual description

    Store coordinates every IP other pass at labeled elements.

    If either FNAME or first LABEL is ’none’ then no storage occurs. Store occurs at all elements if first LABEL is
    ’all’ or ’ALL’.
    """
    KEYWORD = 'FAISTORE'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'FNAME': ('zgoubi.fai', 'Storage file name.'),
        'LABELS': ('ALL', 'Label(s) of the element(s) at the exit of which the storage occurs (10 labels maximum).'),
        'IP': (1, 'Store every IP other pass (when using REBELOTE with NPASS ≥ IP − 1).'),
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


class FitType(CommandType):
    """Type for fit commands."""
    pass


class Fit(Command, metaclass=FitType):
    """Fitting procedure.

    TODO
    """
    KEYWORD = 'FIT'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'PARAMS': ([], 'Physical parameters to be varied'),
        'CONSTRAINTS': ([], 'Constraints'),
        'PENALTY': (1.0e-8, 'Penalty'),
        'ITERATIONS': (50000, 'Iterations'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    class FitCoordinates:
        """Zgoubi coordinates."""
        DP = 1
        Y = 2
        T = 3
        Z = 4
        P = 5

    class Parameter:
        """
        TODO
        """
        def __init__(self,
                     line: zgoubidoo.Input,
                     place: Union[str, Command],
                     parameter: Union[int, Iterable],
                     range: Tuple[float] = None):
            """

            Args:
                line:
                place:
                parameter:
                range:
            """
            self.IR: int = line.zgoubi_index(place)
            try:
                self.IP: int = parameter[2]
            except TypeError:
                self.IP: int = parameter
            self.XC: int = 0
            self.DV: Tuple[float] = range if range is not None else [-100.0, 100.0]

        def __getitem__(self, item):
            return getattr(self, item)

    class Constraint:
        """Generic constraint."""
        def __getitem__(self, item):
            return getattr(self, item)

    class SigmaMatrixConstraint(Constraint):
        """Constraint on the coefficients of the sigma matrix."""
        pass

    class FirstOrderTransportCoefficientsConstraint(Constraint):
        """Constraint on the coefficients of the transfer matrix."""
        pass

    class SecondOrderTransportCoefficientsConstraint(Constraint):
        """Constraint on the coefficients of the second-order transport tensor."""
        pass

    class EllipseParametersConstraint(Constraint):
        """Constraint on the beam ellipse."""
        pass

    class EqualityConstraint(Constraint):
        """Equality constraint on the trajectories."""
        def __init__(self,
                     line: zgoubidoo.Input,
                     place: Union[str, Command],
                     variable: int,
                     value: float = 0.0,
                     weight: float = 1.0,
                     particle: int = 1
                     ):
            """

            Args:
                line:
                place:
                variable:
                value:
                weight:
            """
            self.IC: float = 3
            self.I: int = particle
            self.J: int = variable
            self.IR: int = line.zgoubi_index(place)
            self.V: float = value
            self.WV: float = weight
            self.NP: int = 0

    class DifferenceEqualityConstraint(EqualityConstraint):
        """Equality constraint on the difference between current and initial coordinates."""
        def __init__(self,
                     line: zgoubidoo.Input,
                     place: Union[str, Command],
                     variable: int,
                     value: float = 0.0,
                     weight: float = 1.0,
                     particle: int = 1
                     ):
            super().__init__(line, place, variable, value, weight, particle)
            self.IC = 3.1

    class SumEqualityConstraint(EqualityConstraint):
        """Equality constraint on the difference between current and initial coordinates."""
        def __init__(self,
                     line: zgoubidoo.Input,
                     place: Union[str, Command],
                     variable: int,
                     value: float = 0.0,
                     weight: float = 1.0,
                     particle: int = 1
                     ):
            super().__init__(line, place, variable, value, weight, particle)
            self.IC = 3.2

    class MaxEqualityConstraint(EqualityConstraint):
        """Equality constraint on the difference between current and initial coordinates."""
        def __init__(self,
                     line: zgoubidoo.Input,
                     place: Union[str, Command],
                     variable: int,
                     value: float = 0.0,
                     weight: float = 1.0,
                     particle: int = 1
                     ):
            super().__init__(line, place, variable, value, weight, particle)
            self.IC = 3.3
            self.NP = 2

    class MinEqualityConstraint(EqualityConstraint):
        """Equality constraint on the difference between current and initial coordinates."""
        def __init__(self,
                     line: zgoubidoo.Input,
                     place: Union[str, Command],
                     variable: int,
                     value: float = 0.0,
                     weight: float = 1.0,
                     particle: int = 1
                     ):
            super().__init__(line, place, variable, value, weight, particle)
            self.IC = 3.3
            self.NP = 1

    def __str__(self):
        command = list()
        command.append(super().__str__().rstrip())
        command.append(f"""
        {len(self.PARAMS) - list(self.PARAMS).count(None)}
        """)
        for p in self.PARAMS:
            if p is None:
                continue
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
        {len(self.CONSTRAINTS) - list(self.PARAMS).count(None)} {self.PENALTY:.12e} {self.ITERATIONS}
        """)
        for c in self.CONSTRAINTS:
            if c is None:
                continue
            command.append(f"""
        {c['IC']} {c['I']} {c['J']} {c['IR']} {c['V']} {c['WV']} {c['NP']}
        """)
        return ''.join(map(lambda x: x.rstrip(), command))

    def process_output(self,
                       output: List[str],
                       parameters: dict,
                       zgoubi_input: zgoubidoo.Input
                       ) -> bool:
        """

        Args:
            output: the output from a Zgoubi run to be processed by the command.
            parameters: TODO
            zgoubi_input: the Input sequence (required and some cases by the command output processor).

        Returns:
            a flag indicating if the processing is valid.
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
                        return _Q(v[0]).units
                except (TypeError, IndexError):
                    continue
            return None

        grab: bool = False
        status: list = []
        data: list = []
        for l in output:
            if l.strip().startswith('Lmnt'):
                status.append(l)
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
                        'min': fortran_float(values[3]),
                        'initial': fortran_float(values[4]),
                        'final': fortran_float(values[5]) * find_dimension_by_id(int(values[0]), int(values[2])),
                        'max': fortran_float(values[6]),
                        'stepsize': fortran_float(values[7]),
                }
                if len(values) >= 9:
                    d['name'] = values[8]
                    d['label1'] = values[9]
                    d['label2'] = values[10]
                data.append(d)
        success = False if len(data) == 0 or len(status) > 0 else True
        try:
            _ = _pd.DataFrame(data).set_index('variable_id')
        except KeyError:
            pass
        try:
            self._results.append(
                (
                    parameters,
                    Command.CommandResult(success=success, results=_)
                )
            )
        except UnboundLocalError:
            raise Exception(f"Parameters: {parameters}, output={output}")
        return success


class Fit2(Fit, metaclass=FitType):
    """Fitting procedure.

    Alternative fitting procedure implemented in Zgoubi, see manual.
    """
    KEYWORD = 'FIT2'
    """Keyword of the command used for the Zgoubi input data."""


class Focale(Command):
    """Particle coordinates and horizontal beam size at distance XL."""
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
    """Particle coordinates and vertical beam size at distance XL."""
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

    .. note:: Implementation is to be completed in Zgoubi.
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


class Marker(Command, _Patchable):
    """Marker."""
    KEYWORD = 'MARKER'
    """Keyword of the command used for the Zgoubi input data."""

    def __init__(self, label1='', label2='', *params, with_plt=True, **kwargs):
        super().__init__(label1, label2, self.PARAMETERS, *params, **kwargs)
        self.LABEL2 = '.plt' if with_plt else ''

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        """


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
        {super().__str__().rstrip()}
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

    PARAMETERS = {
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        1 1
        QUADRUPO
        -1
        1
        1
        """


class Separa(Command):
    """Wien Filter - analytical simulation."""
    KEYWORD = 'SEPARA'
    """Keyword of the command used for the Zgoubi input data."""


class Target(Command):
    """Generate a secondary beam following target interaction."""
    KEYWORD = 'TARGET'
    """Keyword of the command used for the Zgoubi input data."""


class TransferMatrix(Command):
    """Transfer matrix.

    .. rubric:: Zgoubi manual description

    TRANSMAT performs a second order transport of the particle coordinates using R and T. [Rij] ([Tijk]) is the first
    order (second order) transfer matrix as usually involved in second order beam optics [28]. Second order transfer
    is optional. The length of the element represented by the matrix may be introduced for the purpose of path length
    updating.

    .. Note:: MATRIX delivers [Rij] and [Tijk] matrices in a format suitable for straightforward use with TRANSMAT.
    """
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
    """Parameters of the command, with their default value, their description and optionally an index used by other 
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
