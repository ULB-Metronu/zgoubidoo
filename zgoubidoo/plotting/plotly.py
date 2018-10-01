import numpy as np
import math
from ..units import _cm
import plotly.offline as py
import plotly.graph_objs as go
from .zgoubiplot import ZgoubiPlot


class ZgoubiPlotly(ZgoubiPlot):
    def __init__(self, with_boxes=True, with_frames=True, **kwargs):
        super().__init__(with_boxes, with_frames, **kwargs)
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
    def __init__(self, with_boxes=True, with_frames=True, **kwargs):
        super().__init__(with_boxes, with_frames, **kwargs)
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
        def do_frame() -> None:
            self._data.append(go.Scatter3d(x=[magnet.entry_patched.x(self.reference_frame)],
                                           y=[magnet.entry_patched.y(self.reference_frame)],
                                           z=[0], mode='markers', name = 'entry',
                                           marker=dict(
                                               size=5,
                                               color = 'red',
                                               opacity=0.8
                                           )))
            self._data.append(go.Scatter3d(x=[magnet.exit_patched.x(self.reference_frame)],
                                           y=[magnet.exit_patched.y(self.reference_frame)],
                                           z=[0],
                                           mode='markers', name = 'exit',
                                           marker=dict(
                                               size=5,
                                               color = 'green',
                                               opacity=0.8
                                           )))
            self._data.append(go.Scatter3d(x=[magnet.center.x(self.reference_frame)],
                                           y=[magnet.center.y(self.reference_frame)],
                                           z=[0], mode='markers', name='center',
                                           marker=dict(
                                               size=5,
                                               color='blue',
                                               opacity=0.8
                                           )))

        def build_vertices(m):
            x = []
            y = []
            z = []
            u = np.linspace(0, m.AT.to('radian').magnitude, m.AT.to('radian').magnitude*180/math.pi )
            for elem in u:
                y.append(m.RM.to('centimeter').magnitude * math.cos(elem+np.deg2rad(m.entry_patched.ty(self.reference_frame))) + m.center.y(self.reference_frame))
                x.append(m.RM.to('centimeter').magnitude * math.sin(elem+np.deg2rad(m.entry_patched.tx(self.reference_frame))) + m.center.x(self.reference_frame))
                z.append(0)

                y.append((m.RM.to('centimeter').magnitude + m.WIDTH.to('centimeter').magnitude) * math.cos(elem+np.deg2rad(m.entry_patched.ty(self.reference_frame))) + m.center.y(self.reference_frame))
                x.append((m.RM.to('centimeter').magnitude + m.WIDTH.to('centimeter').magnitude) * math.sin(elem+np.deg2rad(m.entry_patched.tx(self.reference_frame))) + m.center.x(self.reference_frame))
                z.append(0)

            for elem in u:
                y.append(m.RM.to('centimeter').magnitude * math.cos(elem+np.deg2rad(m.entry_patched.ty(self.reference_frame))) + m.center.y(self.reference_frame))
                x.append(m.RM.to('centimeter').magnitude * math.sin(elem+np.deg2rad(m.entry_patched.tx(self.reference_frame))) + m.center.x(self.reference_frame))
                z.append(m.HEIGHT.to('centimeter').magnitude)

                y.append((m.RM.to('centimeter').magnitude + m.WIDTH.to('centimeter').magnitude) * math.cos(elem+np.deg2rad(m.entry_patched.ty(self.reference_frame))) + m.center.y(self.reference_frame))
                x.append((m.RM.to('centimeter').magnitude + m.WIDTH.to('centimeter').magnitude) * math.sin(elem+np.deg2rad(m.entry_patched.tx(self.reference_frame))) + m.center.x(self.reference_frame))
                z.append(m.HEIGHT.to('centimeter').magnitude)

            print('Angle du dernier référentiel :', m.entry_patched.tx(self.reference_frame))
            return x, y, z

        def build_indices(vec):
            # --- Filling the arrays containing the indices of the coordinates relative to the x,y,z arrays ---
            # {i[m],j[m],k[m]} completely define the mth vertex. i[m] = n where (x[n],y[n],z[n]) are the coordinates of the first
            # vertex of the mth triangle. j[m] = n where (x[n],y[n],z[n]) are the coordinates of the second vertex of the mth
            # triangle. k[m] = n where (x[n],y[n],z[n]) are the coordinates of the third vertex of the mth triangle.
            i = []
            j = []
            k = []
            # Bottom face
            for n in range(0, int(len(vec) / 2 - 2)):
                i.append(n)
                j.append(n + 1)
                k.append(n + 2)
            # Top face
            for n in range(0, int(len(vec) / 2 - 2)):
                i.append(n + int(len(vec) / 2))
                j.append(n + 1 + int(len(vec) / 2))
                k.append(n + 2 + int(len(vec) / 2))

            # Outer lateral face
            for n in range(0, int(len(vec) / 2 - 2)):
                if n % 2 == 0:  # even n
                    i.append(n + int(len(vec) / 2) + 1)
                    j.append(n + 1)
                    k.append(n + int(len(vec) / 2) + 3)
                else:  # odd n
                    i.append(n)
                    j.append(n + int(len(vec) / 2) + 2)
                    k.append(n + 2)

            # Inner lateral face
            for n in range(0, int(len(vec) / 2 - 2)):
                if n % 2 == 0:  # even n
                    i.append(n + int(len(vec) / 2))
                    j.append(n)
                    k.append(n + int(len(vec) / 2) + 2)
                else:  # odd n
                    i.append(n - 1)
                    j.append(n + int(len(vec) / 2) + 1)
                    k.append(n + 1)
            # External face 1
            i.append(0)
            j.append(int(len(vec) / 2))
            k.append(1)
            i.append(1)
            j.append(int(len(vec) / 2))
            k.append(int(len(vec) / 2) + 1)
            # External face 2
            i.append(int(len(vec)) - 1)
            j.append(int(len(vec)) - 2)
            k.append(int(len(vec) / 2) - 1)
            i.append(int(len(vec) / 2) - 1)
            j.append(int(len(vec) / 2) - 2)
            k.append(int(len(vec)) - 2)

            return i, j, k

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

        if self._with_frames:
            do_frame()

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
