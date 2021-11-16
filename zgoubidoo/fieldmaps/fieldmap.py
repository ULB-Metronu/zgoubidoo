"""Field map module."""
from abc import ABC
from typing import Optional, Union, Tuple, Type, Dict
import os
import lmfit
import sympy as _sp
import tempfile
import shutil
import numpy as _np
import pandas as _pd
from scipy import interpolate
from lmfit import Model as _Model
from lmfit import Parameter as _Parameter
from ..units import _ureg as _ureg
from ..commands import fieldmaps as _fieldmaps
from ..commands import ZgoubidooException as _ZgoubidooException
from ..vis import ZgoubidooMatplotlibArtist as _ZgoubidooMatplotlibArtist
from ..vis import ZgoubidooPlotlyArtist as _ZgoubidooPlotlyArtist


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


def load(file: str, path: str = '.') -> _pd.DataFrame:
    # Check if the file is a binary
    if os.path.basename(file).startswith("b_"):  # This is a binary file
        fieldmap = _pd.DataFrame(data=_np.fromfile(os.path.join(path, file)).reshape(-1, 6),
                                 columns=['Y', 'Z', 'X', 'BY', 'BZ', 'BX'])
    else:
        fieldmap = _pd.read_csv(os.path.join(path, file), skiprows=8, names=['Y', 'Z', 'X', 'BY', 'BZ', 'BX'],
                                sep=r'\s+')
    return fieldmap


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


