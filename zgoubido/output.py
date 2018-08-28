import pandas as pd


def read_fai_file(filename='zgoubi.fai'):
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


def read_plt_file(filename='zgoubi.plt'):
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