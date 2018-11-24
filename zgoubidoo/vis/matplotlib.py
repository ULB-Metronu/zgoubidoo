from __future__ import annotations
from typing import NoReturn
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from .. import ureg as _ureg
from .zgoubiplot import ZgoubiPlot
from ..units import _cm, _degree, _radian
from ..frame import Frame
import zgoubidoo.commands


class ZgoubiMpl(ZgoubiPlot):
    """
    A matplotlib implementation of a `ZgoubiPlot` artist.
    """
    def __init__(self,
                 ax=None,
                 with_boxes: bool=True,
                 with_frames: bool=True,
                 with_centers: bool=False,
                 tracks_color: str='b',
                 **kwargs):
        """

        :param ax: the matplotlib ax used for plotting. If None it will be created with `init_plot`
        (kwargs are forwarded).
        :param with_boxes: draw the body of each elements
        :param with_frames: draw the entry and exit frames of each elements
        :param with_centers: draw the center of each polar coordinate elements
        :param tracks_color: color for the plotting of tracks
        :param kwargs: forwarded to `ZgoubiPlot` and to `init_plot`.
        """
        super().__init__(with_boxes, with_frames, **kwargs)
        self._with_centers = with_centers
        self._tracks_color = tracks_color
        if ax is None:
            self.init_plot(**kwargs)
        else:
            self._ax = ax

    def init_plot(self, subplots=111) -> matplotlib.figure.Figure:
        fig = plt.figure()
        self._ax = fig.add_subplot(subplots)
        return fig

    def plot(self, *args, **kwargs) -> NoReturn:
        """
        Same as `matplotlib.pyplot.plot`, forwards all arguments.
        :param args: see `matplotlib.pyplot.plot`
        :param kwargs: see `matplotlib.pyplot.plot`
        :return: NoReturn.
        """
        self._ax.plot(*args, **kwargs)

    def polarmagnet(self, magnet: zgoubidoo.commands.PolarMagnet) -> NoReturn:
        """

        :param magnet:
        :return:
        """

        def do_frame() -> None:
            self.plot(_cm(magnet.entry.x), _cm(magnet.entry.y), 'gv', ms=5)
            self.plot(_cm(magnet.entry_patched.x), _cm(magnet.entry_patched.y), 'bs', ms=5)
            self.plot(_cm(magnet.exit.x), _cm(magnet.exit.y), 'k^', ms=5)
            self.plot(_cm(magnet.exit_patched.x), _cm(magnet.exit_patched.y), 'rv', ms=10)
            if self._with_centers:
                self.plot(_cm(magnet.center.x), _cm(magnet.center.y), 'r.', ms=5)

        def do_box() -> None:
            if np.cos(_radian(magnet.entry_patched.tz)) > 0:
                theta1 = 90 - _degree(magnet.entry_patched.tx + magnet.angular_opening)
                theta2 = 90 - _degree(magnet.entry_patched.tx)
                theta3 = 90 - _degree(magnet.entry_patched.tx + magnet.reference_angle)
                theta4 = 90 - _degree(magnet.entry_patched.tx + magnet.reference_angle - magnet.entrance_efb)
                theta5 = 90 - _degree(magnet.entry_patched.tx + magnet.reference_angle - magnet.exit_efb)
            else:
                theta1 = -90 - _degree(magnet.entry_patched.tx)
                theta2 = -90 - _degree(magnet.entry_patched.tx - magnet.angular_opening)
                theta3 = -90 - _degree(magnet.entry_patched.tx - magnet.reference_angle)
                theta4 = -90 - _degree(magnet.entry_patched.tx - magnet.reference_angle + magnet.entrance_efb)
                theta5 = -90 - _degree(magnet.entry_patched.tx - magnet.reference_angle + magnet.exit_efb)
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
            self._ax.add_patch(
                patches.Wedge(
                    (
                        _cm(magnet.center.x),
                        _cm(magnet.center.y),
                    ),
                    _cm(magnet.radius + magnet.WIDTH / 2.0),
                    theta1,
                    theta2,
                    width=_cm(magnet.WIDTH / 2.0),
                    alpha=0.2,
                    facecolor=self._palette.get(magnet.COLOR, 'gray'),
                    edgecolor=self._palette.get(magnet.COLOR, 'gray'),
                    linewidth=2,
                )
            )
            self._ax.add_patch(
                patches.Wedge(
                    (
                        _cm(magnet.center.x),
                        _cm(magnet.center.y),
                    ),
                    _cm(magnet.radius + magnet.WIDTH / 2.0),
                    theta5,
                    theta4,
                    width=_cm(magnet.WIDTH),
                    alpha=0.2,
                    facecolor=self._palette.get(magnet.COLOR, 'gray'),
                    edgecolor=self._palette.get(magnet.COLOR, 'gray'),
                    linewidth=2,
                )
            )
            self._ax.add_patch(
                patches.Wedge(
                    (
                        _cm(magnet.center.x),
                        _cm(magnet.center.y),
                    ),
                    _cm(magnet.radius + magnet.WIDTH / 2.0),
                    theta3,
                    theta3,
                    width=_cm(magnet.WIDTH),
                    alpha=0.2,
                    facecolor='k',
                    edgecolor='k',
                    linewidth=4,
                )
            )
        if self._with_boxes:
            do_box()
        if self._with_frames:
            do_frame()

    def cartesianmagnet(self, magnet: zgoubidoo.commands.CartesianMagnet) -> NoReturn:

        def do_frame():
            self.plot(_cm(magnet.entry.x), _cm(magnet.entry.y), 'gv', ms=5)
            self.plot(_cm(magnet.entry_patched.x), _cm(magnet.entry_patched.y), 'bs', ms=5)
            self.plot(_cm(magnet.exit.x), _cm(magnet.exit.y), 'k^', ms=5)
            self.plot(_cm(magnet.exit_patched.x), _cm(magnet.exit_patched.y), 'r>', ms=5)

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

    def tracks_cartesianmagnet(self, magnet: zgoubidoo.commands.CartesianMagnet, tracks) -> NoReturn:
        v = 100 * tracks[['X', 'Y-DY', 'Z']].values
        m = Frame(magnet.entry_patched).rotate_z(2 * magnet.entry_patched.tx).get_rotation_matrix()
        tmp = np.dot(v, m)
        tracks_x = _cm(magnet.entry_patched.x) + tmp[:, 0]
        tracks_y = _cm(magnet.entry_patched.y) + tmp[:, 1]
        self.plot(tracks_x,
                  tracks_y,
                  '.',
                  markeredgecolor=self._tracks_color,
                  markerfacecolor=self._tracks_color,
                  ms=1
                  )

    def tracks_polarmagnet(self, magnet: zgoubidoo.commands.PolarMagnet, tracks) -> NoReturn:
        x = 100 * tracks['X'].values  # Polar angle
        y = 100 * tracks['Y-DY'].values
        if np.cos(_radian(magnet.entry.tz)) > 0:
            angle = _radian(90 * _ureg.degree - magnet.center.tx) - x
        else:
            angle = _radian(-90 * _ureg.degree - magnet.center.tx) + x
        tracks_x = _cm(magnet.center.x) + y * np.cos(angle)
        tracks_y = _cm(magnet.center.y) + y * np.sin(angle)
        self.plot(tracks_x,
                  tracks_y,
                  '.c',
                  markeredgecolor=self._tracks_color,
                  markerfacecolor=self._tracks_color,
                  ms=1
                  )