def generate_from_expression(bx_expression, by_expression, bz_expression,
                             mesh: _np.ndarray, use_njit: bool = True) -> _pd.DataFrame:
    x, y, z = _sp.symbols('x:z')
    bx = _sp.lambdify([x, y, z], bx_expression)
    by = _sp.lambdify([x, y, z], by_expression)
    bz = _sp.lambdify([x, y, z], bz_expression)

    if use_njit:
        try:
            from numba import njit
            bx = njit(bx)
            by = njit(by)
            bz = njit(bz)
        except ModuleNotFoundError:
            pass
        except ImportError:
            pass

    return _pd.DataFrame({'X': mesh[:, 0],
                          'Y': mesh[:, 1],
                          'Z': mesh[:, 2],
                          'BX': bx(mesh[:, 0], mesh[:, 1], mesh[:, 2]),
                          'BY': by(mesh[:, 0], mesh[:, 1], mesh[:, 2]),
                          'BZ': bz(mesh[:, 0], mesh[:, 1], mesh[:, 2])
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
         lmap: float = 1.0,
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
        offset_e: offset for the positioning of the entrance fall-off
        offset_s: offset for the positioning of the exit fall-off
        lmap: length of the map
        amplitude: field amplitude (not necessarily equal to the maximum)
        field_offset: field offset

    Returns:
        the value of the Enge function at coordinate s.
    """
    p_e = _np.polyval([ce_5, ce_4, ce_3, ce_2, ce_1, ce_0], -(s - offset_e) / lam_e)
    p_s = _np.polyval([cs_5, cs_4, cs_3, cs_2, cs_1, cs_0], (s - (lmap - offset_s)) / lam_s)

    return field_offset + (amplitude * (1 + _np.exp(p_e)) ** -1 * (1 + _np.exp(p_s)) ** -1)


class EngeModel(_Model, ABC):
    """Enge model to be used with lmfit."""

    def __init__(self):
        super().__init__(enge)
        self._params = None

    @property
    def params(self):
        """The parameters of the Enge model (interface to `lmfit.Model.make_params()`)."""
        if self._params is None:
            self._params = self.make_params()

        # Force some parameters to a minimal value
        self._params['lam_e'].min = 0
        self._params['lam_s'].min = 0
        self._params['offset_e'].min = 0
        self._params['offset_s'].min = 0
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
        self._path: str = ""
        self._filepath: str = ""
        self._length = 0 * _ureg.cm

    def __repr__(self):
        return self._data.__repr__()

    @property
    def length(self):
        return self._length

    @classmethod
    def load(cls, file: str, path: str = '.'):
        return cls(field_map=load(file, path))

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
    def generate_from_expression(cls, bx_expression: _sp = None, by_expression: _sp = None,
                                 bz_expression: _sp = None, mesh: _np.ndarray = None, use_njit: bool = True,
                                 generate_3d_map: bool = False, nterms: int = 4):
        """
        Factory method to generate a field map from analytic expressions

        Args:
            bx_expression: expression of the magnetic field in x
            by_expression: expression of the magnetic field in y
            bz_expression: expression of the magnetic field in z
            mesh: numpy array of sampling points
            use_njit: use njit to compute the field
            generate_3d_map: from the field at mid-plane, the expressions for off-plane field are generated
            nterms: number of terms to evaluate the off-plane field.
        Returns:
            A FieldMap generated from analytic expression.
        """
        if generate_3d_map:
            bx_expression, by_expression, bz_expression = cls.get_off_plane_field(bx_expression=bx_expression or 0,
                                                                                  by_expression=by_expression or 0,
                                                                                  bz_expression=bz_expression or 0,
                                                                                  nterms=nterms)

        return cls(field_map=generate_from_expression(bx_expression=bx_expression, by_expression=by_expression,
                                                      bz_expression=bz_expression, mesh=mesh, use_njit=use_njit))

    @staticmethod
    def get_off_plane_field(bx_expression,
                            by_expression,
                            bz_expression,
                            nterms: int = 4):

        x, y, z = _sp.symbols('x:z')
        bx_mid = _sp.Function('Bx')(x, z)
        by_mid = _sp.Function('By')(x, z)
        bz_mid = _sp.Function('Bz')(x, z)

        ax = _sp.zeros(1, nterms)
        ay = _sp.zeros(1, nterms)
        az = _sp.zeros(1, nterms)

        ax[0] = [_sp.Derivative(bz_mid, x)]
        ay[0] = [_sp.Derivative(bz_mid, y)]
        az[0] = [-(_sp.Derivative(bx_mid, x) + _sp.Derivative(by_mid, y))]

        # Compute the a_i
        for i in range(1, nterms):
            az[i] = -(1 / (i + 1)) * (_sp.Derivative(ax[i - 1], x) + _sp.Derivative(ay[i - 1], y))
            ax[i] = (1 / (i + 1)) * _sp.Derivative(az[i - 1], x)
            ay[i] = (1 / (i + 1)) * _sp.Derivative(az[i - 1], y)

        bx_off = bx_mid
        by_off = by_mid
        bz_off = bz_mid

        for i in range(0, nterms - 1):
            bx_off += ax[i] * z ** (i + 1)
            by_off += ay[i] * z ** (i + 1)
            bz_off += az[i] * z ** (i + 1)

        b_x = bx_off.replace(bx_mid, bx_expression).replace(by_mid, by_expression).replace(bz_mid,
                                                                                           bz_expression).simplify()
        b_y = by_off.replace(bx_mid, bx_expression).replace(by_mid, by_expression).replace(bz_mid,
                                                                                           bz_expression).simplify()
        b_z = bz_off.replace(bx_mid, bx_expression).replace(by_mid, by_expression).replace(bz_mid,
                                                                                           bz_expression).simplify()

        return b_x, b_y, b_z

    def cleanup(self):
        shutil.rmtree(self._path)

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

    def fit_field_profile(self,
                          model: Optional[lmfit.Model] = None,
                          field_component: str = 'MOD',
                          sampling_method: str = 'nearest',
                          fitting_method: str = 'leastsq',
                          initial_parameters: Dict[str, _Parameter] = None) -> lmfit.model.ModelResult:
        """

        Args:
            model:
            field_component:
            sampling_method:
            fitting_method: Method used to make the fit. See lmfit doc for usage
            initial_parameters: Give some initial value for the fit.

        Returns:
            The fit of the field
        """
        if self.reference_trajectory is None:
            raise ValueError("The reference trajectory is not defined.")
        model = model or EngeModel()

        samples = self.sample(self.reference_trajectory, field_component=field_component, method=sampling_method)
        sval = _np.linalg.norm(self.reference_trajectory - self.reference_trajectory[0], axis=1)

        if initial_parameters:
            for i in initial_parameters.items():
                model.params[i[0]] = i[1]

        # Define default values for EngeModel
        if isinstance(model, EngeModel):
            model.params['amplitude'].value = _np.max(samples)
            model.params['lmap'] = _Parameter('lmap', value=sval[-1], vary=False)
            model.params['offset_e'].value = 4 * model.params['lam_e'].value
            model.params['offset_s'].value = 4 * model.params['lam_s'].value

        fit = model.fit(
            samples,
            model.params,
            s=sval,
            method=fitting_method
        )
        self._field_profile_fit = fit
        return fit

    def plot_field_profile(self, ax, field_component: str = 'MOD', sampling_method: str = 'nearest'):
        """

        Args:
            ax: Instance of Artist, can be Matplotlib or Plotly
            field_component:
            sampling_method:
        Returns:

        """
        sval = _np.linalg.norm(self.reference_trajectory - self.reference_trajectory[0], axis=1)
        data = self.sample(self.reference_trajectory, field_component=field_component, method=sampling_method)
        fit_data = self.field_profile_fit.best_fit
        if isinstance(ax, _ZgoubidooMatplotlibArtist):
            if self.reference_trajectory is not None:
                ax.plot(
                    sval,
                    data,
                    'bo',
                    ms=1,
                )
            if self.field_profile_fit is not None:
                ax.plot(
                    sval,
                    fit_data,
                    'r-',
                )
        elif isinstance(ax, _ZgoubidooPlotlyArtist):
            if self.reference_trajectory is not None:
                ax.scatter(x=sval,
                           y=data,
                           mode='markers',
                           marker={'color': 'blue', 'symbol': 303},
                           name="data"
                           )
            if self.field_profile_fit is not None:
                ax.scatter(x=sval,
                           y=fit_data,
                           mode='lines',
                           line={'color': 'red', 'width': 2},
                           name="fit"
                           )
        else:
            raise _ZgoubidooException(f"{ax} is not a valid artist. Use ZgoubidooPlotlyArtist() or "
                                      f"ZgoubidooMatplotlibArtist")

    def plot_field_map(self,
                       ax,
                       field_component: str,
                       plane1: int = 0,
                       plane2: int = 1,
                       bins: int = 50,
                       colorscale: str = None):
        """
        Args:
            ax:
            field_component:
            plane1:
            plane2:
            bins:
            colorscale: colorscale to use for the field maps
        Returns:

        """
        if isinstance(ax, _ZgoubidooMatplotlibArtist):
            ax.hist2d(self.data[:, plane1], self.data[:, plane2], weights=self.df[field_component], bins=bins)
            if self.reference_trajectory is not None:
                ax.plot(self.reference_trajectory[:, plane1], self.reference_trajectory[:, plane2], linewidth=5)
        elif isinstance(ax, _ZgoubidooPlotlyArtist):
            ax.histogram2d(x=self.data[:, plane1],
                           y=self.data[:, plane2],
                           z=self.df[field_component].values,
                           nbinsx=bins,
                           nbinsy=bins,
                           histfunc='avg',
                           colorscale=colorscale or 'RdYlBu',
                           zsmooth='best',
                           reversescale=True,
                           colorbar={'title': "Bz [kG]"}
                           )
            if self.reference_trajectory is not None:
                ax.scatter(x=self.reference_trajectory[:, plane1],
                           y=self.reference_trajectory[:, plane2],
                           mode='lines',
                           line={'width': 2, 'color': 'black'}
                           )
        else:
            raise _ZgoubidooException(
                f"{ax} is not a valid artist. Use ZgoubidooPlotlyArtist() or ZgoubidooMatplotlibArtist")


class CartesianFieldMap(FieldMap):

    def __call__(self, label1: str = 'Map', path: str = None,
                 filename: str = 'tosca.table', binary: bool = False,
                 generator: Type[_fieldmaps.Tosca] = _fieldmaps.ToscaCartesian3D,
                 load_map: bool = True, columns=None, **kwargs):
        """

        Args:
            label1: Label of the keyword
            path: Path to write the map (default: tmpdir)
            filename: Name of the map
            binary: Field map is written as binary file with numpy (default: False)
            generator: Class used to generate the Zgoubi input (defaut: ToscaCartesian3D)
            load_map: Load map to compute its length (default: True)
            columns: Columns to use for the map
            **kwargs: Other arguments that can use for the TOSCA keyword (MOD, MOD2)

        Returns:
            the Zgoubi object for the fieldmap
        """

        self.write(path=path, filename=filename, binary=binary, columns=columns)
        self._input = generator(LABEL1=label1,
                                TITL="HEADER 0",
                                FILES=[self._filepath],
                                IX=self.mesh_sampling_x[1],
                                IY=self.mesh_sampling_y[1],
                                IZ=self.mesh_sampling_z[1],
                                infer_and_check_meshes=False,  # TODO method is only valid for csv file
                                **kwargs)
        if load_map:
            self._input.load()
            self._length = self._input.length
            if self._length == 0 * _ureg.cm:
                raise _ZgoubidooException("Length of your map is 0*cm, please check your input")
        return self._input

    def write(self, path: str = None,
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

        self._path = path or tempfile.mkdtemp()
        if binary:
            filename = f"b_{filename}"
        self._filepath = os.path.abspath(os.path.join(self._path, filename))
        data = self._data.sort_values(by=columns).reindex(columns=['Y', 'Z', 'X', 'BY', 'BZ', 'BX'])
        if binary:
            # The method to file from numpy must be used with access='stream' with Zgoubi
            data.values.tofile(self._filepath)
        else:
            data.to_csv(self._filepath,
                        sep='\t',
                        header=False,
                        index=False)

    @classmethod
    def generate_from_cartesian_expression(cls, bx_expression: _sp = None, by_expression: _sp = None,
                                           bz_expression: _sp = None, mesh: _np.ndarray = None,
                                           generate_3d_map: bool = False, nterms: int = 4):
        """
        Factory method to generate a field map from analytic expressions

        Args:
            bx_expression: expression of the magnetic field in x
            by_expression: expression of the magnetic field in y
            bz_expression: expression of the magnetic field in z
            mesh: numpy array of sampling points
            generate_3d_map: from the field at mid-plane, the expressions for off-plane field are generated
            nterms: number of terms to evaluate the off-plane field.
        Returns:
            A FieldMap generated from analytic expression.
        """
        if generate_3d_map:
            bx_expression, by_expression, bz_expression = cls.get_off_plane_field(bx_expression=bx_expression or 0,
                                                                                  by_expression=by_expression or 0,
                                                                                  bz_expression=bz_expression or 0,
                                                                                  nterms=nterms)

        return cls(field_map=generate_from_expression(bx_expression=bx_expression, by_expression=by_expression,
                                                      bz_expression=bz_expression, mesh=mesh))

    @property
    def mesh_sampling_x(self) -> Tuple[_np.array, int]:
        """Sampling points of the field map along the X axis."""
        return self.mesh_sampling_along_axis(axis='X')

    @property
    def mesh_sampling_y(self) -> Tuple[_np.array, int]:
        """Sampling points of the field map along the Y axis."""
        return self.mesh_sampling_along_axis(axis='Y')

    @property
    def mesh_sampling_z(self) -> Tuple[_np.array, int]:
        """Sampling points of the field map along the Z axis."""
        return self.mesh_sampling_along_axis(axis='Z')

    def mesh_sampling_along_axis(self, axis: str) -> Tuple[_np.array, int]:
        """
        Sampling points of the field map along a given axis.

        Args:
            axis: the index of the axis.

        Returns:
            A numpy array containing the data points of the field map sampling.
        """
        _ = self._data[axis].unique()
        return _, len(_)

    def attach_cartesian_trajectory(self,
                                    axis: str = 'X',
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


class PolarFieldMap(FieldMap):

    def __init__(self, field_map: _pd.DataFrame, mesh_sampling_radius: _np.ndarray = 0,
                 mesh_sampling_theta: _np.ndarray = 0, mesh_sampling_z: _np.ndarray = 0):
        super().__init__(field_map=field_map)
        self.mesh_sampling_radius = mesh_sampling_radius
        self.mesh_sampling_theta = mesh_sampling_theta
        self.mesh_sampling_vertical_position = mesh_sampling_z

    def __call__(self, label1: str = 'Map', path: str = None,
                 filename: str = 'tosca.table', binary: bool = False,
                 generator: Type[_fieldmaps.Tosca] = _fieldmaps.ToscaPolar,
                 load_map: bool = True, **kwargs):
        """

        Args:
            label1: Label of the keyword
            path: Path to write the map (default: tmpdir)
            filename: Name of the map
            binary: Field map is written as binary file with numpy (default: False)
            generator: Class used to generate the Zgoubi input (defaut: ToscaCartesian3D)
            load_map: Load map to compute its length (default: True)
            **kwargs: Other arguments that can use for the TOSCA keyword (MOD, MOD2)

        Returns:
            the Zgoubi object for the fieldmap
        """
        self.write(path=path, filename=filename, binary=binary)
        self._input = generator(LABEL1=label1,
                                TITL="HEADER 1",
                                FILES=[self._filepath],
                                IX=len(self.mesh_sampling_theta),
                                IY=len(self.mesh_sampling_radius),
                                IZ=len(self.mesh_sampling_vertical_position),
                                infer_and_check_meshes=False,  # TODO method is only valid for csv file
                                **kwargs)
        if load_map:
            self._input.load()
            self._length = self._input.length
            if self._length == 0 * _ureg.cm:
                raise _ZgoubidooException("Length of your map is 0*cm, please check your input")
        return self._input

    def write(self, path: str = None,
              filename: str = "tosca.table",
              binary: bool = False):
        """
        Args:
            path: Path to write the field map (default: '.')
            filename: filename of the map (default: 'tosca.table')
            binary: write the field as a binary file. Use it for large fielmaps

        Returns:
            """
        # TODO How to add a line to a binary file
        if binary:
            raise _ZgoubidooException("Binary format is not yet implemented for polar map")
        self._path = path or tempfile.mkdtemp()
        self._filepath = os.path.abspath(os.path.join(self._path, filename))
        data = self._data.reindex(columns=['Y', 'Z', 'X', 'BY', 'BZ', 'BX'])
        data.to_csv(self._filepath,
                    sep='\t',
                    header=False,
                    index=False)

        # Append first line to the file to indicate the reference radius and the mesh size
        # Rmi/cm, dR/cm, dA/deg, dZ/cm
        dr = self.mesh_sampling_radius[1] - self.mesh_sampling_radius[0]
        da = _np.degrees(self.mesh_sampling_theta[1] - self.mesh_sampling_theta[0])
        dz = 0

        with open(self._filepath, 'r+') as f:
            lines = f.readlines()  # read old content
            f.seek(0)  # go back to the beginning of the file
            f.write(f"{self.mesh_sampling_radius[0]} {dr} {da} {dz}\n")  # write new content at the beginning
            for line in lines:  # write old content after new
                f.write(line)

    @classmethod
    def generate_from_polar_expression(cls, bx_expression: _sp = None, by_expression: _sp = None,
                                       bz_expression: _sp = None, radius: _np.ndarray = None,
                                       theta: _np.ndarray = None, vertical_positions: _np.ndarray = None):
        """
        Factory method to generate a field map from analytic expressions

        Args:
            bx_expression: expression of the magnetic field in x
            by_expression: expression of the magnetic field in y
            bz_expression: expression of the magnetic field in z
            radius: numpy array of the radius
            theta: numpy array of the angles
            vertical_positions: Z position of the field map
        Returns:
            A FieldMap generated from analytic expression.
        """
        if vertical_positions is None:
            vertical_positions = _np.array([0])

        def compute_mesh(r_val, theta_val):
            x = _np.zeros(len(r_val) * len(theta_val) * len(vertical_positions))
            y = _np.zeros(len(r_val) * len(theta_val) * len(vertical_positions))
            z = _np.zeros(len(r_val) * len(theta_val) * len(vertical_positions))
            idx = 0
            for i in r_val:
                for j in theta_val:
                    x[idx] = i * _np.sin(j)
                    y[idx] = i * _np.cos(j)
                    z[idx] = vertical_positions[0]
                    idx += 1
            return _np.vstack((x, y, z)).T

        try:
            from numba import njit
            mesh = njit()(compute_mesh)(radius, theta)
        except ModuleNotFoundError:
            mesh = compute_mesh(radius, theta)
        except ImportError:
            mesh = compute_mesh(radius, theta)

        return cls(field_map=generate_from_expression(bx_expression=bx_expression, by_expression=by_expression,
                                                      bz_expression=bz_expression, mesh=mesh),
                   mesh_sampling_radius=radius, mesh_sampling_theta=theta,
                   mesh_sampling_z=vertical_positions)

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
        # TODO
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
