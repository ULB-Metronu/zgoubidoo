"""
Commands controlling Zgoubi's control flow, geometry, tracking options, etc.

TODO
"""
from __future__ import annotations
from typing import Any, Tuple, Dict, Mapping, List, Union
from abc import ABCMeta
import inspect
import uuid
import numpy as _np
import pandas as _pd
import parse as _parse
from pint import UndefinedUnitError as _UndefinedUnitError
from .patchable import Patchable as _Patchable
from .. import ureg as _ureg
from .. import Q_ as _Q
from georges_core.frame import Frame as _Frame
from ..units import _radian, _degree, _m, _cm
from ..constants import ZGOUBI_LABEL_LENGTH as _ZGOUBI_LABEL_LENGTH
import zgoubidoo


class ZgoubidooException(Exception):
    """Exception raised for errors in the Zgoubidoo commands module."""

    def __init__(self, m):
        self.message = m


class ZgoubidooAttributeException(ZgoubidooException):
    """Exception raised for errors in the Zgoubidoo commands module."""
    pass


class Comment:
    """Fake comment allowing to insert comments in the Zgoubi input.

    Examples:
        >>> c = Comment(COMMENT="A very long comment.")
    """
    def __init__(self, comment: str = ''):
        self.COMMENT = comment

    def __str__(self):
        return f"""
        ! {self.COMMENT}
    """
    
    def __repr__(self):
        return str(self)


