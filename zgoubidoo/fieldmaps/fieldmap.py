"""Field map module."""
from typing import Optional, Union, Tuple, List
import os
import lmfit
import sympy
import tempfile
import numpy as _np
import pandas as _pd
from scipy import interpolate
from lmfit import Model as _Model


def load_mesh_data(file: str, path: str = '.') -> _np.meshgrid:
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
        data = _np.array(list(map(float, ' '.join(f.readlines()).split())))
    x = data[0:x_dim]
    y = data[x_dim:x_dim + y_dim]
    z = data[x_dim + y_dim:x_dim + y_dim + z_dim]
    return _np.meshgrid(x, y, z, indexing='ij')


def load_field_data(file: str, path: str = '.') -> _pd.DataFrame:
    """

    Args:
        file: the file containing the field map data
        path: path to the field mpa data file

    Returns:
        A DataFrame containing the field data.
    """
    return _pd.read_csv(os.path.join(path, file), sep=r'\s+', names=['BX', 'BY', 'BZ', 'M'], header=None)


def load_opera_fieldmap_with_mesh(field_file: str, mesh_file: str, path: str = '.') -> _pd.DataFrame:
    """

    Args:
        field_file: the file containing the field map data
        mesh_file: the file containing the mesh data
        path: path to the field mpa data files

    Returns:
        A Numpy array containing the mesh points and the associated field values.
    """
    x, y, z = [c.reshape((_np.prod(c.shape),)) for c in load_mesh_data(file=mesh_file, path=path)]
    f = load_field_data(file=field_file, path=path).values.T.reshape((4, _np.prod(x.shape)))
    return _pd.DataFrame(
        _np.array([x, y, z, *f]).T,
        columns=['X', 'Y', 'Z', 'BX', 'BY', 'BZ', 'MATCODE'],
    )


def load_opera_fieldmap(file: str, path: str = '.') -> _pd.DataFrame:
    """

    Args:
        file: the file containing the field map data
        path: path to the field mpa data file

    Returns:
        A Numpy array containing the mesh points and the associated field values.
    """
    return _pd.read_csv(os.path.join(path, file), skiprows=9, sep=r'\s+', header=None, names=[
        'X', 'Y', 'Z', 'BX', 'BY', 'BZ', 'MATCODE',
    ])


def from_analytic_expression(bx_expression: sympy = None, by_expression: sympy = None, bz_expression: sympy = None,
                             mesh: _np.ndarray = None) -> _pd.DataFrame:
    x, y, z = sympy.symbols('x:z')
    # TODO careful if bx, by or bz is zero or a number

    return _pd.DataFrame({'X': mesh[:, 0],
                          'Y': mesh[:, 1],
                          'Z': mesh[:, 2],
                          'BX': sympy.lambdify([x, y, z], bx_expression, 'numpy')(mesh[:, 0], mesh[:, 1], mesh[:, 2]),
                          'BY': sympy.lambdify([x, y, z], by_expression, 'numpy')(mesh[:, 0], mesh[:, 1], mesh[:, 2]),
                          'BZ': sympy.lambdify([x, y, z], bz_expression, 'numpy')(mesh[:, 0], mesh[:, 1], mesh[:, 2])
                          })


