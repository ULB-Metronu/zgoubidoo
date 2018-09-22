
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
                   'green':   '#859900'
                   }
}
PALETTE['solarized']['gray'] = PALETTE['solarized']['base03']


class ZgoubiPlot:
    def __init__(self, with_boxes=True, with_frames=True, with_drifts=True, **kwargs):
        self._reference_frame = kwargs['reference_frame']
        self._with_boxes = with_boxes
        self._with_frames = with_frames
        self._with_drifts = with_drifts
        self._palette = PALETTE['solarized']

    @property
    def with_drifts(self) -> bool:
        return self._with_drifts

    def cartesianmagnet(self, **kwargs):
        pass

    def polarmagnet(self, **kwargs):
        pass
