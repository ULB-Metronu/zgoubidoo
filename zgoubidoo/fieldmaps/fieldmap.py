import os
import numpy as np
import pandas as pd
from scipy import interpolate
from lmfit import Model


def enge(s,
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
         ):
    p_e = ce_0 + ce_1 * (-(s - offset_e) / lam_e) + ce_2 * (-(s - offset_e) / lam_e) ** 2 + ce_3 * (
                -(s - offset_e) / lam_e) ** 3 + ce_4 * (-(s - offset_e) / lam_e) ** 4 + ce_5 * (
                      -(s - offset_e) / lam_e) ** 5
    p_s = cs_0 + cs_1 * ((s - offset_s) / lam_s) + cs_2 * ((s - offset_s) / lam_s) ** 2 + cs_3 * (
                (s - offset_s) / lam_s) ** 3 + cs_4 * ((s - offset_s) / lam_s) ** 4 + cs_5 * (
                      (s - offset_s) / lam_s) ** 5
    return amplitude * (1 / (1 + np.exp(p_e))) * (1 / (1 + np.exp(p_s))) + field_offset


def load_mesh_data(file: str, path: str = ''):
    with open(os.path.join(path, file)) as f:
        _, x_dim, y_dim, z_dim, _, _ = tuple(map(int, f.readline().split()))
        data = np.array(list(map(float, ' '.join(f.readlines()).split())))
    x = data[0:x_dim]
    y = data[x_dim:x_dim + y_dim]
    z = data[x_dim + y_dim:x_dim + y_dim + z_dim]
    return np.meshgrid(x, y, z, indexing='ij')


def load_field_data(file: str, path: str = '.') -> pd.DataFrame:
    return pd.read_csv(os.path.join(path, file), sep='\s+', names=['BX', 'BY', 'BZ', 'M'], header=None)


def load_fieldmap(field_file: str, mesh_file: str, path: str = '.'):
    x, y, z = [c.reshape((np.prod(c.shape),)) for c in load_mesh_data(file=mesh_file, path=path)]
    f = load_field_data(file=field_file, path=path).values.T.reshape((4, np.prod(x.shape)))
    return np.array([x, y, z, *f]).T


class FieldMap:
    def __init__(self, field_file: str, mesh_file: str, path: str = '.'):
        self._df: Optional[pd.DataFrame] = None
        self._data = load_fieldmap(field_file=field_file, mesh_file=mesh_file, path=path)

    @property
    def data(self):
        return self._data

    @property
    def sampling_x(self):
        return self.sampling_axis(axis=0)

    @property
    def sampling_y(self):
        return self.sampling_axis(axis=1)

    @property
    def sampling_z(self):
        return self.sampling_axis(axis=2)

    def sampling_axis(self, axis=0):
        _ = np.unique(self.data[:, axis])
        return _, len(_)

    def to_df(self) -> pd.DataFrame:
        if self._df is None:
            self._df = pd.DataFrame(self._data)
            self._df.columns = ['X', 'Y', 'Z', 'BX', 'BY', 'BZ', 'M']
        return self._df

    def sample(self, points, field_component: str = 'BX', method: str = 'nearest'):
        field_components = {
            'BX': self._data[:, 3],
            'BY': self._data[:, 4],
            'BZ': self._data[:, 5],
            'MOD': np.sqrt((self._data[:, 3:6] * self._data[:, 3:6]).sum(axis=1)),
        }
        return interpolate.griddata(self._data[:, 0:3], field_components[field_component], points, method=method)

    def export():
        pass


class EngeModel(Model):
    def __init__(self):
        super().__init__(enge)
        self._params = None

    @property
    def params(self):
        if self._params is None:
            self._params = self.make_params()
        return self._params


class FieldProfile:
    def __init__(self, fieldmap, trajectory):
        pass

    def fit(self):
        pass

