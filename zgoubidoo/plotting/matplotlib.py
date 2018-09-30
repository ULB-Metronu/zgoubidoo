import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from .zgoubiplot import ZgoubiPlot
from ..units import _cm, _degree, _radian


class ZgoubiMpl(ZgoubiPlot):
    def __init__(self, ax=None, with_boxes: bool=True, with_frames: bool=True, with_centers: bool=False, **kwargs):
        super().__init__(with_boxes, with_frames, **kwargs)
        self._with_centers = with_centers
        if ax is None:
            self._init_plot()
        else:
            self._ax = ax

    def _init_plot(self):
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot(111)

    def plot(self, *args, **kwargs) -> None:
        self._ax.plot(*args, **kwargs)

    def polarmagnet(self, magnet) -> None:

        def do_frame() -> None:
            self.plot(_cm(magnet.entry.x), _cm(magnet.entry.y), 'gv', ms=5)
            self.plot(_cm(magnet.entry_patched.x), _cm(magnet.entry_patched.y), 'bs', ms=2)
            self.plot(_cm(magnet.exit.x), _cm(magnet.exit.y), 'k^', ms=5)
            if self._with_centers:
                self.plot(_cm(magnet.center.x), _cm(magnet.center.y), 'r.', ms=5)

        def do_box() -> None:
            if np.cos(_radian(magnet.entry.tz)) > 0:
                theta1 = 90 - _degree(magnet.entry.tx + magnet.angular_opening)
                theta2 = 90 - _degree(magnet.entry.tx)
            else:
                theta1 = -90 - _degree(magnet.entry.tx)
                theta2 = -90 - _degree(magnet.entry.tx - magnet.angular_opening)
            self._ax.add_patch(
                patches.Wedge(
                    (
                        _cm(magnet.center.x),
                        _cm(magnet.center.y),
                    ),
                    _cm(magnet.radius + magnet.WIDTH / 2.0),
                    theta1,
                    theta2,
                    width=_cm(magnet.WIDTH),
                    alpha=0.2,
                    facecolor=self._palette.get(magnet.COLOR, 'gray'),
                    edgecolor=self._palette.get(magnet.COLOR, 'gray'),
                    linewidth=2,
                )
            )

        if self._with_boxes:
            do_box()
        if self._with_frames:
            do_frame()

    def cartesianmagnet(self, magnet) -> None:

        def do_frame():
            self.plot(_cm(magnet.entry_patched.x), _cm(magnet.entry_patched.y), 'gv', ms=5)
            self.plot(_cm(magnet.entry_patched.x), _cm(magnet.entry_patched.y), 'bs', ms=2)
            self.plot(_cm(magnet.exit.x), _cm(magnet.exit.y), 'k^', ms=5)

        def do_box():
            angle = -magnet.entry_patched.tx
            tr = transforms.Affine2D().rotate_deg_around(
                _cm(magnet.entry_patched.x),
                _cm(magnet.entry_patched.y),
                _degree(angle)
            ) + self._ax.transData
            self._ax.add_patch(
                patches.Rectangle(
                    (
                        _cm(magnet.entry_patched.x),
                        _cm(magnet.entry_patched.y - magnet.WIDTH / 2)
                    ),
                    np.linalg.norm(
                        np.array([
                            _cm(magnet.exit.x - magnet.entry_patched.x),
                            _cm(magnet.exit.y - magnet.entry_patched.y)
                        ]).astype(float)
                    ),
                    _cm(magnet.WIDTH),
                    alpha=0.2,
                    facecolor=self._palette.get(magnet.COLOR, 'gray'),
                    edgecolor=self._palette.get(magnet.COLOR, 'gray'),
                    linewidth=2,
                    transform=tr,
                )
            )

        if self._with_boxes:
            do_box()
        if self._with_frames:
            do_frame()

    def tracks_cartesianmagnet(self, magnet, tracks) -> None:
        x = tracks['X'].values
        y = 100 * tracks['Y-DY'].values
        angle = - np.radians(magnet.entry_patched.tx)
        if np.sign(np.cos(magnet.entry.tz)) > 0:
            pass
        else:
            y *= -1
        s = np.sin(angle)
        c = np.cos(angle)
        xx = c * x - s * y
        yy = s * x + c * y
        tracks_x = _cm(magnet.entry_patched.x) + xx
        tracks_y = _cm(magnet.entry_patched.y) + yy
        self.plot(tracks_x, tracks_y, 'b.', ms=1)

    def tracks_polarmagnet(self, magnet, tracks) -> None:
        x = tracks['X'].values  # Polar angle
        y = 100 * tracks['Y-DY'].values
        if np.sign(np.cos(magnet.entry.tx)) > 0:
            rotation_angle = np.radians(90 - magnet.center.tz) - x
        else:
            rotation_angle = np.radians(-90 - magnet.center.tx) + x
        tracks_x = _cm(magnet.center.x) + y * np.cos(rotation_angle)
        tracks_y = _cm(magnet.center.y) + y * np.sin(rotation_angle)
        self.plot(tracks_x, tracks_y, '.', ms=2)
