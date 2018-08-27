import pandas as pd


def read_fai_file():
    # Header line from the Zgoubi output
    with open('zgoubi.fai') as file:
        headers = list(map(lambda str: str.strip(' '), file.read().split('\n')[2].split(',')))
    return pd.read_table("/Users/chernals/zgoubi.fai",
                         skiprows=4,
                         names=headers,
                         sep='\s+',
                         skipinitialspace=True,
                         quotechar='\''
                         )
