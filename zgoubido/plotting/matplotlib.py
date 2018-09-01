import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from .zgoubiplot import ZgoubiPlot


class ZgoubiMpl(ZgoubiPlot):
    def __init__(self, ax=None, with_boxes=True, with_frames=True):
        super().__init__()
        if ax is None:
            self._init_plot()
        else:
            self._ax = ax
        self._with_boxes = with_boxes
        self._with_frames = with_frames

    def _init_plot(self):
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot(111)

    def cartesian_bend(self, entry, exit, rotation, width):
        def do_frame():
            self._ax.annotate(s='',
                              xy=(
                                  entry[0].to('cm').magnitude,
                                  entry[1].to('cm').magnitude
                              ),
                              xytext=(
                                  exit[0].to('cm').magnitude,
                                  exit[1].to('cm').magnitude
                              ),
                              arrowprops=dict(arrowstyle='<->')
                              )

        def do_box():
            tr = transforms.Affine2D().rotate_deg_around(
                entry[0].to('cm').magnitude,
                entry[1].to('cm').magnitude,
                rotation.to('degree').magnitude) + self._ax.transData
            self._ax.add_patch(
                patches.Rectangle(
                    (
                        entry[0].to('cm').magnitude,
                        (entry[1] - width / 2).to('cm').magnitude
                    ),
                    (exit[0] - entry[0]).to('cm').magnitude,
                    width.to('cm').magnitude,
                    alpha=0.2,
                    facecolor='#268bd2',
                    edgecolor='#268bd2',
                    transform=tr,
                )
            )

        if self._with_boxes:
            do_box()
        if self._with_frames:
            do_frame()
