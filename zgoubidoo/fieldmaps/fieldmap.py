"""Field map module."""
from typing import Optional, Union, Tuple, Type
import os
import lmfit
import sympy as _sp
import tempfile
import shutil
import numpy as _np
import pandas as _pd
from scipy import interpolate
from lmfit import Model as _Model
from ..units import _ureg as _ureg
from ..commands import fieldmaps as _fieldmaps
from ..commands import ZgoubidooException as _ZgoubidooException


def compute_xi_range_with_edge_angle(tau, d_y, ymax, d_z, zmin, IZ, y_range):
    d_xi = tau * d_y
    n_factor = round(d_z / d_xi)
    if n_factor == 0:
        n_factor = 1
    d_xi = d_z / n_factor
    d_y = d_xi / tau
    xi_supp = tau * ymax.m_as('m')
    n_xi_supp = round(xi_supp / d_xi + 0.5)

    IXI = IZ * n_factor + n_xi_supp
    xi_min = zmin.to('m') - n_xi_supp * d_xi * _ureg.m
    IY = round(y_range / d_y + 0.5)
    return d_xi, d_y, IXI, xi_min, n_factor, n_xi_supp, IY


def compute_xi_range_without_edge_angle(d_z, IZ, zmin, IY_approx):
    d_xi = d_z
    IXI = IZ
    xi_min = zmin.to('m')
    n_factor = 1
    n_xi_supp = 0
    IY = IY_approx
    return d_xi, IXI, xi_min, n_factor, n_xi_supp, IY


def compute_range_and_steps(xmin: _Q, xmax: _Q, ymin: _Q, ymax: _Q, zmin: _Q, zmax: _Q,
                            IX, IY_approx, IZ,
                            tau):
    xi_max = zmax
    x_range = (xmax - xmin).m_as('m')
    y_range = (ymax - ymin).m_as('m')
    z_range = (zmax - zmin).m_as('m')

    d_z = z_range / IZ
    d_y = y_range / IY_approx
    d_x = x_range / IX

    if tau != 0.0:
        d_xi, d_y, IXI, xi_min, n_factor, n_xi_supp, IY = compute_xi_range_with_edge_angle(tau, d_y, ymax, d_z, zmin,
                                                                                           IZ, y_range)

    else:
        d_xi, IXI, xi_min, n_factor, n_xi_supp, IY = compute_xi_range_without_edge_angle(d_z, IZ, zmin, IY_approx)

    return xi_min, xi_max, IXI, d_xi, d_x, n_xi_supp, n_factor, d_y, IY


def compute_A_matrix(n, k, tau):
    a = _np.zeros(((n + 1) + 1, (2 * n + 2) + 1))
    a[0, 0] = 1 / k

    for i in range(_np.shape(a)[0] - 1):
        for j in range(2 * (i + 1) + 1):
            if j == 0:
                a[i + 1, j] = -k ** 2 * a[i, j]
            if j == 1:
                a[i + 1, j] = -k ** 2 * a[i, j] + 2 * k * tau * a[i, j - 1]
            else:
                a[i + 1, j] = -k ** 2 * a[i, j] + 2 * k * tau * a[i, j - 1] - (1 + tau ** 2) * a[i, j - 2]
    return a


def compute_T_matrix(n_prime):
    t = _np.zeros((n_prime + 1, (n_prime + 1) + 1))
    t[0, 1] = 1
    for i in range(_np.shape(t)[0] - 1):
        for j in range(0, i + 3):
            if j == 0:
                t[i + 1, j] = (j + 1) * t[i, j + 1]
            elif j == i + 2:
                t[i + 1, j] = - (j - 1) * t[i, j - 1]
            else:
                t[i + 1, j] = (j + 1) * t[i, j + 1] - (j - 1) * t[i, j - 1]
    return t


def compute_tanh_multiple_orders(l, L, IXI, d_xi, xi_min, n_prime):
    tan = _np.zeros(((n_prime + 1) + 1, IXI + 1))
    for j in range(_np.shape(tan)[0]):
        for xixi in range(IXI + 1):
            xi = xi_min.to('m').magnitude + xixi * d_xi
            t_1j = (_np.tanh(xi / l)) ** j
            t_2j = (_np.tanh((xi - L) / l)) ** j
            tan[j, xixi] = t_1j - t_2j
    return tan


def compute_fringe_field_function_derivatives(gap, Lmag, n_prime, IXI, d_xi, xi_min):
    l = gap.to('m').magnitude
    L = Lmag.to('m').magnitude
    t = compute_T_matrix(n_prime)
    tan = compute_tanh_multiple_orders(l, L, IXI, d_xi, xi_min, n_prime)

    scaling = _np.zeros((n_prime + 1, 1))
    for nn in range(n_prime + 1):
        scaling[nn, :] = 1 / (2 * l ** nn)
    f_nprime = t.dot(tan)
    f_nprime = scaling * f_nprime
    return f_nprime


