"""Zgoubidoo's input module: interface for Zgoubi input file.

This module interfaces Zgoubi input files to the other components of Zgoubidoo. Its main feature is the `Input` class,
which allows to represent a set of Zgoubi input commands and serialize it into a valid input file. The input can also
be validated using a set of validators, following the Zgoubi input constraints.

The inputs are serialized and saved as `zgoubi.dat` in temporary directories. When serializing an input it is possible
to provide a parametric mapping (combinations of the variations of one or more parameters) to generate multiple Zgoubi
input files.
"""
from __future__ import annotations
from typing import Callable, Sequence, Mapping, Union, List, Tuple
from dataclasses import dataclass, field
import itertools
from functools import partial, reduce
import tempfile
import logging
import os
import pandas as _pd
import parse as _parse
from . import ureg as _ureg
from . import _Q
from .commands import *
from .frame import Frame as _Frame
import zgoubidoo.commands
import zgoubidoo.commands.madx

_logger = logging.getLogger(__name__)
ParametersMappingType = Mapping[str, Sequence[Union[_Q, float]]]
"""Type alias for a parametric mapping of string keys and values."""

ParametersMappingListType = List[ParametersMappingType]
"""Type alias for a list of parametric mappings."""

MappedParametersType = Mapping[str, Union[_Q, float]]
"""Type alias for a dictionnary of parametric keys and values."""

MappedParametersListType = List[MappedParametersType]
"""Type alias for a list of mapped parameters."""

PathsListType = List[Tuple[MappedParametersType, Union[str, tempfile.TemporaryDirectory]]]
"""Type alias for a list of parametric keys and paths values."""

ZGOUBI_INPUT_FILENAME: str = 'zgoubi.dat'
"""File name for Zgoubi input data."""

MAD_INPUT_FILENAME: str = 'input.mad'
"""File name for MAD-X input data."""

ZGOUBI_IMAX: int = 10000
"""Maximum number of particles that a Zgoubi objet can contain."""

flatten = itertools.chain.from_iterable
"""Helper function to flatten an iterable."""


class ZgoubiInputException(Exception):
    """Exception raised for errors within Zgoubi Input."""

    def __init__(self, m):
        self.message = m


@dataclass
class ParametricMapping:
    """Abstraction for multi-dimensional parametric mappings.

    Main feature is to compute the complete "cross product" of the different parameters to support multi-dimensional
    mapping. It also accounts for "coupled" variables.

    Note:
        TODO FIX Using the special value "LABEL" for the first element of the mapping's label deactivate the sequence adjustment
        mechanism.

    See also:
        for implementation details, see also https://codereview.stackexchange.com/q/211121/52027 .

    Examples:
        >>> pm = ParametricMapping([{('B3G', 'B1'): [1.0, 2.0], ('B1G', 'B1'): [11.0, 12.0]}, {('B2G', 'B1'): [1.5, 2.5, 3.5]}])
        >>> pm.combinations
        [{('B3G', 'B1'): 1.0, ('B1G', 'B1'): 11.0, ('B2G', 'B1'): 1.5},
         {('B3G', 'B1'): 1.0, ('B1G', 'B1'): 11.0, ('B2G', 'B1'): 2.5},
         {('B3G', 'B1'): 1.0, ('B1G', 'B1'): 11.0, ('B2G', 'B1'): 3.5},
         {('B3G', 'B1'): 2.0, ('B1G', 'B1'): 12.0, ('B2G', 'B1'): 1.5},
         {('B3G', 'B1'): 2.0, ('B1G', 'B1'): 12.0, ('B2G', 'B1'): 2.5},
         {('B3G', 'B1'): 2.0, ('B1G', 'B1'): 12.0, ('B2G', 'B1'): 3.5}]
    """
    mappings: ParametersMappingListType = field(default_factory=lambda: [{}])

    @property
    def labels(self) -> Tuple[str]:
        """List of labels of the parametric mapping."""
        return tuple(flatten(self.mappings))

    @property
    def pools(self) -> List[List[Sequence[Union[_Q, float]]]]:
        """All combinations of values for the parametric mapping."""
        return [list(map(tuple, zip(*arg.values()))) for arg in self.mappings]

    @property
    def combinations(self) -> MappedParametersListType:
        """Cartesian product adapted to work with dictionaries, roughly similar to `itertools.product`.

        Returns:
            a list of the cartesian product of the mappings.

        See also:

            - https://docs.python.org/3/library/itertools.html#itertools.product
            - https://codereview.stackexchange.com/q/211121/52027
        """
        pool_values = [flatten(term) for term in itertools.product(*self.pools)]
        return [dict(zip(self.labels, v)) for v in pool_values] or [{}]

    def __add__(self, other):
        """TODO might need to be adapted or with iadd also ?"""
        if len(self.labels) == 0:
            self.mappings = other.mappings
        elif len(other.labels) == 0:
            return self
        else:
            self.mappings += other.mappings
        return self


