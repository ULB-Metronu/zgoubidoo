"""
TODO
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping
import numpy as _np
import plotly.offline
import plotly.graph_objs as go
from zgoubidoo.vis import Artist
from ..commands import Plotable as _Plotable
from ..commands import Patchable as _Patchable
from ..commands import PolarMagnet as _PolarMagnet
from ..commands import CartesianMagnet as _CartesianMagnet
from ..commands import Drift as _Drift
from ..commands import Quadrupole as _Quadrupole
from ..commands import Sextupole as _Sextupole
from ..commands import Multipole as _Multipole
from ..commands import Bend as _Bend

if TYPE_CHECKING:
    from ..input import Input as _Input


class PlotlyArtist(Artist):
    """
    TODO
    """

    def __init__(self, config: Optional[Mapping] = None, **kwargs):
        """

        Args:
            config:
            **kwargs:
        """
        super().__init__(**kwargs)
        self._data = []
        self._config = config or {
            'showLink'      : False,
            'scrollZoom'    : True,
            'displayModeBar': False,
            'editable'      : False,
        }
        self._layout = {
            'xaxis': {
                'showgrid' : True,
                'linecolor': 'black',
                'linewidth': 1,
                'mirror'   : True,
            },
            'yaxis': {
                'linecolor': 'black',
                'linewidth': 1,
                'mirror'   : True,
            },
        }
        self._shapes = []

    def _init_plot(self):
        pass

    @property
    def fig(self):
        """Provides the plotly figure."""
        return {
            'data'  : self.data,
            'layout': self.layout,
        }

    @property
    def config(self):
        return self._config

    @property
    def data(self):
        return self._data

    @property
    def layout(self):
        self._layout['shapes'] = self._shapes
        return self._layout

    @property
    def shapes(self):
        return self._shapes

    def __iadd__(self, other):
        """Add a trace to the figure."""
        self._data.append(other)
        return self

    def add_secondary_axis(self, title: str = ''):
        self.layout['yaxis2'] = {
            'title'     : title,
            'titlefont' : dict(
                color='rgb(148, 103, 189)'
            ),
            'tickfont'  : dict(
                color='rgb(148, 103, 189)'
            ),
            'overlaying': 'y',
            'side'      : 'right',
        }

    def render(self):
        if len(self._data) == 0:
            self._data.append(go.Scatter(x=[0.0], y=[0.0]))
        plotly.offline.iplot(self.fig, config=self.config)

    def save(self, file: str, file_format: str = 'png'):
        plotly.io.write_image(self.fig, file=file, format=file_format)

    def save_html(self, file: str):
        return plotly.offline.plot(self.fig, config=self.config, auto_open=False, filename=file)

    def scatter(self, *args, **kwargs):
        """A proxy for plotly.graph_objs.Scatter ."""
        self._data.append(go.Scatter(*args, **kwargs))

    def scatter3d(self, *args, **kwargs):
        """A proxy for plotly.graph_objs.Scatter3d ."""
        self._data.append(go.Scatter3d(*args, **kwargs))

    def plot_cartouche(self,
                       beamline: _Input,
                       vertical_position: float = 1.2,
                       ):
        """

        Args:
            beamline:
            vertical_position:

        Returns:

        """
        self.shapes.append(
            {
                'type': 'line',
                'xref': 'paper',
                'yref': 'paper',
                'x0': 0,
                'y0': vertical_position,
                'x1': 1,
                'y1': vertical_position,
                'line': {
                    'color': 'rgb(150, 150, 150)',
                    'width': 2,
                },
            },
        )
        for e in beamline:
            if not isinstance(e, _Patchable) and not isinstance(e, _Plotable):
                continue
            if isinstance(e, (_Quadrupole, _Sextupole)):
                self.shapes.append(
                    {
                        'type': 'rect',
                        'xref': 'x',
                        'yref': 'paper',
                        'x0': e.entry_patched.x.m_as('m'),
                        'y0': vertical_position if e.B0.magnitude > 0 else vertical_position - 0.1,
                        'x1': e.exit.x.m_as('m'),
                        'y1': vertical_position + 0.1 if e.B0.magnitude > 0 else vertical_position,
                        'line': {
                            'width': 1,
                        },
                        'fillcolor': e.COLOR,
                    },
                )
            if isinstance(e, (_Multipole,)):
                self.shapes.append(
                    {
                        'type': 'rect',
                        'xref': 'x',
                        'yref': 'paper',
                        'x0': e.entry_patched.x.m_as('m'),
                        'y0': vertical_position - 0.05,
                        'x1': e.exit.x.m_as('m'),
                        'y1': vertical_position + 0.05,
                        'line': {
                            'width': 1,
                        },
                        'fillcolor': e.COLOR,
                    },
                )
            if isinstance(e, _Bend):
                path = f"M{e.entry_patched.x_},1.3 " \
                       f"H{e.exit.x_} " \
                       f"L{e.exit.x_ - 0.1 * e.length.m_as('m')},1.1 " \
                       f"H{e.exit.x_ - 0.9 * e.length.m_as('m')} " \
                       f"Z"
                self.shapes.append(
                    {
                        'type': 'path',
                        'xref': 'x',
                        'yref': 'paper',
                        'path': path,
                        'line': {
                            'width': 1,
                        },
                        'fillcolor': '#4169E1',
                    },
                )

    def plot_beamline(self,
                      beamline: _Input,
                      with_drifts: bool = False,
                      points_in_polar_paths: int = 20,
                      opacity: float = 0.5,
                      ) -> None:
        """
        Use a `ZgoubiPlot` artist to perform the rendering of the beamline with elements and tracks.

        The `Input` must be surveyed first so that all the placements are taken into account for the plotting.

        Args:
            beamline:
            with_drifts:
            points_in_polar_paths:
        """
        def add_svg_path(points):
            points = points.dot(_np.linalg.inv(e.entry_patched.get_rotation_matrix())) + _np.array([
                e.entry.x_, e.entry.y_, 0.0
            ])
            path = f"M{points[0, 0]},{points[0, 1]} "
            for p in points[1:]:
                path += f"L{p[0]},{p[1]} "
            path += "Z"
            try:
                if e.B2.magnitude > 0:
                    color = 'blue'
                else:
                    color = 'red'
            except AttributeError:
                color = e.COLOR
            self.shapes.append(
                {
                    'type': 'path',
                    'xref': 'x',
                    'yref': 'y',
                    'path': path,
                    'line': {
                        'width': 1,
                    },
                    'fillcolor': color,
                    'opacity': opacity,
                },
            )

        for e in beamline:
            if not isinstance(e, _Plotable):
                continue
            if not with_drifts and isinstance(e, _Drift):
                continue
            if isinstance(e, _PolarMagnet):
                r = e.RM.m_as('m')
                pts = []
                thetas = _np.linspace(0, e.AT.m_as('radian'), points_in_polar_paths)
                for theta in thetas:
                    pts.append([(r+0.1) * _np.sin(theta), -r + (r+0.1) * _np.cos(theta), 0.0])
                for theta in thetas[::-1]:
                    pts.append([(r+0.2) * _np.sin(theta), -r + (r+0.2) * _np.cos(theta), 0.0])
                add_svg_path(_np.array(pts))
                pts = []
                for theta in thetas:
                    pts.append([(r - 0.1) * _np.sin(theta), -r + (r - 0.1) * _np.cos(theta), 0.0])
                for theta in thetas[::-1]:
                    pts.append([(r - 0.2) * _np.sin(theta), -r + (r - 0.2) * _np.cos(theta), 0.0])
                add_svg_path(_np.array(pts))
            else:
                add_svg_path(_np.array([
                    [0.0, -e.APERTURE_LEFT.m_as('m') - 0.1, 0.0],
                    [0.0, -e.APERTURE_LEFT.m_as('m'), 0.0],
                    [e.length.m_as('m'), -e.APERTURE_LEFT.m_as('m'), 0.0],
                    [e.length.m_as('m'), -e.APERTURE_LEFT.m_as('m') - 0.1, 0.0],
                ]))
                add_svg_path(_np.array([
                    [0.0, e.APERTURE_LEFT.m_as('m'), 0.0],
                    [0.0, e.APERTURE_LEFT.m_as('m') + 0.1, 0.0],
                    [e.length.m_as('m'), e.APERTURE_LEFT.m_as('m') + 0.1, 0.0],
                    [e.length.m_as('m'), e.APERTURE_LEFT.m_as('m'), 0.0],
                ]))
