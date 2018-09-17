import numpy as np

X = 0
Y = 1
Z = 2
TX = 3
TY = 4
TZ = 5


class Frame:

    def __init__(self, coords=None):
        self._coords = coords or np.zeros(6)

    @property
    def x(self):
        return self._coords[X]

    @x.setter
    def x(self, v):
        self._coords[X] = v

    @property
    def y(self):
        return self._coords[Y]

    @y.setter
    def y(self, v):
        self._coords[Y] = v

    @property
    def z(self):
        return self._coords[Z]

    @z.setter
    def z(self, v):
        self._coords[Z] = v

    @property
    def tx(self):
        return self._coords[TX]

    @tx.setter
    def tx(self, v):
        self._coords[TX] = v

    @property
    def ty(self):
        return self._coords[TY]

    @ty.setter
    def ty(self, v):
        self._coords[TY] = v

    @property
    def tz(self):
        return self._coords[TZ]

    @tz.setter
    def tz(self, v):
        self._coords[TZ] = v

    @property
    def roll(self):
        return self.tx

    @roll.setter
    def roll(self, v):
        self.tx = v

    @property
    def pitch(self):
        return self.ty

    @pitch.setter
    def pitch(self, v):
        self.ty = v

    @property
    def yaw(self):
        return self.tz

    @yaw.setter
    def yaw(self, v):
        self.tz = v
