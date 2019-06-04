"""TODO

"""
import os
import pandas as pd


def read_fai_file(filename: str = 'zgoubi.fai', path: str = '.') -> pd.DataFrame:
    """Function to read Zgoubi .fai files.

    Reads the content of a Zgoubi .fai file ('faisceau', 'beam' file) and formats it as a valid Pandas DataFrame with
    headers.

    Example:
        >>> read_fai_file()

    Args:
        filename: the name of the file
        path: the path to the .fai file

    Returns:
        a Pandas DataFrame with the .fai file content.

    Raises:
        a FileNotFoundError in case the file is not found.
    """
    # Header line from the Zgoubi .fai file
    with open(os.path.join(path, filename)) as file:
        headers = list(map(lambda s: s.strip(' '), file.read().split('\n')[2].split(',')))
    return pd.read_csv(os.path.join(path, filename),
                       skiprows=4,
                       names=headers,
                       sep=r'\s+',
                       skipinitialspace=True,
                       quotechar='\''
                       )


def read_plt_file(filename: str = 'zgoubi.plt', path: str = '.') -> pd.DataFrame:
    """Function to read Zgoubi .plt files.

    Reads the content of a Zgoubi .plt file ('plot' file) and formats it as a valid Pandas DataFrame with headers.

    Notes:
        each coordinate is converted from the Zgoubi internal unit system onto the SI system. This means, in particular,
        that the positions are in meters and the angles in mrad.

    The special columns have the following meaning:
        - *LET*: one character string (for tagging (groups of) particles)
        - *IREP* is an index which indicates a symmetry with respect to the median plane. For instance,
        if Z(I + 1) = −Z(I), then normally IREP(I + 1) = IREP(I ). Consequently the coordinates of particle I + 1
        will not be obtained from ray-tracing but instead deduced from those of particle I by simple symmetry.
        This saves on computing time.

    Example:
        >>> read_plt_file()

    Args:
        filename: the name of the file
        path: the path to the .plt file

    Returns:
        a Pandas DataFrame with the .plt file content.

    Raises:
        a FileNotFoundError in case the file is not found.
    """
    # Header line from the Zgoubi .plt file
    with open(os.path.join(path, filename)) as file:
        headers = list(map(lambda s: s.strip(' '), file.read().split('\n')[2].split(',')))
    df = pd.read_csv(os.path.join(path, filename),
                     skiprows=4,
                     names=headers,
                     sep=r'\s+',
                     skipinitialspace=True,
                     quotechar='\''
                     )
    df['LABEL1'] = df['LABEL1'].map(lambda x: x.strip())
    df['X'] *= 1e-2
    df['S'] *= 1e-2
    df['Y'] = 1e-2 * df['Y-DY']
    del df['Y-DY']
    df['T'] *= 1e-3
    df['Z'] *= 1e-2
    df['P'] *= 1e-3
    df['Yo'] *= 1e-2
    df['To'] *= 1e-3
    df['Zo'] *= 1e-2
    df['Po'] *= 1e-3
    df['KEX'] = df['# KEX']
    df['KEYWORD'] = df['KLEY'].apply(str.strip)
    del df['# KEX']
    del df['KLEY']

    return df


def read_srloss_file(filename: str = 'zgoubi.SRLOSS.out', path: str = '.') -> pd.DataFrame:
    """Read Zgoubi SRLOSS files to a DataFrame.

    Reads the content of a Zgoubi SRLOSS (synchrotron radiation losses) file (produced with SRPrint) and formats it as a
    valid Pandas DataFrame with headers.

    Example:
        >>> read_srloss_file()

    Args:
        filename: the name of the file
        path: the path to the SRLOSS file

    Returns:
        a Pandas DataFrame with the SRLOSS file content.

    Raises:
        a FileNotFoundException in case the file is not found.
    """
    headers = [
        'KLE',
        'LABEL1',
        'LABEL2',
        'NOEL',
        'IPASS',
        'BORO',
        'DPREF',
        'AM',
        'Q',
        'G',
        'IMAX',
        'PI*EMIT(1)',
        'ALP(1)',
        'BET(1)',
        'XM(1)',
        'XPM(1)',
        'NLIV(1)',
        'NINL(1)',
        'RATIN(1)',
        'PI*EMIT(2)',
        'ALP(2)',
        'BET(2)',
        'XM(2)',
        'XPM(2)',
        'NLIV(2)',
        'NINL(2)',
        'RATIN(2)',
        'PI*EMIT(3)',
        'ALP(3)',
        'BET(3)',
        'XM(3)',
        'XPM(3)',
        'NLIV(3)',
        'NINL(3)',
        'RATIN(3)',
        'DE_LOCAL',
        'SIGE_LOCAL',
        'DE_AVG_THEO',
        'E_AVG_PHOTON',
        'E_RMS_PHOTON',
    ]

    df = pd.read_csv(os.path.join(path, filename),
                     skiprows=4,
                     names=headers,
                     sep=r'\s+',
                     skipinitialspace=True,
                     quotechar='\''
                     )

    return df


