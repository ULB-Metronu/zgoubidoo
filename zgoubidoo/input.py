from __future__ import annotations
from typing import Callable, List, Sequence, Optional, NoReturn
import tempfile
import os
from functools import reduce
from . import commands
from . beam import Beam
import zgoubidoo.commands

ZGOUBI_INPUT_FILENAME: str = 'zgoubi.dat'
ZGOUBI_IMAX: int = 10000


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

    def __str__(self) -> str:
        return self.build(self._name, self._line)

    def __repr__(self) -> str:
        return str(self)

    def __call__(self, beam: Optional[Beam]=None, filename: str=ZGOUBI_INPUT_FILENAME, path: str='.') -> NoReturn:
        """
        Write the string representation of the object onto a file (Zgoubi input file).
        :param filename: the Zgoubi input file name (default: zgoubi.dat)
        :return: NoReturn
        """
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
        return len(self._line)

    def __iadd__(self, o) -> Input:
        self._line.append(o)
        return self

    def __getitem__(self, items) -> Input:
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
        if key.startswith('_'):
            self.__dict__[key] = value
        else:
            for e in self._line:
                if getattr(e, key) is not None:
                    setattr(e, key, value)

    def __contains__(self, items) -> int:
        if not isinstance(items, tuple):
            items = (items,)
        l, i = self._filter(items)
        return len(l)

    def _filter(self, items) -> tuple:
        try:
            items = tuple(map(lambda x: getattr(commands, x) if isinstance(x, str) else x, items))
        except AttributeError:
            return list(), tuple()
        return list(filter(lambda x: reduce(lambda u, v: u or v, [isinstance(x, i) for i in items]), self._line)), items

    def apply(self, f: Callable[[commands.Command], commands.Command]) -> None:
        self._line = list(map(f, self._line))

    def cleanup(self):
        for p in self._paths:
            p.cleanup()
        self._paths = list()

    def get_labels(self, label="LABEL1") -> List[str]:
        return [getattr(e, label, '') for e in self._line]

    labels = property(get_labels)
    labels1 = property(get_labels)

    @property
    def labels2(self) -> List[str]:
        return [e.LABEL2 for e in self._line]

    @property
    def name(self):
        return self._name

    @property
    def paths(self):
        return self._paths

    @property
    def inputs(self):
        return self._inputs

    @property
    def keywords(self) -> List[str]:
        return [e.KEYWORD for e in self._line]

    @property
    def line(self) -> Sequence[commands.Command]:
        return self._line

    @staticmethod
    def write(_: Input, filename: str=ZGOUBI_INPUT_FILENAME, path: str='.', mode: str='w') -> NoReturn:
        """
        Write a Zgoubi Input object to file.
        :param _: a Zgoubidoo Input object
        :param filename: the file name (default: zgoubi.dat)
        :param path: path for the file (default: .)
        :param mode: the mode for the writer (default: 'w' - overwrite)
        :return: NoReturn
        """
        with open(os.path.join(path, filename), mode) as f:
            f.write(str(_))

    @staticmethod
    def build(name='beamline', line=None) -> str:
        if len(line) == 0 or not isinstance(line[-1], commands.End):
            line.append(commands.End())
        return ''.join(map(str, [name] + (line or [])))


class Beamline(Input):
    def __init__(self, name: Optional[str]=None, input_line: Optional[Input]=None):
        if name is None:
            n = f"BEAMLINE_{input_line.name if input_line is not None else ''}"
        else:
            n = name
        if input_line is None:
            line = []
        else:
            line = input_line[commands.Magnet].line
        super().__init__(n, line)

    @staticmethod
    def build(name='beamline', line=None) -> str:
        return ''.join(map(str, [name] + (line or [])))