def enge(s: Union[float, _np.array],
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
         ) -> Union[float, _np.array]:
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

    # TODO is it correct ? should be amplitude * FE * FS
    return amplitude * ((1 / (1 + _np.exp(p_e))) + (1 / (1 + _np.exp(p_s))) - 1) + field_offset


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

    def __init__(self, field_map: _pd.DataFrame):
        """

        Args:
            field_map:
        """
        self._data = field_map
        self._reference_trajectory: Optional[_np.array] = None
        self._field_profile_fit: Optional[_np.array] = None
        self._filepath: str = ""

    def __repr__(self):
        return self._data.__repr__()

    @classmethod
    def load_from_opera(cls, file: str, path: str = '.'):
        """
        Factory method to load a field map from a Opera parent file.

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
        Factory method to load a field map from Opera parent files (field map and mesh definition).

        Args:
            field_file: the file containing the field map data
            mesh_file: the file containing the mesh data
            path: path to the field mpa data files

        Returns:
            A FieldMap loaded from files.
        """
        return cls(field_map=load_opera_fieldmap_with_mesh(field_file=field_file, mesh_file=mesh_file, path=path))

    @classmethod
    def generate_from_analytic_expression(cls, bx_expression: sympy = None, by_expression: sympy = None,
                                          bz_expression: sympy = None, mesh: _np.ndarray = None):
        """
        Factory method to generate a field map from analytic expressions

        Args:
            bx_expression: expression of the magnetic field in x
            by_expression: expression of the magnetic field in y
            bz_expression: expression of the magnetic field in z
            mesh: numpy array of sampling points

        Returns:
            A FieldMap generated from analytic expression.
        """
        return cls(field_map=from_analytic_expression(bx_expression=bx_expression, by_expression=by_expression,
                                                      bz_expression=bz_expression, mesh=mesh))

    def write(self, path: str = ".",
              filename: str = "tosca.table",
              binary: bool = False,
              columns=None):
        """
        Args:
            path: Path to write the field map (default: '.')
            filename: filename of the map (default: 'tosca.table')
            binary: write the field as a binary file. Use it for large fielmaps
            columns:

        Returns:
            """
        if columns is None:
            columns = ['Y', 'Z', 'X']

        # TODO
        if path is None:
            # The folder is directly deleted at the end of the function and the df is erased.
            p = tempfile.TemporaryDirectory()
            path = p.name

        if binary:
            filename = f"b_{filename}"
        filename = os.path.join(path, filename)
        self._filepath = os.path.abspath(filename)
        data = self._data.sort_values(by=columns)
        data = data.reindex(columns=['Y', 'Z', 'X', 'BY', 'BZ', 'BX'])
        if binary:
            # The method tofile from numpy must be used with access='stream' with Zgoubi
            data.values.tofile(filename)
        else:
            data.to_csv(filename,
                        sep='\t',
                        header=False,
                        index=False)

    @property
    def file(self):
        return self._filepath

    @property
    def df(self):
        """Field map dataframe."""
        return self._data

    @property
    def data(self):
        """Field map raw data in a numpy array."""
        return self._data.values

    @property
    def reference_trajectory(self) -> _np.array:
        """Reference trajectory attached to the field map."""
        return self._reference_trajectory

    @property
    def field_profile_fit(self) -> _np.array:
        """Fit of the field profile."""
        return self._field_profile_fit

    @property
    def mesh_sampling_x(self) -> Tuple[_np.array, int]:
        """Sampling points of the field map along the X axis."""
        return self.mesh_sampling_along_axis(axis=0)

    @property
    def mesh_sampling_y(self) -> Tuple[_np.array, int]:
        """Sampling points of the field map along the Y axis."""
        return self.mesh_sampling_along_axis(axis=1)

    @property
    def mesh_sampling_z(self) -> Tuple[_np.array, int]:
        """Sampling points of the field map along the Z axis."""
        return self.mesh_sampling_along_axis(axis=2)

    def mesh_sampling_along_axis(self, axis: int) -> Tuple[_np.array, int]:
        """
        Sampling points of the field map along a given axis.

        Args:
            axis: the index of the axis.

        Returns:
            A numpy array containing the data points of the field map sampling.
        """
        _ = _np.unique(self.data[:, axis])
        return _, len(_)

    def translate(self, x: float = 0, y: float = 0, z: float = 0):
        """

        Args:
            x:
            y:
            z:

        Returns:

        """
        self._data['X'] -= x
        self._data['Y'] -= y
        self._data['Z'] -= z
        return self

    def rotate(self):
        """TODO"""
        pass

    def slice(self, slicing: str = 'Z == 0'):
        """
        Slices the field map following a slicing query.

        Args:
            slicing: the slicing query string

        Returns:
            The object itself (allows method chaining).
        """
        self._data.query(slicing, inplace=True)
        return self

    def sample(self, points, field_component: str = 'MOD', method: str = 'nearest'):
        """

        Args:
            points:
            field_component: field component to be sampled ('BX', 'BY', 'BZ' or 'MOD')
            method: method used for the grid interpolation ('nearest' or 'linear')

        Returns:

        """
        if points is None:
            raise ValueError("The sampling points are not defined (`points is None`).")
        # The lambda trick is used so that the modulus is only computed if needed
        field_components = {
            'BX': lambda: self.data[:, 3],
            'BY': lambda: self.data[:, 4],
            'BZ': lambda: self.data[:, 5],
            'MOD': lambda: _np.sqrt((self.data[:, 3:6] * self.data[:, 3:6]).sum(axis=1)),
        }
        return interpolate.griddata(self.data[:, 0:3], field_components[field_component](), points, method=method)

    def attach_cartesian_trajectory(self,
                                    axis: int = 0,
                                    lower: Optional[float] = None,
                                    upper: Optional[float] = None,
                                    samples: Optional[int] = None,
                                    offset_x: float = 0.0,
                                    offset_y: float = 0.0,
                                    offset_z: float = 0.0,
                                    ):
        """
        TODO: support arbitrary rotations

        Args:
            axis:
            lower:
            upper:
            samples:
            offset_x:
            offset_y:
            offset_z:

        Returns:

        """
        length_sampling = samples or self.mesh_sampling_along_axis(axis)[1]
        lower = lower or _np.min(self.mesh_sampling_along_axis(axis)[0])
        upper = upper or _np.max(self.mesh_sampling_along_axis(axis)[0])
        sampling = _np.linspace(lower, upper, length_sampling)
        zeros = _np.zeros(length_sampling)
        if axis == 'X':
            v = [sampling, zeros, zeros]
        elif axis == 'Y':
            v = [zeros, sampling, zeros]
        elif axis == 'Z':
            v = [zeros, zeros, sampling]
        else:
            raise ValueError("Invalid value for 'axis'.")
        v[0] += offset_x
        v[1] += offset_y
        v[2] += offset_z
        self._reference_trajectory = _np.stack(v).T
        return self

    def attach_polar_trajectory(self,
                                radius: float,
                                lower_angle: float,
                                upper_angle: float,
                                samples: int,
                                plane: str = 'XY',
                                offset_x: float = 0.0,
                                offset_y: float = 0.0,
                                offset_z: float = 0.0,
                                ):
        """

        Args:
            radius:
            lower_angle:
            upper_angle:
            samples:
            plane:
            offset_x:
            offset_y:
            offset_z:

        Returns:

        """

        angles = _np.linspace(lower_angle, upper_angle, samples)
        x = _np.cos(angles) * radius
        y = _np.sin(angles) * radius
        zeros = _np.zeros(samples)
        if plane == 'XY':
            v = [x, y, zeros]
        elif plane == 'YZ':
            v = [zeros, x, y]
        elif plane == 'XZ':
            v = [x, zeros, y]
        else:
            raise ValueError("Invalid value for 'plane'.")
        v[0] += offset_x
        v[1] += offset_y
        v[2] += offset_z
        self._reference_trajectory = _np.stack(v).T
        return self

    def fit_field_profile(self,
                          model: Optional[lmfit.Model] = None,
                          field_component: str = 'MOD',
                          sampling_method: str = 'nearest') -> lmfit.model.ModelResult:
        """

        Args:
            model:
            field_component:
            sampling_method:

        Returns:

        """
        if self.reference_trajectory is None:
            raise ValueError("The reference trajectory is not defined.")
        model = model or EngeModel()
        fit = model.fit(
            self.sample(self.reference_trajectory, field_component=field_component, method=sampling_method),
            model.params,
            s=_np.linalg.norm(self.reference_trajectory - self.reference_trajectory[0], axis=1),
        )
        self._field_profile_fit = fit
        return fit

    def plot_field_profile(self, ax, field_component: str = 'MOD', sampling_method: str = 'nearest'):
        """

        Args:
            ax:
            field_component:
            sampling_method:

        Returns:

        """
        if self.reference_trajectory is not None:
            ax.plot(
                _np.linalg.norm(self.reference_trajectory - self.reference_trajectory[0], axis=1),
                self.sample(self.reference_trajectory, field_component=field_component, method=sampling_method),
                'bo',
                ms=1,
            )
        if self.field_profile_fit is not None:
            ax.plot(
                _np.linalg.norm(self._reference_trajectory - self._reference_trajectory[0], axis=1),
                self.field_profile_fit.best_fit,
                'r-',
            )

    def plot_field_map(self, ax, field_component: str, plane1: int = 0, plane2: int = 2, bins: int = 50):
        """

        Args:
            ax:
            field_component:
            plane1:
            plane2:
            bins:

        Returns:

        """
        ax.hist2d(self.data[:, plane1], self.data[:, plane2], weights=self.df[field_component], bins=bins)
        if self.reference_trajectory is not None:
            ax.plot(self.reference_trajectory[:, plane1], self.reference_trajectory[:, plane2], linewidth=5)

    def export_for_bdsim(self, method: str = 'nearest'):
        """

        Args:
            method: method used for the grid interpolation ('nearest' or 'linear')

        Returns:

        """
        new_mesh = _np.mgrid[
                   self.mesh_sampling_x[0].min():self.mesh_sampling_x[0].max():100j,
                   self.mesh_sampling_y[0].min():self.mesh_sampling_y[0].max():100j,
                   self.mesh_sampling_z[0].min():self.mesh_sampling_z[0].max():100j
                   ].T.reshape(100 ** 3, 3)

        fx = -self.sample(new_mesh, field_component='BX', method=method)
        fy = -self.sample(new_mesh, field_component='BY', method=method)
        fz = -self.sample(new_mesh, field_component='BZ', method=method)
        return _np.concatenate([new_mesh, _np.stack([fx, fy, fz]).T], axis=1)
