import matplotlib.pyplot as plt
from .zgoubiplot import ZgoubiPlot


class ZgoubiMpl(ZgoubiPlot):
    def __init__(self, ax=None):
        super().__init__()
        if ax is None:
            self._init_plot()

    def _init_plot(self):
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot(111)


