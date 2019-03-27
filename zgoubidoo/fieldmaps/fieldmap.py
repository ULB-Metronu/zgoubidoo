"""Field map module."""
from typing import Optional, Union, Tuple
import os
import numpy as np
import pandas as pd
from scipy import interpolate
from lmfit import Model as _Model


def load_mesh_data(file: str, path: str = '.'):  # -> List[np.array]
    """
    Load a mesh data file and creates a complete mesh grid using numpy.

    Args:
        file: the file containing the mesh data
        path: path to the mesh data file

    Returns:
        A Numpy mesh grid (list of arrays).
    """
    with open(os.path.join(path, file)) as f:
        _, x_dim, y_dim, z_dim, _, _ = tuple(map(int, f.readline().split()))
        data = np.array(list(map(float, ' '.join(f.readlines()).split())))
    x = data[0:x_dim]
    y = data[x_dim:x_dim + y_dim]
    z = data[x_dim + y_dim:x_dim + y_dim + z_dim]
    return np.meshgrid(x, y, z, indexing='ij')


def load_field_data(file: str, path: str = '.') -> pd.DataFrame:
    """

    Args:
        file: the file containing the field map data
        path: path to the field mpa data file

    Returns:
        A DataFrame containing the field data.
    """
    return pd.read_csv(os.path.join(path, file), sep=r'\s+', names=['BX', 'BY', 'BZ', 'M'], header=None)


def load_opera_fieldmap_with_mesh(field_file: str, mesh_file: str, path: str = '.') -> np.array:
    """

    Args:
        field_file: the file containing the field map data
        mesh_file: the file containing the mesh data
        path: path to the field mpa data files

    Returns:
        A Numpy array containing the mesh points and the associated field values.
    """
    x, y, z = [c.reshape((np.prod(c.shape),)) for c in load_mesh_data(file=mesh_file, path=path)]
    f = load_field_data(file=field_file, path=path).values.T.reshape((4, np.prod(x.shape)))
    return np.array([x, y, z, *f]).T


def load_opera_fieldmap(file: str, path: str = '.') -> np.array:
    """

    Args:
        file: the file containing the field map data
        path: path to the field mpa data file

    Returns:
        A Numpy array containing the mesh points and the associated field values.
    """
    return pd.read_csv(os.path.join(path, file), skiprows=9, sep=r'\s+', header=None, names=[
        'X', 'Y', 'Z', 'BX', 'BY', 'BZ', 'MATCODE',
    ]).values


def enge(s: Union[float, np.array],
         ce_0: float = 0.0,
         ce_1: float = 1.0,
         ce_2: float = 0.0,
         ce_3: float = 0.0,
         ce_4: float = 0.0,
         ce_5: float = 0.0,
         cs_0: float = 0.0,
         cs_1: float = 1.0,
         cs_2: float = 0.0,
         cs_3: float = 0.0,
         cs_4: float = 0.0,
         cs_5: float = 0.0,
         lam_e: float = 1.0,
         lam_s: float = 1.0,
         offset_e: float = -1.0,
         offset_s: float = 1.0,
         amplitude: float = 1.0,
         field_offset: float = 0.0,
         ) -> Union[float, np.array]:
    """
    Enge function for the modelling of fringe fields.

    Args:
        s: the coordinate (can be a numpy array)
        ce_0: zero-th order coefficient for the entrance fringe
        ce_1: first order coefficient for the entrance fringe (usually set to 1)
        ce_2: second order coefficent for the entrance fringe
        ce_3: third order coefficient for the entrance fringe
        ce_4: fourth order coefficient for the entrance fringe
        ce_5: fifth order coefficient for the entrance fringe
        cs_0: zero-th order coefficient for the exit fringe
        cs_1: first order coefficient for the exit fringe (usually set to 1)
        cs_2: second order coefficient for the exit fringe
        cs_3: third order coefficient for the exit fringe
        cs_4: fourth order coefficient for the exit fringe
        cs_5: fifth order coefficient for the exit fringe
        lam_e: characteristic length of the entrance fringe
        lam_s: characteristic length of the exit fringe
        offset_e: offset for the positionning of the entrance fall-off
        offset_s: offset for the positionning of the exit fall-off
        amplitude: field amplitude (not necesserally equal to the maximum)
        field_offset: field offset

    Returns:
        the value of the Enge function at coordinate s.
    """
    p_e = ce_0 + ce_1 * (-(s - offset_e) / lam_e) + ce_2 * (-(s - offset_e) / lam_e) ** 2 + ce_3 * (
                -(s - offset_e) / lam_e) ** 3 + ce_4 * (-(s - offset_e) / lam_e) ** 4 + ce_5 * (
                      -(s - offset_e) / lam_e) ** 5
    p_s = cs_0 + cs_1 * ((s - offset_s) / lam_s) + cs_2 * ((s - offset_s) / lam_s) ** 2 + cs_3 * (
                (s - offset_s) / lam_s) ** 3 + cs_4 * ((s - offset_s) / lam_s) ** 4 + cs_5 * (
                      (s - offset_s) / lam_s) ** 5
    return amplitude * ((1 / (1 + np.exp(p_e))) + (1 / (1 + np.exp(p_s))) - 1) + field_offset


