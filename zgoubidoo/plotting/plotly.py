import numpy as np
import math
from ..units import _cm
import plotly.offline as py
import plotly.graph_objs as go
from .zgoubiplot import ZgoubiPlot
from stl import mesh
import stl
from .. import ureg
import matplotlib.pyplot as plt
from ..units import _cm, _degree, _radian
import numpy as np

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


class ZgoubiMesh(ZgoubiPlot):
    def __init__(self, with_boxes=True, with_frames=True, **kwargs):
        super().__init__(with_boxes, with_frames, **kwargs)
        self._data = []

    @property
    def dataframe(self):
        return self._data

    def cartesianmagnet(self, magnet):
        # Define the 8 vertices of the cube
        vertices = np.array([
            [0, 0, 0],
            [magnet.LENGTH, 0, 0],
            [magnet.LENGTH, magnet.WIDTH, 0],
            [0, magnet.WIDTH, 0],
            [0, 0, magnet.HEIGHT],
            [magnet.LENGTH, 0, magnet.HEIGHT],
            [magnet.LENGTH, magnet.WIDTH, magnet.HEIGHT],
            [0, magnet.WIDTH, magnet.HEIGHT]])

        # Define the 12 triangles composing the cube
        faces = np.array([
            [0, 3, 1],
            [1, 3, 2],
            [0, 4, 7],
            [0, 7, 3],
            [4, 5, 6],
            [4, 6, 7],
            [5, 1, 2],
            [5, 2, 6],
            [2, 3, 6],
            [3, 7, 6],
            [0, 1, 5],
            [0, 5, 4]])

        m = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))

        for i, f in enumerate(faces):
            for j in range(3):
                m.vectors[i][j] = vertices[f[j], :]

        self._data.append(m)

    def polarmagnet(self, magnet):

        # Define the vertices of the dipole
        print('Référentiel entrée :', magnet.center.x, magnet.center.y, 'angles :', magnet.entry.tx, magnet.entry.ty)
        print('Référentiel sortie :', magnet.center.x, magnet.center.y, 'angles :', magnet.exit.tx, magnet.exit.ty)
        number_of_points = int(2 * _degree(magnet.ACENT))
        vertices = np.empty([2 * number_of_points, 3])

        for angle in range(0, number_of_points, 2):
            vertices[angle][:] = [_cm(magnet.RM) * math.cos(np.deg2rad(angle) + _radian(magnet.entry.tx)) + _cm(magnet.center.x),
                                  _cm(magnet.RM) * math.sin(np.deg2rad(angle) + _radian(magnet.entry.ty)) + _cm(magnet.center.y),
                                  0.0]
            vertices[angle + 1][:] = [(_cm(magnet.RM) + _cm(magnet.WIDTH)) * math.cos(np.deg2rad(angle) + _radian(magnet.entry.tx)) + _cm(magnet.center.x),
                                      (_cm(magnet.RM) + _cm(magnet.WIDTH)) * math.sin(np.deg2rad(angle) + _radian(magnet.entry.ty)) + _cm(magnet.center.y),
                                      0.0]
            vertices[angle + number_of_points][:] = [ _cm(magnet.RM) * math.cos(np.deg2rad(angle) + _radian(magnet.entry.tx)) + _cm(magnet.center.x),
                                                     _cm(magnet.RM) * math.sin(np.deg2rad(angle) + _radian(magnet.entry.ty)) + _cm(magnet.center.y),
                                                      _cm(magnet.HEIGHT)]
            vertices[angle + number_of_points + 1][:] = [(_cm(magnet.RM) + _cm(magnet.WIDTH)) * math.cos(np.deg2rad(angle) + _radian(magnet.entry.tx)) + _cm(magnet.center.x),
                                                         (_cm(magnet.RM) + _cm(magnet.WIDTH)) * math.sin(np.deg2rad(angle) + _radian(magnet.entry.ty)) + _cm(magnet.center.y),
                                                         _cm(magnet.HEIGHT)]

        # print('vertices :', vertices)

        # Define the triangles composing the dipole

        number_of_faces = int(len(vertices) / 2 - 2)
        faces = np.empty([4 * number_of_faces + 2 * 2, 3])

        for i in range(0, number_of_faces):
            faces[i][:] = [i, i + 1, i + 2]
            faces[i + 1 * number_of_faces][:] = [i + number_of_points, i + 1 + number_of_points,
                                                 i + 2 + number_of_points]
            if i % 2 == 0:
                faces[i + 2 * number_of_faces][:] = [i, i + number_of_points, i + 2]
                faces[i + 1 + 2 * number_of_faces][:] = [i + number_of_points, i + number_of_points + 2, i + 2]
            else:
                faces[i + 3 * number_of_faces][:] = [i, i + number_of_points, i + 2]
                faces[i - 1 + 3 * number_of_faces][:] = [i + number_of_points, i + number_of_points + 2, i + 2]

        faces[-1][:] = [0, 1, number_of_points]
        faces[-2][:] = [1, number_of_points, number_of_points + 1]
        faces[-3][:] = [number_of_points - 1, number_of_points - 2, 2 * number_of_points - 1]
        faces[-4][:] = [2 * number_of_points - 1, 2 * number_of_points - 2, number_of_points - 2]

        faces = faces.astype(int)

        # print('faces :', faces)

        x = []
        y = []
        for i in range(0, 2 * number_of_points):
            x.append(vertices[i][0])
            y.append(vertices[i][1])
        #plt.plot(x, y, '.')
        #plt.show()

        m = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))

        for i, f in enumerate(faces):
            for j in range(3):
                m.vectors[i][j] = vertices[f[j], :]

        self._data.append(m)

    def render(self):
        total_length_data = 0
        for i in range(len(self._data)):
            total_length_data += len(self._data[i].data)

        data = np.zeros(total_length_data, dtype=mesh.Mesh.dtype)
        data['vectors'] = np.array(self._data).reshape((-1, 9)).reshape((-1, 3, 3))
        mesh_final = mesh.Mesh(data.copy())
        mesh_final.save('/Users/arthurvandenhoeke/scale.stl', mode=stl.Mode.ASCII)  # save as ASCII

    def tracks_polarmagnet(self):
        return None
