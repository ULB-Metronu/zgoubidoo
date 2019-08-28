"""Zgoubidoo's input module: interface for Zgoubi input file.

This module interfaces Zgoubi input files to the other components of Zgoubidoo. Its main feature is the `Input` class,
which allows to represent a set of Zgoubi input commands and serialize it into a valid input file. The input can also
be validated using a set of validators, following the Zgoubi input constraints.

The inputs are serialized and saved as `zgoubi.dat` in temporary directories. When serializing an input it is possible
to provide a parametric mapping (combinations of the variations of one or more parameters) to generate multiple Zgoubi
input files.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable, Sequence, Union, List, Tuple, Iterable, Any, Deque, Mapping
from collections import deque
import itertools
from inspect import getmembers, isfunction
from functools import partial, reduce
import tempfile
import logging
import shutil
import os
import pandas as _pd
import parse as _parse
from georges_core.frame import Frame as _Frame
import zgoubidoo.converters as _zgoubi_converters
import zgoubidoo.commands
from .zgoubi import Zgoubi as _Zgoubi
from .commands.commands import ZgoubidooException as _ZgoubidooException
from zgoubidoo.commands import Command as _Command
from .commands.actions import End as _End
from .commands.beam import Beam as _Beam
from .commands.beam import BeamTwiss as _BeamTwiss
from .commands import particules as _particules
from .commands.particules import Particule as _Particule
from .commands.particules import ParticuleType as _ParticuleType
from .commands.mcobjet import MCObjet as _MCObjet
from .constants import ZGOUBI_IMAX, ZGOUBI_INPUT_FILENAME
from .mappings import MappedParametersType as _MappedParametersType
from .mappings import MappedParametersListType as _MappedParametersListType
from .mappings import flatten as _flatten
from . import Kinematics as _Kinematics
if TYPE_CHECKING:
    import georges_core.sequences
    from zgoubidoo.commands import CommandType
    from .commands.beam import BeamType as _BeamType

_logger = logging.getLogger(__name__)

PathsListType = List[Tuple[_MappedParametersType, Union[str, tempfile.TemporaryDirectory], bool]]
"""Type alias for a list of parametric keys and paths values."""


class ZgoubiInputException(Exception):
    """Exception raised for errors within Zgoubi Input."""

    def __init__(self, m):
        self.message = m


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
                 line: Optional[Sequence[_Command]] = None,
                 ):
        self._name: str = name
        line = line or list()
        self._line: Deque[_Command] = deque(line)
        self._paths: PathsListType = list()
        self._reference_frame: Optional[_Frame] = None

    def __del__(self):
        _logger.debug(f"Input object '{self.name }' for paths {self.paths} is being destroyed.")

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
                 *,
                 mappings: Optional[_MappedParametersListType] = None,
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
        self._paths = self.paths + self._generate(mappings=mappings, filename=filename, path=path)
        return self

    def _generate(self,
                  mappings: Optional[_MappedParametersListType] = None,
                  filename: str = ZGOUBI_INPUT_FILENAME,
                  path: Optional[str] = None,
                  ) -> PathsListType:
        """Writes the string representation of the object onto files (Zgoubi input files).

        Args:
            mappings: TODO
            filename: the Zgoubi input file name (default: zgoubi.dat)
            path: an optional path for the temporary directories that will be created for the input files (default:
            uses temporary paths)

        Return:


        """
        paths: PathsListType = list()
        mappings = mappings or [{}]
        if len(self.beam_mappings) > 0:
            mappings = list(map(lambda _: {**_[0], **_[1]}, itertools.product(mappings, self.beam_mappings)))
        initial_state: _MappedParametersType = {}
        for mapping in mappings:
            if mapping in self.mappings:  # Prevent duplicate entries but allows existing mappings to be regenerated
                for i, p in enumerate(self._paths):
                    if p[0] == mapping:
                        del self._paths[i]
            previous_state = self.adjust(mapping)
            if initial_state is None:
                initial_state = previous_state
            if path is not None:
                path = path.rstrip('/') + '/'
            target_dir = tempfile.TemporaryDirectory(prefix=path)
            paths.append((mapping, target_dir, False))
            Input.write(self, filename, path=target_dir.name)
        self.adjust(initial_state)
        return paths

    def __len__(self) -> int:
        """Length of the input sequence.

        Returns:
            the number of elements in the sequence.
        """
        return len(self._line)

    def __iadd__(self, command: _Command) -> Input:
        """Append a command at the end of the input sequence.

        Args:
            command: the command to be appended.

        Returns:
            the input sequence (in-place operation).
        """
        self._line.append(command)
        return self

    def __isub__(self, other: Union[str, _Command]) -> Input:
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
                    ) -> Union[_Command, Input]:
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
            if isinstance(items.start, (_Command, str)):
                start = self.index(items.start)
            if isinstance(items.stop, (_Command, str)):
                end = self.index(items.stop) + 1
            return Input(name=f"{self._name}_sliced_from_{getattr(items.start, 'LABEL1', items.start)}"
                              f"_to_{getattr(items.stop, 'LABEL1', items.stop)}",
                         line=list(itertools.islice(self._line, start, end, items.step)),
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
                         )

    def __getattr__(self, item: str) -> _Command:
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
                try:
                    setattr(e, key, value)
                except _ZgoubidooException:
                    pass

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
            items = tuple(map(
                lambda x: getattr(zgoubidoo.commands, x.capitalize()) if isinstance(x, str) else x, items
            ))
        except AttributeError:
            return list(), tuple()
        return list(filter(lambda x: reduce(lambda u, v: u or v, [isinstance(x, i) for i in items]), self._line)), items

    def apply(self, f: Callable[[_Command], _Command]) -> Input:
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
                p[1].cleanup()
            except AttributeError:
                pass
        self.apply(lambda _: _.clean_output_and_results())
        self._paths = []

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

    def adjust(self, mapping: _MappedParametersType) -> _MappedParametersType:
        """

        Args:
            mapping:

        Returns:

        """
        initial_values = {}
        for k, v in mapping.items():
            try:
                _ = k.split('.')
            except AttributeError:
                _ = k
            if len(_) > 1:
                assert len(_) == 2, "Parametric mapping labels must be a tuple of 2 strings."
                if _[0] == 'ALL_LINE':
                    initial_values[k] = None
                    setattr(self, _[1], v)
                else:
                    initial_values[k] = getattr(getattr(self, _[0]), _[1].rstrip('_'))
                    setattr(getattr(self, _[0]), _[1], v)
        return initial_values

    def index(self, obj: Union[str, _Command]) -> int:
        """Index of an object in the sequence.

        Provides an index for a given object within a sequence.

        Args:
            obj: the object; can be an instance of a Zgoubidoo Command or a string representing the element's LABEL1.

        Returns:
            the index of the object in the input sequence.

        Raises:
            ValueError if the object is not present in the input sequence.
        """
        if isinstance(obj, _Command):
            return self.line.index(obj)
        elif isinstance(obj, str):
            for i, e in enumerate(self.line):
                if e.LABEL1 == obj:
                    return i
        raise ValueError(f"Element {obj} not found.")

    def zgoubi_index(self, obj: Union[str, _Command]) -> int:
        """Index of an object in the sequence (following Zgoubi elements numbering).

        Provides an index for a given object within a sequence. This index is a valid Zgoubi command numbering index
        and can be used as such, for example, as a parameter to the Fit command.

        Args:
            obj: the object; can be an instance of a Zgoubidoo Command or a string representing the element's LABEL1.

        Returns:
            the index of the object in the input sequence.

        Raises:
            ValueError if the object is not present in the input sequence.
        """
        return self.index(obj) + (3 if self.beam is not None else 1)

    def replace(self, element, other) -> Input:
        """

        Args:
            element:
            other:

        Returns:

        """
        self.line[self.index(element)] = other
        return self

    def insert_before(self, element, other) -> Input:
        """

        Args:
            element:
            other:

        Returns:

        """
        self.line.insert(self.index(element), other)
        return self

    def insert_after(self, element, other) -> Input:
        """

        Args:
            element:
            other:

        Returns:

        """
        self.line.insert(self.index(element)+1, other)
        return self

    def remove(self, prefix: str) -> Input:
        """

        Args:
            prefix:

        Returns:

        """
        self._line = list(filter(lambda _: not (_.LABEL1 == prefix or _.LABEL1.startswith(prefix + '_')), self.line))
        return self

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

    labels2 = property(partial(get_attributes, attribute='LABEL2'))
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
    def mappings(self) -> List[_MappedParametersType]:
        """List of mappings existing for the input sequence."""
        return [p[0] for p in self.paths]

    @property
    def keywords(self) -> List[str]:
        """

        Returns:

        """
        return [e.KEYWORD for e in self._line]

    @property
    def line(self) -> Deque[_Command]:
        """

        Returns:

        """
        return self._line

    @property
    def valid_survey(self) -> bool:
        """Boolean indicating if the line has been surveyed."""
        return self._reference_frame is not None

    @property
    def survey_reference_frame(self) -> _Frame:
        """Provides the reference frame which was used for the prior survey of the line."""
        return self._reference_frame

    @property
    def beam(self) -> Optional[_Beam]:
        """

        Returns:

        Raises:
            TODO

        """
        _ = self[_Beam]
        if len(_) > 1:
            raise ZgoubiInputException("Multiple beams found in input.")
        else:
            return next(iter(_), None)

    @property
    def beam_mappings(self) -> _MappedParametersListType:
        """

        Returns:

        """
        if self.beam is None:
            return []
        else:
            return self.beam.mappings

    def survey(self, reference_frame: _Frame = None,
               with_reference_trajectory: bool = False,
               reference_kinematics: Optional[_Kinematics] = None,
               reference_particle: Optional[Union[_Particule, _ParticuleType]] = None,
               output: bool = False
               ) -> _pd.DataFrame:
        """Perform a survey on the input sequence.

        Args:
            reference_frame: a Zgoubidoo Frame object acting as the global reference frame.
            with_reference_trajectory:
            reference_kinematics:
            reference_particle:
            output:

        Returns:
            the surveyed input sequence.
        """
        self._reference_frame = reference_frame or _Frame()
        return zgoubidoo.survey(self,
                                reference_frame=reference_frame,
                                with_reference_trajectory=with_reference_trajectory,
                                reference_kinematics=reference_kinematics,
                                reference_particle=reference_particle,
                                output=output
                                )

    def clear_survey(self):
        """

        Returns:

        """
        zgoubidoo.clear_survey(self)
        self._reference_frame = None

    def execute(self):
        """

        Returns:

        """
        return _Zgoubi()(self).collect()

    def plot(self,
             ax=None,
             tracks=None,
             artist: zgoubidoo.vis.Artist = None,
             start: Optional[Union[str, _Command]] = None,
             stop: Optional[Union[str, _Command]] = None,
             with_frames: bool = True,
             with_elements: bool = True,
             with_apertures: bool = False,
             set_equal_aspect: bool = True,
             ) -> zgoubidoo.vis.Artist:
        """Plot the input sequence.

        TODO

        Args:
            ax: an optional matplotlib axis to draw on
            tracks: TODO
            artist: an artist object for the rendering
            start: first element of the beamline to be plotted
            stop: last element of the beamline to be plotted
            with_frames:
            with_elements:
            with_apertures:
            set_equal_aspect:
        """
        if self._reference_frame is None:
            raise ZgoubiInputException("The input must be surveyed explicitely before plotting.")
        if artist is None:
            artist = zgoubidoo.vis.MatplotlibArtist(ax=ax, with_frames=with_frames)
        if ax is not None:
            artist.ax = ax

        zgoubidoo.vis.beamline(line=self[start:stop],
                               tracks=tracks,
                               artist=artist,
                               with_elements=with_elements,
                               with_apertures=with_apertures,
                               )
        artist.ax.autoscale_view()
        if set_equal_aspect:
            artist.ax.set_aspect('equal', 'datalim')
        return artist

    def save(self, destination: str = '.',
             what: Optional[List[str]] = None,
             executed_only: bool = True):
        """Save input and/or output Zgoubi files to a user specified directory.

        This is essentially a functionality allowing the user to save data files for further (external) post-processing.

        Args:
            destination: path to the destination where the files will be saved
            what: a list of files to be saved (default: only zgoubi.dat)
            executed_only: if True, will save only the files for the paths that have been executed by Zgoubi
        """

        files = what or [
            ZGOUBI_INPUT_FILENAME,
        ]
        for m, p, e in self.paths:
            if executed_only and not e:
                continue
            mapping_string = ''
            for k, v in m.items():
                if len(mapping_string) != 0:
                    mapping_string += '__'
                mapping_string += f"{k}_{v}"
            mapped_destination = os.path.join(destination, mapping_string)
            if m != {}:
                os.mkdir(mapped_destination)
            for f in files:
                shutil.copyfile(os.path.join(p.name, f),
                                os.path.join(mapped_destination, f)
                                )

    @classmethod
    def from_sequence(cls,
                      sequence: georges_core.sequences.Sequence,
                      options: Optional[dict] = None,
                      converters: Optional[dict] = None,
                      elements_database: Optional[dict] = None,
                      beam: Optional[_BeamType] = _BeamTwiss,
                      beam_options: Optional[Mapping] = None,
                      with_survey: bool = True,
                      with_survey_reference: bool = True,
                      ):
        """

        Args:
            sequence:
            options:
            converters:
            elements_database:
            beam:
            beam_options:
            with_survey:
            with_survey_reference:

        Returns:

        """
        madx_converters = {k.split('_')[0].upper(): v
                           for k, v in getmembers(_zgoubi_converters, isfunction) if k.endswith('to_zgoubi')}
        conversion_functions = {**madx_converters, **(converters or {})}
        elements_database = elements_database or {}
        options = options or {}
        converted_sequence = deque(
            sequence.apply(
                lambda _: elements_database.get(_.name,
                                                conversion_functions.get(_['KEYWORD'], lambda _, __, ___: None)
                                                (_, sequence.kinematics, options.get(_['KEYWORD'], {}))
                                                ),
                axis=1
            ).values
        )
        if beam is not None:
            converted_sequence.appendleft(
                (beam.from_sequence(sequence, **(beam_options or {})), )  # Note the tuple here
            )
        _ = cls(
            name=sequence.name,
            line=list(_flatten(converted_sequence)),
        )
        _.KINEMATICS = sequence.kinematics
        if with_survey:
            _.survey(with_reference_trajectory=with_survey_reference,
                     reference_kinematics=sequence.kinematics,
                     reference_particle=getattr(_particules, sequence.particle.__name__)
                     )
        return _

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
    def build(name: str = 'beamline', line: Optional[Deque[_Command]] = None) -> str:
        """Build a string representing the complete input.

        A string is built based on the Zgoubi serialization of all elements (commands) of the input sequence.

        Args:
            name: the name of the resulting Zgoubi input.
            line: the input sequence.

        Returns:
            a string in a valid Zgoubi input format.
        """
        extra_end = None
        if len(line) == 0 or not isinstance(line[-1], _End):
            extra_end = [_End()]
        return ''.join(map(str, [name] + (list(line) or []) + (extra_end or [])))

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


class ZgoubiInputValidator:
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