class EngeModel(_Model):
    """Enge model to be used with lmfit."""
    def __init__(self):
        super().__init__(enge)
        self._params = None

    @property
    def params(self):
        """The parameters of the Enge model (interface to `lmfit.Model.make_params()`)."""
        if self._params is None:
            self._params = self.make_params()
        return self._params


class FieldMap:
    """
    TODO
    """
    def __init__(self, field_map: pd.DataFrame):
        """

        Args:
            field_map:
        """
        self._df: Optional[pd.DataFrame] = None
        self._data = field_map

    @classmethod
    def load_from_opera(cls, file: str, path: str = '.'):
        """
        Factory method to load a field map from a Opera output file.

        Args:
            file: the file containing the field map data
            path: path to the field mpa data file

        Returns:
            A FieldMap loaded from file.
        """
        return cls(field_map=load_opera_fieldmap(file=file, path=path))

    @classmethod
    def load_from_opera_with_mesh(cls, field_file: str, mesh_file: str, path: str = '.'):
        """
        Factory method to load a field map from Opera output files (field map and mesh definition).

        Args:
            field_file: the file containing the field map data
            mesh_file: the file containing the mesh data
            path: path to the field mpa data files

        Returns:
            A FieldMap loaded from files.
        """
        return cls(field_map=load_opera_fieldmap_with_mesh(field_file=field_file, mesh_file=mesh_file, path=path))

    @property
    def data(self):
        """Field map raw data in a numpy array."""
        return self._data

    @property
    def sampling_x(self) -> Tuple[np.array, int]:
        """Sampling points of the field map along the X axis."""
        return self.sampling_axis(axis=0)

    @property
    def sampling_y(self) -> Tuple[np.array, int]:
        """Sampling points of the field map along the Y axis."""
        return self.sampling_axis(axis=1)

    @property
    def sampling_z(self) -> Tuple[np.array, int]:
        """Sampling points of the field map along the Z axis."""
        return self.sampling_axis(axis=2)

    def sampling_axis(self, axis: int) -> Tuple[np.array, int]:
        """
        Sampling points of the field map along a given axis.

        Args:
            axis: the index of the axis.

        Returns:
            A numpy array containing the data points of the field map sampling.
        """
        _ = np.unique(self.data[:, axis])
        return _, len(_)

    def to_df(self) -> pd.DataFrame:
        """
        Exports the field map to a Pandas dataframe.

        Returns:
            A dataframe containing the field map vector field information.
        """
        if self._df is None:
            self._df = pd.DataFrame(self._data)
            self._df.columns = ['X', 'Y', 'Z', 'BX', 'BY', 'BZ', 'M']
        return self._df

    def sample(self, points, field_component: str = 'MOD', method: str = 'nearest'):
        """

        Args:
            points:
            field_component: field component to be sampled ('BX', 'BY', 'BZ' or 'MOD')
            method: method used for the grid interpolation ('nearest' or 'linear')

        Returns:

        """
        # The lambda trick is used so that the modulus is only computed if needed
        field_components = {
            'BX': lambda: self._data[:, 3],
            'BY': lambda: self._data[:, 4],
            'BZ': lambda: self._data[:, 5],
            'MOD': lambda: np.sqrt((self._data[:, 3:6] * self._data[:, 3:6]).sum(axis=1)),
        }
        return interpolate.griddata(self._data[:, 0:3], field_components[field_component](), points, method=method)

    def export_for_bdsim(self, method: str = 'nearest'):
        """

        Args:
            method: method used for the grid interpolation ('nearest' or 'linear')

        Returns:

        """
        new_mesh = np.mgrid[
                   self.sampling_x[0].min():self.sampling_x[0].max():100j,
                   self.sampling_y[0].min():self.sampling_y[0].max():100j,
                   self.sampling_z[0].min():self.sampling_z[0].max():100j
                   ].T.reshape(100 ** 3, 3)

        fx = -self.sample(new_mesh, field_component='BX', method=method)
        fy = -self.sample(new_mesh, field_component='BY', method=method)
        fz = -self.sample(new_mesh, field_component='BZ', method=method)
        return np.concatenate([new_mesh, np.stack([fx, fy, fz]).T], axis=1)
