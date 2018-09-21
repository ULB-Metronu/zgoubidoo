import numpy as np
import math
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

    def polarmagnet(self, magnet):
       pass

    def cartesianmagnet(self, entry, sortie, rotation, width, color='gray'):
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


class ZgoubiPlotly3d(ZgoubiPlot):
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

    def polarmagnet(self, magnet):
        def build_vertices(m):
            x = []
            y = []
            z = []
            u = np.linspace(0, m.AT.to('radian').magnitude, m.AT.to('radian').magnitude*180/math.pi)
            for elem in u:
                x.append(m.RM.to('meter').magnitude * math.cos(elem+m.entry[5].to('radians').magnitude) + m.center[0].to('meter').magnitude)
                y.append(m.RM.to('meter').magnitude * math.sin(elem+m.entry[5].to('radians').magnitude) + m.center[1].to('meter').magnitude)
                z.append(0)

                x.append((m.RM.to('meter').magnitude + m.WIDTH.to('meter').magnitude) * math.cos(elem+m.entry[5].to('radians').magnitude) + m.center[0].to('meter').magnitude)
                y.append((m.RM.to('meter').magnitude + m.WIDTH.to('meter').magnitude) * math.sin(elem+m.entry[5].to('radians').magnitude) + m.center[1].to('meter').magnitude)
                z.append(0)

            for elem in u:
                x.append(m.RM.to('meter').magnitude * math.cos(elem+m.entry[5].to('radians').magnitude) + m.center[0].to('meter').magnitude)
                y.append(m.RM.to('meter').magnitude * math.sin(elem+m.entry[5].to('radians').magnitude) + m.center[1].to('meter').magnitude)
                z.append(m.HEIGHT.to('meter').magnitude)

                x.append((m.RM.to('meter').magnitude + m.WIDTH.to('meter').magnitude) * math.cos(elem+m.entry[5].to('radians').magnitude) + m.center[0].to('meter').magnitude)
                y.append((m.RM.to('meter').magnitude + m.WIDTH.to('meter').magnitude) * math.sin(elem+m.entry[5].to('radians').magnitude) + m.center[1].to('meter').magnitude)
                z.append(m.HEIGHT.to('meter').magnitude)

            return x, y, z

        def build_indices(x):
            # --- Filling the arrays containing the indices of the coordinates relative to the x,y,z arrays ---
            # {i[m],j[m],k[m]} completely define the mth vertex. i[m] = n where (x[n],y[n],z[n]) are the coordinates of the first
            # vertex of the mth triangle. j[m] = n where (x[n],y[n],z[n]) are the coordinates of the second vertex of the mth
            # triangle. k[m] = n where (x[n],y[n],z[n]) are the coordinates of the third vertex of the mth triangle.
            un = []
            deux = []
            trois = []
            # --- bottom face---
            for i in range(0, int(len(x) / 2 - 2)):
                un.append(i)
                deux.append(i + 1)
                trois.append(i + 2)
            # --- top face---
            for i in range(0, int(len(x) / 2 - 2)):
                un.append(i + int(len(x) / 2))
                deux.append(i + 1 + int(len(x) / 2))
                trois.append(i + 2 + int(len(x) / 2))

            # Outer lateral face
            for i in range(0, int(len(x) / 2 - 2)):
                if i % 2 == 0:  # even i
                    un.append(i + int(len(x) / 2) + 1)
                    deux.append(i + 1)
                    trois.append(i + int(len(x) / 2) + 3)
                else:  # odd i
                    un.append(i)
                    deux.append(i + int(len(x) / 2) + 2)
                    trois.append(i + 2)

            # Inner lateral face
            for i in range(0, int(len(x) / 2 - 2)):
                if i % 2 == 0:  # even i
                    un.append(i + int(len(x) / 2))
                    deux.append(i)
                    trois.append(i + int(len(x) / 2) + 2)
                else:  # odd i
                    un.append(i - 1)
                    deux.append(i + int(len(x) / 2) + 1)
                    trois.append(i + 1)
            # --- external face 1---
            un.append(0)
            deux.append(int(len(x) / 2))
            trois.append(1)
            un.append(1)
            deux.append(int(len(x) / 2))
            trois.append(int(len(x) / 2) + 1)
            # --- external face 2---
            un.append(int(len(x)) - 1)
            deux.append(int(len(x)) - 2)
            trois.append(int(len(x) / 2) - 1)
            un.append(int(len(x) / 2) - 1)
            deux.append(int(len(x) / 2) - 2)
            trois.append(int(len(x)) - 2)

            return un, deux, trois

        x, y, z = build_vertices(magnet)
        i, j, k = build_indices(x)
        my_data = go.Mesh3d(
                x=x,
                y=y,
                z=z,

                i=i,
                j=j,
                k=k,
                showscale=True,
                opacity=0.3,
                color=magnet.COLOR,
            )
        self._data.append(my_data)

    def cartesianmagnet(self, entry, sortie, rotation, width, color='gray'):
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
