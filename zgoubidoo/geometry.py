"""
TODO
"""
import numpy as _np

import numpy as np


class Intersections:
    def __init__(self, lines1, line2):
        self._lines1, self._line2 = self.validate_format(lines1, line2)
        self._u = None
        self._v = None
        self._w = None
        self._parallels = None
        self._coincidents = None
        self._s_intersections = None
        self._t_intersections = None

    def validate_format(self, lines1, line2):
        assert lines1.ndim > 1
        lines1 = np.atleast_3d(lines1)
        assert line2.shape == (2, 2)
        return lines1, line2

    @property
    def u(self):
        if self._u is None:
            self._u = self._lines1[:, 1] - self._lines1[:, 0]
        return self._u

    @property
    def v(self):
        if self._v is None:
            self._v = self._line2[1] - self._line2[0]
        return self._v

    @property
    def w(self):
        if self._w is None:
            self._w = self._lines1[:, 0] - self._line2[0]
        return self._w

    @property
    def parallels(self):
        if self._parallels is None:
            self._parallels = np.cross(self.u, self.v) == 0.0
        return self._parallels

    @property
    def not_parallels(self):
        return np.invert(self.parallels)

    @property
    def coincidents(self):
        if self._coincidents is None:
            self._coincidents = self.parallels & (np.cross(self.w, self.v) == 0.0)
        return self._coincidents

    @property
    def not_coincidents(self):
        return np.invert(self.coincidents)

    @property
    def parameters_at_intersections(self):
        if self._s_intersections is None:
            s_num = np.cross(-self.v, self.w)
            denom = np.ma.masked_values(np.cross(self.v, self.u), 0.0)
            self._s_intersections = s_num / denom
        if self._t_intersections is None:
            t_num = np.cross(self.u, self.w)
            self._t_intersections = -t_num / denom
        return (
            self._s_intersections,
            self._t_intersections
        )

    @property
    def intersects_ray_segment(self):
        s_intersections, t_intersections = self.parameters_at_intersections
        return ((s_intersections >= 0) & (t_intersections >= 0) & (t_intersections <= 1)).filled(False)

    @property
    def intersections(self):
        s_intersections, t_intersections = self.parameters_at_intersections
        return np.ma.masked_where(
            ~np.column_stack((self.intersects_ray_segment, self.intersects_ray_segment)),
            self._lines1[:, 0] + np.stack([self._s_intersections, self._s_intersections]).T * self._u
        )