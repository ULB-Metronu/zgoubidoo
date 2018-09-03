import numpy as np
import plotly.offline as py
import plotly.graph_objs as go
from .zgoubiplot import ZgoubiPlot


class ZgoubiPlotly(ZgoubiPlot):
    def __init__(self, with_boxes=True, with_frames=True):
        super().__init__(with_boxes, with_frames)
        self._data = []
        self._layout = {}
        self._shapes = []

    def _init_plot(self):
        pass

    @property
    def fig(self):
        return {
            'data': self.data,
            'layout': self.layout,
        }

    @property
    def config(self):
        return {
            'showLink': False,
            'scrollZoom': True,
            'displayModeBar': True,
            'editable': False,
        }

    @property
    def data(self):
        return self._data

    @property
    def layout(self):
        return {
            'xaxis': {
                'range': [0, 250],
                'showgrid': True,
                'linecolor': 'black',
                'linewidth': 1,
                'mirror': True,
            },
            'yaxis': {
                'range': [-75, 75],
                'linecolor': 'black',
                'linewidth': 1,
                'mirror': True,
            },
            'shapes': self._shapes,
        }

    def __iadd__(self, other):
        self._data.append(other)
        return self

    def render(self):
        py.iplot(self.fig, config=self.config)

    def cartesian_bend(self, entry, sortie, rotation, width, color='gray'):
        def do_frame():
            pass

        def do_box():
            self._data.append(
                go.Scatter(
                    x=[1.5, 3],
                    y=[2.5, 2.5],
                    showlegend=False,
                )
            )
            self._shapes.append(
                {
                    'type': 'rect',
                    'xref': 'x',
                    'yref': 'y',
                    'x0': entry[0].to('cm').magnitude,
                    'y0': (entry[1] - width / 2).to('cm').magnitude,
                    'x1': sortie[0].to('cm').magnitude,
                    'y1': (sortie[1] + width / 2).to('cm').magnitude,
                    'line': {
                        'color': 'rgb(55, 128, 191)',
                        'width': 1,
                    },
                    'fillcolor': 'rgba(55, 128, 191, 0.6)',
                },
            )

        if self._with_boxes:
            do_box()
        if self._with_frames:
            do_frame()
