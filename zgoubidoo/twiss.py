"""Step-by-step computation of the transfer matrix and Twiss parameters from Zgoubi tracks.

The functions in this module perform a first-order analysis of the dynamics, via the computation of the transfer matrix
and its parametrizations.

The standard uncoupled Twiss parametrization (including off-momentum effects, aka. dispersion) is the default option.

Additional formalisms for the parametrization of fully coupled transfer matrices are also available (Teng, Ripken,
etc.).

Example:
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    import zgoubidoo
    from zgoubidoo.commands import *
    _ = zgoubidoo.ureg

"""
from typing import Tuple, Optional, Union
import numpy as np
import pandas as pd
from .commands import PolarMagnet as _PolarMagnet
from .input import Input as _Input
from georges_core.sequences import BetaBlock as _BetaBlock
import zgoubidoo


def _get_parameters(m: pd.DataFrame, twiss: Optional[_BetaBlock], plane: int = 1) -> Tuple:
    """Extract parameters from the DataFrame."""
    p = 1 if plane == 1 else 3
    v = 1 if plane == 1 else 2
    r11: pd.Series = m[f"R{p}{p}"]
    r12: pd.Series = m[f"R{p}{p+1}"]
    r21: pd.Series = m[f"R{p+1}{p}"]
    r22: pd.Series = m[f"R{p+1}{p+1}"]
    if twiss is not None:
        alpha: float = twiss[f"ALPHA{v}{v}"]
        beta: float = twiss[f"BETA{v}{v}"]
        gamma: float = twiss[f"GAMMA{v}{v}"]
        return r11, r12, r21, r22, alpha, beta, gamma
    else:
        return r11, r12, r21, r22


def compute_alpha_from_matrix(m: pd.DataFrame, twiss: _BetaBlock, plane: int = 1) -> pd.Series:
    """
    Computes the Twiss alpha values at every steps of the input step-by-step transfer matrix.

    Args:
        m: the step-by-step transfer matrix for which the alpha values should be computed
        twiss: the initial Twiss values
        plane: an integer representing the plane (1 or 2)

    Returns:
        a Pandas Series with the alpha values computed at all steps of the input step-by-step transfer matrix
    """
    r11, r12, r21, r22, alpha, beta, gamma = _get_parameters(m, twiss, plane)
    return -r11 * r21 * beta + r12 * r21 * alpha + r11 * r12 * gamma


def compute_beta_from_matrix(m: pd.DataFrame, twiss: _BetaBlock, plane: int = 1, strict: bool = False) -> pd.Series:
    """
    Computes the Twiss beta values at every steps of the input step-by-step transfer matrix.

    Args:
        m: the step-by-step transfer matrix for which the beta values should be computed
        twiss: the initial Twiss values
        plane: an integer representing the plane (1 or 2)
        strict: flag to activate the strict mode: checks and ensures that all computed beta are positive

    Returns:
        a Pandas Series with the beta values computed at all steps of the input step-by-step transfer matrix
    """
    r11, r12, r21, r22, alpha, beta, gamma = _get_parameters(m, twiss, plane)
    _ = r11**2 * beta - 2.0 * r11 * r12 * alpha + r12**2 * gamma
    if strict:
        assert (_ > 0).all(), "Not all computed beta are positive."
    return _


def compute_gamma_from_matrix(m: pd.DataFrame, twiss: _BetaBlock, plane: int = 1) -> pd.Series:
    """
    Computes the Twiss gamma values at every steps of the input step-by-step transfer matrix.

    Args:
        m: the step-by-step transfer matrix for which the beta values should be computed
        twiss: the initial Twiss values
        plane: an integer representing the plane (1 or 2)

    Returns:
        a Pandas Series with the gamma values computed at all steps of the input step-by-step transfer matrix
    """
    r11, r12, r21, r22, alpha, beta, gamma = _get_parameters(m, twiss, plane)
    return r21**2 * beta - 2.0 * r21 * r22 * alpha + r22**2 * gamma


