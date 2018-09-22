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
        ref = self._reference_frame

        def do_frame() -> None:
            self.plot(magnet.entry.x(ref), magnet.entry.y(ref), 'gv', ms=5)
            self.plot(magnet.exit.x(ref), magnet.exit.y(ref), 'k^', ms=5)
            self.plot(magnet.center.x(ref), magnet.center.y(ref), 'r.', ms=5)

        def do_box() -> None:
            if np.sign(np.cos(magnet.entry.tz(ref))) > 0:
                theta1 = 90 - magnet.entry.tx(ref) - magnet.angular_opening.to('degree').magnitude
                theta2 = 90 - magnet.entry.tx(ref)
            else:
                theta1 = -90 - magnet.entry.tx(ref)
                theta2 = -90 - magnet.entry.tx(ref) + magnet.angular_opening.to('degree').magnitude
            self._ax.add_patch(
                patches.Wedge(
                    (
                        magnet.center.x(ref),
                        magnet.center.y(ref),
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
        ref = self._reference_frame

        def do_frame():
            self.plot(magnet.entry_patched.x(ref), magnet.entry_patched.y(ref), 'gv', ms=5)
            self.plot(magnet.exit.x(ref), magnet.exit.y(ref), 'k^', ms=5)

        def do_box():
            tr = transforms.Affine2D().rotate_deg_around(
                magnet.entry_patched.x(ref),
                magnet.entry_patched.y(ref),
                -magnet.entry_patched.tx(ref)
            ) + self._ax.transData
            self._ax.add_patch(
                patches.Rectangle(
                    (
                        magnet.entry_patched.x(ref),
                        magnet.entry_patched.y(ref) - magnet.WIDTH.to('cm').magnitude / 2
                    ),
                    np.linalg.norm(
                        np.array([
                            magnet.exit.x(ref) - magnet.entry_patched.x(ref),
                            magnet.exit.y(ref) - magnet.entry_patched.y(ref)
                        ]).astype(float)
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