def read_srloss_steps_file(filename: str = 'zgoubi.SRLOSS.STEPS.out', path: str = '.') -> pd.DataFrame:
    """Read Zgoubi SRLOSS STEPS files to a DataFrame.

    Reads the content of a Zgoubi SRLOSS STEPS (synchrotron radiation losses for each integration steps) file
    (produced with SRPrint) and formats it as a valid Pandas DataFrame with headers.

    Example:
        >>> read_srloss_steps_file()

    Args:
        filename: the name of the file
        path: the path to the SRLOSS STEPS file

    Returns:
        a Pandas DataFrame with the SRLOSS STEPS file content.

    Raises:
        a FileNotFoundException in case the file is not found.
    """
    headers = [
        'LABEL1',
        'NOEL',
        'IT',
        'K',
        'E',
        'S',
        'X',
        'Y',
        'Z',
        'T',
        'P',
    ]

    df = pd.read_csv(os.path.join(path, filename),
                     skiprows=0,
                     names=headers,
                     sep=r'\s+',
                     skipinitialspace=False,
                     quotechar='\''
                     )
    df['S'] *= 1e-2
    df['X'] *= 1e-2
    df['Y'] *= 1e-2
    df['Z'] *= 1e-2

    return df


def read_matrix_file(filename: str = 'zgoubi.MATRIX.out', path: str = '.') -> pd.DataFrame:
    """Read Zgoubi MATRIX files to a DataFrame.

    Reads the content of a Zgoubi matrix file (output from a Twiss command) and formats it as a valid Pandas
    DataFrame with headers.

    Notes:
        the resulting DataFrame uses SI units.

    Example:
        >>> read_matrix_file()

    Args:
        filename: the name of the file
        path: the path to the zgoubi.MATRIX.out file

    Returns:
        a Pandas DataFrame with the zgoubi.MATRIX.out file content.

    Raises:
        a FileNotFoundError in case the file is not found.
    """
    # Cleaned up header lines
    headers = [
        'R11', 'R12', 'R13', 'R14', 'R15', 'R16',
        'R21', 'R22', 'R23', 'R24', 'R25', 'R26',
        'R31', 'R32', 'R33', 'R34', 'R35', 'R36',
        'R41', 'R42', 'R43', 'R44', 'R45', 'R46',
        'R51', 'R52', 'R53', 'R54', 'R55', 'R56',
        'R61', 'R62', 'R63', 'R64', 'R65', 'R66',
        'ALFY', 'BETY',
        'ALFZ', 'BETZ',
        'DY', 'DYP',
        'DZ', 'DZP',
        'PHIY', 'PHIZ',
        'F(1IREF)', 'F(2IREF)', 'F(3IREF)', 'F(4IREF)', 'F(5IREF)', 'F(6IREF)', 'F(7IREF)',
        'CMUY',
        'CMUZ',
        'QY',
        'QZ',
        'XCE',
        'YCE',
        'ALE'
    ]

    df = pd.read_csv(os.path.join(path, filename),
                     skiprows=2,
                     names=headers,
                     sep=r'\s+',
                     skipinitialspace=True,
                     quotechar='\''
                     )

    df['ALPHA11'] = df['ALFY']
    df['BETA11'] = df['BETY']
    df['GAMMA11'] = (1 + df['ALPHA11']**2) / df['BETA11']
    df['ALPHA22'] = df['ALFZ']
    df['BETA22'] = df['BETZ']
    df['GAMMA22'] = (1 + df['ALPHA22']**2) / df['BETA22']

    return df


def read_optics_file(filename: str = 'zgoubi.OPTICS.out', path: str = '.') -> pd.DataFrame:
    """Read Zgoubi OPTICS files to a DataFrame.

    Reads the content of a Zgoubi optics file (output from a Optics) and formats it as a valid Pandas
    DataFrame with headers.

    Notes:
        the resulting DataFrame uses SI units.

    Example:
        >>> read_optcs_file()

    Args:
        filename: the name of the file
        path: the path to the zgoubi.OPTICS.out file

    Returns:
        a Pandas DataFrame with the zgoubi.OPTICS.out file content.

    Raises:
        a FileNotFoundError in case the file is not found.
    """
    # Cleaned up header lines
    headers = [
        'alfx', 'btx', 'alfx', 'bty', 'alfl', 'btl',
        'Dx', 'Dxp', 'Dy', 'Dyp', 'phix/2pi', 'phiy/2pi',
        'cumul_s/m', '#lmnt', 'x/m', 'xp/rad', 'y/m', 'yp/rad',
        'KEYWORD', 'label1', 'label2', 'FO', 'K0', 'K1',
        'K2', 'C', 'r', '!', 'iptimpf', 'IPASS', 'frac', 'int', 'R11', 'R12', 'R13', 'R14', 'R15',
    'R16', 'R21', 'R22', 'R23', 'R24', 'R25', 'R26', 'R31', 'R32', 'R33', 'R34', 'R35', 'R36',
    'R41', 'R42', 'R43', 'R44', 'R45','R46',
    'R51', 'R52', 'R53', 'R54', 'R55','R56',
    'path', 'S', 'AL', 'D'
    ]

    df = pd.read_csv(os.path.join(path, filename),
                     skiprows=3,
                     names=headers,
                     sep=r'\s+',
                     skipinitialspace=True,
                     quotechar='\''
                     )
    return df
