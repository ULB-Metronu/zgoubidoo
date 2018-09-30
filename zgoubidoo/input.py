from functools import reduce
from typing import Callable, List, Sequence, Optional
from . import commands


class Input:
    """Zgoubi input data."""

    def __init__(self, name: str='beamline', line: Sequence[commands.Command]=None):
        self._name: str = name
        if line is None:
            line = []
        self._line: List[commands.Command] = line

    def __str__(self) -> str:
        return self.build(self._name, self._line)

    def __repr__(self) -> str:
        return str(self)

    def __call__(self, filename='zgoubi.dat') -> None:
        self.write(self, filename)

    def __len__(self) -> int:
        return len(self._line)

    def __iadd__(self, o):
        self._line.append(o)
        return self

    def __getitem__(self, items):
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

    def __contains__(self, items):
        if not isinstance(items, tuple):
            items = (items,)
        l, i = self._filter(items)
        return len(l)

    def _filter(self, items) -> tuple:
        items = tuple(map(lambda x: getattr(commands, x) if isinstance(x, str) else x, items))
        return list(filter(lambda x: reduce(lambda u, v: u or v, [isinstance(x, i) for i in items]), self._line)), items

    def apply(self, f: Callable[[commands.Command], commands.Command]) -> None:
        self._line = list(map(f, self._line))

    @property
    def labels(self) -> list:
        return [e.LABEL1 for e in self._line]

    @property
    def labels1(self) -> list:
        return self.labels

    @property
    def labels2(self) -> list:
        return [e.LABEL2 for e in self._line]

    @property
    def keywords(self) -> list:
        return [e.KEYWORD for e in self._line]

    @property
    def line(self) -> Sequence[commands.Command]:
        return self._line

    @staticmethod
    def write(_, filename='zgoubi.dat') -> None:
        with open(filename, 'w') as f:
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