def compute_mu_from_matrix(m: pd.DataFrame, twiss: _BetaBlock, plane: int = 1) -> pd.Series:
    """
    Computes the phase advance values at every steps of the input step-by-step transfer matrix.

    Args:
        m: the step-by-step transfer matrix for which the beta values should be computed
        twiss: the initial Twiss values
        plane: an integer representing the plane (1 or 2)

    Returns:
        a Pandas Series with the phase advance computed at all steps of the input step-by-step transfer matrix
    """
    r11, r12, r21, r22, alpha, beta, gamma = _get_parameters(m, twiss, plane)
    return np.arctan2(r12, r11 * beta - r12 * alpha)


def compute_jacobian_from_matrix(m: pd.DataFrame, plane: int = 1) -> pd.Series:
    """
    Computes the jacobian of the 2x2 transfer matrix (useful to verify the simplecticity).

    Args:
        m: the step-by-step transfer matrix for which the jacobians should be computed
        plane: an integer representing the plane (1 or 2)

    Returns:
        a Pandas Series with the jacobian computed at all steps of the input step-by-step transfer matrix
    """
    r11, r12, r21, r22 = _get_parameters(m, None, plane)
    return r11 * r22 - r12 * r21


def compute_dispersion_from_matrix(m: pd.DataFrame, twiss: _BetaBlock, plane: int = 1) -> pd.Series:
    """
    Computes the dispersion function at every steps of the input step-by-step transfer matrix.

    Args:
        m: the step-by-step transfer matrix for which the dispersion function should be computed
        twiss: initial values for the Twiss parameters
        plane: an integer representing the plane (1 or 2)

    Returns:
        a Pandas Series with the dispersion function computed at all steps of the input step-by-step transfer matrix

    """
    p = 1 if plane == 1 else 3
    if p == 1:
        d0 = twiss['DISP1']
        dp0 = twiss['DISP2']
    else:
        d0 = twiss['DISP3']
        dp0 = twiss['DISP4']
    r11: pd.Series = m[f"R{p}{p}"]
    r12: pd.Series = m[f"R{p}{p + 1}"]
    r15: pd.Series = m[f"R{p}5"]
    return d0 * r11 + dp0 * r12 + r15


def compute_dispersion_prime_from_matrix(m: pd.DataFrame, twiss: _BetaBlock, plane: int = 1) -> pd.Series:
    """
    Computes the dispersion prime function at every steps of the input step-by-step transfer matrix.

    Args:
        m: the step-by-step transfer matrix for which the dispersion prime function should be computed
        twiss: initial values for the Twiss parameters
        plane: an integer representing the plane (1 or 2)

    Returns:
        a Pandas Series with the dispersion prime function computed at all steps of the input step-by-step transfer
        matrix

    Example:
        >>> 1 + 1 # TODO

    """
    p = 1 if plane == 1 else 3
    if p == 1:
        d0 = twiss['DISP1']
        dp0 = twiss['DISP2']
    else:
        d0 = twiss['DISP3']
        dp0 = twiss['DISP4']
    r21: pd.Series = m[f"R{p + 1}{p}"]
    r22: pd.Series = m[f"R{p + 1}{p + 1}"]
    r25: pd.Series = m[f"R{p + 1}5"]
    return d0 * r21 + dp0 * r22 + r25


def compute_periodic_twiss(matrix: pd.DataFrame, end: Union[int, str] = -1) -> pd.Series:
    """
    Compute twiss parameters from a transfer matrix which is assumed to be a periodic transfer matrix.

    Args:
        matrix: the (periodic) transfer matrix
        end:

    Returns:
        a Series object with the values of the periodic Twiss parameters.
    """
    if isinstance(end, int):
        m = matrix.iloc[end]
    elif isinstance(end, str):
        m = matrix[matrix.LABEL1 == end].iloc[-1]
    twiss = dict({
        'CMU1': (m['R11'] + m['R22'])/2.0,
        'CMU2': (m['R33'] + m['R44'])/2.0,
    })
    twiss['MU1'] = np.arccos(twiss['CMU1'])
    twiss['MU2'] = np.arccos(twiss['CMU2'])
    twiss['BETA11'] = m['R12'] / np.sin(twiss['MU1'])
    twiss['BETA22'] = m['R34'] / np.sin(twiss['MU2'])
    twiss['ALPHA11'] = (m['R11'] - m['R22']) / (2.0 * np.sin(twiss['MU1']))
    twiss['ALPHA22'] = (m['R33'] - m['R44']) / (2.0 * np.sin(twiss['MU2']))
    twiss['GAMMA11'] = -m['R21'] / np.sin(twiss['MU1'])
    twiss['GAMMA22'] = -m['R43'] / np.sin(twiss['MU2'])
    m44 = m[['R11', 'R12', 'R13', 'R14',
             'R21', 'R22', 'R23', 'R24',
             'R31', 'R32', 'R33', 'R34',
             'R41', 'R42', 'R43', 'R44']].apply(float).values.reshape(4, 4)
    r6 = m[['R15', 'R25', 'R35', 'R45']].apply(float).values.reshape(4, 1)
    disp = np.dot(np.linalg.inv(np.identity(4) - m44), r6).reshape(4)
    twiss['DY'] = disp[0]
    twiss['DYP'] = disp[1]
    twiss['DZ'] = disp[2]
    twiss['DZP'] = disp[3]
    twiss['DISP1'] = disp[0]
    twiss['DISP2'] = disp[1]
    twiss['DISP3'] = disp[2]
    twiss['DISP4'] = disp[3]

    return pd.Series(twiss)


