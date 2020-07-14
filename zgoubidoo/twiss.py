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
from typing import Tuple, Optional
import numpy as _np
import pandas as _pd
from .input import Input as _Input
from georges_core.sequences import BetaBlock as _BetaBlock
from georges_core.twiss import compute_periodic_twiss, \
    compute_beta_from_matrix, \
    compute_alpha_from_matrix, \
    compute_mu_from_matrix, \
    compute_jacobian_from_matrix, \
    compute_gamma_from_matrix, \
    compute_dispersion_from_matrix, \
    compute_dispersion_prime_from_matrix
import zgoubidoo


def compute_twiss(matrix: _pd.DataFrame,
                  twiss_init: Optional[_BetaBlock] = None,
                  with_phase_unrolling: bool = True
                  ) -> _pd.DataFrame:
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
            phi[0] += 2 * _np.pi
        for i in range(1, phi.shape[0]):
            if phi[i] < 0:
                phi[i] += 2 * _np.pi
            if phi[i - 1] - phi[i] > 0.5:
                phi[i:] += 2 * _np.pi
        return phi

    try:
        from numba import njit
        phase_unrolling = njit(phase_unrolling)
    except ModuleNotFoundError:
        pass

    if with_phase_unrolling:
        matrix['MU1U'] = phase_unrolling(matrix['MU1'].values)
        matrix['MU2U'] = phase_unrolling(matrix['MU2'].values)

    return matrix


def align_tracks(tracks: _pd.DataFrame,
                 align_on: str = 'SREF',
                 identifier: str = 'LET',
                 reference_track: str = 'O',
                 ) -> Tuple[_np.array, _pd.DataFrame]:
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
    coordinates: list = ['YT', 'T', 'ZT', 'P', 'D-1', 'YT0', 'T0', 'ZT0', 'P0', 'Do']  # Keep it in this order
    particules: list = ['O', 'A', 'C', 'E', 'G', 'I', 'B', 'D', 'F', 'H', 'J']  # Keep it in this order
    assert set(particules) == set(tracks[identifier].unique()), \
        f"Required particles not found for element {tracks['LABEL1'].unique()[0]} (are you using Objet5?)."
    ref: _pd.DataFrame = tracks.query(f"{identifier} == '{reference_track}'")[coordinates +
                                                                              [align_on,
                                                                               'LABEL1',
                                                                               ]]
    ref_alignment_values = ref[align_on].values
    assert _np.all(_np.diff(ref_alignment_values) >= 0), "The reference alignment values " \
                                                         "are not monotonously increasing"
    data = _np.zeros((len(particules), ref_alignment_values.shape[0], len(coordinates)))
    data[0, :, :] = ref[coordinates].values
    for i, p in enumerate(particules[1:]):
        particule = tracks.query(f"{identifier} == '{p}'")
        for j, c in enumerate(coordinates):
            try:
                assert _np.all(_np.diff(particule[align_on].values) >= 0), \
                    "The alignment values are not monotonously increasing"
                data[i+1, :, j] = _np.interp(ref_alignment_values, particule[align_on].values, particule[c].values)
            except ValueError:
                pass
    assert data.ndim == 3, "The aligned tracks do not form a homogenous array."
    return data, ref


def compute_transfer_matrix(beamline: _Input, tracks: _pd.DataFrame) -> _pd.DataFrame:
    """
    Constructs the step-by-step transfer matrix from tracking data (finite differences). The approximation
    uses the O(3) formula (not just the O(1) formula) and therefore makes use of all the 11 particles.

    Args:
        beamline: the Zgoubidoo Input beamline
        tracks: tracking data

    Returns:
        a Panda DataFrame representing the transfer matrix

    Example:
        Here is a typical example to call ``compute_transfer_matrix``:

        >>> tracks = zgoubidoo.read_plt_file()
        >>> zi = zgoubidoo.Input()
        >>> matrix = zgoubidoo.twiss.compute_transfer_matrix(zi, tracks)
    """
    elements = tracks.LABEL1.unique()
    matrix = _pd.DataFrame()
    for e in beamline.line:
        if e.LABEL1 not in elements:
            continue
        t = tracks[tracks.LABEL1 == e.LABEL1]
        data, ref = align_tracks(t)
        n_dimensions: int = 5
        normalization = [2 * (data[i + 1, :, i + n_dimensions] - data[0, :, i + n_dimensions])
                         for i in range(0, n_dimensions)
                         ]
        m = _pd.DataFrame(
            {
                f"R{j + 1}{i + 1}": _pd.Series(
                    (data[i + 1, :, j] - data[i + 1 + n_dimensions, :, j]) / normalization[i]
                )
                for i in range(0, n_dimensions)
                for j in range(0, n_dimensions)
            }
        )
        m['S'] = ref['SREF'].values
        m['LABEL1'] = e.LABEL1
        m['KEYWORD'] = e.KEYWORD
        matrix = matrix.append(m)
    return matrix.reset_index()
