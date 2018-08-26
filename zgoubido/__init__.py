__version__ = "2018.1"

from . import commands


def build(name='beamline', line=[], filename='zgoubi.dat', debug=False):
    _ = ''.join(map(lambda x: str(x), [name]+line))
    if debug:
        print(_)
    with open(filename, 'w') as f:
        f.write(_)
