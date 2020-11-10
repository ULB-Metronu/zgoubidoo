"""
TODO
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Optional, Union
import numpy as _np
import pandas as _pd
from georges_core.vis import PlotlyArtist as _PlotlyArtist
from ..commands import Command as _Command
from ..commands import Plotable as _Plotable
from ..commands import Patchable as _Patchable
from ..commands import PolarMagnet as _PolarMagnet
from ..commands import PolarMultiMagnet as _PolarMultiMagnet
from ..commands import Drift as _Drift
from ..commands import Quadrupole as _Quadrupole
from ..commands import Sextupole as _Sextupole
from ..commands import Octupole as _Octupole
from ..commands import Solenoid as _Solenoid
from ..commands import Multipole as _Multipole
from ..commands import Bend as _Bend
from ..commands import Dipole as _Dipole
from ..commands import FFAGSpirale as _FFAGSPI
from ..commands import FFAG as _FFAG

if TYPE_CHECKING:
    from ..input import Input as _Input


class ZgoubidooPlotlyArtist(_PlotlyArtist):
    """
    TODO
    """

    def plot_cartouche(self,
                       beamline: _Input,
                       vertical_position: float = 1.2,
                       ):
        """

        Args:
            beamline:
            vertical_position:

        Returns:

        """
        if not beamline.valid_survey:
            print("You should do a survey")

        self.shapes.append(
            {
                'type': 'line',
                'xref': 'paper',
                'yref': 'paper',
                'x0': 0,
                'y0': vertical_position,
                'x1': 1,
                'y1': vertical_position,
                'line': {
                    'color': 'rgb(150, 150, 150)',
                    'width': 2,
                },
            },
        )
        for e in beamline:
            if not isinstance(e, _Patchable) and not isinstance(e, _Plotable):
                continue
            if isinstance(e, (_Quadrupole, _Sextupole, _Octupole, _Solenoid)):
                self.shapes.append(
                    {
                        'type': 'rect',
                        'xref': 'x',
                        'yref': 'paper',
                        'x0': e.entry_s.m_as('m'),
                        'y0': vertical_position if e.B0.magnitude > 0 else vertical_position - 0.1,
                        'x1': e.exit_s.m_as('m'),
                        'y1': vertical_position + 0.1 if e.B0.magnitude > 0 else vertical_position,
                        'line': {
                            'width': 0,
                        },
                        'fillcolor': e.COLOR,
                    },
                )
            if isinstance(e, (_Multipole,)):
                self.shapes.append(
                    {
                        'type': 'rect',
                        'xref': 'x',
                        'yref': 'paper',
                        'x0': e.entry_s.m_as('m'),
                        'y0': vertical_position - 0.05,
                        'x1': e.exit_s.m_as('m'),
                        'y1': vertical_position + 0.05,
                        'line': {
                            'width': 0,
                        },
                        'fillcolor': e.COLOR,
                    },
                )
            if isinstance(e, (_Bend, _Dipole, _FFAGSPI, _FFAG)):
                length = e.optical_length.m_as('m')
                m = e.entry_patched.get_rotation_matrix()
                if _np.dot(m, _np.array([0, 0, 1]))[2] >= 0.0:
                    path = f"M{e.entry_s.m_as('m')},{vertical_position + 0.1} " \
                           f"H{e.exit_s.m_as('m')} " \
                           f"L{e.exit_s.m_as('m') - 0.15 * length},{vertical_position - 0.1} " \
                           f"H{e.exit_s.m_as('m') - 0.85 * length} " \
                           f"Z"
                else:
                    path = f"M{e.entry_s.m_as('m') + 0.15 * length},{vertical_position + 0.1} " \
                           f"H{e.exit_s.m_as('m') - 0.15 * length} " \
                           f"L{e.exit_s.m_as('m')},{vertical_position - 0.1} " \
                           f"H{e.entry_s.m_as('m')} " \
                           f"Z"
                self.shapes.append(
                    {
                        'type': 'path',
                        'xref': 'x',
                        'yref': 'paper',
                        'path': path,
                        'line': {
                            'width': 0,
                        },
                        'fillcolor': e.COLOR,
                    },
                )

    def plot_beamline(self,
                      beamline: _Input,
                      start: Optional[Union[str, _Command]] = None,
                      stop: Optional[Union[str, _Command]] = None,
                      with_drifts: bool = False,
                      with_magnet_poles: bool = True,
                      with_apertures: bool = True,
                      with_frames: bool = False,
                      with_legend: bool = False,
                      with_map: bool = False,
                      points_in_polar_paths: int = 20,
                      opacity: float = 0.5,
                      reference_frame: str = 'entry_patched',
                      ) -> None:
        """
        Use a `ZgoubiPlot` artist to perform the rendering of the beamline with elements and tracks.

        The `Input` must be surveyed first so that all the placements are taken into account for the plotting.

        Args:
            beamline:
            start:
            stop:
            with_drifts:
            with_magnet_poles:
            with_apertures:
            with_frames:
            with_legend:
            with_map:
            points_in_polar_paths:
            opacity:
            reference_frame:
        """

        def add_svg_path(points, reference_frame: str = 'entry_patched',
                         color: Optional[str] = None,
                         opacity: Optional[float] = 0.5, shape='', line: Dict[str, float] = None):
            points = points.dot(_np.linalg.inv(getattr(e, reference_frame).get_rotation_matrix())) + _np.array([
                getattr(e, reference_frame).x_, getattr(e, reference_frame).y_, 0.0
            ])
            if shape == 'lines':
                self.scatter(x=points[0],
                             y=points[1],
                             line=line,
                             mode='lines',
                             showlegend=False)
            else:
                path = f"M{points[0, 0]},{points[0, 1]} "
                for p in points[1:]:
                    path += f"L{p[0]},{p[1]} "
                path += "Z"
                if color is None:
                    try:
                        if e.B2.magnitude > 0:
                            color = 'blue'
                        else:
                            color = 'red'
                    except AttributeError:
                        color = e.COLOR
                self.shapes.append(
                    {
                        'type': 'path',
                        'xref': 'x',
                        'yref': 'y',
                        'path': path,
                        'line': {
                            'width': 1,
                        },
                        'fillcolor': color,
                        'opacity': opacity,
                    },
                )

        def compute_face_angles(width):

            roots = _np.roots([1, -2 * r * _np.cos(_np.pi + entrance_face_angle), r ** 2 - (r + width) ** 2])
            length = roots[roots > 0][0]
            entrance_up = _np.arcsin((length / (r + width)) * _np.sin(-entrance_face_angle))

            roots = _np.roots([1, -2 * r * _np.cos(-entrance_face_angle), r ** 2 - (r - width) ** 2])
            length = _np.min(roots[roots > 0])
            entrance_down = _np.sign(-entrance_face_angle) * _np.arccos(
                _np.min([((r - width) ** 2 + r ** 2 - length ** 2) / (2 * ((r - width) * r)), 1]))

            roots = _np.roots([1, -2 * r * _np.cos(_np.pi + exit_face_angle), r ** 2 - (r + width) ** 2])
            length = roots[roots > 0][0]
            exit_up = _np.arcsin((length / (r + width)) * _np.sin(exit_face_angle))

            roots = _np.roots([1, -2 * r * _np.cos(exit_face_angle), r ** 2 - (r - width) ** 2])
            length = _np.min(roots[roots > 0])
            exit_down = _np.sign(exit_face_angle) * _np.arccos(
                _np.min([((r - width) ** 2 + r ** 2 - length ** 2) / (2 * ((r - width) * r)), 1]))

            return [entrance_up, entrance_down, exit_up, exit_down]

        def plot_polar_magnet():
            if with_magnet_poles:
                width_up = 2 * _np.abs(_np.min([entrance_efb_extent_up, exit_efb_extent_up]))
                width_down = 2 * _np.abs(_np.min([entrance_efb_extent_down,  exit_efb_extent_down]))
                pts = []
                if not isinstance(e, _FFAGSPI):
                    entrance_up, _, exit_up, _ = compute_face_angles(width=width_up / 2)
                    _, entrance_down, _, exit_down = compute_face_angles(width=width_down / 2)

                    thetas_up = _np.linspace(
                        reference_angle - omega_e - entrance_up,
                        reference_angle - omega_s + exit_up,
                        points_in_polar_paths)

                    thetas_down = _np.linspace(
                        reference_angle - omega_e + entrance_down,
                        reference_angle - omega_s - exit_down,
                        points_in_polar_paths)

                    for theta in thetas_up:
                        pts.append(
                            [(r + width_up / 2) * _np.sin(theta), -r0 + (r + width_up / 2) * _np.cos(theta), 0.0])

                    for theta in thetas_down[::-1]:
                        pts.append(
                            [(r - width_down / 2) * _np.sin(theta), -r0 + (r - width_down / 2) * _np.cos(theta), 0.0])

                if isinstance(e, _FFAGSPI):
                    pts = []
                    x_e, y_e = compute_spiral_coordinates(entrance_spiral_angle, omega_e, width / 2, width / 2)
                    theta_entry_down = _np.arctan(x_e[0] / (r + y_e[0]))
                    theta_entry_up = _np.arctan(x_e[-1] / (r + y_e[-1]))

                    x_s, y_s = compute_spiral_coordinates(exit_spiral_angle, omega_s, width / 2, width / 2)
                    theta_exit_down = _np.arctan(x_s[0] / (r + y_s[0]))
                    theta_exit_up = _np.arctan(x_s[-1] / (r + y_s[-1]))

                    thetas_up = _np.linspace(theta_entry_up,
                                             theta_exit_up,
                                             points_in_polar_paths)

                    thetas_down = _np.linspace(theta_entry_down,
                                               theta_exit_down,
                                               points_in_polar_paths)

                    for i in range(len(x_e)):
                        pts.append([x_e[i], (r-r0) + y_e[i], 0.0])

                    for theta in thetas_up:
                        pts.append(
                            [(r + width / 2) * _np.sin(theta), -r0 + (r + width / 2) * _np.cos(theta), 0.0])

                    for i in reversed(range(len(x_s))):
                        pts.append([x_s[i], (r-r0) + y_s[i], 0.0])

                    for theta in thetas_down[::-1]:
                        pts.append(
                            [(r - width / 2) * _np.sin(theta), -r0 + (r - width / 2) * _np.cos(theta), 0.0])

                add_svg_path(_np.array(pts), reference_frame=reference_frame)

            if with_apertures:
                if not isinstance(e, _FFAGSPI):
                    pts = []
                    # Aperture left
                    entrance_up, _, exit_up, _ = compute_face_angles(width=aper_left + pipe_thickness)
                    thetas_up = _np.linspace(
                        reference_angle - omega_e - entrance_up,
                        reference_angle - omega_s + exit_up,
                        points_in_polar_paths)
                    entrance_up, _, exit_up, _ = compute_face_angles(width=aper_left)
                    thetas_down = _np.linspace(
                        reference_angle - omega_e - entrance_up,
                        reference_angle - omega_s + exit_up,
                        points_in_polar_paths)
                    for theta in thetas_down:
                        pts.append(
                            [(r + aper_left) * _np.sin(theta), -r0 + (r + aper_left) * _np.cos(theta), 0.0])
                    for theta in thetas_up[::-1]:
                        pts.append([(r + aper_left + pipe_thickness) * _np.sin(theta),
                                    -r0 + (r + aper_left + pipe_thickness) * _np.cos(theta), 0.0])

                    add_svg_path(_np.array(pts), reference_frame=reference_frame, color=e.PIPE_COLOR)
                    # Aperture right
                    pts = []
                    _, entrance_down, _, exit_down = compute_face_angles(width=aper_right)
                    thetas_up = _np.linspace(
                        reference_angle - omega_e + entrance_down,
                        reference_angle - omega_s - exit_down,
                        points_in_polar_paths)
                    for theta in thetas_up:
                        pts.append(
                            [(r - aper_right) * _np.sin(theta), -r0 + (r - aper_right) * _np.cos(theta), 0.0])
                    _, entrance_down, _, exit_down = compute_face_angles(width=aper_right + pipe_thickness)
                    thetas_down = _np.linspace(
                        reference_angle - omega_e + entrance_down,
                        reference_angle - omega_s - exit_down,
                        points_in_polar_paths)
                    for theta in thetas_down[::-1]:
                        pts.append([(r - aper_right - pipe_thickness) * _np.sin(theta),
                                    -r0 + (r - aper_right - pipe_thickness) * _np.cos(theta), 0.0])

                    add_svg_path(_np.array(pts), reference_frame=reference_frame, color=e.PIPE_COLOR)

                if isinstance(e, _FFAGSPI):
                    # Aperture left
                    pts = []
                    x_e, y_e = compute_spiral_coordinates(entrance_spiral_angle, omega_e, -aper_left, aper_left + pipe_thickness)
                    theta_entry_down = _np.arctan(x_e[0] / (r + y_e[0]))
                    theta_entry_up = _np.arctan(x_e[-1] / (r + y_e[-1]))

                    x_s, y_s = compute_spiral_coordinates(exit_spiral_angle, omega_s, -aper_left, aper_left + pipe_thickness)
                    theta_exit_down = _np.arctan(x_s[0] / (r + y_s[0]))
                    theta_exit_up = _np.arctan(x_s[-1] / (r + y_s[-1]))

                    thetas_up = _np.linspace(theta_entry_up,
                                             theta_exit_up,
                                             points_in_polar_paths)

                    thetas_down = _np.linspace(theta_entry_down,
                                               theta_exit_down,
                                               points_in_polar_paths)

                    for i in range(len(x_e)):
                        pts.append([x_e[i], (r-r0) + y_e[i], 0.0])

                    for theta in thetas_up:
                        pts.append(
                            [(r + aper_left + pipe_thickness) * _np.sin(theta),
                             -r0 + (r + aper_left + pipe_thickness) * _np.cos(theta), 0.0])

                    for i in reversed(range(len(x_s))):
                        pts.append([x_s[i], (r-r0) + y_s[i], 0.0])

                    for theta in thetas_down[::-1]:
                        pts.append(
                            [(r + aper_left) * _np.sin(theta), -r0 + (r + aper_left) * _np.cos(theta), 0.0])

                    add_svg_path(_np.array(pts), reference_frame=reference_frame, color=e.PIPE_COLOR)

                    # Aperture right
                    pts = []
                    x_e, y_e = compute_spiral_coordinates(entrance_spiral_angle, omega_e, aper_right + pipe_thickness, -aper_right)
                    theta_entry_down = _np.arctan(x_e[0] / (r + y_e[0]))
                    theta_entry_up = _np.arctan(x_e[-1] / (r + y_e[-1]))

                    x_s, y_s = compute_spiral_coordinates(exit_spiral_angle, omega_s, aper_right + pipe_thickness, -aper_right)
                    theta_exit_down = _np.arctan(x_s[0] / (r + y_s[0]))
                    theta_exit_up = _np.arctan(x_s[-1] / (r + y_s[-1]))

                    thetas_up = _np.linspace(theta_entry_up,
                                             theta_exit_up,
                                             points_in_polar_paths)

                    thetas_down = _np.linspace(theta_entry_down,
                                               theta_exit_down,
                                               points_in_polar_paths)

                    for i in range(len(x_e)):
                        pts.append([x_e[i], (r-r0) + y_e[i], 0.0])

                    for theta in thetas_up:
                        pts.append(
                            [(r - aper_right) * _np.sin(theta),
                             -r0 + (r - aper_right) * _np.cos(theta), 0.0])

                    for i in reversed(range(len(x_s))):
                        pts.append([x_s[i], (r-r0) + y_s[i], 0.0])

                    for theta in thetas_down[::-1]:
                        pts.append(
                            [(r - aper_right - pipe_thickness) * _np.sin(theta),
                             -r0 + (r - aper_right - pipe_thickness) * _np.cos(theta), 0.0])

                    add_svg_path(_np.array(pts), reference_frame=reference_frame, color=e.PIPE_COLOR)

        def plot_fringes(theta_init, omega, face_angle, radius, linear_extent, sign_up=1):

            xa = (r + sign_up * linear_extent) * _np.sin(theta_init)
            ya = -r0 + (r + sign_up * linear_extent) * _np.cos(theta_init)

            # Draw the arc circle
            beta = reference_angle - omega - sign_up * face_angle
            xr = xa + radius * _np.cos(beta)
            yr = ya - radius * _np.sin(beta)
            delta_mu = linear_extent / radius
            if radius > 0:
                mu0 = sign_up * _np.pi - (reference_angle - omega) + sign_up * face_angle
            else:
                mu0 = -(reference_angle - omega) + sign_up * face_angle
            delta_mu = -sign_up * delta_mu
            delta_mu = _np.sign(delta_mu) * _np.min([_np.abs(delta_mu), _np.pi / 2])  # To avoid return loop
            mus = _np.linspace(mu0, mu0 + delta_mu, points_in_polar_paths)
            x, y = [], []
            if not _np.isclose(mu0, mu0 - sign_up * delta_mu, rtol=1e-03):
                x = xr + _np.abs(radius) * _np.cos(mus)
                y = yr + _np.abs(radius) * _np.sin(mus)
            return [_np.concatenate(([xa], x)), _np.concatenate(([ya], y))]

        def rotate(origin, point, angle):
            """
            Rotate a point counterclockwise by a given angle around a given origin.
            """
            ox, oy = origin
            px, py = point

            qx = ox + _np.cos(angle) * (px - ox) - _np.sin(angle) * (py - oy)
            qy = oy + _np.sin(angle) * (px - ox) + _np.cos(angle) * (py - oy)
            return qx, qy

        def compute_spiral_coordinates(angle, omega, width_down, width_up):
            b = 1 / _np.tan(angle)
            r_min = r - width_down
            r_max = r + width_up

            theta_min = (1 / b) * _np.log(r_min / r)
            theta_max = (1 / b) * _np.log(r_max / r)

            theta = _np.linspace(theta_min, theta_max, 20)

            rspi = r * _np.exp(b * theta)
            x = rspi * _np.sin(theta)
            y = -r + rspi * _np.cos(theta)

            (x, y) = rotate((0, -r), (x, y), -reference_angle + omega)
            return [x, y]

        def plot_polar_map():
            # Plot the map
            thetas = _np.linspace(0, total_angle, points_in_polar_paths)
            pts = []
            for theta in thetas:
                pts.append([(r0 + 1.2 * width / 2) * _np.sin(theta), -r0 + (r0 + 1.2 * width / 2) * _np.cos(theta), 0.0])

            for theta in thetas[::-1]:
                pts.append([(r0 - 1.2 * width / 2) * _np.sin(theta), -r0 + (r0 - 1.2 * width / 2) * _np.cos(theta), 0.0])

            add_svg_path(_np.array(pts), reference_frame=reference_frame, opacity=0.2)

            x0 = 0
            y0 = -r0

            x1 = x0 + (r0 + 1.2 * width / 2) * _np.sin(reference_angle)
            y1 = y0 + (r0 + 1.2 * width / 2) * _np.cos(reference_angle)

            x = _np.array([x0, x1])
            y = _np.array([y0, y1])
            add_svg_path(points=_np.array([x, y, 0], dtype="object"),
                         reference_frame=reference_frame,
                         shape='lines',
                         line={'color': 'black',
                               'width': 1,
                               'dash': 'dash'})

            x1 = x0 + (r0 + 1.2 * width / 2) * _np.sin(reference_angle - omega_e)
            y1 = y0 + (r0 + 1.2 * width / 2) * _np.cos(reference_angle - omega_e)

            x = _np.array([x0, x1])
            y = _np.array([y0, y1])
            add_svg_path(points=_np.array([x, y, 0], dtype="object"),
                         reference_frame=reference_frame,
                         shape='lines',
                         line={'color': 'black',
                               'width': 1,
                               'dash': 'dash'})

            x1 = x0 + (r0 + 1.2 * width / 2) * _np.sin(reference_angle - omega_s)
            y1 = y0 + (r0 + 1.2 * width / 2) * _np.cos(reference_angle - omega_s)

            x = _np.array([x0, x1])
            y = _np.array([y0, y1])
            add_svg_path(points=_np.array([x, y, 0], dtype="object"),
                         reference_frame=reference_frame,
                         shape='lines',
                         line={'color': 'black',
                               'width': 1,
                               'dash': 'dash'})

            # Plot the field boundary extension if it is not a FFAG-SPI
            if not isinstance(e, _FFAGSPI):
                pts = []

                # Left up
                entrance_up, entrance_down, exit_up, exit_down = compute_face_angles(width=entrance_efb_extent_up)
                theta_init = reference_angle - omega_e - entrance_up
                points_x, points_y = plot_fringes(theta_init, omega_e, -entrance_face_angle,
                                                  entrance_efb_radius_up, entrance_efb_extent_up)

                for i in reversed(range(len(points_x))):
                    pts.append([points_x[i], points_y[i], 0.0])

                # Left down
                entrance_up, entrance_down, exit_up, exit_down = compute_face_angles(width=entrance_efb_extent_down)
                theta_init = reference_angle - omega_e + entrance_down
                points_x, points_y = plot_fringes(theta_init, omega_e, entrance_face_angle, entrance_efb_radius_down,
                                                  entrance_efb_extent_down, -1)
                for i in range(len(points_x)):
                    pts.append([points_x[i], points_y[i], 0.0])

                x = _np.array(pts)[:, 0]
                y = _np.array(pts)[:, 1]
                add_svg_path(points=_np.array([x, y, 0], dtype="object"),
                             reference_frame=reference_frame,
                             shape='lines',
                             line={'color': 'black',
                                   'width': 1})

                pts = []
                # Right down
                entrance_up, entrance_down, exit_up, exit_down = compute_face_angles(width=exit_efb_extent_down)
                theta_init = reference_angle - omega_s - exit_down
                points_x, points_y = plot_fringes(theta_init, omega_s, exit_face_angle, exit_efb_radius_down,
                                                  exit_efb_extent_down, -1)

                for i in reversed(range(len(points_x))):
                    pts.append([points_x[i], points_y[i], 0.0])

                # Right up
                entrance_up, entrance_down, exit_up, exit_down = compute_face_angles(width=exit_efb_extent_up)
                theta_init = reference_angle - omega_s + exit_up
                points_x, points_y = plot_fringes(theta_init, omega_s, -exit_face_angle, exit_efb_radius_up,
                                                  exit_efb_extent_up)

                for i in range(len(points_x)):
                    pts.append([points_x[i], points_y[i], 0.0])

                x = _np.array(pts)[:, 0]
                y = _np.array(pts)[:, 1]
                add_svg_path(points=_np.array([x, y, 0], dtype="object"),
                             reference_frame=reference_frame,
                             shape='lines',
                             line={'color': 'black',
                                   'width': 1})

        def plot_frames():
            color = ['red', 'green', 'blue', 'magenta', 'darkorange']
            for i, frame in enumerate(['entry', 'entry_patched', 'exit', 'exit_patched', 'center']):
                self.scatter(
                    {
                        'x': [getattr(e, frame).x_],
                        'y': [getattr(e, frame).y_],
                        'marker': {'size': 5, 'color': color[i]},
                        'legendgroup': f"{e.LABEL1}",
                        'name': f"{frame} - {e.LABEL1}",
                        'showlegend': with_legend,
                    })

        for e in beamline[start:stop]:
            if not isinstance(e, _Plotable):
                continue
            if not with_drifts and isinstance(e, _Drift):
                continue
            try:
                if e.plotly is None:
                    raise AttributeError
                self._data.append(e.plotly())
            except AttributeError:
                if with_frames:
                    plot_frames()

                aper_left = e.APERTURE_LEFT.m_as('m')
                aper_right = e.APERTURE_RIGHT.m_as('m')
                width = e.POLE_WIDTH.m_as('m')
                pipe_thickness = e.PIPE_THICKNESS.m_as('m')
                if isinstance(e, _PolarMagnet):
                    r0 = e.RM.m_as('m')
                    for i in range(0, e.n_magnets):
                        r = r0 + e.delta_radius[i].m_as('m')
                        reference_angle = e.reference_angles[i].m_as('radian')
                        omega_e = e.entrance_efb[i].m_as('radian')
                        omega_s = e.exit_efb[i].m_as('radian')
                        total_angle = e.angular_opening.m_as('radians')
                        entrance_face_angle = e.entrance_field_boundary_wedge_angle[i].m_as('radians')
                        exit_face_angle = e.exit_field_boundary_wedge_angle[i].m_as('radians')

                        entrance_efb_extent_up = _np.min([e.entrance_field_boundary_linear_extent_up[i].m_as('m'),
                                                          width / 2])
                        entrance_efb_radius_up = e.entrance_field_boundary_linear_radius_up[i].m_as('m')
                        entrance_efb_extent_down = _np.min(
                            [e.entrance_field_boundary_linear_extent_down[i].m_as('m'),
                             width / 2])
                        entrance_efb_radius_down = e.entrance_field_boundary_linear_radius_down[i].m_as('m')
                        exit_efb_extent_up = _np.min([e.exit_field_boundary_linear_extent_up[i].m_as('m'),
                                                      width / 2])
                        exit_efb_radius_up = e.exit_field_boundary_linear_radius_up[i].m_as('m')
                        exit_efb_extent_down = _np.min([e.exit_field_boundary_linear_extent_down[i].m_as('m'),
                                                        width / 2])
                        exit_efb_radius_down = e.exit_field_boundary_linear_radius_down[i].m_as('m')
                        if isinstance(e, _FFAGSPI):
                            entrance_spiral_angle = e.entrance_spiral_angle[i].m_as('radians')
                            exit_spiral_angle = e.exit_spiral_angle[i].m_as('radians')
                        plot_polar_magnet()

                        if with_map:
                            plot_polar_map()

                else:  # This is a cartesian magnet
                    w_e = e.wedge_angle_entrance.m_as('radians')
                    w_s = e.wedge_angle_exit.m_as('radians')
                    if with_magnet_poles:
                        add_svg_path(_np.array([
                            [-(width/2)*_np.tan(w_e), -width / 2, 0.0],
                            [(width/2)*_np.tan(w_e), width / 2, 0.0],
                            [e.length.m_as('m') + (width/2)*_np.tan(w_s), width / 2, 0.0],
                            [e.length.m_as('m') - (width/2)*_np.tan(w_s), -width / 2, 0.0],
                        ]))

                    if with_apertures:
                        add_svg_path(_np.array([
                            [-aper_left * _np.tan(w_e), -aper_left, 0.0],
                            [-(aper_left + pipe_thickness)*_np.tan(w_e), -aper_left - pipe_thickness, 0.0],
                            [e.length.m_as('m') - (aper_left + pipe_thickness)*_np.tan(w_s), -aper_left - pipe_thickness,
                             0.0],
                            [e.length.m_as('m')- aper_left*_np.tan(w_s), -aper_left, 0.0],
                        ]), reference_frame=reference_frame, color=e.PIPE_COLOR)
                        add_svg_path(_np.array([
                            [aper_right * _np.tan(w_e), aper_right, 0.0],
                            [(aper_right + pipe_thickness) * _np.tan(w_e), aper_right + pipe_thickness, 0.0],
                            [e.length.m_as('m') + (aper_right + pipe_thickness) * _np.tan(w_s), aper_right + pipe_thickness, 0.0],
                            [e.length.m_as('m') + aper_right * _np.tan(w_s), aper_right, 0.0],
                        ]), reference_frame=reference_frame, color=e.PIPE_COLOR)

    @classmethod
    def plot_twiss(cls,
                   beamline,
                   twiss: _pd.DataFrame,
                   twiss_madx: Optional[_pd.DataFrame],
                   beta: bool = True,
                   dispersion: bool = True,
                   dispersion_prime: bool = False,
                   alpha: bool = False,
                   mu: bool = False,
                   ):
        """

        Args:
            beamline:
            twiss:
            twiss_madx:
            beta:
            dispersion:
            dispersion_prime:
            alpha:
            mu:

        Returns:

        """

        artist = cls(layout={
            'xaxis': {'title': 'S (m)',
                      'mirror': True,
                      'linecolor': 'black',
                      'linewidth': 1
                      },
            'legend': {
                'bordercolor': '#888',
                'borderwidth': 1,
                'xanchor': 'right',
                'x': 0.98,
                'yanchor': 'top',
                'y': 0.98
            },
        })

        if beta:
            artist.add_axis(axis={
                'title': 'Beta function (m)',
                'linecolor': 'black',
                'linewidth': 1,
                'exponentformat': 'power',
            })
            artist.scatter(
                x=twiss['S'],
                y=twiss['BETA11'],
                line={'width': 2, 'color': 'blue'},
                name='BETA11',
                mode='lines',
            )

            artist.scatter(
                x=twiss['S'],
                y=twiss['BETA22'],
                line={'width': 2, 'color': 'FireBrick'},
                name='BETA22',
                mode='lines',
            )

            if twiss_madx is not None:
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['BETX'],
                    marker={'color': 'blue', 'symbol': 'cross-thin', 'size': 5, 'line': {'width': 1, 'color': 'blue'}},
                    mode='markers',
                    showlegend=False,
                )
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['BETY'],
                    marker={'color': 'FireBrick', 'symbol': 'cross-thin', 'size': 5,
                            'line': {'width': 1, 'color': 'FireBrick'}},
                    mode='markers',
                    showlegend=False
                )

        if alpha:
            artist.add_axis(axis={
                'title': 'Alpha function',
                'linecolor': 'black',
                'linewidth': 1,
                'exponentformat': 'power',
            })
            artist.scatter(
                x=twiss['S'],
                y=twiss['ALPHA11'],
                line={'width': 2, 'color': 'blue'},
                name='ALPHA11',
                mode='lines',
            )

            artist.scatter(
                x=twiss['S'],
                y=twiss['ALPHA22'],
                line={'width': 2, 'color': 'FireBrick'},
                name='ALPHA22',
                mode='lines',
            )

            if twiss_madx is not None:
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['ALFX'],
                    marker={'color': 'blue', 'symbol': 'cross-thin', 'size': 5, 'line': {'width': 1, 'color': 'blue'}},
                    mode='markers',
                    showlegend=False,
                )
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['ALFY'],
                    marker={'color': 'FireBrick', 'symbol': 'cross-thin', 'size': 5,
                            'line': {'width': 1, 'color': 'FireBrick'}},
                    mode='markers',
                    showlegend=False
                )

        if dispersion:
            artist.add_secondary_axis(title='Dispersion (m)')

            artist.scatter(
                x=twiss['S'],
                y=twiss['DISP1'],
                line={'width': 2, 'color': 'green', 'dash': 'dashdot'},
                name='DISP1',
                mode='lines',
                yaxis='y2',
            )

            artist.scatter(
                x=twiss['S'],
                y=twiss['DISP3'],
                line={'width': 1, 'color': 'magenta', 'dash': 'dashdot'},
                name='DISP3',
                mode='lines',
                yaxis='y2',
            )

            if twiss_madx is not None:
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['DX'],
                    marker={'color': 'green', 'symbol': 'cross-thin', 'size': 5,
                            'line': {'width': 1, 'color': 'green'}},
                    mode='markers',
                    yaxis='y2',
                    showlegend=False
                )
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['DY'],
                    marker={'color': 'magenta', 'symbol': 'cross-thin', 'size': 5,
                            'line': {'width': 1, 'color': 'magenta'}},
                    mode='markers',
                    yaxis='y2',
                    showlegend=False
                )

        if dispersion_prime:
            artist.add_axis(title='Dispersion prime')

            artist.scatter(
                x=twiss['S'],
                y=twiss['DISP2'],
                line={'width': 2, 'color': 'green', 'dash': 'dashdot'},
                name='DISP2',
                mode='lines',
            )

            artist.scatter(
                x=twiss['S'],
                y=twiss['DISP4'],
                line={'width': 1, 'color': 'magenta', 'dash': 'dashdot'},
                name='DISP4',
                mode='lines',
            )

            if twiss_madx is not None:
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['DPX'],
                    marker={'color': 'green', 'symbol': 'cross-thin', 'size': 5,
                            'line': {'width': 1, 'color': 'green'}},
                    mode='markers',
                    showlegend=False
                )
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['DPY'],
                    marker={'color': 'magenta', 'symbol': 'cross-thin', 'size': 5,
                            'line': {'width': 1, 'color': 'magenta'}},
                    mode='markers',
                    showlegend=False
                )

        if mu:
            artist.add_axis(title='Phase advance')

            artist.scatter(
                x=twiss['S'],
                y=twiss['MU1'] / (2 * _np.pi),
                line={'width': 2, 'color': 'blue', 'dash': 'dashdot'},
                name='MU1',
                mode='lines',
            )

            artist.scatter(
                x=twiss['S'],
                y=twiss['MU2'] / (2 * _np.pi),
                line={'width': 1, 'color': 'FireBrick', 'dash': 'dashdot'},
                name='MU2',
                mode='lines',
            )

            if twiss_madx is not None:
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['MUX'],
                    marker={'color': 'blue', 'symbol': 'cross-thin', 'size': 5, 'line': {'width': 1, 'color': 'blue'}},
                    mode='markers',
                    showlegend=False
                )
                artist.scatter(
                    x=twiss_madx['S'],
                    y=twiss_madx['MUY'],
                    marker={'color': 'FireBrick', 'symbol': 'cross-thin', 'size': 5,
                            'line': {'width': 1, 'color': 'FireBrick'}},
                    mode='markers',
                    showlegend=False
                )

        artist.plot_cartouche(beamline)
        artist.render()
        return artist