class Input:
    """Main class interfacing Zgoubi input files data structure.

    A Zgoubidoo `Input` object represents the Zgoubi input file data structure. It is thus essentially a list of
    Zgoubidoo objects representing commands and elements for the generation of Zgoubi input files.

    The `Input` supports a `str` representation allowing to generate the Zgoubi input. Additionnally, calling the object
    will write the string representation to a Zgoubi input file.

    Args:
        name: name of the input to be created.
        line: if not `None` the new input will contain that `Command` sequence.

    Examples:
        >>> zi = Input(name='test_beamline')
        >>> len(zi) == 0
        True
        >>> zi.name
        'test_beamline'
        >>> zi()
    """
    def __init__(self,
                 name: str = 'beamline',
                 line: Optional[Sequence[commands.Command]] = None,
                 with_survey: bool = True):
        self._name: str = name
        if line is None:
            line = []
        self._line: List[commands.Command] = line
        self._paths: PathsListType = list()
        self._optical_length: _Q = 0 * _ureg.m
        if with_survey:
            zgoubidoo.survey(beamline=self)

    def __del__(self):
        _logger.info(f"Input object for paths {self.paths} is being destroyed.")

    def __str__(self) -> str:
        """Provides the string representation, a valid Zgoubi input stream.

        Constructs the Zgoubi input sequence with the serialization of each command. An implicit `End` command is added
        in case it is not present. The `Input` name is used as a header.

        Returns:
            a valid Zgoubi input stream as a string.
        """
        return self.build(self._name, self._line)

    def __repr__(self) -> str:
        return str(self)

    def __call__(self,
                 mappings: Optional[MappedParametersListType] = None,
                 filename: str = ZGOUBI_INPUT_FILENAME,
                 path: Optional[str] = None) -> Input:
        """
        TODO
        Args:
            mappings:
            filename:
            path:

        Returns:

        """
        self._paths = [*self.paths, *self._generate(mappings=mappings, filename=filename, path=path)]
        return self

    def _generate(self,
                  mappings: Optional[MappedParametersListType] = None,
                  filename: str = ZGOUBI_INPUT_FILENAME,
                  path: Optional[str] = None,
                  ) -> PathsListType:
        """Writes the string representation of the object onto a file (Zgoubi input file).

        Args:
            mappings: TODO
            filename: the Zgoubi input file name (default: zgoubi.dat)
            path: an optional path for the temporary directories that will be created for the input files

        Raises:

        """
        paths: PathsListType = list()
        mappings = mappings or []
        if len(self.beam_mappings) > 0:
            mappings = list(map(lambda _: {**_[0], **_[1]}, itertools.product(mappings, self.beam_mappings)))
        initial_state: MappedParametersType = {}
        existing_mappings = [p[0] for p in self._paths]
        for mapping in mappings:
            if mapping in existing_mappings:
                continue
            previous_state = self.adjust(mapping)
            if initial_state is None:
                initial_state = previous_state
            target_dir = tempfile.TemporaryDirectory(prefix=path)
            paths.append((mapping, target_dir))
            Input.write(self, filename, path=target_dir.name)
        self.adjust(initial_state)
        return paths

    def __len__(self) -> int:
        """Length of the input sequence.

        Returns:
            the number of elements in the sequence.

        """
        return len(self._line)

    def __iadd__(self, command: commands.Command) -> Input:
        """Append a command at the end of the input sequence.

        Args:
            command: the command to be appended.

        Returns:
            the input sequence (in-place operation).

        """
        self._line.append(command)
        return self

    def __isub__(self, other: Union[str, commands.Command]) -> Input:
        """Remove a command from the input sequence.

        Args:
            other: the `Command` to be removed or the LABEL1 of the command to be removed as a string.

        Returns:
            the `Input` itself (in-place operation).
        """
        if isinstance(other, str):
            self._line = [c for c in self._line if c.LABEL1 != other]
        else:
            self._line = [c for c in self._line if c != other]
        return self

    def __getitem__(self,
                    items: Union[slice,
                                 int,
                                 float,
                                 str,
                                 CommandType,
                                 type,
                                 Iterable[Union[CommandType, type, str]]]
                    ) -> Union[zgoubidoo.commands.Command, Input]:
        """Multi-purpose dictionnary-like elements access and filtering.

        A triple interafce is provided:

            - **numerical index**: provides the element from its numeric index (starting at 0, looked-up in the `line`
              property of the input (the returned object is a `Command`);

            - **slicing**: provides a powerful slicing feature, using either object slice or string slice (or a mix of
              both); see example below (the returned object is a copy of the sliced input);

            - **element access**: returns a filtered input containing only the given elements. The elements are given
              either in the form of a list of strings (or a single string), representing the class name of the element or
              in the form of a list of classes (or a single class).

        Args:
            items: index based accessor, slice or elements types for filtering access (see above).

        Returns:

                - with numerical index returns the object located at that position (an instance of a `Command`);
                - with slicing returns a copy of the input, with the slicing applied (an instance of a `Input`);
                - with element access returns a filtering copy of the input (an instance of a `Input`).

        """
        # Behave like element access
        if isinstance(items, (int, float)):
            return self._line[int(items)]

        # Behave like slicing
        if isinstance(items, slice):
            start = items.start
            end = items.stop
            if isinstance(items.start, (zgoubidoo.commands.Command, str)):
                start = self.index(items.start) - 1
            if isinstance(items.stop, (zgoubidoo.commands.Command, str)):
                end = self.index(items.stop)
            slicing = slice(start, end, items.step)
            return Input(name=f"{self._name}_sliced_from_{getattr(items.start, 'LABEL1', items.start)}"
                              f"_to_{getattr(items.stop, 'LABEL1', items.stop)}",
                         line=self._line[slicing],
                         with_survey=False,
                         )

        else:
            # Behave like a filtering
            if not isinstance(items, (tuple, list)):
                items = (items,)
            l, i = self._filter(items)
            items = tuple(map(lambda x: x.__name__ if isinstance(x, type) else x, items))
            return Input(name=f"{self._name}_filtered_by_{items}"
                         .replace(',', '_')
                         .replace(' ', '')
                         .replace("'", '')
                         .replace("(", '')
                         .replace(")", '')
                         .rstrip('_'),
                         line=l,
                         with_survey=False,
                         )

    def __getattr__(self, item: str) -> commands.Command:
        """

        Args:
            item:

        Returns:

        """
        for e in self._line:
            if e.LABEL1 == item:
                return e
        raise AttributeError(f"Command with LABEL1 = {item} not found in the input sequence.")

    def __setattr__(self, key: str, value: Any):  # -> NoReturn
        """

        Args:
            key:
            value:

        Returns:

        """
        if key.startswith('_'):
            self.__dict__[key] = value
        else:
            for e in self._line:
                if getattr(e, key, None) is not None:
                    setattr(e, key, value)

    def __contains__(self, items: Union[str, CommandType, Tuple[Union[str, CommandType]]]) -> int:
        """

        Args:
            items:

        Returns:

        """
        if not isinstance(items, tuple):
            items = (items,)
        l, i = self._filter(items)
        return len(l)

    def _filter(self, items: Union[str, CommandType, Tuple[Union[str, CommandType]]]) -> tuple:
        """

        Args:
            items:

        Returns:

        """
        try:
            items = tuple(map(lambda x: getattr(zgoubidoo.commands, x) if isinstance(x, str) else x, items))
        except AttributeError:
            return list(), tuple()
        return list(filter(lambda x: reduce(lambda u, v: u or v, [isinstance(x, i) for i in items]), self._line)), items

    def apply(self, f: Callable[[commands.Command], commands.Command]) -> Input:
        """Apply (map) a function on each command of the input sequence.

        The function must take a single command as unique parameter and return the (modified) command.

        Args:
            f: the calable function.

        Returns:
            the input sequence (in place operation).
        """
        self._line = list(map(f, self._line))
        return self

    def cleanup(self):
        """Cleanup temporary paths.

        Performs the cleanup to remove the temporary paths and the Zgoubi data files (input file, but also other output
        files). This is essentially the inverse of calling the input. Note that coding the input multiple times will
        automatically cleanup previous sets of temporary directories.

        Examples:
            >>> zi = Input()
            >>> pm = ParametricMapping()
            >>> zi(mappings=pm)  # Writes input files in newly created tempoary directories
            >>> zi.cleanup()  # Cleanup the temporary directories and Zgoubi input files
        """
        for p in self._paths:
            try:
                p.cleanup()
            except AttributeError:
                pass
        self._paths = dict()

    def validate(self, validators: Optional[List[Callable]]) -> bool:
        """

        Args:
            validators:

        Returns:

        """
        if validators is not None:
            for v in validators:
                v(self)
        return True

    def update(self, parameters: _pd.DataFrame) -> Input:
        """
        TODO

        This is essentially an update following a fit.

        Args:
            parameters:

        Returns:

        """
        for i, r in parameters.iterrows():
            setattr(self[r['element_id'] - 1], r['parameter'], r['final'])
        return self

    def adjust(self, mapping: MappedParametersType) -> MappedParametersType:
        """

        Args:
            mapping:

        Returns:

        """
        initial_values = {}
        for k, v in mapping.items():
            _ = k.split('.')
            if len(_) > 1:
                assert len(_) == 2, "Parametric mapping labels must be a tuple of 2 strings."
                initial_values[k] = getattr(getattr(self, _[0]), _[1].rstrip('_'))
                setattr(getattr(self, _[0]), _[1], v)
        return initial_values

    def index(self, obj: Union[str, commands.Command]) -> int:
        """Index of an object in the sequence.

        Provides an index for a given object within a sequence. This index is a valid Zgoubi command numbering index
        and can be used as such, for example, as a parameter to the Fit command.

        Args:
            obj: the object; can be an instance of a Zgoubidoo Command or a string representing the element's LABEL1.

        Returns:
            the index of the object in the input sequence.

        Raises:
            ValueError if the object is not present in the input sequence.
        """
        if isinstance(obj, zgoubidoo.commands.Command):
            return self.line.index(obj) + 1
        elif isinstance(obj, str):
            for i, e in enumerate(self.line):
                if e.LABEL1 == obj:
                    return i + 1
        raise ValueError(f"Element {obj} not found.")

    def get_attributes(self, attribute: str = "LABEL1") -> List[str]:
        """List a given command attribute in the input sequence.

        In case some elements in the input sequence do not have that attribute, None is used.

        Args:
            attribute: the name of the attribute.

        Returns:
            the list of the values of the given attribute across the input sequence.
        """
        return [getattr(e, attribute, None) for e in self._line]

    labels = property(get_attributes)
    """List of the LABEL1 property of each element of the input sequence."""

    labels1 = property(get_attributes)
    """Same as ``labels``."""

    labels2 = property(partial(get_attributes, label='LABEL2'))
    """List of the LABEL2 property of each element of the input sequence."""

    @property
    def name(self) -> str:
        """Name of the input sequence.

        Returns:
            the name of the input sequence or None.
        """
        return self._name

    @property
    def paths(self) -> PathsListType:
        """Paths where the input has been written.

        Returns:
            a list of paths.
        """
        return self._paths

    @property
    def keywords(self) -> List[str]:
        """

        Returns:

        """
        return [e.KEYWORD for e in self._line]

    @property
    def line(self) -> List[zgoubidoo.commands.Command]:
        """

        Returns:

        """
        return self._line

    @property
    def optical_length(self) -> _Q:
        """

        Returns:

        """
        return self._optical_length

    @property
    def beam(self) -> Optional[zgoubidoo.commands.Beam]:
        """

        Returns:

        Raises:
            TODO

        """
        _ = self[zgoubidoo.commands.Beam]
        if len(_) > 1:
            raise ZgoubiInputException("Multiple beams found in input.")
        else:
            return next(iter(_), None)

    @property
    def beam_mappings(self) -> MappedParametersListType:
        """

        Returns:

        """
        if self.beam is None:
            return []
        else:
            return self.beam.mappings

    def increase_optical_length(self, l: _Q):
        """

        Args:
            l:

        Returns:

        """
        self._optical_length += l

    def survey(self, reference_frame: _Frame = None) -> Input:
        """Perform a survey on the input sequence.

        Args:
            reference_frame: a Zgoubidoo Frame object acting as the global reference frame.

        Returns:
            the surveyed input sequence.
        """
        return zgoubidoo.survey(self, reference_frame)

    def plot(self,
             ax=None,
             tracks=None,
             artist: zgoubidoo.vis.ZgoubiPlot = None,
             start: Optional[Union[str, zgoubidoo.commands.Command]] = None,
             stop: Optional[Union[str, zgoubidoo.commands.Command]] = None,
             z_rotation: Optional[_.Q] = 0 * _ureg.radian,
             ) -> zgoubidoo.vis.ZgoubiPlot:
        """Plot the input sequence.

        TODO

        Args:
            ax: an optional matplotlib axis to draw on
            tracks: TODO
            artist: an artist object for the rendering
            start: first element of the beamline to be plotted
            stop: last element of the beamline to be plotted
            z_rotation:
        """
        zgoubidoo.survey(beamline=self, reference_frame=_Frame().rotate_z(z_rotation))

        if artist is None:
            artist = zgoubidoo.vis.ZgoubiMpl(ax=ax)
        if ax is not None:
            artist.ax = ax

        zgoubidoo.vis.beamline(line=self[start:stop],
                               tracks=tracks,
                               artist=artist,
                               )

        artist.ax.set_aspect('equal', 'datalim')

        return artist

    @staticmethod
    def write(_: Input,
              filename: str = ZGOUBI_INPUT_FILENAME,
              path: str = '.',
              mode: str = 'w',
              validators: Optional[List[Callable]] = None) -> int:
        f"""
        Write a Zgoubi Input object to file after performing optional validation.

        Args:
            _: a Zgoubidoo Input object
            filename: the file name (default: {ZGOUBI_INPUT_FILENAME})
            path: path for the file (default: .)
            mode: the mode for the writer (default: 'w' - overwrite)
            validators: callables used to validate the input
        """
        _.validate(validators)
        with open(os.path.join(path, filename), mode) as f:
            return f.write(str(_))

    @staticmethod
    def build(name: str = 'beamline', line: Optional[List[zgoubidoo.commands.Command]] = None) -> str:
        """Build a string representing the complete input.

        A string is built based on the Zgoubi serialization of all elements (commands) of the input sequence.

        Args:
            name: the name of the resulting Zgoubi input.
            line: the input sequence.

        Returns:
            a string in a valid Zgoubi input format.
        """
        extra_end = None
        if len(line) == 0 or not isinstance(line[-1], zgoubidoo.commands.End):
            extra_end = [zgoubidoo.commands.End()]
        return ''.join(map(str, [name] + (line or []) + (extra_end or [])))

    @classmethod
    def parse(cls, stream: str, debug: bool = False) -> Input:
        """

        Args:
            stream:
            debug:

        Returns:

        """
        return cls(
            line=[getattr(zgoubidoo.commands, _parse.search("'{KEYWORD}'", c)['KEYWORD'].capitalize()).build(c, debug)
                  for c in "\n".join([_.strip() for _ in stream.split('\n')]).strip('\n').split('\n\n')]
        )


