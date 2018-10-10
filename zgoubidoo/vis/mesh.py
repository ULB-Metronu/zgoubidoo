import os
import math
import numpy as np
import stl
from stl import mesh
from ..units import _cm, _degree, _radian
from .zgoubiplot import ZgoubiPlot


class ZgoubiMesh(ZgoubiPlot):
    def __init__(self, with_boxes=True, with_frames=True, **kwargs):
        super().__init__(with_boxes, with_frames, **kwargs)
        self._data = []
        self._entry = []
        self._exit = []
        self._center = []

    @property
    def dataframe(self):
        return self._data

    def cartesianmagnet(self, magnet):
        # Define the 8 vertices of the cube
        vertices = np.array([
            [_cm(magnet.entry_patched.x), _cm(magnet.entry_patched.y) - _cm(magnet.WIDTH)/2, 0],
            [_cm(magnet.entry_patched.x) + _cm(magnet.length), _cm(magnet.entry_patched.y) - _cm(magnet.WIDTH)/2, 0],
            [_cm(magnet.entry_patched.x) + _cm(magnet.length), _cm(magnet.entry_patched.y) + _cm(magnet.WIDTH/2), 0],
            [_cm(magnet.entry_patched.x), _cm(magnet.entry_patched.y) +_cm(magnet.WIDTH/2), 0],
            [_cm(magnet.entry_patched.x), _cm(magnet.entry_patched.y) - _cm(magnet.WIDTH)/2, _cm(magnet.HEIGHT)],
            [_cm(magnet.entry_patched.x) + _cm(magnet.length), _cm(magnet.entry_patched.y) - _cm(magnet.WIDTH)/2, _cm(magnet.HEIGHT)],
            [_cm(magnet.entry_patched.x) + _cm(magnet.length), _cm(magnet.entry_patched.y) + _cm(magnet.WIDTH)/2, _cm(magnet.HEIGHT)],
            [_cm(magnet.entry_patched.x), _cm(magnet.entry_patched.y) + _cm(magnet.WIDTH)/2, _cm(magnet.HEIGHT)]])

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

        m.rotate(np.array([0.0, 0.0, 0.5]),
                 _radian(magnet.entry_patched.tx),
                 point=np.array([
                     _cm(magnet.entry_patched.x),
                     _cm(magnet.entry_patched.y),
                     0
                 ])
                 )

        self._data.append(m)

    def tracks_cartesianmagnet(self):
        pass

    def polarmagnet(self, magnet):

        # Define the vertices of the dipole
        number_of_points = int(2 * _degree(magnet.AT))
        vertices = np.empty([2 * number_of_points, 3])

        self._entry.append([_cm(magnet.entry.x), _cm(magnet.entry.y)])
        self._exit.append([_cm(magnet.exit.x), _cm(magnet.exit.y)])
        self._center.append([_cm(magnet.center.x), _cm(magnet.center.y)])

        if np.cos(_radian(magnet.entry.tz)) > 0:
            for angle in range(1, number_of_points + 1, 2):
                vertices[angle - 1][:] = [(_cm(magnet.RM) - _cm(magnet.WIDTH) / 2) * math.cos(
                    math.pi / 2 - (magnet.entry.tx + np.deg2rad(angle / 2))) + _cm(magnet.center.x),
                                          (_cm(magnet.RM) - _cm(magnet.WIDTH) / 2) * math.sin(
                                              math.pi / 2 - (magnet.entry.tx + np.deg2rad(angle / 2))) + _cm(
                                              magnet.center.y),
                                          0.0]
                vertices[angle][:] = [(_cm(magnet.RM) + _cm(magnet.WIDTH) / 2) * math.cos(
                    math.pi / 2 - (magnet.entry.tx + np.deg2rad(angle / 2))) + _cm(magnet.center.x),
                                      (_cm(magnet.RM) + _cm(magnet.WIDTH) / 2) * math.sin(
                                          math.pi / 2 - (magnet.entry.tx + np.deg2rad(angle / 2))) + _cm(
                                          magnet.center.y),
                                      0.0]
                vertices[angle + number_of_points - 1][:] = [(_cm(magnet.RM) - _cm(magnet.WIDTH) / 2) * math.cos(
                    math.pi / 2 - (magnet.entry.tx + np.deg2rad(angle / 2))) + _cm(magnet.center.x),
                                                             (_cm(magnet.RM) - _cm(magnet.WIDTH) / 2) * math.sin(
                                                                 math.pi / 2 - (magnet.entry.tx + np.deg2rad(
                                                                     angle / 2))) + _cm(magnet.center.y),
                                                             _cm(magnet.HEIGHT)]
                vertices[angle + number_of_points][:] = [(_cm(magnet.RM) + _cm(magnet.WIDTH) / 2) * math.cos(
                    math.pi / 2 - (magnet.entry.tx + np.deg2rad(angle / 2))) + _cm(magnet.center.x),
                                                         (_cm(magnet.RM) + _cm(magnet.WIDTH) / 2) * math.sin(
                                                             math.pi / 2 - (magnet.entry.tx + np.deg2rad(
                                                                 angle / 2))) + _cm(magnet.center.y),
                                                         _cm(magnet.HEIGHT)]
        else:
            for angle in range(1, number_of_points + 1, 2):
                vertices[angle - 1][:] = [(_cm(magnet.RM) - _cm(magnet.WIDTH) / 2) * math.cos(
                    -math.pi / 2 - (magnet.entry.tx - np.deg2rad(angle / 2))) + _cm(magnet.center.x),
                                          (_cm(magnet.RM) - _cm(magnet.WIDTH) / 2) * math.sin(
                                              -math.pi / 2 - (magnet.entry.tx - np.deg2rad(angle / 2))) + _cm(
                                              magnet.center.y),
                                          0.0]
                vertices[angle][:] = [(_cm(magnet.RM) + _cm(magnet.WIDTH) / 2) * math.cos(
                    -math.pi / 2 - (magnet.entry.tx - np.deg2rad(angle / 2))) + _cm(magnet.center.x),
                                      (_cm(magnet.RM) + _cm(magnet.WIDTH) / 2) * math.sin(
                                          -math.pi / 2 - (magnet.entry.tx - np.deg2rad(angle / 2))) + _cm(
                                          magnet.center.y),
                                      0.0]
                vertices[angle + number_of_points - 1][:] = [(_cm(magnet.RM) - _cm(magnet.WIDTH) / 2) * math.cos(
                    -math.pi / 2 - (magnet.entry.tx - np.deg2rad(angle / 2))) + _cm(magnet.center.x),
                                                             (_cm(magnet.RM) - _cm(magnet.WIDTH) / 2) * math.sin(
                                                                 -math.pi / 2 - (magnet.entry.tx - np.deg2rad(
                                                                     angle / 2))) + _cm(magnet.center.y),
                                                             _cm(magnet.HEIGHT)]
                vertices[angle + number_of_points][:] = [(_cm(magnet.RM) + _cm(magnet.WIDTH) / 2) * math.cos(
                    -math.pi / 2 - (magnet.entry.tx - np.deg2rad(angle / 2))) + _cm(magnet.center.x),
                                                         (_cm(magnet.RM) + _cm(magnet.WIDTH) / 2) * math.sin(
                                                             -math.pi / 2 - (magnet.entry.tx - np.deg2rad(
                                                                 angle / 2))) + _cm(magnet.center.y),
                                                         _cm(magnet.HEIGHT)]

        # Define the triangles composing the polar magnet
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

        x = []
        y = []
        for i in range(0, 2 * number_of_points):
            x.append(vertices[i][0])
            y.append(vertices[i][1])

        x_entry = []
        y_entry = []
        for i in range(0, len(self._entry)):
            x_entry.append(self._entry[i][0])
            y_entry.append(self._entry[i][1])

        x_exit = []
        y_exit = []
        for i in range(0, len(self._entry)):
            x_exit.append(self._exit[i][0])
            y_exit.append(self._exit[i][1])

        x_center = []
        y_center = []
        for i in range(0, len(self._entry)):
            x_center.append(self._center[i][0])
            y_center.append(self._center[i][1])

        m = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))

        for i, f in enumerate(faces):
            for j in range(3):
                m.vectors[i][j] = vertices[f[j], :]

        self._data.append(m)

    def render(self, file='mesh.stl', path='.'):
        mesh.Mesh(np.concatenate([d.data for d in self._data])).save(
            os.path.join(path, file),
            mode=stl.Mode.ASCII,
        )

    def tracks_polarmagnet(self):
        return None
