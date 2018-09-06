import numpy as np
import pandas as pd


def compute_alpha_from_matrix(m, twiss, plane='X'):
    p = 1 if plane == 1 else 3
    v = 1 if plane == 1 else 2
    return (m[f"R{p}{p}"] ** 2 * twiss[f"BETA{v}{v}"] \
            - 2.0 * m[f"R{p}{p}"] * m[f"R{p}{p+1}"] * twiss[f"ALPHA{v}{v}"] \
            + m[f"R{p}{p+1}"] ** 2 * twiss[f"GAMMA{v}{v}"]
            )


def compute_beta_from_matrix(m, twiss, plane='X'):
    p = 1 if plane == 1 else 3
    v = 1 if plane == 1 else 2
    return ( \
                m[f"R{p}{p}"] ** 2 * twiss[f"BETA{v}{v}"] \
                - 2.0 * m[f"R{p}{p}"] * m[f"R{p}{p+1}"] * twiss[f"ALPHA{v}{v}"] \
                + m[f"R{p}{p+1}"] ** 2 * twiss[f"GAMMA{v}{v}"]
    )


def compute_gamma_from_matrix(m, twiss, plane='X'):
    p = 1 if plane == 1 else 3
    v = 1 if plane == 1 else 2
    return (m[f"R{p}{p}"] ** 2 * twiss[f"BETA{v}{v}"] \
            - 2.0 * m[f"R{p}{p}"] * m[f"R{p}{p+1}"] * twiss[f"ALPHA{v}{v}"] \
            + m[f"R{p}{p+1}"] ** 2 * twiss[f"GAMMA{v}{v}"]
            )


def compute_jacobian_from_matrix(m, plane):
    p = 1 if plane == 1 else 3
    return m[f"R{p}{p}"] * m[f"R{p+1}{p+1}"] - m[f"R{p}{p+1}"] * m[f"R{p+1}{p}"]


def align_tracks(tracks, align_on='X', reference_track='O'):
    coordinates = ['Y-DY', 'T', 'Z', 'P', 'Yo', 'To', 'Zo', 'Po']
    particules = ['O', 'A', 'C', 'E', 'G', 'B', 'D', 'F', 'H']
    # particules = ['O', 'B', 'D', 'F', 'H']
    ref = tracks.query(f"LET == '{reference_track}'")[coordinates + [align_on, 'LABEL1']]
    alignment_values = ref[align_on].values
    data = np.zeros((len(particules), alignment_values.shape[0], len(coordinates)))
    data[0, :, :] = ref[coordinates].values
    for i, p in enumerate(particules[1:]):
        particule = tracks.query(f"LET == '{p}'")
        for j, c in enumerate(coordinates):
            data[i + 1, :, j] = np.interp(alignment_values, particule[align_on].values, particule[c].values)
    assert (data.ndim == 3)  # To verify that we indeed have a homogenous array
    return data


def compute_twiss(t, alignment='X'):
    elements = t.LABEL1.unique()
    offset = 0
    matrix = pd.DataFrame()
    for e in di.line:
        if e.LABEL1 not in elements:
            if isinstance(e, Magnet):
                offset += e.exit[0].to('cm').magnitude
            continue
        tracks = t[t.LABEL1 == e.LABEL1]
        data = align_tracks(tracks)
        n = 4
        normalization = [
            data[i + 1, :, i + n] - data[0, :, i + n] for i in range(0, n)
        ]
        m = pd.DataFrame(
            {
                f"R{i+1}{j+1}": pd.Series(((data[i + 1, :, j]) - data[0, :, j]) / normalization[i]) for i in range(0, n)
            for j in range(0, n)
            }
        )
        twiss_init = twiss.iloc[-1]
        m['BETA11'] = compute_beta_from_matrix(m, twiss_init, 1)
        m['BETA22'] = compute_beta_from_matrix(m, twiss_init, 2)
        m['ALPHA11'] = compute_alpha_from_matrix(m, twiss_init, 1)
        m['ALPHA22'] = compute_alpha_from_matrix(m, twiss_init, 2)
        m['GAMMA11'] = compute_gamma_from_matrix(m, twiss_init, 1)
        m['GAMMA22'] = compute_gamma_from_matrix(m, twiss_init, 2)
        m['DET1'] = compute_jacobian_from_matrix(m, 1)
        m['DET2'] = compute_jacobian_from_matrix(m, 2)
        # m[alignment] = alignment_values + offset
        matrix = matrix.append(m)
        offset += ref[alignment].max()
    return matrix.reset_index()