def compute_twiss(matrix: pd.DataFrame,
                  twiss_init: Optional[_BetaBlock] = None,
                  with_phase_unrolling: bool = True
                  ) -> pd.DataFrame:
    """
    Uses a step-by-step transfer matrix to compute the Twiss parameters (uncoupled). The phase advance and the
    determinants of the jacobians are computed as well.

    Args:
        matrix: the input step-by-step transfer matrix
        twiss_init: the initial values for the Twiss computation (if None, periodic conditions are assumed and the
        Twiss parameters are computed from the transfer matrix).
        with_phase_unrolling: TODO

    Returns:
        the same DataFrame as the input, but with added columns for the computed quantities.
    """
    if twiss_init is None:
        twiss_init = compute_periodic_twiss(matrix)

    matrix['BETA11'] = compute_beta_from_matrix(matrix, twiss_init)
    matrix['BETA22'] = compute_beta_from_matrix(matrix, twiss_init, plane=2)
    matrix['ALPHA11'] = compute_alpha_from_matrix(matrix, twiss_init)
    matrix['ALPHA22'] = compute_alpha_from_matrix(matrix, twiss_init, plane=2)
    matrix['GAMMA11'] = compute_gamma_from_matrix(matrix, twiss_init)
    matrix['GAMMA22'] = compute_gamma_from_matrix(matrix, twiss_init, plane=2)
    matrix['MU1'] = compute_mu_from_matrix(matrix, twiss_init)
    matrix['MU2'] = compute_mu_from_matrix(matrix, twiss_init, plane=2)
    matrix['DET1'] = compute_jacobian_from_matrix(matrix)
    matrix['DET2'] = compute_jacobian_from_matrix(matrix, plane=2)
    matrix['DISP1'] = compute_dispersion_from_matrix(matrix, twiss_init)
    matrix['DISP2'] = compute_dispersion_prime_from_matrix(matrix, twiss_init)
    matrix['DISP3'] = compute_dispersion_from_matrix(matrix, twiss_init, plane=2)
    matrix['DISP4'] = compute_dispersion_prime_from_matrix(matrix, twiss_init, plane=2)

    def phase_unrolling(phi):
        """TODO"""
        if phi[0] < 0:
            phi[0] += 2 * np.pi
        for i in range(1, phi.shape[0] - 1):
            if phi[i] < 0:
                phi[i] += 2 * np.pi
            if phi[i - 1] - phi[i] > 0.5:
                phi[i:] += 2 * np.pi
        return phi

    try:
        from numba import njit
        phase_unrolling = njit(phase_unrolling)
    except ModuleNotFoundError:
        pass

    if with_phase_unrolling:
        matrix['MU1'] = phase_unrolling(matrix['MU1'].values)
        matrix['MU2'] = phase_unrolling(matrix['MU2'].values)

    return matrix


