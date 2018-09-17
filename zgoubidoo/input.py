from typing import Callable
from .commands import Command


class Input:
    """Zgoubi input data."""

    def __init__(self, name: str='beamline', line=None):
        self._name = name
        self._line = list(line or [])

    def __str__(self):
        return self.build(self._name, self._line)

    def __repr__(self) -> str:
        return str(self)

    def __call__(self, filename='zgoubi.dat'):
        self.write(self, filename)

    def __len__(self):
        return len(self._line)

    def __iadd__(self, o):
        self._line.append(o)
        return self

    def __getitem__(self, item):
        l, i = self._filter(item)
        return Input(name=f"{self._name}_filtered_by_{i}"
                     .replace(',', '_')
                     .replace(' ', '')
                     .replace("'", '')
                     .replace("(", '')
                     .replace(")", ''),
                     line=l
                     )

    def __getattr__(self, item):
        pass

    def __contains__(self, item):
        l, i = self._filter(item)
        return len(l)

    def _filter(self, item):
        if not isinstance(item, tuple):
            item = (item,)
        item = tuple(map(lambda x: x.KEYWORD if isinstance(x, MetaCommand) else x, item))
        return list(filter(lambda x: x.KEYWORD in item, self._line)), item

    def apply(self, f: Callable[[Command],Command]):
        self._line = list(map(f, self._line))

    @property
    def line(self):
        return self._line

    @staticmethod
    def write(_, filename='zgoubi.dat'):
        with open(filename, 'w') as f:
            f.write(str(_))

    @staticmethod
    def build(name='beamline', line=None):
        if len(line) == 0 or not isinstance(line[-1], End):
            line.append(End())
        return ''.join(map(str, [name] + (line or [])))
