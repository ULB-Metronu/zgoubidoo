class Input:
    """Zgoubi input data."""

    def __init__(self, name='beamline', line=None):
        self._name = name
        self._line = list(line or [])

    def __str__(self):
        return self.build(self._name, self._line)

    def __repr__(self):
        return str(self)

    def __call__(self, filename='zgoubi.dat'):
        self.write(self, filename)

    def __len__(self):
        return len(self._line)

    def __iadd__(self, o):
        self._line.append(o)
        return self

    @property
    def line(self):
        return list(self._line)

    @staticmethod
    def write(_, filename='zgoubi.dat'):
        with open(filename, 'w') as f:
            f.write(str(_))

    @staticmethod
    def build(name='beamline', line=None):
        return ''.join(map(str, [name] + (line or [])))
