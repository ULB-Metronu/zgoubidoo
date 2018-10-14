from typing import Tuple
import numpy as np
import pandas as pd
from .commands import Patchable
from .input import Input


def compute_alpha_from_matrix(m: pd.DataFrame, twiss: pd.DataFrame, plane: int=1) -> pd.Series:
    """

    :param m:
    :param twiss:
    :param plane:
    :return:
    """
    p = 1 if plane == 1 else 3
    v = 1 if plane == 1 else 2
    R11: pd.Series = m[f"R{p}{p}"]
    R12: pd.Series = m[f"R{p}{p+1}"]
    R21: pd.Series = m[f"R{p+1}{p}"]
    R22: pd.Series = m[f"R{p+1}{p+1}"]
    ALPHA = twiss[f"ALPHA{v}{v}"]
    BETA = twiss[f"BETA{v}{v}"]
    GAMMA = twiss[f"GAMMA{v}{v}"]
    return -R11 * R21 * BETA + (R11 * R22 + R12 * R21) * ALPHA - R12 * R22 * GAMMA


def compute_beta_from_matrix(m, twiss, plane=1) -> pd.Series:
    """

    :param m:
    :param twiss:
    :param plane:
    :return:
    """
    p = 1 if plane == 1 else 3
    v = 1 if plane == 1 else 2
    R11 = m[f"R{p}{p}"]
    R12 = m[f"R{p}{p+1}"]
    #R21 = m[f"R{p+1}{p}"]
    #R22 = m[f"R{p+1}{p+1}"]
    ALPHA = twiss[f"ALPHA{v}{v}"]
    BETA = twiss[f"BETA{v}{v}"]
    GAMMA = twiss[f"GAMMA{v}{v}"]
    _ = R11**2 * BETA - 2.0 * R11 * R12 * ALPHA + R12**2 * GAMMA
    #assert (_ > 0).all(), "Not all computed beta are positive."
    return _


def compute_gamma_from_matrix(m, twiss, plane=1) -> pd.Series:
    """

    :param m:
    :param twiss:
    :param plane:
    :return:
    """
    p = 1 if plane == 1 else 3
    v = 1 if plane == 1 else 2
    #R11 = m[f"R{p}{p}"]
    #R12 = m[f"R{p}{p+1}"]
    R21 = m[f"R{p+1}{p}"]
    R22 = m[f"R{p+1}{p+1}"]
    ALPHA = twiss[f"ALPHA{v}{v}"]
    BETA = twiss[f"BETA{v}{v}"]
    GAMMA = twiss[f"GAMMA{v}{v}"]
    return R21**2 * BETA - 2.0 * R21 * R22 * ALPHA + R22**2 * GAMMA


def compute_mu_from_matrix(m, twiss, plane=1) -> pd.Series:
    """

    :param m:
    :param twiss:
    :param plane:
    :return:
    """
    return 0.0


def compute_jacobian_from_matrix(m, plane) -> pd.Series:
    """

    :param m:
    :param plane:
    :return:
    """
    p = 1 if plane == 1 else 3
    R11 = m[f"R{p}{p}"]
    R12 = m[f"R{p}{p+1}"]
    R21 = m[f"R{p+1}{p}"]
    R22 = m[f"R{p+1}{p+1}"]
    return R11 * R22 - R12 * R21


def compute_twiss(matrix: pd.DataFrame, twiss_init: pd.DataFrame) -> pd.DataFrame:
    """

    :param matrix:
    :param twiss_init:
    :return:
    """
    matrix['BETA11'] = compute_beta_from_matrix(matrix, twiss_init, 1)
    matrix['BETA22'] = compute_beta_from_matrix(matrix, twiss_init, 2)
    matrix['ALPHA11'] = compute_alpha_from_matrix(matrix, twiss_init, 1)
    matrix['ALPHA22'] = compute_alpha_from_matrix(matrix, twiss_init, 2)
    matrix['GAMMA11'] = compute_gamma_from_matrix(matrix, twiss_init, 1)
    matrix['GAMMA22'] = compute_gamma_from_matrix(matrix, twiss_init, 2)
    matrix['MU1'] = compute_mu_from_matrix(matrix, twiss_init, 1)
    matrix['MU2'] = compute_mu_from_matrix(matrix, twiss_init, 2)
    matrix['DET1'] = compute_jacobian_from_matrix(matrix, 1)
    matrix['DET2'] = compute_jacobian_from_matrix(matrix, 2)
    return matrix


def align_tracks(tracks: pd.DataFrame,
                 align_on: str='X',
                 identifier: str='LET',
                 reference_track: str='O') -> Tuple[np.array, pd.DataFrame]:
    """
    Align the tracks to obtain a homegenous array with all coordinates given at the same location.

    Required for example to compute the transfer matrix (not all particules would have integration step at the
    same coordinate and must be aligned. Uses a linear interpolation.

    :param tracks: tracking data
    :param align_on: coordinates on which the tracks are aligned (typically 'X' or 'S')
    :param identifier:
    :param reference_track:
    :return:
    """
    coordinates = ['Y-DY', 'T', 'Z', 'P', 'Yo', 'To', 'Zo', 'Po']
    particules = ['O', 'A', 'C', 'E', 'G']
    ref: pd.DataFrame = tracks.query(f"{identifier} == '{reference_track}'")[coordinates + [align_on, 'LABEL1']]
    alignment_values = ref[align_on].values
    data = np.zeros((len(particules), alignment_values.shape[0], len(coordinates)))
    data[0, :, :] = ref[coordinates].values
    for i, p in enumerate(particules[1:]):
        particule = tracks.query(f"{identifier} == '{p}'")
        for j, c in enumerate(coordinates):
            try:
                data[i+1, :, j] = np.interp(alignment_values, particule[align_on].values, particule[c].values)
            except ValueError:
                pass
    assert data.ndim == 3, "The aligned tracks do not form a homogenous array."
    return data, ref


def compute_transfer_matrix(beamline: Input, tracks: pd.DataFrame, align_on: str='X') -> pd.DataFrame:
    """
    Constructs the step-by-step transfer matrix from tracking data (finite differences).
    :param beamline: the Zgoubidoo Input beamline
    :param tracks: tracking data
    :param align_on: coordinates on which the tracks are aligned (typically 'X' or 'S')
    :return: a Panda DataFrame representing the transfer matrix
    """
    elements = tracks.LABEL1.unique()
    offset = 0
    matrix = pd.DataFrame()
    for e in beamline.line:
        if e.LABEL1 not in elements:
            if isinstance(e, Patchable):
                offset += (e.exit.x - e.entry.x).to('cm').magnitude
            continue
        t = tracks[tracks.LABEL1 == e.LABEL1]
        data, ref = align_tracks(t, align_on=align_on)
        n = 4
        normalization = [
            data[i + 1, :, i + n] - data[0, :, i + n] for i in range(0, n)
        ]
        m = pd.DataFrame(
            {
                f"R{i+1}{j+1}": pd.Series((data[i + 1, :, j] - data[0, :, j]) / normalization[i])
                #f"R{i + 1}{j + 1}": pd.Series(data[i + 1, :, j])
                for i in range(0, n)
                for j in range(0, n)
            }
        )
        m[align_on] = ref[align_on].values + offset
        m['LABEL1'] = ref['LABEL1']
        matrix = matrix.append(m)
        offset += ref[align_on].max() if align_on != 'S' else 0.0
    return matrix.reset_index()
