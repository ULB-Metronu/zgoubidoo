import numpy as np
import quaternion
from typing import Optional

_X = 0
_Y = 1
_Z = 2


class Frame:
    pass


class Frame:
    def __init__(self, parent: Optional[Frame] = None):
        self._p: Optional[Frame] = parent
        self._q: np.quaternion = np.quaternion(1, 0, 0, 0)
        self._o: np.ndarray = np.zeros(3)

    @property
    def parent(self) -> Optional[Frame]:
        return self._p

    @parent.setter
    def parent(self, _):
        raise Exception("Setting the parent is not allowed.")

    def get_quaternion(self, ref: Optional[Frame] = None):
        if self._p == ref:
            return self._q
        elif ref == self:
            return np.quaternion(1, 0, 0, 0)
        else:
            return self._q * self._p.get_quaternion(ref)

    quaternion = property(get_quaternion)
    q = property(get_quaternion)

    def get_origin(self, ref: Optional[Frame] = None):
        if self._p == ref:
            return self._o
        elif ref == self:
            return np.zeros(3)
        else:
            return self._p.get_origin(ref) + np.matmul(quaternion.as_rotation_matrix(self._p.get_quaternion(ref)),
                                                       self._o)

    o = property(get_origin)
    origin = property(get_origin)

    def get_x(self, ref: Optional[Frame] = None) -> float:
        return self.get_origin(ref)[_X]

    x = property(get_x)

    def get_y(self, ref: Optional[Frame] = None) -> float:
        return self.get_origin(ref)[_Y]

    y = property(get_y)

    def get_z(self, ref: Optional[Frame] = None) -> float:
        return self.get_origin(ref)[_Z]

    z = property(get_z)

    def get_angles(self, ref: Optional[Frame] = None) -> float:
        return quaternion.as_rotation_vector(self.get_quaternion(ref))

    def get_tx(self, ref: Optional[Frame] = None) -> float:
        return self.get_angles(ref)[_X]

    tx = property(get_tx)

    def get_ty(self, ref: Optional[Frame] = None) -> float:
        return self.get_angles(ref)[_Y]

    ty = property(get_ty)

    def get_tz(self, ref: Optional[Frame] = None) -> float:
        return self.get_angles(ref)[_Z]

    tz = property(get_tz)

    def rotate(self, angles):
        self._q *= quaternion.from_rotation_vector(angles)

    def rotate_x(self, angle):
        self.rotate([angle, 0, 0])

    def rotate_y(self, angle):
        self.rotate([0, angle, 0])

    def rotate_z(self, angle):
        self.rotate([0, 0, angle])

    def translate(self, offset: np.ndarray):
        self._o += offset
        print(self._o)

    def translate_x(self, offset: float):
        self._o[_X] += offset

    def translate_y(self, offset: float):
        self._o[_Y] += offset

    def translate_z(self, offset: float):
        self._o[_Z] += offset