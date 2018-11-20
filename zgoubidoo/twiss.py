"""Step-by-step computation of the transfer matrix and Twiss parameters from Zgoubi tracks.

Blabla

Example:
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    import zgoubidoo
    from zgoubidoo.commands import *
    _ = zgoubidoo.ureg

"""
from typing import Tuple
import numpy as np
import pandas as pd
from .commands import Patchable
from .input import Input


def compute_alpha_from_matrix(m: pd.DataFrame, twiss: pd.Series, plane: int=1) -> pd.Series:
    """
    Computes the Twiss alpha values at every steps of the input step-by-step transfer matrix.

    Args:
        m: the step-by-step transfer matrix for which the alpha values should be computed
        twiss: the initial Twiss values
        plane: an integer representing the plane (1 or 2)

    Returns:
        a Pandas Series with the alpha values computed at all steps of the input step-by-step transfer matrix
    """
    p = 1 if plane == 1 else 3
    v = 1 if plane == 1 else 2
    r11: pd.Series = m[f"R{p}{p}"]
    r12: pd.Series = m[f"R{p}{p+1}"]
    r21: pd.Series = m[f"R{p+1}{p}"]
    r22: pd.Series = m[f"R{p+1}{p+1}"]
    alpha: float = twiss[f"ALPHA{v}{v}"]
    beta: float = twiss[f"BETA{v}{v}"]
    gamma: float = twiss[f"GAMMA{v}{v}"]
    return -r11 * r21 * beta + (r11 * r22 + r12 * r21) * alpha - r12 * r22 * gamma


def compute_beta_from_matrix(m: pd.DataFrame, twiss: pd.Series, plane: int=1, strict: bool=False) -> pd.Series:
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
    p = 1 if plane == 1 else 3
    v = 1 if plane == 1 else 2
    r11: pd.Series = m[f"R{p}{p}"]
    r12: pd.Series = m[f"R{p}{p+1}"]
    alpha: float = twiss[f"ALPHA{v}{v}"]
    beta: float = twiss[f"BETA{v}{v}"]
    gamma: float = twiss[f"GAMMA{v}{v}"]
    _ = np.square(r11) * beta - 2.0 * r11 * r12 * alpha + np.square(r12) * gamma
    if strict:
        assert (_ > 0).all(), "Not all computed beta are positive."
    return _


def compute_gamma_from_matrix(m: pd.DataFrame, twiss: pd.Series, plane: int=1) -> pd.Series:
    """
    Computes the Twiss gamma values at every steps of the input step-by-step transfer matrix.

    Args:
        m: the step-by-step transfer matrix for which the beta values should be computed
        twiss: the initial Twiss values
        plane: an integer representing the plane (1 or 2)

    Returns:
        a Pandas Series with the gamma values computed at all steps of the input step-by-step transfer matrix
    """
    p = 1 if plane == 1 else 3
    v = 1 if plane == 1 else 2
    r21: pd.Series = m[f"R{p+1}{p}"]
    r22: pd.Series = m[f"R{p+1}{p+1}"]
    alpha: float = twiss[f"ALPHA{v}{v}"]
    beta: float = twiss[f"BETA{v}{v}"]
    gamma: float = twiss[f"GAMMA{v}{v}"]
    return np.square(r21) * beta - 2.0 * r21 * r22 * alpha + np.square(r22) * gamma


def compute_mu_from_matrix(m: pd.DataFrame, twiss: pd.Series, beta=None, plane: int=1) -> pd.Series:
    """
    Computes the phase advance values at every steps of the input step-by-step transfer matrix.

    Args:
        m: the step-by-step transfer matrix for which the beta values should be computed
        twiss: the initial Twiss values
        beta: pre-computed step-by-step beta values (to improve effiency if already compyted)
        plane: an integer representing the plane (1 or 2)

    Returns:
        a Pandas Series with the phase advance computed at all steps of the input step-by-step transfer matrix
    """
    p = 1 if plane == 1 else 3
    v = 1 if plane == 1 else 2
    r11: pd.Series = m[f"R{p}{p}"]
    r12: pd.Series = m[f"R{p}{p+1}"]
    alpha0 = twiss[f"ALPHA{v}{v}"]
    beta0 = twiss[f"BETA{v}{v}"]
    if beta is None:
        beta = compute_beta_from_matrix(m, twiss, plane)
    return np.power(beta0 / beta, 0.5) * r11 - alpha0 * r12 / np.power(beta * beta0, 0.5)