class MadInput(Input):
    """MAD-X input sequence with correct grammer."""
    ZGOUBI_INPUT_FILENAME: str = 'input.mad'
    """File name for input data."""

    @staticmethod
    def build(name: str = 'beamline', line: Optional[List[zgoubidoo.commands.Command]] = None) -> str:
        """Build a string representing the complete input.

        A string is built based on the MAD-X serialization of all elements (commands) of the input sequence.

        Args:
            name: the name of the resulting Zgoubi input.
            line: the input sequence.

        Returns:
            a string in a valid Zgoubi input format.
        """
        extra_end = None
        if len(line) == 0 or not isinstance(line[-1], zgoubidoo.commands.madx.Stop):
            extra_end = [zgoubidoo.commands.madx.Stop()]
        return '\n'.join(map(str, (line or []) + (extra_end or [])))


class InputValidator:
    """Validation methods for Zgoubi Input.

    Follows the rules as defined in the Zgoubi code and manual.
    """

    @staticmethod
    def validate_objet_is_first_command(_: Input) -> bool:
        """
        Validate that the first input command is a (mc)objet.

        Args:
            _: the input to validate

        Returns:
            True if the validation is successful; otherwise a `ZgoubiInputException` is raised.
        """
        line = _.line
        if len(_) > 0 and not isinstance(line[0], (zgoubidoo.commands.Objet, zgoubidoo.commands.MCObjet)):
            raise ZgoubiInputException("The first command in the input is not an Objet. (or MCObjet).")
        return True

    @staticmethod
    def validate_objets_do_not_exceed_imax(_: Input) -> bool:
        """
        Validate that all objets and mcobjets have their IMAX value below the maximum value.

        Args:
            _: the input to validate

        Returns:
            True is the validation is successful; otherwise a `ZgoubiInputException` is raised.
        """
        objets = _[zgoubidoo.commands.Objet, zgoubidoo.commands.MCObjet]
        for o in objets:
            if (o.IMAX or 0.0) > ZGOUBI_IMAX:
                raise ZgoubiInputException(f"Objet {o.label1} IMAX exceeds maximum value ({ZGOUBI_IMAX}).")
        return True
