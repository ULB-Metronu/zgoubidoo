import pandas as pd
import numpy as np


def read_fai_file(filename='zgoubi.fai') -> pd.DataFrame:
    # Header line from the Zgoubi .plt file
    with open(filename) as file:
        headers = list(map(lambda s: s.strip(' '), file.read().split('\n')[2].split(',')))
    return pd.read_table(filename,
                         skiprows=4,
                         names=headers,
                         sep='\s+',
                         skipinitialspace=True,
                         quotechar='\''
                         )


def read_plt_file(filename='zgoubi.plt') -> pd.DataFrame:
    # Header line from the Zgoubi .plt file
    with open(filename) as file:
        headers = list(map(lambda s: s.strip(' '), file.read().split('\n')[2].split(',')))
    df = pd.read_table(filename,
                       skiprows=4,
                       names=headers,
                       sep='\s+',
                       skipinitialspace=True,
                       quotechar='\''
                       )
    df['LABEL1'] = df['LABEL1'].map(lambda x: x.strip())
    df['Y-DY'] *= 1e-2
    df['T'] *= 1e-3
    df['Z'] *= 1e-2
    df['P'] *= 1e-3
    df['Yo'] *= 1e-2
    df['To'] *= 1e-3
    df['Zo'] *= 1e-2
    df['Po'] *= 1e-3

    return df


def read_matrix_file(filename='zgoubi.MATRIX.out') -> pd.DataFrame:
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

    df = pd.read_table('zgoubi.MATRIX.out',
                       skiprows=2,
                       names=headers,
                       sep='\s+',
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
