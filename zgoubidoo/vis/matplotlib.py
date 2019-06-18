"""Matplotlib plotting module for Zgoubidoo.

TODO
"""
from __future__ import annotations
import numpy as _np
import pandas as _pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from .. import ureg as _ureg
from .zgoubiplot import ZgoubiPlot
from ..units import _m, _cm, _degree, _radian
import zgoubidoo.commands


class ZgoubiMpl(ZgoubiPlot):
    """A matplotlib implementation of a `ZgoubiPlot` artist."""
    def __init__(self,
                 ax=None,
                 with_boxes: bool = True,
                 with_frames: bool = True,
                 with_centers: bool = False,
                 tracks_color: str = 'b',
                 **kwargs):
        """
        Args:
            param ax: the matplotlib ax used for plotting. If None it will be created with `init_plot` (kwargs are
            forwarded).
            with_boxes: draw the body of each elements
            with_frames: draw the entry and exit frames of each elements
            with_centers: draw the center of each polar coordinate elements
            tracks_color: color for the plotting of tracks
            kwargs: forwarded to `ZgoubiPlot` and to `init_plot`.
        """
        super().__init__(with_boxes, with_frames, **kwargs)
        self._with_centers = with_centers
        self._tracks_color = tracks_color
        if ax is None:
            self.init_plot(**kwargs)
        else:
            self._ax = ax
        self._ax2 = self._ax.twinx()
        self._ax2.set_ylim([0, 1])
        self._ax2.axis('off')

    @property
    def tracks_color(self):
        """
        The color for the rendering of the tracks.

        Returns:
            color as a string
        """
        return self._tracks_color

    @tracks_color.setter
    def tracks_color(self, color: str):
        self._tracks_color = color

    @property
    def ax(self):
        """Current Matplotlib ax.

        Returns:
            the Matplotlib ax.
        """
        return self._ax

    @property
    def ax2(self):
        """

        Returns:

        """
        return self._ax2

    @property
    def figure(self):
        """Current Matplotlib figure.

        Returns:
            the Matplotlib figure.
        """
        return self._fig

    @ax.setter
    def ax(self, ax):
        self._ax = ax

    def init_plot(self, figsize=(12, 8), subplots=111):
        """
        Initialize the Matplotlib figure and ax.

        Args:
            subplots: number of subplots
            figsize: figure size
        """
        self._fig = plt.figure(figsize=figsize)
        self._ax = self._fig.add_subplot(subplots)

    def plot(self, *args, **kwargs):
        """Proxy for matplotlib.pyplot.plot

        Same as `matplotlib.pyplot.plot`, forwards all arguments.
        """
        self._ax.plot(*args, **kwargs)

    def polarmagnet(self, magnet: zgoubidoo.commands.PolarMagnet):
        """Rendering of magnets in polar coordinates.

        Plot magnets in polar coordinates using wedges.

        Args:
            magnet: the magnet to be rendered.
        """

        def do_frame() -> None:
            """Plot the coordinates of each frames of the magnet."""
            self.plot(_cm(magnet.entry.x), _cm(magnet.entry.y), 'gv', ms=5)
            self.plot(_cm(magnet.entry_patched.x), _cm(magnet.entry_patched.y), 'bs', ms=5)
            self.plot(_cm(magnet.exit.x), _cm(magnet.exit.y), 'k^', ms=5)
            self.plot(_cm(magnet.exit_patched.x), _cm(magnet.exit_patched.y), 'rv', ms=10)
            if self._with_centers:
                self.plot(_cm(magnet.center.x), _cm(magnet.center.y), 'r.', ms=5)

        def do_box() -> None:
            """Plot the core of the magnet."""
            if _np.cos(_radian(magnet.entry_patched.tz)) > 0:
                theta1 = 90 - _degree(magnet.entry_patched.tx + magnet.angular_opening)
                theta2 = 90 - _degree(magnet.entry_patched.tx)
                theta3 = 90 - _degree(magnet.entry_patched.tx + magnet.reference_angle)
                theta4 = 90 - _degree(magnet.entry_patched.tx + magnet.reference_angle - magnet.entrance_efb)
                theta5 = 90 - _degree(magnet.entry_patched.tx + magnet.reference_angle - magnet.exit_efb)
            else:
                theta1 = -90 - _degree(magnet.entry_patched.tx)
                theta2 = -90 - _degree(magnet.entry_patched.tx - magnet.angular_opening)
                theta3 = -90 - _degree(magnet.entry_patched.tx - magnet.reference_angle)
                theta4 = -90 - _degree(magnet.entry_patched.tx - magnet.reference_angle + magnet.exit_efb)
                theta5 = -90 - _degree(magnet.entry_patched.tx - magnet.reference_angle + magnet.entrance_efb)

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

    def cartesianmagnet(self, magnet: zgoubidoo.commands.CartesianMagnet, apertures: bool = False):
        """Rendering of magnets in cartesian coordinates.

        Plot magnets in cartesian coordinates using rectangles.

        Args:
            magnet: the magnet to be rendered.
            apertures:
        """

        def do_frame():
            """Plot the coordinates of each frames of the magnet."""
            self.plot(_m(magnet.entry.x), _m(magnet.entry.y), 'gv', ms=5)
            self.plot(_m(magnet.entry_patched.x), _m(magnet.entry_patched.y), 'bs', ms=5)
            self.plot(_m(magnet.exit.x), _m(magnet.exit.y), 'k^', ms=5)
            self.plot(_m(magnet.exit_patched.x), _m(magnet.exit_patched.y), 'r>', ms=5)

        def do_box():
            """Plot the core of the magnet."""
            angle = -magnet.entry_patched.tx
            tr = transforms.Affine2D().rotate_deg_around(
                _m(magnet.entry_patched.x),
                _m(magnet.entry_patched.y),
                _degree(angle)
            ) + self._ax.transData
            self._ax.add_patch(
                patches.Rectangle(
                    (
                        _m(magnet.entry_patched.x),
                        _m(magnet.entry_patched.y - magnet.WIDTH / 2)
                    ),
                    _np.linalg.norm(
                        _np.array([
                            _m(magnet.exit.x - magnet.entry_patched.x),
                            _m(magnet.exit.y - magnet.entry_patched.y)
                        ]).astype(float)
                    ),
                    _m(magnet.WIDTH),
                    alpha=0.2,
                    facecolor=self._palette.get(magnet.COLOR, 'gray'),
                    edgecolor=self._palette.get(magnet.COLOR, 'gray'),
                    linewidth=2,
                    transform=tr,
                )
            )

        def do_apertures():
            """Plot the core of the magnet."""
            angle = -magnet.entry_patched.tx
            tr = transforms.Affine2D().rotate_deg_around(
                _m(magnet.entry_patched.x),
                _m(magnet.entry_patched.y),
                _degree(angle)
            ) + self._ax.transData
            self._ax.add_patch(
                patches.Rectangle(
                    (
                        _m(magnet.entry_patched.x),
                        _m(magnet.entry_patched.y - magnet.APERTURE_RIGHT - magnet.WIDTH)
                    ),
                    _np.linalg.norm(
                        _np.array([
                            _m(magnet.exit.x - magnet.entry_patched.x),
                            _m(magnet.exit.y - magnet.entry_patched.y)
                        ]).astype(float)
                    ),
                    _m(magnet.WIDTH),
                    alpha=0.2,
                    facecolor=self._palette.get(magnet.COLOR, 'gray'),
                    edgecolor=self._palette.get(magnet.COLOR, 'gray'),
                    linewidth=2,
                    transform=tr,
                )
            )
            self._ax.add_patch(
                patches.Rectangle(
                    (
                        _m(magnet.entry_patched.x),
                        _m(magnet.entry_patched.y + 1 * magnet.APERTURE_LEFT)
                    ),
                    _np.linalg.norm(
                        _np.array([
                            _m(magnet.exit.x - magnet.entry_patched.x),
                            _m(magnet.exit.y - magnet.entry_patched.y)
                        ]).astype(float)
                    ),
                    _m(magnet.WIDTH),
                    alpha=0.2,
                    facecolor=self._palette.get(magnet.COLOR, 'gray'),
                    edgecolor=self._palette.get(magnet.COLOR, 'gray'),
                    linewidth=2,
                    transform=tr,
                )
            )

        if self._with_boxes and not apertures:
            do_box()
        if self._with_boxes and apertures:
            do_apertures()
        if self._with_frames:
            do_frame()

    def cartouche_drift(self, s_location, magnet: zgoubidoo.commands.CartesianMagnet):
        """

        Args:
            s_location:
            magnet:

        Returns:

        """
        offset = 1.1
        self._ax2.hlines(offset, _m(s_location), _m(s_location) + _m(magnet.length), clip_on=False)

    cartouche_fakedrift = cartouche_drift

    def cartouche_cartesianmagnet(self, s_location, magnet: zgoubidoo.commands.CartesianMagnet):
        """

        Args:
            s_location:
            magnet:

        Returns:

        """
        offset = 1.1
        self._ax2.hlines(offset, _m(s_location), _m(s_location) + _m(magnet.length), clip_on=False)
        self._ax2.add_patch(
            patches.Rectangle(
                (
                    _m(s_location),
                    offset - 0.05,
                ),
                _m(magnet.length),
                0.1,
                alpha=1.0,
                facecolor=self._palette.get(magnet.COLOR, 'gray'),
                edgecolor=self._palette.get(magnet.COLOR, 'gray'),
                linewidth=0,
                clip_on=False,
            )
        )

    def cartouche_quadrupole(self, s_location, magnet: zgoubidoo.commands.CartesianMagnet):
        """

        Args:
            s_location:
            magnet:

        Returns:

        """
        offset = 1.1
        if magnet.B0.m > 0:
            baseline = -0.05
        else:
            baseline = 0.0
        self._ax2.hlines(offset, _m(s_location), _m(s_location) + _m(magnet.length), clip_on=False)
        self._ax2.add_patch(
            patches.Rectangle(
                (
                    _m(s_location),
                    offset + baseline,
                ),
                _m(magnet.length),
                0.05,
                alpha=1.0,
                facecolor=self._palette.get(magnet.COLOR, 'gray'),
                edgecolor=self._palette.get(magnet.COLOR, 'gray'),
                linewidth=0,
                clip_on=False,
            )
        )

    def cartouche_solenoid(self, s_location, magnet: zgoubidoo.commands.CartesianMagnet):
        """

        Args:
            s_location:
            magnet:

        Returns:

        """
        offset = 1.1
        self._ax2.hlines(offset, _m(s_location), _m(s_location) + _m(magnet.length), clip_on=False)
        self._ax2.add_patch(
            patches.Rectangle(
                (
                    _m(s_location),
                    offset - 0.075,
                ),
                _m(magnet.length),
                0.15,
                alpha=0.5,
                facecolor=self._palette.get(magnet.COLOR, 'gray'),
                edgecolor=self._palette.get(magnet.COLOR, 'gray'),
                linewidth=0,
                clip_on=False,
                zorder=10,
            ),
        )

    def cartouche_cavite(self, s_location, cavite: zgoubidoo.commands.Cavite):
        """

        Args:
            s_location:
            cavite:

        Returns:

        """
        offset = 1.1
        self._ax2.hlines(offset, _m(s_location), _m(s_location) + _m(cavite.length), clip_on=False)
        self._ax2.add_patch(
            patches.Rectangle(
                (
                    _m(s_location),
                    offset - 0.05,
                ),
                1,
                0.1,
                alpha=1.0,
                facecolor=self._palette.get(cavite.COLOR, 'gray'),
                edgecolor=self._palette.get(cavite.COLOR, 'gray'),
                linewidth=0,
                clip_on=False,
            )
        )

    def tracks_cartesianmagnet(self, magnet: zgoubidoo.commands.CartesianMagnet, tracks: _pd.DataFrame):
        """Plot tracks for a cartesian magnet.

        Args:
            magnet: the magnet to which the tracks are attached
            tracks: a dataframe containing the tracks
        """
        self.plot(tracks['XG'],
                  tracks['YG'],
                  '.',
                  markeredgecolor=self._tracks_color,
                  markerfacecolor=self._tracks_color,
                  ms=1
                  )

    def tracks_polarmagnet(self, magnet: zgoubidoo.commands.PolarMagnet, tracks):
        """Plot tracks for a polar magnet.

        Args:
            magnet: the magnet to which the tracks are attached
            tracks: a dataframe containing the tracks
        """
        x = 100 * tracks['X'].values  # Polar angle
        y = 100 * tracks['Y-DY'].values
        if _np.cos(_radian(magnet.entry.tz)) > 0:
            angle = _radian(90 * _ureg.degree - magnet.center.tx) - x
        else:
            angle = _radian(-90 * _ureg.degree - magnet.center.tx) + x
        tracks_x = _cm(magnet.center.x) + y * _np.cos(angle)
        tracks_y = _cm(magnet.center.y) + y * _np.sin(angle)
        self.plot(tracks_x,
                  tracks_y,
                  '.',
                  markeredgecolor=self._tracks_color,
                  markerfacecolor=self._tracks_color,
                  ms=1
                  )
