import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms as transforms
from .zgoubiplot import ZgoubiPlot


class ZgoubiMpl(ZgoubiPlot):
    def __init__(self, ax=None, with_boxes: bool=True, with_frames: bool=True, with_centers: bool=False, **kwargs):
        super().__init__(with_boxes, with_frames, **kwargs)
        self._with_centers = with_centers
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
        ref = self.reference_frame

        def do_frame() -> None:
            self.plot(magnet.entry.x(ref), magnet.entry.y(ref), 'gv', ms=5)
            self.plot(magnet.exit.x(ref), magnet.exit.y(ref), 'k^', ms=5)
            if self._with_centers:
                self.plot(magnet.center.x(ref), magnet.center.y(ref), 'r.', ms=5)

        def do_box() -> None:
            if np.cos(magnet.entry.tz(ref)) > 0:
                theta1 = 90 - magnet.entry.tx(ref) - magnet.angular_opening.to('degree').magnitude
                theta2 = 90 - magnet.entry.tx(ref)
            else:
                theta1 = -90 - magnet.entry.tx(ref)
                theta2 = -90 - magnet.entry.tx(ref) + magnet.angular_opening.to('degree').magnitude
                if np.sin(magnet.entry.tx(ref)) < 0:
                    theta1 = magnet.entry.tx(ref) - 90
                    theta2 = magnet.entry.tx(ref) - 90 + magnet.angular_opening.to('degree').magnitude
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
        ref = self.reference_frame

        def do_frame():
            self.plot(magnet.entry_patched.x(ref), magnet.entry_patched.y(ref), 'gv', ms=5)
            self.plot(magnet.exit.x(ref), magnet.exit.y(ref), 'k^', ms=5)

        def do_box():
            tr = transforms.Affine2D().rotate_deg_around(
                magnet.entry_patched.x(ref),
                magnet.entry_patched.y(ref),
                -magnet.entry_patched.tx(ref)*np.sign(np.cos(magnet.entry_patched.tz(ref)))
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

    def tracks_cartesianmagnet(self, magnet, tracks) -> None:
        x = tracks['X'].values
        y = 100 * tracks['Y-DY'].values
        angle = - np.radians(magnet.entry_patched.tx(self.reference_frame))
        if np.sign(np.cos(magnet.entry.tz(self.reference_frame))) > 0:
            pass
        else:
            y *= -1
        s = np.sin(angle)
        c = np.cos(angle)
        xx = c * x - s * y
        yy = s * x + c * y
        tracks_x = magnet.entry_patched.x(self.reference_frame) + xx
        tracks_y = magnet.entry_patched.y(self.reference_frame) + yy
        self.plot(tracks_x, tracks_y, 'b.', ms=1)

    def tracks_polarmagnet(self, magnet, tracks) -> None:
        x = tracks['X'].values
        y = 100 * tracks['Y-DY'].values
        if np.sign(np.cos(magnet.entry.tz(self.reference_frame))) > 0:
            rotation_angle = np.radians(90 - magnet.center.tx(self.reference_frame)) - x
        else:
            rotation_angle = np.radians(-90 - magnet.center.tx(self.reference_frame)) + x
        tracks_x = magnet.center.x(self.reference_frame) + y * np.cos(rotation_angle)
        tracks_y = magnet.center.y(self.reference_frame) + y * np.sin(rotation_angle)
        self.plot(tracks_x, tracks_y, '.', ms=2)