def compute_jacobian_from_matrix(m: pd.DataFrame, plane: int=1) -> pd.Series:
    """
    Computes the jacobian of the 2x2 transfer matrix (useful to verify the simplecticity).

    Args:
        m: the step-by-step transfer matrix for which the jacobians should be computed
        plane: an integer representing the plane (1 or 2)

    Returns:
        a Pandas Series with the jacobian computed at all steps of the input step-by-step transfer matrix
    """
    p = 1 if plane == 1 else 3
    r11: pd.Series = m[f"R{p}{p}"]
    r12: pd.Series = m[f"R{p}{p+1}"]
    r21: pd.Series = m[f"R{p+1}{p}"]
    r22: pd.Series = m[f"R{p+1}{p+1}"]
    return r11 * r22 - r12 * r21


def compute_dispersion_from_matrix(m: pd.DataFrame, twiss: pd.Series, plane: int=1) -> pd.Series:
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
        d0 = twiss['DY']
        dp0 = twiss['DYP']
    else:
        d0 = twiss['DZ']
        dp0 = twiss['DZP']
    r11: pd.Series = m[f"R{p}{p}"]
    r12: pd.Series = m[f"R{p}{p + 1}"]
    r15: pd.Series = m[f"R{p}5"]
    return d0 * r11 + dp0 * r12 + r15


def compute_dispersion_prime_from_matrix(m: pd.DataFrame, twiss: pd.Series, plane: int=1) -> pd.Series:
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
        d0 = twiss['DY']
        dp0 = twiss['DYP']
    else:
        d0 = twiss['DZ']
        dp0 = twiss['DZP']
    r21: pd.Series = m[f"R{p + 1}{p}"]
    r22: pd.Series = m[f"R{p + 1}{p + 1}"]
    r25: pd.Series = m[f"R{p + 1}5"]
    return d0 * r21 + dp0 * r22 + r25


def compute_twiss(matrix: pd.DataFrame, twiss_init: pd.Series) -> pd.DataFrame:
    """
    Uses a step-by-step transfer matrix to compute the Twiss parameters (uncoupled). The phase advance and the
    determinants of the jacobians are computed as well.

    Args:
        matrix: the input step-by-step transfer matrix
        twiss_init: the initial values for the Twiss computation

    Returns:
        the same DataFrame as the input, but with added columns for the computed quantities.
    """
    matrix['BETA11'] = compute_beta_from_matrix(matrix, twiss_init, plane=1)
    matrix['BETA22'] = compute_beta_from_matrix(matrix, twiss_init, plane=2)
    matrix['ALPHA11'] = compute_alpha_from_matrix(matrix, twiss_init, plane=1)
    matrix['ALPHA22'] = compute_alpha_from_matrix(matrix, twiss_init, plane=2)
    matrix['GAMMA11'] = compute_gamma_from_matrix(matrix, twiss_init, plane=1)
    matrix['GAMMA22'] = compute_gamma_from_matrix(matrix, twiss_init, plane=2)
    matrix['MU1'] = compute_mu_from_matrix(matrix, twiss_init, plane=1, beta=matrix['BETA11'])
    matrix['MU2'] = compute_mu_from_matrix(matrix, twiss_init, plane=2, beta=matrix['BETA22'])
    matrix['DET1'] = compute_jacobian_from_matrix(matrix, plane=1)
    matrix['DET2'] = compute_jacobian_from_matrix(matrix, plane=2)
    matrix['DISP1'] = compute_dispersion_from_matrix(matrix, twiss_init, plane=1)
    matrix['DISP2'] = compute_dispersion_prime_from_matrix(matrix, twiss_init, plane=1)
    matrix['DISP3'] = compute_dispersion_from_matrix(matrix, twiss_init, plane=2)
    matrix['DISP4'] = compute_dispersion_prime_from_matrix(matrix, twiss_init, plane=2)
    return matrix


