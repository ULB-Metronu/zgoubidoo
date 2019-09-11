"""
TODO
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping
import numpy as _np
import pandas as _pd
import plotly.offline
import plotly.graph_objs as go
from zgoubidoo.vis import Artist
from ..commands import Plotable as _Plotable
from ..commands import Patchable as _Patchable
from ..commands import PolarMagnet as _PolarMagnet
from ..commands import Drift as _Drift
from ..commands import Quadrupole as _Quadrupole
from ..commands import Sextupole as _Sextupole
from ..commands import Multipole as _Multipole
from ..commands import Bend as _Bend
from ..commands import Dipole as _Dipole

if TYPE_CHECKING:
    from ..input import Input as _Input


class PlotlyArtist(Artist):
    """
    TODO
    """

    def __init__(self, config: Optional[Mapping] = None, layout: Optional[Mapping] = None, **kwargs):
        """

        Args:
            config:
            **kwargs:
        """
        super().__init__(**kwargs)
        self._data = []
        self._config = config or {
            'showLink': False,
            'scrollZoom': True,
            'displayModeBar': False,
            'editable': False,
        }
        self._layout = layout or {
            'xaxis': {
                'showgrid': True,
                'linecolor': 'black',
                'linewidth': 1,
                'mirror': True,
            },
            'yaxis': {
                'linecolor': 'black',
                'linewidth': 1,
                'mirror': True,
                'exponentformat': 'power',
            },
        }
        self._shapes = []
        self._n_y_axis = len([ax for ax in self._layout.keys() if ax.startswith('yaxis')])

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

    def add_axis(self, title: str = '', axis: Optional[Mapping] = None):
        """

        Args:
            title:
            axis:

        Returns:

        """
        self._n_y_axis += 1
        self.layout[f"yaxis{self._n_y_axis if self._n_y_axis > 1 else ''}"] = axis or {
            'title': title,
            'titlefont': dict(
                color='black'
            ),
            'tickfont': dict(
                color='black'
            ),
            'linewidth': 1,
            'exponentformat': 'power',
            'overlaying': 'y',
            'side': 'left',
        }

    def add_secondary_axis(self, title: str = '', axis: Optional[Mapping] = None):
        """

        Args:
            title:
            axis:

        Returns:

        """
        self._n_y_axis += 1
        self.layout[f"yaxis{self._n_y_axis}"] = axis or {
            'title': title,
            'titlefont': dict(
                color='black'
            ),
            'tickfont': dict(
                color='black'
            ),
            'linewidth': 1,
            'exponentformat': 'power',
            'overlaying': 'y',
            'side': 'right',
        }

    def render(self):
        if len(self._data) == 0:
            self._data.append(go.Scatter(x=[0.0], y=[0.0]))
        plotly.offline.iplot(self.fig, config=self.config)

    def save(self, file: str, file_format: str = 'png'):
        plotly.io.write_image(self.fig, file=file, format=file_format)

    def save_html(self, file: str):
        return plotly.offline.plot(self.fig, config=self.config, auto_open=False, filename=file)

    def histogram(self, *args, **kwargs):
        """A proxy for plotly.graph_objs.Histogram"""
        self._data.append(go.Histogram(*args, **kwargs))

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
                        'x0': e.entry_s.m_as('m'),
                        'y0': vertical_position if e.B0.magnitude > 0 else vertical_position - 0.1,
                        'x1': e.exit_s.m_as('m'),
                        'y1': vertical_position + 0.1 if e.B0.magnitude > 0 else vertical_position,
                        'line': {
                            'width': 0,
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
                        'x0': e.entry_s.m_as('m'),
                        'y0': vertical_position - 0.05,
                        'x1': e.exit_s.m_as('m'),
                        'y1': vertical_position + 0.05,
                        'line': {
                            'width': 0,
                        },
                        'fillcolor': e.COLOR,
                    },
                )
            if isinstance(e, (_Bend, _Dipole)):
                length = (e.exit_s - e.entry_s).m_as('m')
                if e.entry_patched.get_rotation_vector()[0] >= 0.0:
                    path = f"M{e.entry_s.m_as('m')},{vertical_position + 0.1} " \
                           f"H{e.exit_s.m_as('m')} " \
                           f"L{e.exit_s.m_as('m') - 0.15 * length},{vertical_position - 0.1} " \
                           f"H{e.exit_s.m_as('m') - 0.85 * length} " \
                           f"Z"
                else:
                    path = f"M{e.entry_s.m_as('m') + 0.15 * e.length.m_as('m')},{vertical_position + 0.1} " \
                           f"H{e.exit_s.m_as('m') - 0.15 * e.length.m_as('m')} " \
                           f"L{e.exit_s.m_as('m')},{vertical_position - 0.1} " \
                           f"H{e.entry_s.m_as('m')} " \
                           f"Z"
                self.shapes.append(
                    {
                        'type': 'path',
                        'xref': 'x',
                        'yref': 'paper',
                        'path': path,
                        'line': {
                            'width': 0,
                        },
                        'fillcolor': e.COLOR,
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
            opacity:
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

    @classmethod
    def plot_twiss(cls,
                   beamline,
                   twiss: _pd.DataFrame,
                   twiss_madx: Optional[_pd.DataFrame],
                   beta: bool = True,
                   dispersion: bool = True,
                   dispersion_prime: bool = False,
                   alpha: bool = False,
                   mu: bool = False,
                   ):
        """

        Args:
            beamline:
            twiss:
            twiss_madx:
            beta:
            dispersion:
            dispersion_prime:
            alpha:
            mu:

        Returns:

        """

        artist = cls(layout={
            'xaxis': {'title': 'S (m)',
                      'mirror': True,
                      'linecolor': 'black',
                      'linewidth': 1
                      },
            'legend': {
                'bordercolor': '#888',
                'borderwidth': 1,
                'xanchor': 'right',
                'x': 0.98,
                'yanchor': 'top',
                'y': 0.98
            },
        })

        if beta:
            artist.add_axis(axis={
                'title': 'Beta function (m)',
                'linecolor': 'black',
                'linewidth': 1,
                'exponentformat': 'power',
            })
            artist.scatter(
                x=twiss['S'],
                y=twiss['BETA11'],
                line={'width': 2, 'color': 'blue'},
                name='BETA11',
                mode='lines',
            )

            artist.scatter(
                x=twiss['S'],
                y=twiss['BETA22'],
                line={'width': 2, 'color': 'FireBrick'},
                name='BETA22',
                mode='lines',
            )

            if twiss_madx is not None:
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['BETX'],
                    marker={'color': 'blue', 'symbol': 'cross-thin', 'size': 5, 'line': {'width': 1, 'color': 'blue'}},
                    mode='markers',
                    showlegend=False,
                )
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['BETY'],
                    marker={'color': 'FireBrick', 'symbol': 'cross-thin', 'size': 5,
                            'line': {'width': 1, 'color': 'FireBrick'}},
                    mode='markers',
                    showlegend=False
                )

        if alpha:
            artist.add_axis(axis={
                'title': 'Alpha function',
                'linecolor': 'black',
                'linewidth': 1,
                'exponentformat': 'power',
            })
            artist.scatter(
                x=twiss['S'],
                y=twiss['ALPHA11'],
                line={'width': 2, 'color': 'blue'},
                name='ALPHA11',
                mode='lines',
            )

            artist.scatter(
                x=twiss['S'],
                y=twiss['ALPHA22'],
                line={'width': 2, 'color': 'FireBrick'},
                name='ALPHA22',
                mode='lines',
            )

            if twiss_madx is not None:
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['ALFX'],
                    marker={'color': 'blue', 'symbol': 'cross-thin', 'size': 5, 'line': {'width': 1, 'color': 'blue'}},
                    mode='markers',
                    showlegend=False,
                )
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['ALFY'],
                    marker={'color': 'FireBrick', 'symbol': 'cross-thin', 'size': 5,
                            'line': {'width': 1, 'color': 'FireBrick'}},
                    mode='markers',
                    showlegend=False
                )

        if dispersion:
            artist.add_secondary_axis(title='Dispersion (m)')

            artist.scatter(
                x=twiss['S'],
                y=twiss['DISP1'],
                line={'width': 2, 'color': 'green', 'dash': 'dashdot'},
                name='DISP1',
                mode='lines',
                yaxis='y2',
            )

            artist.scatter(
                x=twiss['S'],
                y=twiss['DISP3'],
                line={'width': 1, 'color': 'magenta', 'dash': 'dashdot'},
                name='DISP3',
                mode='lines',
                yaxis='y2',
            )

            if twiss_madx is not None:
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['DX'],
                    marker={'color': 'green', 'symbol': 'cross-thin', 'size': 5, 'line': {'width': 1, 'color': 'green'}},
                    mode='markers',
                    yaxis='y2',
                    showlegend=False
                )
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['DY'],
                    marker={'color': 'magenta', 'symbol': 'cross-thin', 'size': 5,
                            'line': {'width': 1, 'color': 'magenta'}},
                    mode='markers',
                    yaxis='y2',
                    showlegend=False
                )

        if dispersion_prime:
            artist.add_axis(title='Dispersion prime')

            artist.scatter(
                x=twiss['S'],
                y=twiss['DISP2'],
                line={'width': 2, 'color': 'green', 'dash': 'dashdot'},
                name='DISP2',
                mode='lines',
            )

            artist.scatter(
                x=twiss['S'],
                y=twiss['DISP4'],
                line={'width': 1, 'color': 'magenta', 'dash': 'dashdot'},
                name='DISP4',
                mode='lines',
            )

            if twiss_madx is not None:
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['DPX'],
                    marker={'color': 'green', 'symbol': 'cross-thin', 'size': 5, 'line': {'width': 1, 'color': 'green'}},
                    mode='markers',
                    showlegend=False
                )
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['DPY'],
                    marker={'color': 'magenta', 'symbol': 'cross-thin', 'size': 5,
                            'line': {'width': 1, 'color': 'magenta'}},
                    mode='markers',
                    showlegend=False
                )

        if mu:
            artist.add_axis(title='Phase advance')

            artist.scatter(
                x=twiss['S'],
                y=twiss['MU1'] / (2 * _np.pi),
                line={'width': 2, 'color': 'blue', 'dash': 'dashdot'},
                name='MU1',
                mode='lines',
            )

            artist.scatter(
                x=twiss['S'],
                y=twiss['MU2'] / (2 * _np.pi),
                line={'width': 1, 'color': 'FireBrick', 'dash': 'dashdot'},
                name='MU2',
                mode='lines',
            )

            if twiss_madx is not None:
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['MUX'],
                    marker={'color': 'blue', 'symbol': 'cross-thin', 'size': 5, 'line': {'width': 1, 'color': 'blue'}},
                    mode='markers',
                    showlegend=False
                )
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['MUY'],
                    marker={'color': 'FireBrick', 'symbol': 'cross-thin', 'size': 5,
                            'line': {'width': 1, 'color': 'FireBrick'}},
                    mode='markers',
                    showlegend=False
                )

        artist.plot_cartouche(beamline)
        artist.render()
        return artist
