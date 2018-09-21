import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from .zgoubiplot import ZgoubiPlot


class ZgoubiMpl(ZgoubiPlot):
    def __init__(self, ax=None, with_boxes: bool=True, with_frames: bool=True, **kwargs):
        super().__init__(with_boxes, with_frames, **kwargs)
        if ax is None:
            self._init_plot()
        else:
            self._ax = ax

    def _init_plot(self):
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot(111)

    def plot(self, *args, **kwargs) -> None:
        self._ax.plot(*args, **kwargs)

    def polarmagnet(self, magnet) -> None:
        def do_frame() -> None:
            self.plot(magnet.entry.x, magnet.entry.y, 'gv', ms=5)
            self.plot(magnet.sortie.x, magnet.sortie.y, 'k^', ms=5)

        def do_box() -> None:
            theta1 = 90 + magnet.entry.tz.to('degree').magnitude - magnet.angular_opening.to('degree').magnitude
            theta2 = 90 + magnet.entry.tz.to('degree').magnitude
            if np.sign(np.cos(magnet.PLACEMENT.tx.to('radian').magnitude)) < 0:
                theta1, theta2 = theta2, theta1
                theta1 -= 180
                theta2 -= 180

            self._ax.add_patch(
                patches.Wedge(
                    (
                        magnet.center[0].to('cm').magnitude,
                        magnet.center[1].to('cm').magnitude,
                    ),
                    (magnet.radius + magnet.WIDTH / 2.0).to('cm').magnitude,
                    theta1,
                    theta2,
                    width=magnet.WIDTH.to('cm').magnitude,
                    alpha=0.2,
                    facecolor=self._palette.get(magnet.COLOR, 'gray'),
                    edgecolor=self._palette.get(magnet.COLOR, 'gray'),
                    linewidth=2,
                )
            )

        if self._with_boxes:
            do_box()
        if self._with_frames:
            do_frame()

    def cartesianmagnet(self, magnet) -> None:
        def do_frame():
            self.plot(magnet.entry.x, magnet.entry.y, 'gv', ms=5)
            self.plot(magnet.sortie.x, magnet.sortie.y, 'k^', ms=5)

        def do_box():
            tr = transforms.Affine2D().rotate_deg_around(
                magnet.entry.x.to('cm').magnitude,
                magnet.entry.y.to('cm').magnitude,
                magnet.entry.tz.to('degree').magnitude) + self._ax.transData
            self._ax.add_patch(
                patches.Rectangle(
                    (
                        magnet.entry.x.to('cm').magnitude,
                        (magnet.entry.y - magnet.WIDTH / 2).to('cm').magnitude
                    ),
                    np.linalg.norm(
                        np.array([magnet.sortie.x.to('cm').magnitude, magnet.sortie.y.to('cm').magnitude])
                        - np.array([magnet.entry.x.to('cm').magnitude, magnet.entry.y.to('cm').magnitude])
                    ),
                    magnet.WIDTH.to('cm').magnitude,
                    alpha=0.2,
                    facecolor=self._palette.get(magnet.COLOR, 'gray'),
                    edgecolor=self._palette.get(magnet.COLOR, 'gray'),
                    linewidth=2,
                    transform=tr,
                )
            )

        if self._with_boxes:
            do_box()
        if self._with_frames:
            do_frame()
