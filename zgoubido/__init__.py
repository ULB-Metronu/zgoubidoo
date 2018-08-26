__version__ = "2018.1"

from . import commands


def build(name='beamline', line=[]):
    with open('zgoubi.dat', 'w') as f:
        f.write(''.join(map(lambda x: str(x), [name]+line)))
