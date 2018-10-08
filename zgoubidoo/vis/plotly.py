import numpy as np
import math
import plotly.offline as py
import plotly.graph_objs as go
from .zgoubiplot import ZgoubiPlot
from stl import mesh
import stl

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