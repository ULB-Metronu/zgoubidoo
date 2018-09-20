import numpy as np
from . import ureg, Q_


class Frame:
    X = 0
    Y = 1
    Z = 2
    TX = 3
    TY = 4
    TZ = 5

    def __init__(self, coords=None):
        self._coords = coords or [0 * ureg.cm,
                                  0 * ureg.cm,
                                  0 * ureg.cm,
                                  0 * ureg.degree,
                                  0 * ureg.degree,
                                  0 * ureg.degree
                                  ]

    def __getitem__(self, item):
        return self._coords[item]

    @property
    def coordinates(self):
        return self._coords

    @property
    def origin(self):
        return np.array(self._coords[:3])

    @property
    def angles(self):
        return np.array(self._coords[3:])

    @property
    def x(self):
        return self._coords[Frame.X]

    @x.setter
    def x(self, v):
        self._coords[Frame.X] = v

    @property
    def y(self):
        return self._coords[Frame.Y]

    @y.setter
    def y(self, v):
        self._coords[Frame.Y] = v

    @property
    def z(self):
        return self._coords[Frame.Z]

    @z.setter
    def z(self, v):
        self._coords[Frame.Z] = v

    @property
    def tx(self):
        return self._coords[Frame.TX]

    @tx.setter
    def tx(self, v):
        self._coords[Frame.TX] = v

    @property
    def ty(self):
        return self._coords[Frame.TY]

    @ty.setter
    def ty(self, v):
        self._coords[Frame.TY] = v

    @property
    def tz(self):
        return self._coords[Frame.TZ]

    @tz.setter
    def tz(self, v):
        self._coords[Frame.TZ] = v

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
