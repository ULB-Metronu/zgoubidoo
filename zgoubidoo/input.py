"""

"""
from __future__ import annotations
from typing import Callable, List, Sequence, Optional, NoReturn, Union
from functools import partial
import tempfile
import os
from functools import reduce
import pandas as _pd
from . import ureg as _ureg
from . import _Q
from . import commands
from .beam import Beam
import zgoubidoo.commands

ZGOUBI_INPUT_FILENAME: str = 'zgoubi.dat'
"""File name for Zgoubi input data."""

ZGOUBI_IMAX: int = 10000
"""Maximum number of particles that a Zgoubi objet can contain."""


class ZgoubiInputException(Exception):
    """Exception raised for errors within Zgoubi Input."""

    def __init__(self, m):
        self.message = m


class Input:
    """
    A Zgoubidoo `Input` object represents the Zgoubi input file data structure. It is thus essentially a list of
    Zgoubidoo objects representing commands and elements for the generation of Zgoubi input files.

    The `Input` supports a `str` representation allowing to generate the Zgoubi input. Additionnally, calling the object
    will write the string representation to a Zgoubi input file.

    Examples:
        >>> zi = Input(name='test_beamline')
        >>> len(zi) == 0
        True
        >>> zi.name
        'test_beamline'
    """

    def __init__(self, name: str='beamline', line: Sequence[commands.Command]=None) -> NoReturn:
        self._name: str = name
        if line is None:
            line = []
        self._line: List[commands.Command] = line
        self._paths = list()
        self._inputs = list()
        self._optical_length = 0 * _ureg.m

    def __str__(self) -> str:
        """

        Returns:

        """
        return self.build(self._name, self._line)

    def __repr__(self) -> str:
        return str(self)

    def __call__(self, beam: Optional[Beam]=None, filename: str=ZGOUBI_INPUT_FILENAME, path: str='.') -> NoReturn:
        """
        Write the string representation of the object onto a file (Zgoubi input file).
        :param filename: the Zgoubi input file name (default: zgoubi.dat)
        :return: NoReturn
        """
        self._paths = list()
        if beam is None:
            self._paths.append(path)
            self.write(self, filename, path)
        else:
            objets = self[zgoubidoo.commands.Objet2]
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
        """

        Returns:

        """
        return len(self._line)

    def __iadd__(self, o) -> Input:
        """

        Args:
            o:

        Returns:

        """
        self._line.append(o)
        return self

    def __isub__(self, other) -> Input:
        """

        Args:
            other:

        Returns:

        """
        self._line = [c for c in self._line if c != other]
        return self

    def __getitem__(self, items) -> Union[zgoubidoo.commands.Command, Input]:
        """

        Args:
            items:

        Returns:

        """
        # Behave like element access
        if isinstance(items, int):
            return self._line[items]

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

    def __setattr__(self, key: str, value) -> NoReturn:
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

    def __contains__(self, items) -> int:
        """

        Args:
            items:

        Returns:

        """
        if not isinstance(items, tuple):
            items = (items,)
        l, i = self._filter(items)
        return len(l)

    def _filter(self, items) -> tuple:
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

    def validate(self, validators: List[Callable]) -> bool:
        """

        Args:
            validators:

        Returns:

        """
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

    def get_labels(self, label="LABEL1") -> List[str]:
        """

        Args:
            label:

        Returns:

        """
        return [getattr(e, label, '') for e in self._line]

    labels = property(get_labels)
    """"""

    labels1 = property(get_labels)
    """"""

    labels2 = property(partial(get_labels, label='LABEL2'))
    """"""

    @property
    def name(self):
        """

        Returns:

        """
        return self._name

    @property
    def paths(self):
        """

        Returns:

        """
        return self._paths

    @property
    def inputs(self):
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
    def optical_length(self) -> Optional[_Q]:
        """

        Returns:

        """
        return self._optical_length

    def increase_optical_length(self, l: _Q) -> NoReturn:
        """

        Args:
            l:

        Returns:

        """
        self._optical_length += l

    @staticmethod
    def write(_: Input,
              filename: str=ZGOUBI_INPUT_FILENAME,
              path: str='.',
              mode: str='w',
              validators: Optional[List[Callable]]=None) -> int:
        """
        Write a Zgoubi Input object to file after performing optional validation.
        :param _: a Zgoubidoo Input object
        :param filename: the file name (default: zgoubi.dat)
        :param path: path for the file (default: .)
        :param mode: the mode for the writer (default: 'w' - overwrite)
        :param validators: callables used to validate the input
        :return: NoReturn
        """
        if validators is not None:
            _.validate(validators)
        with open(os.path.join(path, filename), mode) as f:
            return f.write(str(_))

    @staticmethod
    def build(name='beamline', line=None) -> str:
        """

        Args:
            name:
            line:

        Returns:

        """
        extra_end = None
        if len(line) == 0 or not isinstance(line[-1], commands.End):
            extra_end = [commands.End()]
        return ''.join(map(str, [name] + (line or []) + (extra_end or [])))


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
        if len(_) > 0 and not isinstance(line[0], (commands.Objet, commands.MCObjet)):
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
        objets = _[commands.Objet, commands.MCObjet]
        for o in objets:
            if (o.IMAX or 0.0) > ZGOUBI_IMAX:
                raise ZgoubiInputException(f"Objet {o.label1} IMAX exceeds maximum value ({ZGOUBI_IMAX}).")
        return True
