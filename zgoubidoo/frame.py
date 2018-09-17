import numpy as np


class Frame:

    def __init__(self, coords):
        try:
            c =
        self._coords = np.zeros(6)

    def getter(self, i):
        return lambda _: self._coords[i]

    for i in ['X', 'Y', 'Z']:
        setattr(Frame, i.lower(), property(getter(getattr(Frame, i))))

