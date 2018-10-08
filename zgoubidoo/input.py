from __future__ import annotations
from functools import reduce
from typing import Callable, List, Sequence, Optional, NoReturn
from . import commands

ZGOUBI_INPUT_FILENAME: str = 'zgoubi.dat'


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

    def __str__(self) -> str:
        return self.build(self._name, self._line)

    def __repr__(self) -> str:
        return str(self)

    def __call__(self, filename=ZGOUBI_INPUT_FILENAME) -> NoReturn:
        """
        Write the string representation of the object onto a file (Zgoubi input file).
        :param filename: the Zgoubi input file name (default: zgoubi.dat)
        :return: NoReturn
        """
        self.write(self, filename)

    def __len__(self) -> int:
        return len(self._line)

    def __iadd__(self, o) -> Input:
        self._line.append(o)
        return self

    def __getitem__(self, items) -> Input:
        if not isinstance(items, (tuple, list)):
            items = (items,)
        l, i = self._filter(items)
        items = tuple(map(lambda x: x.__name__ if isinstance(x, type) else x, items))
        return Input(name=f"{self._name}_filtered_by_{items}"
                     .replace(',', '_')
                     .replace(' ', '')
                     .replace("'", '')
                     .replace("(", '')
                     .replace(")", ''),
                     line=l
                     )

    def __getattr__(self, item):
        pass

    def __contains__(self, items) -> int:
        if not isinstance(items, tuple):
            items = (items,)
        l, i = self._filter(items)
        return len(l)

    def _filter(self, items) -> tuple:
        items = tuple(map(lambda x: getattr(commands, x) if isinstance(x, str) else x, items))
        return list(filter(lambda x: reduce(lambda u, v: u or v, [isinstance(x, i) for i in items]), self._line)), items

    def apply(self, f: Callable[[commands.Command], commands.Command]) -> None:
        self._line = list(map(f, self._line))

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
    def keywords(self) -> List[str]:
        return [e.KEYWORD for e in self._line]

    @property
    def line(self) -> Sequence[commands.Command]:
        return self._line

    @staticmethod
    def write(_: Input, filename=ZGOUBI_INPUT_FILENAME, mode='w') -> NoReturn:
        """
        Write a Zgoubi Input object to file.
        :param _: a Zgoubidoo Input object
        :param filename: the file name (default: zgoubi.dat)
        :param mode: the mode for the writer (default: 'w' - overwrite)
        :return: NoReturn
        """
        with open(filename, mode) as f:
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