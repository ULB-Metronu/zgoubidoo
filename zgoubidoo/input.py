"""Zgoubidoo's input module: interface for Zgoubi input file.

This module interfaces Zgoubi input files to the other components of Zgoubidoo. Its main feature is the `Input` class,
which allows to represent a set of Zgoubi input commands and serialize it into a valid input file. The input can also
be validated using a set of validators, following the Zgoubi input constraints.
"""
from __future__ import annotations
from typing import Callable, Sequence
from functools import partial, reduce
import tempfile
import os
import pandas as _pd
import parse as _parse
from . import ureg as _ureg
from . import _Q
from .commands import *
from .beam import Beam
from .frame import Frame as _Frame
import zgoubidoo.commands

ListPaths = List[Union[str, tempfile.TemporaryDirectory]]

ZGOUBI_INPUT_FILENAME: str = 'zgoubi.dat'
"""File name for Zgoubi input data."""

ZGOUBI_IMAX: int = 10000
"""Maximum number of particles that a Zgoubi objet can contain."""


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

    def __init__(self, name: str = 'beamline', line: Optional[Sequence[commands.Command]] = None):
        self._name: str = name
        if line is None:
            line = []
        self._line: List[commands.Command] = line
        self._paths: ListPaths = list()
        self._inputs: List[Input] = list()
        self._optical_length: _Q = 0 * _ureg.m

    def __str__(self) -> str:
        """Provides the string representation, a valid Zgoubi input stream.

        Constructs the Zgoubi input sequence with the serialization of each command. An implicit `End` command is added
        in case it is not present. The `Input` name is used as a header.

        Returns:
            a valid Zgoubi input stream as a string.
        """
        return Input.build(self._name, self._line)

    def __repr__(self) -> str:
        return str(self)

    def __call__(self, beam: Optional[Beam] = None, filename: str = ZGOUBI_INPUT_FILENAME, path: str = '.'):
        """Writes the string representation of the object onto a file (Zgoubi input file).

        Args:
            beam:
            filename: the Zgoubi input file name (default: zgoubi.dat)
            path:

        Raises:

        """
        self._paths: ListPaths = list()
        if beam is None:
            self._paths.append(path)
            self.write(self, filename, path)
        else:
            objets = self[zgoubidoo.commands.Objet]
            particules = self[zgoubidoo.commands.Particule]
            if len(objets) == 0 and len(particules) == 0:
                generated_input = Input(name=self.name, line=self.line.copy())
                generated_input._line.insert(0, beam.particle())
                objet = beam.objet(BORO=beam.brho)
                generated_input._line.insert(0, objet)
                if beam.distribution is None:
                    objet.clear()
                    temp_dir = tempfile.TemporaryDirectory()
                    self._paths.append(temp_dir)
                    self._inputs.append(generated_input)
                    generated_input.write(generated_input, filename, path=temp_dir.name)
                else:
                    for s in beam.slices:
                        if len(s) > ZGOUBI_IMAX:
                            raise ZgoubiInputException(f"Trying to track too many particles (IMAX={ZGOUBI_IMAX}). "
                                                       f"Try to increase the number of slices.")
                        objet.clear()
                        objet += s
                        temp_dir = tempfile.TemporaryDirectory()
                        self._paths.append(temp_dir)
                        self._inputs.append(generated_input)
                        generated_input.write(generated_input, filename, path=temp_dir.name)
            else:
                raise ZgoubiInputException("When applying a Beam on an Input, the input should not contain "
                                           "any 'Particle' or 'Objet'.")
        return self

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
            other: the `Command` to be removed or its LABEL1 as a string.

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
            if isinstance(items.start, (Command, str)):
                start = self.index(items.start) - 1
            if isinstance(items.stop, (Command, str)):
                end = self.index(items.stop)
            slicing = slice(start, end, items.step)
            return Input(name=f"{self._name}_sliced_from_{getattr(items.start, 'LABEL1', items.start)}"
                              f"_to_{getattr(items.stop, 'LABEL1', items.stop)}",
                         line=self._line[slicing]
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
                         line=l
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
        raise AttributeError

    def __setattr__(self, key: str, value: Any):
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
                if getattr(e, key) is not None:
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
            items = tuple(map(lambda x: getattr(commands, x) if isinstance(x, str) else x, items))
        except AttributeError:
            return list(), tuple()
        return list(filter(lambda x: reduce(lambda u, v: u or v, [isinstance(x, i) for i in items]), self._line)), items

    def apply(self, f: Callable[[commands.Command], commands.Command]) -> None:
        """

        Args:
            f:

        Returns:

        """
        self._line = list(map(f, self._line))

    def cleanup(self):
        """

        Returns:

        """
        for p in self._paths:
            try:
                p.cleanup()
            except AttributeError:
                pass
        self._paths = list()

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

        Args:
            parameters:

        Returns:

        """
        for i, r in parameters.iterrows():
            setattr(self[r['element_id'] - 1], r['parameter'], r['final'])
        return self

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
        if isinstance(obj, Command):
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
    def paths(self) -> ListPaths:
        """Paths where the input has been written.

        Returns:
            a list of paths.
        """
        return self._paths

    @property
    def inputs(self) -> List[Input]:
        """

        Returns:

        """
        return self._inputs

    @property
    def keywords(self) -> List[str]:
        """

        Returns:

        """
        return [e.KEYWORD for e in self._line]

    @property
    def line(self) -> List[commands.Command]:
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
            reference_frame: a Zgoubidoo Frame object acting as the global reference frame

        Returns:
            the surveyed input sequence.
        """
        return zgoubidoo.survey(self, reference_frame)

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
    def build(name: str = 'beamline', line: Optional[List[commands.Command]] = None) -> str:
        """Build a string representing the complete input.

        A string is built based on the Zgoubi serialization of all elements (commands) of the input sequence.

        Args:
            name: the name of the resulting Zgoubi input.
            line: the input sequence.

        Returns:
            a string in a valid Zgoubi input format.
        """
        extra_end = None
        if len(line) == 0 or not isinstance(line[-1], commands.End):
            extra_end = [commands.End()]
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
