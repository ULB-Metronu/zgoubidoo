"""Module for handling of affine geometry transformations (rotations and translations).

This module provides support for affine geometry transformations, mainly through the `Frame` class.

Example:
    example

    >>> 1 + 1
    2


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
    with open(filename) as file:
        headers = list(map(lambda s: s.strip(' '), file.read().split('\n')[2].split(',')))
    return pd.read_table(os.path.join(path, filename),
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
        each coordinate is converted from the Zgoubi internal unit system onto the SI system. This means, in particular
        that the positions are in meters and the angles in mrad.

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
    with open(filename) as file:
        headers = list(map(lambda s: s.strip(' '), file.read().split('\n')[2].split(',')))
    df = pd.read_table(os.path.join(path, filename),
                       skiprows=4,
                       names=headers,
                       sep=r'\s+',
                       skipinitialspace=True,
                       quotechar='\''
                       )
    df['LABEL1'] = df['LABEL1'].map(lambda x: x.strip())
    df['X'] *= 1e-2
    df['S'] *= 1e-2
    df['Y-DY'] *= 1e-2
    df['T'] *= 1e-3
    df['Z'] *= 1e-2
    df['P'] *= 1e-3
    df['Yo'] *= 1e-2
    df['To'] *= 1e-3
    df['Zo'] *= 1e-2
    df['Po'] *= 1e-3

    return df


def read_matrix_file(filename: str = 'zgoubi.MATRIX.out', path: str = '.') -> pd.DataFrame:
    """Function to read Zgoubi MATRIX files.

    Reads the content of a Zgoubi matrix file (output from a Twiss or Optics command) and formats it as a valid Pandas
    DataFrame with headers.

    Notes:
        the resulting DataFrame uses SI units.

    Example:
        >>> read_matrix_file()

    Args:
        filename: the name of the file
        path: the path to the .plt file

    Returns:
        a Pandas DataFrame with the .plt file content.

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

    df = pd.read_table(os.path.join(path, filename),
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