def align_tracks(tracks: pd.DataFrame,
                 align_on: str='X',
                 identifier: str='LET',
                 reference_track: str='O') -> Tuple[np.array, pd.DataFrame]:
    """
    Align the tracks to obtain a homegenous array with all coordinates given at the same location.

    Required for example to compute the transfer matrix (not all particules would have integration step at the
    same coordinate and must be aligned. Uses a linear interpolation.

    Args:
        tracks: tracking data
        align_on: coordinates on which the tracks are aligned (typically 'X' or 'S')
        identifier: identifier of the column used for the particles indexing
        reference_track:

    Returns:
        aligned data and reference data
    """
    coordinates: list = ['Y-DY', 'T', 'Z', 'P', 'D-1', 'Yo', 'To', 'Zo', 'Po', 'Do-1']  # Keep it in this order
    particules: list = ['O', 'A', 'C', 'E', 'G', 'I', 'B', 'D', 'F', 'H', 'J']  # Keep it in this order
    ref: pd.DataFrame = tracks.query(f"{identifier} == '{reference_track}'")[coordinates + [align_on, 'LABEL1']]
    alignment_values = ref[align_on].values
    assert np.all(np.diff(alignment_values) >= 0), "The reference alignment values are not monotonously increasing"
    data = np.zeros((len(particules), alignment_values.shape[0], len(coordinates)))
    data[0, :, :] = ref[coordinates].values
    for i, p in enumerate(particules[1:]):
        particule = tracks.query(f"{identifier} == '{p}'")
        for j, c in enumerate(coordinates):
            try:
                assert np.all(np.diff(particule[align_on].values) >= 0), \
                    "The alignment values are not monotonously increasing"
                data[i+1, :, j] = np.interp(alignment_values, particule[align_on].values, particule[c].values)
            except ValueError:
                pass
    assert data.ndim == 3, "The aligned tracks do not form a homogenous array."
    return data, ref


def compute_transfer_matrix(beamline: Input, tracks: pd.DataFrame, align_on: str='X') -> pd.DataFrame:
    """
    Constructs the step-by-step transfer matrix from tracking data (finite differences). The approximation
    uses the O(3) formula (not just the O(1) formula) and therefore makes use of all the particles.

    Args:
        beamline: the Zgoubidoo Input beamline
        tracks: tracking data
        align_on: coordinates on which the tracks are aligned (typically 'X' or 'S')

    Returns:
        a Panda DataFrame representing the transfer matrix

    Example:
        Here is a typical example to call ``compute_transfer_matrix``:

        >>> tracks = zgoubidoo.read_plt_file()
        >>> zi = zgoubidoo.Input()
        >>> matrix = zgoubidoo.twiss.compute_transfer_matrix(zi, tracks, align_on='X')
    """
    elements = tracks.LABEL1.unique()
    offset: float = 0
    matrix = pd.DataFrame()
    for e in beamline.line:
        if e.LABEL1 not in elements:
            if isinstance(e, Patchable):
                offset += (e.exit.x - e.entry.x).to('m').magnitude if align_on != 'S' else 0.0
            continue
        t = tracks[tracks.LABEL1 == e.LABEL1]
        data, ref = align_tracks(t, align_on=align_on)
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
        m['X'] = ref[align_on].values + offset
        m['S'] = ref[align_on].values + offset
        m['LABEL1'] = ref['LABEL1']
        matrix = matrix.append(m)
        offset += ref[align_on].max() if align_on != 'S' else 0.0
    return matrix.reset_index()