def compute_g_h_matrix(n, a, f_nprime):
    g = a[:, 0:2 * n + 1].dot(f_nprime[0:2 * n + 1, :])
    h = a[:, 0:2 * n + 1].dot(f_nprime[1:2 * n + 2, :])
    return g, h


def compute_field_in_initial_plane(d_x, IX, n, xmin, g, h, B0, k, tau):
    # B DANS LE PLAN XI_Z pour Y=0

    X = _np.zeros((IX + 1, n + 1))
    X_prime = _np.zeros((IX + 1, n + 1))

    for xx in range(IX + 1):
        x = xmin.to('m').magnitude + xx * d_x
        for nn in range(n + 1):
            X[xx, nn] = x ** (2 * nn + 1) / _np.math.factorial(2 * nn + 1)
            X_prime[xx, nn] = x ** (2 * nn) / _np.math.factorial(2 * nn)

    BX = B0 * X.dot(g[1:, :])
    BY = B0 * X_prime.dot(k * g[0:n + 1, :] - tau * h[0:n + 1, :])
    BZ = B0 * X_prime.dot(h[0:n + 1, :])
    B = _np.dstack((BX, BY, BZ))
    return B


def compute_total_fieldmap(B, tau, k, IY, ymin, d_y, n_xi_supp, IXI, n_factor):
    B_fieldmap = []

    if tau != 0.0:
        for yy in range(IY + 1):
            y = ymin.to("m").magnitude + yy * d_y
            B_XXI = copy.deepcopy(B[:, n_xi_supp - yy:IXI + 1 - yy, :])
            B_XXI = _np.exp(k * y) * B_XXI
            B_XZ = copy.deepcopy(B_XXI[:, ::n_factor, :])
            B_fieldmap.append(B_XZ)
    else:
        for yy in range(IY + 1):
            y = ymin.to("m").magnitude + yy * d_y
            B_XXI = copy.deepcopy(B[:, :IXI + 1, :])
            B_XXI = _np.exp(k * y) * B_XXI
            B_XZ = copy.deepcopy(B_XXI[:, ::n_factor, :])
            B_fieldmap.append(B_XZ)

    B_fieldmap = _np.array(B_fieldmap)
    return B_fieldmap