class CommandType(ABCMeta):
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
                defaults = {}
                if 'post_init' in dct:
                    defaults = {
                        _: __.default
                        for _, __ in inspect.signature(dct['post_init']).parameters.items()
                        if __.default is not inspect.Parameter.empty
                    }
                bases[0].__init__(self, label1, label2, dct.get('PARAMETERS', {}), *params, **{**defaults, **kwargs})
                if 'post_init' in dct:
                    dct['post_init'](self, **kwargs)
            dct['__init__'] = default_init

        # Collect all post_init arguments
        if '_POST_INIT' not in dct:
            dct['_POST_INIT'] = {}
        if 'post_init' in dct and len(bases) > 0:
            dct['_POST_INIT'] = {*getattr(bases[0], '_POST_INIT', {}), *dct['post_init'].__code__.co_varnames}

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
    """Parameters of the command, with their default value, their description and optionally an index used by other 
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
            if len(label1) > _ZGOUBI_LABEL_LENGTH:
                raise ZgoubidooAttributeException(f"LABEL1 '{label1}' for element {self.KEYWORD} is too long.")
            self._attributes['LABEL1'] = label1
        if label2:
            if len(label2) > _ZGOUBI_LABEL_LENGTH:
                raise ZgoubidooAttributeException(f"LABEL2 '{label2}' for element {label1} ({self.KEYWORD}) is too long.")
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
        ]))[:_ZGOUBI_LABEL_LENGTH]
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
                raise ZgoubidooAttributeException(f"The parameter {k_} is not part of the {self.__class__.__name__} "
                                                  f"definition.")

            default = self._retrieve_default_parameter_value(k_)
            try:  # Avoid a bug in pint where a string starting with '#' cannot be parsed
                default = default.lstrip('#')
            except AttributeError:
                pass
            if isinstance(v, (int, float)) and k.endswith('_'):
                v = _ureg.Quantity(v, _ureg.Quantity(default).units)
            elif isinstance(v, str) and default is not None and not isinstance(default, str) and not v.startswith('#'):
                try:
                    v = _ureg.Quantity(v)
                except _UndefinedUnitError:
                    pass
            try:
                dimension = v.dimensionality
            except AttributeError:
                dimension = _ureg.Quantity(1).dimensionality  # No dimension
            try:
                if default is not None and dimension != _ureg.Quantity(default).dimensionality:
                    raise ZgoubidooAttributeException(f"Invalid dimension ({dimension} "
                                                      f"instead of {_ureg.Quantity(default).dimensionality}) "
                                                      f"for parameter {k_}={v} of {self.__class__.__name__}."
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
        return self.__class__(label2=self.LABEL2, **self.attributes).generate_label(prefix=self.LABEL1)

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

    def process_output(self,
                       output: List[str],
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

    This can also be used to implement new commands easily by using formatted INPUT together with OPTIONS.
    
    Examples:
        >>> c = Fake('FAKE1', INPUT="'COMMAND_NAME' {LABEL1} 1.0 2.0 3.0")
        >>> str(c)
    """
    PARAMETERS = {
        'INPUT': ('', 'Input string.'),
        'OPTIONS': {},
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return self.INPUT.format(**{**self.OPTIONS, **self.attributes})


class AutoRef(Command):
    """Automatic transformation to a new reference frame.

    .. rubric:: Zgoubi manual description

    ``AUTOREF`` positions the new reference frame following 3 options:

    - If I = 1, ``AUTOREF`` is equivalent to CHANGREF[XCE = 0, YCE = Y (1), ALE = T(1)] so that the new reference
      frame is at the exit of the last element, with particle 1 at the origin with its horizontal angle set to T = 0.
    - If I = 2, it is equivalent to CHANGREF[XW,Y W,T(1)] so that the new reference frame is at the position (X W, Y W )
      of the waist (calculated automatically in the same way as for IMAGE) of the three rays number 1, 4 and 5
      (compatible for instance with OBJET, KOBJ = 5, 6, together with the use of MATRIX) while T(1), the horizontal
      angle of particle number I1, is set to zero.
    - If I = 3, it is equivalent to CHANGREF[XW,Y W,T(I1)] so that the new reference frame is at the position (X W, Y W)
     of the waist (calculated automatically in the same way as for IMAGE) of the three rays number I1, I2 and I3
     specified as data, while T(I1) is set to zero.
    - If I = 4 : new horizontal beam centroid positionning XCE, YCE, ALE is provided. The beam is moved by XCE and then
      centered on YCE, ALE.
    - If I = 4.1 : new beam centroid positionning XCE, YCE, ALE, DCE, TIME is provided. The beam is moved by XCE and
      then centered on YCE, ALE. In addition, the beam is centered on a new relative momentum DCE and new timing value
      TIME.
    - If I = 4.2 : same as 4.1, except that particles all have their timing set to TIME.
    - If I = 5 : new vertical beam centroid positionning ZCE, PLE (position, angle) is provided. The beam is centered on
      vertical position and angle ZCE, PLE.

    """
    KEYWORD = 'AUTOREF'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'I': (1, 'Mode (1, 2 or 3).'),
        'I1': (1, 'Particle number (only used if I = 3)'),
        'I2': (1, 'Particle number (only used if I = 3)'),
        'I3': (1, 'Particle number (only used if I = 3)'),
        'XCE': (0.0 * _ureg.cm, ''),
        'YCE': (0.0 * _ureg.cm, 'Beam centroid new coordinates YCE'),
        'ALE': (0.0 * _ureg.mradian, 'Beam centroid new coordinates ALE'),
        'DCE': (0.0, 'New beam centroid positionning: new relative momentum DCE'),
        'TIME': (0.0 *_ureg.micros, 'New beam centroid positionning: new timing value'),
        'ZCE': (0.0 * _ureg.cm, 'New vertical beam centroid positionning: position ZCE'),
        'PLE': (0.0 * _ureg.mradian, 'New vertical beam centroid positionning: angle')
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
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
        elif self.I == 4:
            c += f"""
        {_cm(self.XCE):.12e} {_cm(self.YCE):.12e} {self.ALE.to('mradian').magnitude:.12e}
            """
        elif self.I == 4.1 or self.I == 4.2:
            c += f"""
        {_cm(self.XCE):.12e} {_cm(self.YCE):.12e} {self.ALE.to('mradian').magnitude:.12e} {self.DCE:.12e} {self.TIME.to('micros').magnitude:.12e}
            """
        elif self.I == 5:
            c += f"""
        {_cm(self.ZCE):.12e} {self.PLE.to('mradian').magnitude:.12e}
            """
        return c


class BeamBeam(Command):
    """Beam-beam lens.

    .. rubric:: Zgoubi manual description

    ``BEAMBEAM`` is a beam-beam lens simulation, a thin-lens transform [43], in the weak-strong approximation.
    Upon option using SPNTRK, ``BEAMBEAM`` will include spin kicks, after modelling as described in Ref. [44].

    *For software developers*
    rbb.f reads the data from zgoubi.dat; bb.f and programs therein do the beam (and spin when requested) dynamics.
    """
    KEYWORD = 'BEAMBEAM'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'SW': (0, '0/1 : off/on'),
        'I': (0.0 * _ureg.ampere, 'beam intensity'),
        'ALPHA_Y': (0.0, 'Horizontal beam parameters'),
        'BETA_Y': (0.0 *_ureg.m, 'Horizontal beam parameters'),
        'EPSILON_Y': (0.0 *_ureg.m*_ureg.radian, 'Horizontal beam parameters : (EPSILON_Y,norm)/pi'),
        'ALPHA_Z': (0.0, 'Vertical beam parameters'),
        'BETA_Z': (0.0 *_ureg.m, 'Vertical beam parameters'),
        'EPSILON_Z': (0.0 *_ureg.m*_ureg.radian, 'Vertical beam parameters (EPSILON_Z,norm)/pi'),
        'SIGMA_X': (0.0 *_ureg.m, 'rms bunch length'),
        'SIGMA_DP': (0.0 , 'rms momentum spread'),
        'C': (0.0 * _ureg.m, 'Ring circumference'),
        'ALPHA': (0.0, 'momentum compaction'),
        'QY': (0.0, 'Horizontal tune'),
        'QZ': (0.0, 'Vertical tune'),
        'QS': (0.0, 'Synchrotron tune'),
        'AY': (0.0, 'Horizontal amplitude'),
        'AZ': (0.0, 'Vertical amplitude'),
        'AX': (0.0, 'Longitudinal amplitude'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.SW} {self.I.m_as('ampere'):.12e}
        {self.ALPHA_Y:.12e} {self.BETA_Y.m_as('m'):.12e} {self.EPSILON_Y.m_as('m*rad'):.12e}
        {self.ALPHA_Z:.12e} {self.BETA_Z.m_as('m'):.12e} {self.EPSILON_Z.m_as('m*rad'):.12e}
        {self.SIGMA_X.m_as('m'):.12e} {self.SIGMA_DP:.12e}
        {self.C.m_as('m'):.12e} {self.ALPHA:.12e}
        {self.QY:.12e} {self.QZ:.12e} {self.QS:.12e} 
        {self.AY:.12e} {self.AZ:.12e} {self.AS:.12e} 
        """

class Binary(Command):
    """BINARY/FORMATTED data converter.

    TODO
    """
    KEYWORD = 'BINARY'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'FILES': ([], 'List of files to convert'),
        'NCOL': (6, 'Number of columns in each files'),
        'NHDR': (8, 'Number of header lines in each files'),
        'FORMAT': (None, 'READ format')
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        newline = '\n        '
        return f"""
        {super().__str__().rstrip()}
        {len(self.FILES)}.{self.FORMAT or ''} {self.NCOL} {self.NHDR}
        {newline.join(self.FILES)}
        """


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
    """Parameters of the command, with their default value, their description and optionally an index used by other 
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
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        c = f"""
        {super().__str__().rstrip()}
        """
        cc = ""
        for t in self.TRANSFORMATIONS:
            if t[0] is None or t[1] is None or _np.isclose(t[1].magnitude, 0.0):
                continue
            if t[1].dimensionality == _ureg.cm.dimensionality:
                cc += f"{t[0]} {_cm(t[1])} "
            elif t[1].dimensionality == _ureg.radian.dimensionality:
                cc += f"{t[0]} {_degree(t[1])} "
            else:
                raise ZgoubidooException(f"Incorrect dimensionality in {self.__class__.__name__}.")
        if cc != '':
            return c + cc
        else:
            return ''

    @property
    def length(self) -> _Q:
        """

        Returns:

        """
        return 0.0 * _ureg.cm

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
    r"""Collimator.

    .. rubric:: Zgoubi manual description

    ``COLLIMA`` acts as a mathematical aperture of zero length. It causes the identification, counting and stop- ping of
    particles that reach the aperture limits.

    *Physical Aperture*

    A physical aperture can be either rectangular (IFORM = 1) or elliptic (IFORM = 2). The collimator is centered at
    YC, ZC and has transverse dimensions ±Y L and ±ZL such that any particle will be stopped if its coordinates Y , Z
    satisfy

    $$(Y − YC)^2 ≥ YL^2 \quad or \quad (Z−ZC)^2 ≥ ZL^2 \quad if \quad IFORM = 1 $$
    $$\frac{(Y − YC)^2}{YL^2} + \frac{(Z − ZC)^2}{ZL^2} ≥ 1 \quad if \quad IFORM = 2 $$

    *Longitudinal Collimation*

    ``COLLIMA`` can act as a longitudinal phase-space aperture, coordinates acted on are selected with IFORM.J.
    Any particle will be stopped if its horizontal (h) and vertical (v) coordinates satisfy

`    .. math::
`
    (h ≤ h_{min} or h ≥ h_{max}) or (v ≤ v_{min} or v ≥ v_{max})

    wherein, h is either path length S if IFORM=6 or time if IFORM=7, and v is either 1+DP/P if J=1 or kinetic energy
    if J=2 (provided mass and charge have been defined using the keyword ``PARTICUL``).

    *Phase-Space Elliptical Collimation*
    ``COLLIMA` can act as a phase-space elliptical aperture. Any particle will be stopped if its coordinates satisfy

    .. math::

        \begin{align}
            γ_Y Y^2 + 2α_Y YT + β_Y T^2 &≥ ε_Y/π if IFORM = 11 or 14 \\
            γ_Z Z^2 + 2α_Z ZP + β_Z P^2 &≥ ε_Z/π if IFORM = 12 or 15 \\
            γ_S S^2 + 2α_S SD + β_S D^2 ≥ ε_S/π if IFORM = 13 or 16 (under development)
        \end{align}


    If IFORM=11 (respectively 12, 13) then :math:`ε_Y /π` (respectively :math:`ε_Z/π`, :math:`ε_S/π`) is to be
    specified by the user as well as :math:`α_{Y,Z,S}`, :math:`β_{Y,Z,S}`. If IFORM =14 (respectively 15, 16) then
    :math:`α_Y` and :math:`β_Y` (respectively :math:`α_{Z,S}, β_{Z,S}`) are determined by zgoubi by prior computation
    of the matched ellipse to the particle population, so only :math:`ε_{Y,Z,S}/π` need be specified by the user.

    When a particle is stopped, its index IEX (see ``OBJET`` and section 7.12) is set to the value -4, and its actual
    path length is stored in the array SORT for possible further use (e.g., by ``HISTO``, or for loss studies, etc.).
    """
    KEYWORD = 'COLLIMA'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IA': (2, 'Element active or not (0 - inactive, 1 - active, 2 - active and prints information.'),
        'IFORM': (
            1,
            'Aperture shape (1 - rectangular, 2 - elliptic (other options, see documentation). '
            'IFORM = 6 or 7 for longitudinal collimation, '
            '11 ≤ IFORM ≤ 16 for phase-space elliptical collimation'
        ),
        'J': (0, 'Description of the aperture coordinates system.'),
        'C1': (0.0 * _ureg.cm, 'Half opening (Y).'),
        'C2': (0.0 * _ureg.cm, 'Half opening (Z).'),
        'C3': (0.0 * _ureg.cm, 'Center of the aperture (Y).'),
        'C4': (0.0 * _ureg.cm, 'Center of the aperture (Z).'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
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


class FaiStore(Command):
    """Store coordinates at labeled elements.

    .. rubric:: Zgoubi manual description

    Store coordinates every IP other pass at labeled elements.

    If either FNAME or first LABEL is ’none’ then no storage occurs. Store occurs at all elements if first LABEL is
    ’all’ or ’ALL’.

    ``FAISTORE`` has an effect similar to ``FAISCNL``, with more features.

        - On the first data line, FNAME may be followed by a series of up to 10 LABELs. If there is no label, the print
          occurs by default at the location of ``FAISTORE`` ; if there are labels the print occurs right downstream of
          all optical elements wearing those labels (and no longer at the FAISTORE location).

        - The next data line gives a parameter, IP : printing will occur at pass 1 and then at every IP other pass,
          if using REBELOTE with NPASS ≥ IP − 1.

    *Case of Binary storage:* it can be obtained from ``FAISCNL`` and ``FAISTORE``. This is for the sake of compactness
    and access speed, for instance in case voluminous amounts of data would have to be manipulated using zpop.
    This is achieved by giving the storage file a name of the form b FNAME or B FNAME (e.g., ‘b zgoubi.fai’).
    The FORTRAN WRITE list is the same as in the FORMATTED case above.
    This is compatible with the READ statements in zpop that will recognize binary storage from that very radical ’b ’
    or ’B ’.

    *Case of FIT[2] procedure :* it may not be desired to store during the FITting process, but instead only when the
    FITtinig is completed. It is sufficient for that to (i) put ’AtFITfinal’ as the first label following FAISTORE
    keyword, this will inhibit all storage until the final run following a FIT procedure, and (ii) avoid using the
    ’nofinal’ instruction in FIT[2] (see p. 156)).
    """
    KEYWORD = 'FAISTORE'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'FNAME': ('zgoubi.fai', 'Storage file name.'),
        'LABELS': ('ALL', 'Label(s) of the element(s) at the exit of which the storage occurs (10 labels maximum).'),
        'IP': (1, 'Store every IP other pass (when using REBELOTE with NPASS ≥ IP − 1).'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.FNAME}
        {self.IP}
        """


class Focale(Command):
    r"""Particle coordinates and horizontal beam size at distance XL.

    .. rubric:: Zgoubi manual description

    ``FOCALE` calculates the dimensions of the beam and its mean transverse position, at a longitudinal distance XL `
    from the position corresponding to the keyword ``FOCALE`.

    ``IMAGE`` computes the location and size of the closest horizontal waist.

    ``IMAGES`` has th same effect as ``IMAGE``, but, in addition, for a non-monochromatic beam it calculates as many
    waists as there are distinct momenta in the beam, provided that the object has been defined with a classification
    of momenta (see OBJET, KOBJ= 1, 2 for instance).

    Optionally, for each of these three procedures, zgoubi can list a trace of the coordinates in the X, Y and in the
    Y , Z planes. The following quantities are calculated for the N particles of the beam (``IMAGE``, ``FOCALE``) or of
    each group of momenta (``IMAGES``)

    • Longitudinal position :

        FOCALE : X = XL

        .. math::

        IMAGE[S] : X = - \frac{\sum_{i=1}^N Y_i * tgT_i -(\sum_{i=1}^N Y_i * \sum_{i=1}^N tgT_i)/N}{\sum_{i=1}^N tg^2 T_i -(\sum_{i=1}^N tg T_i)^2/N}

        .. math::

        Y = Y_1 + X * tgT_1

    where :math:`Y1` and :math:`T_1` are the coordinates of the first particle of the beam (``IMAGE``, ``FOCALE``) or
    the first particle of each group of momenta (``IMAGES``).

    • Transverse position of the center of mass of the waist (``IMAGE``[S]) or of the beam (``FOCALE``), with respect
    to the reference trajectory

    .. math::

    YM = \frac{1}{N} \sum_{i=1}^N (Y_i + X tg T_i) - Y = \frac{1}{N} \sum_{i=1}^N Y M_i


    • FWHM of the image (``IMAGE``[S])  or of the beam (``FOCALE``), and total width, respectively, W and :math:`W_T`

    $$W = 2.35(\frac{1}{N} \sum_{i=1}^N Y M_i^2 - Y M^2)^{1/2}$$
    $$WT = max(YM_i) - min(YM_i)$$
    """
    KEYWORD = 'FOCALE'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'XL': (0.0 * _ureg.centimeter, 'Distance from the location of the keyword.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {_cm(self.XL)}
        """


class FocaleZ(Command):
    r"""Particle coordinates and vertical beam size at distance XL.

    .. rubric:: Zgoubi manual description

    Similar to ``FOCALE``, but the calculations are performed with respect to the vertical coordinates
    :math:`Z_i` and :math:`P_i`, in place of :math:`Y_i` and :math:`T_i`.
    """
    KEYWORD = 'FOCALEZ'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'XL': (0.0 * _ureg.centimeter, 'Distance from the location of the keyword.'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
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
        'KGA': (0, 'Off/On switch'),
        'AI': (0.0, 'Atomic number'),
        'DEN': (0.0, 'density'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
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
    """Parameters of the command, with their default value, their description and optionally an index used by other 
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
    r"""Localization and size of horizontal waist.

    .. rubric:: Zgoubi manual description

    ``FOCALE` calculates the dimensions of the beam and its mean transverse position, at a longitudinal distance XL `
    from the position corresponding to the keyword ``FOCALE`.

    ``IMAGE`` computes the location and size of the closest horizontal waist.

    ``IMAGES`` has th same effect as ``IMAGE``, but, in addition, for a non-monochromatic beam it calculates as many
    waists as there are distinct momenta in the beam, provided that the object has been defined with a classification
    of momenta (see OBJET, KOBJ= 1, 2 for instance).

    Optionally, for each of these three procedures, zgoubi can list a trace of the coordinates in the X, Y and in the
    Y , Z planes. The following quantities are calculated for the N particles of the beam (``IMAGE``, ``FOCALE``) or of
    each group of momenta (``IMAGES``)

    • Longitudinal position :

        FOCALE : X = XL

        .. math::

        IMAGE[S] : X = - \frac{\sum_{i=1}^N Y_i * tgT_i -(\sum_{i=1}^N Y_i * \sum_{i=1}^N tgT_i)/N}{\sum_{i=1}^N tg^2 T_i -(\sum_{i=1}^N tg T_i)^2/N}

        .. math::

        Y = Y_1 + X * tgT_1

    where :math:`Y1` and :math:`T_1` are the coordinates of the first particle of the beam (``IMAGE``, ``FOCALE``) or
    the first particle of each group of momenta (``IMAGES``).

    • Transverse position of the center of mass of the waist (``IMAGE``[S]) or of the beam (``FOCALE``), with respect
    to the reference trajectory

    .. math::

    YM = \frac{1}{N} \sum_{i=1}^N (Y_i + X tg T_i) - Y = \frac{1}{N} \sum_{i=1}^N Y M_i


    • FWHM of the image (``IMAGE``[S])  or of the beam (``FOCALE``), and total width, respectively, W and :math:`W_T`

    $$W = 2.35(\frac{1}{N} \sum_{i=1}^N Y M_i^2 - Y M^2)^{1/2}$$
    $$WT = max(YM_i) - min(YM_i)$$
    """
    KEYWORD = 'IMAGE'
    """Keyword of the command used for the Zgoubi input data."""


class Images(Command):
    r"""Localization and size of horizontal waists.

    .. rubric:: Zgoubi manual description

    ``FOCALE` calculates the dimensions of the beam and its mean transverse position, at a longitudinal distance XL `
    from the position corresponding to the keyword ``FOCALE`.

    ``IMAGE`` computes the location and size of the closest horizontal waist.

    ``IMAGES`` has th same effect as ``IMAGE``, but, in addition, for a non-monochromatic beam it calculates as many
    waists as there are distinct momenta in the beam, provided that the object has been defined with a classification
    of momenta (see OBJET, KOBJ= 1, 2 for instance).

    Optionally, for each of these three procedures, zgoubi can list a trace of the coordinates in the X, Y and in the
    Y , Z planes. The following quantities are calculated for the N particles of the beam (``IMAGE``, ``FOCALE``) or of
    each group of momenta (``IMAGES``)

    • Longitudinal position :

        FOCALE : X = XL

        .. math::

        IMAGE[S] : X = - \frac{\sum_{i=1}^N Y_i * tgT_i -(\sum_{i=1}^N Y_i * \sum_{i=1}^N tgT_i)/N}{\sum_{i=1}^N tg^2 T_i -(\sum_{i=1}^N tg T_i)^2/N}

        .. math::

        Y = Y_1 + X * tgT_1

    where :math:`Y1` and :math:`T_1` are the coordinates of the first particle of the beam (``IMAGE``, ``FOCALE``) or
    the first particle of each group of momenta (``IMAGES``).

    • Transverse position of the center of mass of the waist (``IMAGE``[S]) or of the beam (``FOCALE``), with respect
    to the reference trajectory

    .. math::

    YM = \frac{1}{N} \sum_{i=1}^N (Y_i + X tg T_i) - Y = \frac{1}{N} \sum_{i=1}^N Y M_i


    • FWHM of the image (``IMAGE``[S])  or of the beam (``FOCALE``), and total width, respectively, W and :math:`W_T`

    $$W = 2.35(\frac{1}{N} \sum_{i=1}^N Y M_i^2 - Y M^2)^{1/2}$$
    $$WT = max(YM_i) - min(YM_i)$$
    """
    KEYWORD = 'IMAGES'
    """Keyword of the command used for the Zgoubi input data."""


class ImageZ(Command):
    r"""Localization and size of vertical waist.

    .. rubric:: Zgoubi manual description

    Similar to IMAGE, but the calculations are performed with respect to the vertical coordinates
    :math:`Z_i` and :math:`P_i`, in place of :math:`Y_i` and :math:`T_i`.
    """
    KEYWORD = 'IMAGEZ'
    """Keyword of the command used for the Zgoubi input data."""


class ImagesZ(Command):
    r"""Localization and size of vertical waists.

    .. rubric:: Zgoubi manual description

    Similar to IMAGES, but the calculations are performed with respect to the vertical coordinates
    :math:`Z_i` and :math:`P_i`, in place of :math:`Y_i` and :math:`T_i`.
    """
    KEYWORD = 'IMAGESZ'
    """Keyword of the command used for the Zgoubi input data."""


class Marker(Command, _Patchable):
    """Marker."""
    KEYWORD = 'MARKER'
    """Keyword of the command used for the Zgoubi input data."""

    def __init__(self, label1='', label2='', *params, with_plt=True, **kwargs):
        super().__init__(label1, label2, self.PARAMETERS, *params, **kwargs)
        if self.LABEL2 == '':
            self.LABEL2 = '.plt' if with_plt else ''

    def __str__(self):
        return f"""
        {super().__str__().strip()}
        """


class Matrix(Command):
    """Calculation of transfer coefficients, periodic parameters."""
    KEYWORD = 'MATRIX'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IORD': 1,
        'IFOC': (11, 'If IFOC=11, periodic parameters (single pass)'),
        'COUPLED': (False, 'If COUPLED = True : use of coupled formalism'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.IORD} {self.IFOC} PRINT {'coupled' if self.COUPLED else ''}
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

    PARAMETERS = {
        'IOPT': 1,
        'LABEL': ('all', 'If IFOC=11, periodic parameters (single pass)'),
        'IMP': 1,
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().strip()}
        {self.IOPT} {self.LABEL} {self.IMP}
        """


class Ordre(Command):
    """Taylor expansions order."""
    KEYWORD = 'ORDRE'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'IO': (4, 'Taylor expansion of R and u up to IO (default is IO = 4, IO = 2..5).'),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().strip()}
        {self.IO}
        """


class Pickups(Command):
    """Beam centroid path; closed orbit."""
    KEYWORD = 'PICKUPS'
    """Keyword of the command used for the Zgoubi input data."""


class PlotData(Command):
    """Intermediate output for the PLOTDATA graphic software."""
    KEYWORD = 'PLOTDATA'
    """Keyword of the command used for the Zgoubi input data."""


class Rebelote(Command):
    r"""
    Do it again
    .. rubric:: Zgoubi manual description

    When ``REBELOTE`` is encountered in the input data file, the code execution jumps,

    - either back to the beginning of the data file - the default behavior,
    - or, if option K=99.1 or K=99.2, back to a particular ``LABEL``.

    Then ``NPASS-1`` passes (from ``LABEL`` to ``REBELOTE``) follow. As to the last pass, number ``NPASS+1``,
    there are two possibilities :

    - either it also encompasses the whole ``LABEL`` to ``REBELOTE`` range,

    - or, upon request (option K=99.2 ), execution may exit that final pass upstream of ``REBELOTE``, at a location
      defined by a second dedicated LABEL placed between the first above mentioned ``LABEL``, and ``REBELOTE``.
      In both cases, following the end of this “multiple-pass” procedure, the execution continues from the keyword which
      follows ``REBELOTE``, until ``END`` is encountered. The two functionalities of ``REBELOTE`` are the following :

      - ``REBELOTE`` can be used for Monte Carlo simulations when more than Max(IMAX) particles are to be tracked.
        Thus, when the following random procedures are used : ``MCOBJET``, ``OBJETA``, ``MCDESINT``, ``SPNTRK`` (KSO = 5),
        their random seeds are not reset and independent statistics will add up.

    This includes Monte Carlo simulations, in beam lines : normally K = 0. ``NPASS`` runs through the same structure,
    from ``MCOBJET`` to ``REBELOTE`` will follow, resulting in the calculation of (1+``NPASS`` )*``IMAX`` trajectories,
    with as many random initial coordinates.

     - ``REBELOTE`` can be used for multi-turn ray-tracing in circular machines : normally K = 99 in that case
        (or K = 99, see below). ``NPASS`` turns in the same structure will follow, resulting in the tracking of ``IMAX``
        particles over 1+NPASS turns. For the simulation of pulsed power supplies, synchrotron motion, and other Q-jump manipulation,
        see ``SCALING``.

    For instance, using option described K=99.2 above, a full “injection line + ring + extraction line” installation
    can be simulated - kicker firing and other magnet ramping can be simulated using ``SCALING``. Using the double-LABEL
    method discussed above with option K=99.2, it is possible to encompass the ring between an injection line section
    (namely, with the element sequence of the latter extending from OBJET to the first ``LABEL``),
    and an extraction line (its description will then follow ``REBELOTE``), whereas the ring description extends from
    to the first LABEL to ``REBELOTE``, with possible extraction, at the last pass, at the location of the second LABEL,
    located between the first one and ``REBELOTE``,

    Note : Some ``CAVITE`` options cause a reset-to-zero of individual particle path length 11. This is for reasons of
    cumulated path length accuracy (a delta-path below computer accuracy compared to total path length would not be
    resolved - it can be for instance bunch length as compared to cumulated multi-turn distance around a large ring).
    This reset may not be desirable, it depends on the multi-turn problem dealt with using ``REBELOTE``,
    it may be necessary for instance in long-term tracking in large rings, it is not in recirculating linacs.
    Option K=99 in ``REBELOTE`` will cause this reset, whereas option K=98 (UNDER DEVELOPMENT, In cavite.f,
    IN THIS VERSION OF THE CODE) will avoid it everything else left unchanged.

    - Case IOPT=1 : In addition to what precedes, ``REBELOTE`` can change the value of arbitrary parameters in zgoubi.dat
      data list, using the forth argument ``IOPT=1`` (see page 299). ``NPRM`` tells the number of parameters to be changed.
      A series of ``NPRM`` lists of values, one list per parameter to be changed and each list with ``NRBLT`` data,
      tells the values to be taken by each one of these parameters, over the ``NRBLT`` passes of the ``REBELOTE`` process.

    ``IOPT=1`` is under development. TO BE DOCUMENT FURTHER.

    - Printouts over ``NPASS+1`` passes might result in a prohibitively big zgoubi.res file. They may be switched on/off by
      means of the option ``KWRIT``= i.j, with i = 1/0 respectively. The j flag allows a printout of the pass number and of some
      additional information to the video output, every 10j−1 turns if j > 0 ; video output is essentially switched off
      during ``REBELOTE`` execution if j = 0.

    ``REBELOTE`` also provides information : statistical calculations and related data regarding particle decay (``MCDESINT``),
    spin tracking (``SPNTRK``), stopped particles (``CHAMBR``, ``COLLIMA``), etc.

    """

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
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.NPASS} {self.KWRIT} {self.K}{'.' if self.N else ''}{self.N or ''} {self.LABL1 or ''} {self.LABL2 or ''}
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
    """Parameters of the command, with their default value, their description and optionally an index used by other 
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
    """Parameters of the command, with their default value, their description and optionally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        s = self
        return f"""
        {super().__str__().rstrip()}
        {_m(s.TX):.12e} {_m(s.TY):.12e} {_m(s.TZ):.12e} {_radian(s.RX):.12e} {_radian(s.RY):.12e} {_radian(s.RZ):.12e}
        """


TraRot = TranslationRotation


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


class Ymy(Command, _Patchable):
    """Reverse signs of Y and Z reference axes, equivalent to a 180 degree rotation around the X axis.
    
    This is particularly useful for example in combination with a `Dipole` that needs to be flipped so that the 
    geometry matches the negative field value.

    ..note: YMY reverses the signs of all transverse variables (Y, T, Z, P); despite its name.

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
            self._entry_patched = self.entry.__class__(self.entry)
            self._entry_patched.rotate_x(180 * _ureg.degree)
        return self._entry_patched
