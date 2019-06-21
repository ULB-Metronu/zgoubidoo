"""
TODO
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Mapping
import plotly.offline
import plotly.graph_objs as go
from zgoubidoo.vis import Artist
from ..commands import Plotable as _Plotable
from ..commands import Patchable as _Patchable
from ..commands import Quadrupole as _Quadrupole
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
            'showLink': False,
            'scrollZoom': True,
            'displayModeBar': False,
            'editable': False,
        }
        self._layout = {
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
            },
        }
        self._shapes = []

    def _init_plot(self):
        pass

    @property
    def fig(self):
        """Provides the plotly figure."""
        return {
            'data': self.data,
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

    def add_secondary_axis(self):
        self.layout['yaxis2'] = {
            'title': 'yaxis2 title',
            'titlefont': dict(
                color='rgb(148, 103, 189)'
            ),
            'tickfont': dict(
                color='rgb(148, 103, 189)'
            ),
            'overlaying': 'y',
            'side': 'right',
        }

    def render(self):
        plotly.offline.iplot(self.fig, config=self.config)

    def save(self, file: str, format: str = 'png'):
        plotly.io.write_image(self.fig, file=file, format=format)

    def save_html(self, file: str):
        return plotly.offline.plot(self.fig, config=self.config, auto_open=False, filename=file)

    def scatter(self, *args, **kwargs):
        """A proxy for plotly.graph_objs.Scatter ."""
        self._data.append(go.Scatter(*args, **kwargs))

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
            if isinstance(e, _Quadrupole):
                self.shapes.append(
                    {
                        'type': 'rect',
                        'xref': 'x',
                        'yref': 'paper',
                        'x0': e.entry_patched.x.m_as('m'),
                        'y0': vertical_position if e.B0.magnitude > 0 else 1.1,
                        'x1': e.exit.x.m_as('m'),
                        'y1': 1.3 if e.B0.magnitude > 0 else vertical_position,
                        'line': {
                            'width': 0,
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
                            'width': 0,
                        },
                        'fillcolor': '#4169E1',
                    },
                )

    def plot_beamline(self,
                      beamline: _Input,
                      tracks=None,
                      tracks_color: str = 'b',
                      with_elements: bool = True,
                      with_apertures: bool = False,
                      with_tracks: bool = True,
                      ) -> None:
        """
        Use a `ZgoubiPlot` artist to perform the rendering of the beamline with elements and tracks.

        The `Input` must be surveyed first so that all the placements are taken into account for the plotting.

        Args:
            beamline:
            tracks: the tracks dataset
            tracks_color: color for the rendering of the tracks
            with_elements: plot the beamline elements
            with_apertures:
            with_tracks: plot the beam tracks
        """
        line = line[_Patchable][_Plotable].line
        if getattr(artist, 'tracks_color'):
            artist.tracks_color = tracks_color
        for e in line:
            if with_elements:
                e.plot(artist=artist, apertures=with_apertures)
            if not with_elements and with_apertures:
                e.plot(artist=artist, apertures=True)
            if tracks is not None and with_tracks:
                e.plot_tracks(artist=artist, tracks=tracks.query(f"LABEL1 == '{e.LABEL1}'"))