def generate_vFFA_fieldmap(B0: _Q, k: _Q, tau: int, Lmag: _Q, gap: _Q,
                                      xmin: _Q, xmax: _Q, ymin: _Q, ymax: _Q, z_ff_1: _Q, z_ff_2: _Q,
                                      n: int, IX: int, IY_approx: int, IZ: int):
    k, B0 = k.m_as('1/m'), B0.to('kilogauss')
    xmin, xmax, ymin, ymax, z_ff_1, z_ff_2 = xmin.to('m'), xmax.to('m'), ymin.to('m'), ymax.to('m'), z_ff_1.to(
        'm'), z_ff_2.to('m')
    Lmag, gap = Lmag.to('m'), gap.to('m')
    zmin = - z_ff_1
    zmax = Lmag + z_ff_2

    xi_min, xi_max, IXI, d_xi, d_x, n_xi_supp, n_factor, d_y, IY = compute_range_and_steps(xmin, xmax, ymin, ymax,
                                                                                           zmin, zmax, IX, IY_approx,
                                                                                           IZ, tau)

    a = compute_A_matrix(n, k, tau)
    n_prime = 2 * n + 2
    f_nprime = compute_fringe_field_function_derivatives(gap, Lmag, n_prime, IXI, d_xi, xi_min)
    g, h = compute_g_h_matrix(n, a, f_nprime)
    B = compute_field_in_initial_plane(d_x, IX, n, xmin, g, h, B0, k, tau)
    B_fieldmap = compute_total_fieldmap(B, tau, k, IY, ymin, d_y, n_xi_supp, IXI, n_factor)

    B_fieldmap_reshaped = B_fieldmap.reshape((IY + 1) * (IX + 1) * (IZ + 1), 3)

    x_val = _np.linspace(xmin.m_as('cm'), xmax.m_as('cm'), IX + 1)
    y_val = _np.linspace(ymin.m_as('cm'), ymax.m_as('cm'), IY + 1)
    z_val = _np.linspace((zmin + z_ff_1).m_as('cm'), (zmax + z_ff_1).m_as('cm'), IZ + 1)
    mesh = _np.array(list(product(y_val, x_val, z_val)))

    fieldmap = _pd.DataFrame({"Y": mesh[:, 1], "Z": mesh[:, 0], "X": mesh[:, 2], "BY": B_fieldmap_reshaped[:, 0],
                              "BZ": B_fieldmap_reshaped[:, 1], "BX": B_fieldmap_reshaped[:, 2]})

    return fieldmap


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
    x, y, z = sympy.symbols('x:z')
    bx = sympy.lambdify([x, y, z], bx_expression)
    by = sympy.lambdify([x, y, z], by_expression)
    bz = sympy.lambdify([x, y, z], bz_expression)

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
        self._path: str = ""
        self._filepath: str = ""

    def __repr__(self):
        return self._data.__repr__()

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
            if self._input.length == 0 * _ureg.cm:
                raise _ZgoubidooException("Length of your map is 0*cm, please check your input")

        return self._input

    @property
    def length(self):
        return self._input.length

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
    def generate_from_expression(cls, bx_expression: sympy = None, by_expression: sympy = None,
                                 bz_expression: sympy = None, mesh: _np.ndarray = None, use_njit: bool = True):
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
                                                      bz_expression=bz_expression, mesh=mesh, use_njit=use_njit))

    @staticmethod
    def get_off_plane_field(bx_expression,
                            by_expression,
                            bz_expression,
                            nterms: int = 4):

        x, y, z = _sp.symbols('x:z')
        Bx_mid = _sp.Function('Bx')(x, z)
        By_mid = _sp.Function('By')(x, z)
        Bz_mid = _sp.Function('Bz')(x, z)

        ax = _sp.zeros(1, nterms)
        ay = _sp.zeros(1, nterms)
        az = _sp.zeros(1, nterms)

        ax[0] = [_sp.Derivative(Bz_mid, x)]
        ay[0] = [_sp.Derivative(Bz_mid, y)]
        az[0] = [-(_sp.Derivative(Bx_mid, x) + _sp.Derivative(By_mid, y))]

        # Compute the a_i
        for i in range(1, nterms):
            az[i] = -(1 / (i + 1)) * (_sp.Derivative(ax[i - 1], x) + _sp.Derivative(ay[i - 1], y))
            ax[i] = (1 / (i + 1)) * _sp.Derivative(az[i - 1], x)
            ay[i] = (1 / (i + 1)) * _sp.Derivative(az[i - 1], y)

        Bx_off = Bx_mid
        By_off = By_mid
        Bz_off = Bz_mid

        for i in range(0, nterms - 1):
            Bx_off += ax[i] * z ** (i + 1)
            By_off += ay[i] * z ** (i + 1)
            Bz_off += az[i] * z ** (i + 1)

        B_x = Bx_off.replace(Bx_mid, bx_expression).replace(By_mid, by_expression).replace(Bz_mid, bz_expression).simplify()
        B_y = By_off.replace(Bx_mid, bx_expression).replace(By_mid, by_expression).replace(Bz_mid, bz_expression).simplify()
        B_z = Bz_off.replace(Bx_mid, bx_expression).replace(By_mid, by_expression).replace(Bz_mid, bz_expression).simplify()

        return B_x, B_y, B_z

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
        if axis == 0:
            v = [sampling, zeros, zeros]
        elif axis == 1:
            v = [zeros, sampling, zeros]
        elif axis == 2:
            v = [zeros, zeros, sampling]
        else:
            raise ValueError("Invalid value for 'axis'.")
        v[0] += offset_x
        v[1] += offset_y
        v[2] += offset_z
        self._reference_trajectory = _np.stack(v).T

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


class VFFAFieldMap(FieldMap):

    def __init__(self, field_map: _pd.DataFrame):
        super().__init__(field_map)

    @classmethod
    def generate(cls, B0, k, tau, Lmag, gap,
                 xmin, xmax, ymin, ymax, z_ff_1, z_ff_2,
                 n, IX, IY_approx, IZ):
        """
        Method to generate a vFFA field map, with tanh fringe field and possible edge angle

        Args:
            B0: Reference magnetic field
            k: Field index
            tau: Tangent of the edge angle
            Lmag: Length of the magnet
            gap: Fringe length
            xmin: Horizontal extent of the field map
            xmax : Horizontal extent of the field map
            ymin: Vertical extent of the field map
            ymax: Vertical extent of the field map
            z_ff_1: Additional length before the magnet for the longitudinal extent of the field map
            z_ff_2: Additional length after the magnet for the longitudinal extent of the field map
            n: Order of the expansion
            IX: Number of nodes of the mesh - X direction
            IY: Number of nodes of the mesh - Y direction
            IZ: Number of nodes of the mesh - Z direction

        Returns:
            A vFFA FieldMap.
        """
        return cls(field_map=generate_vFFA_fieldmap(B0, k, tau, Lmag, gap, xmin, xmax, ymin, ymax,
                                                    z_ff_1, z_ff_2, n, IX, IY_approx, IZ))
