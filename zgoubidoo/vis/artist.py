"""Plotting module.

"""
from __future__ import annotations
from typing import Union, Mapping

PALETTE = {
    'solarized':  {'base03':  '#002b36',
                   'base02':  '#073642',
                   'base01':  '#586e75',
                   'base00':  '#657b83',
                   'base0':   '#839496',
                   'base1':   '#93a1a1',
                   'base2':   '#eee8d5',
                   'base3':   '#fdf6e3',
                   'yellow':  '#b58900',
                   'orange':  '#cb4b16',
                   'red':     '#dc322f',
                   'magenta': '#d33682',
                   'violet':  '#6c71c4',
                   'blue':    '#268bd2',
                   'cyan':    '#2aa198',
                   'green':   '#859900',
                   'goldenrod': '#fac205',
                   }
}
"""Default color palette."""

PALETTE['solarized']['gray'] = PALETTE['solarized']['base03']


class Artist:
    """
    TODO
    """
    def __init__(self, palette: Union[str, Mapping] = None, **kwargs):
        palette = palette or 'solarized'
        self._palette = PALETTE.get(palette, palette)