def align_tracks(tracks: pd.DataFrame,
                 align_on: str = 'S',
                 identifier: str = 'LET',
                 reference_track: str = 'O',
                 global_frame: bool = True) -> Tuple[np.array, pd.DataFrame]:
    """
    Align the tracks to obtain a homegenous array with all coordinates given at the same location.

    Required for example to compute the transfer matrix (not all particules would have integration step at the
    same coordinate and must be aligned. Uses a linear interpolation.

    Args:
        tracks: tracking data
        align_on: coordinates on which the tracks are aligned (typically 'X' or 'S')
        identifier: identifier of the column used for the particles indexing
        reference_track:
        global_frame:

    Returns:
        aligned data and reference data
    """
    if global_frame:
        coordinates: list = ['YG', 'TG', 'ZG', 'PG', 'D-1', 'Yo', 'To', 'Zo', 'Po', 'Do-1']  # Keep it in this order
    else:
        coordinates: list = ['Y', 'T', 'Z', 'P', 'D-1', 'Yo', 'To', 'Zo', 'Po', 'Do-1']  # Keep it in this order
    particules: list = ['O', 'A', 'C', 'E', 'G', 'I', 'B', 'D', 'F', 'H', 'J']  # Keep it in this order
    assert set(particules) == set(tracks[identifier].unique()), "Required particles not found (are you using Objet5?)."
    ref: pd.DataFrame = tracks.query(f"{identifier} == '{reference_track}'")[coordinates +
                                                                             [align_on,
                                                                              'LABEL1',
                                                                              'XG' if global_frame else 'X'
                                                                              ]]
    ref_alignment_values = ref[align_on].values
    assert np.all(np.diff(ref_alignment_values) >= 0), "The reference alignment values are not monotonously increasing"
    data = np.zeros((len(particules), ref_alignment_values.shape[0], len(coordinates)))
    data[0, :, :] = ref[coordinates].values
    for i, p in enumerate(particules[1:]):
        particule = tracks.query(f"{identifier} == '{p}'")
        for j, c in enumerate(coordinates):
            try:
                assert np.all(np.diff(particule[align_on].values) >= 0), \
                    "The alignment values are not monotonously increasing"
                data[i+1, :, j] = np.interp(ref_alignment_values, particule[align_on].values, particule[c].values)
            except ValueError:
                pass
    assert data.ndim == 3, "The aligned tracks do not form a homogenous array."
    return data, ref


def compute_transfer_matrix(beamline: _Input, tracks: pd.DataFrame, global_frame: bool = True) -> pd.DataFrame:
    """
    Constructs the step-by-step transfer matrix from tracking data (finite differences). The approximation
    uses the O(3) formula (not just the O(1) formula) and therefore makes use of all the 11 particles.

    Args:
        beamline: the Zgoubidoo Input beamline
        tracks: tracking data
        global_frame:

    Returns:
        a Panda DataFrame representing the transfer matrix

    Example:
        Here is a typical example to call ``compute_transfer_matrix``:

        >>> tracks = zgoubidoo.read_plt_file()
        >>> zi = zgoubidoo.Input()
        >>> matrix = zgoubidoo.twiss.compute_transfer_matrix(zi, tracks)
    """
    elements = tracks.LABEL1.unique()
    matrix = pd.DataFrame()
    for e in beamline.line:
        if e.LABEL1 not in elements:
            continue
        t = tracks[tracks.LABEL1 == e.LABEL1]
        data, ref = align_tracks(t, global_frame=global_frame)
        n_dimensions: int = 5
        normalization = [2 * (data[i + 1, :, i + n_dimensions] - data[0, :, i + n_dimensions])
                         for i in range(0, n_dimensions)
                         ]
        m = pd.DataFrame(
            {
                f"R{j + 1}{i + 1}": pd.Series(
                    (data[i + 1, :, j] - data[i + 1 + n_dimensions, :, j]) / normalization[i]
                )
                for i in range(0, n_dimensions)
                for j in range(0, n_dimensions)
            }
        )
        if isinstance(e, _PolarMagnet):
            m['S'] = ref['S'].values * 100 * e.radius.to('m').magnitude
        else:
            m['S'] = ref['S'].values
        m['LABEL1'] = e.LABEL1
        m['KEYWORD'] = e.KEYWORD
        if global_frame:
            m['X'] = ref['XG'].values
            m['Y'] = ref['YG'].values
            m['Z'] = ref['ZG'].values
        else:
            m['X'] = ref['X'].values
            m['Y'] = ref['Y'].values
            m['Z'] = ref['Z'].values
        matrix = matrix.append(m)
    # TODO this should most probably disapear
    # if global_frame:
    #     matrix['S'] += tracks['XG'].min()  # Global adjustment
    return matrix.reset_index()
