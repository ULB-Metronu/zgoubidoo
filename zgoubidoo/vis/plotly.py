"""
TODO
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union
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
from ..commands import Multipole as _Multipole
from ..commands import Bend as _Bend
from ..commands import Dipole as _Dipole

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
            if isinstance(e, (_Quadrupole, _Sextupole, _Octupole)):
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
            if isinstance(e, (_Bend, _Dipole)):
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
            points_in_polar_paths:
            opacity:
            reference_frame:
        """

        def add_svg_path(points, reference_frame: str = 'entry_patched', color: Optional[str] = None, opacity: Optional[float] = 0.5):
            points = points.dot(_np.linalg.inv(getattr(e, reference_frame).get_rotation_matrix())) + _np.array([
                getattr(e, reference_frame).x_, getattr(e, reference_frame).y_, 0.0
            ])
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

            roots = _np.roots([1, -2 * r * _np.cos(_np.pi - entrance_face_angle), r ** 2 - (r + width) ** 2])
            length = roots[roots > 0][0]
            entrance_up = _np.arcsin((length / (r + width)) * _np.sin(entrance_face_angle))

            roots = _np.roots([1, -2 * r * _np.cos(entrance_face_angle), r ** 2 - (r - width) ** 2])
            length = _np.min(roots[roots > 0])
            entrance_down = _np.sign(entrance_face_angle) * \
                            _np.min(
                                (_np.arccos(((r - width) ** 2 + r ** 2 - length ** 2) / (2 * ((r - width) * r))), 1))

            roots = _np.roots([1, -2 * r * _np.cos(_np.pi - exit_face_angle), r ** 2 - (r + width) ** 2])
            length = roots[roots > 0][0]
            exit_up = _np.arcsin((length / (r + width)) * _np.sin(-exit_face_angle))

            roots = _np.roots([1, -2 * r * _np.cos(-exit_face_angle), r ** 2 - (r - width) ** 2])
            length = _np.min(roots[roots > 0])
            exit_down = _np.sign(-exit_face_angle) * \
                        _np.min((_np.arccos(((r - width) ** 2 + r ** 2 - length ** 2) / (2 * ((r - width) * r))), 1))

            return [entrance_up, entrance_down, exit_up, exit_down]

        def plot_left_up():
            # Compute the first point up to U2
            entrance_up, entrance_down, exit_up, exit_down = compute_face_angles(width=entrance_efb_extent_up)
            theta_init = reference_angle - omega_e - entrance_up
            xa = (r + entrance_efb_extent_up) * _np.sin(theta_init)
            ya = -r + (r + entrance_efb_extent_up) * _np.cos(theta_init)

            self.scatter(x=[xa],
                         y=[ya],
                         marker={'size': 5, 'color': 'yellow'},
                         mode='markers',
                         showlegend=False)
            # Draw the arc circle
            xr = xa + entrance_efb_radius_up * _np.cos(entrance_face_angle)
            yr = ya + entrance_efb_radius_up * _np.sin(entrance_face_angle)
            self.scatter(x=[xr],
                         y=[yr],
                         marker={'size': 5, 'color': 'magenta'},
                         mode='markers',
                         showlegend=False)

            if entrance_efb_radius_up > 0:
                mu = _np.pi / 2 + entrance_face_angle
                mus = _np.linspace(_np.pi / 2 + mu, _np.pi / 2, 20)
            else:
                mu = entrance_face_angle
                mus = _np.linspace(mu, _np.pi/2, 20)

            x = xr + _np.abs(entrance_efb_radius_up) * _np.cos(mus)
            y = yr + _np.abs(entrance_efb_radius_up) * _np.sin(mus)

            self.scatter(x=x,
                         y=y,
                         marker={'size': 5, 'color': 'black'},
                         mode='markers',
                         showlegend=False)

            # Continue the arc circle
            xb = (xr + _np.abs(entrance_efb_radius_up) * _np.cos(mus[-1]))
            yb = (yr + _np.abs(entrance_efb_radius_up) * _np.sin(mus[-1]))
            beta = _np.arctan(xb / (yb + r))
            thetas_up = _np.linspace(
                beta,
                reference_angle - omega_s + exit_up,
                points_in_polar_paths)

            dr = _np.sqrt(xb ** 2 + (yb + r) ** 2) - r
            for theta in thetas_up:
                x = (r + dr) * _np.sin(theta)
                y = -r + (r + dr) * _np.cos(theta)
                self.scatter(
                    x=[x],
                    y=[y],
                    marker={'size': 5, 'color': 'green'},
                    mode='markers',
                    showlegend=False,
                )

        def plot_left_down():
            # Compute the first point up to U1
            entrance_up, entrance_down, exit_up, exit_down = compute_face_angles(width=entrance_efb_extent_down)
            theta_init = reference_angle - omega_e + entrance_down
            xa = (r - entrance_efb_extent_down) * _np.sin(theta_init)
            ya = -r + (r - entrance_efb_extent_down) * _np.cos(theta_init)
            self.scatter(x=[xa],
                         y=[ya],
                         marker={'size': 5, 'color': 'yellow'},
                         mode='markers',
                         showlegend=False)

            # Draw the arc circle
            xr = xa - entrance_efb_radius_down * _np.cos(entrance_face_angle)
            yr = ya - entrance_efb_radius_down * _np.sin(entrance_face_angle)
            self.scatter(x=[xr],
                         y=[yr],
                         marker={'size': 5, 'color': 'magenta'},
                         mode='markers',
                         showlegend=False)

            if entrance_efb_radius_down < 0:
                mu = _np.pi / 2 - entrance_face_angle
                mus = _np.linspace(-_np.pi / 2 - mu, -_np.pi / 2, 20)
            else:
                mu = -entrance_face_angle
                mus = _np.linspace(-mu, -_np.pi / 2, 20)

            x = xr + _np.abs(entrance_efb_radius_down) * _np.cos(mus)
            y = yr + _np.abs(entrance_efb_radius_down) * _np.sin(mus)

            self.scatter(x=x,
                         y=y,
                         marker={'size': 5, 'color': 'black'},
                         mode='markers',
                         showlegend=False)

            # Continue the arc circle
            xb = (xr + _np.abs(entrance_efb_radius_down) * _np.cos(mus[-1]))
            yb = (yr + _np.abs(entrance_efb_radius_down) * _np.sin(mus[-1]))
            beta = _np.arctan(xb / (yb + r))
            thetas_up = _np.linspace(
                beta,
                reference_angle - omega_s + exit_down,
                points_in_polar_paths)

            dr = _np.sqrt(xb ** 2 + (yb + r) ** 2) - r
            for theta in thetas_up:
                x = (r + dr) * _np.sin(theta)
                y = -r + (r + dr) * _np.cos(theta)
                self.scatter(
                    x=[x],
                    y=[y],
                    marker={'size': 5, 'color': 'green'},
                    mode='markers',
                    showlegend=False,
                )

        def plot_right_down():
            pass

        def plot_right_down():
            pass



        def plot_polar_magnet():
            if with_magnet_poles:

                plot_left_up()
                plot_left_down()



                entrance_up, entrance_down, exit_up, exit_down = compute_face_angles(width=width / 2)
                thetas_up = _np.linspace(
                    reference_angle - omega_e - entrance_up,
                    reference_angle - omega_s + exit_up,
                    points_in_polar_paths)

                thetas_down = _np.linspace(
                    reference_angle - omega_e + entrance_down,
                    reference_angle - omega_s - exit_down,
                    points_in_polar_paths)

                pts = []
                for theta in thetas_up:
                    pts.append(
                        [(r + width / 2) * _np.sin(theta), -r + (r + width / 2) * _np.cos(theta), 0.0])
                for theta in thetas_down[::-1]:
                    pts.append(
                        [(r - width / 2) * _np.sin(theta), -r + (r - width / 2) * _np.cos(theta), 0.0])
                add_svg_path(_np.array(pts), reference_frame=reference_frame)

            if with_apertures:
                pts = []
                entrance_up, _, exit_up, _ = compute_face_angles(width=aper_left)
                thetas_down = _np.linspace(
                    reference_angle - omega_e - entrance_up,
                    reference_angle - omega_s + exit_up,
                    points_in_polar_paths)

                for theta in thetas_down:
                    pts.append(
                        [(r + aper_left) * _np.sin(theta), -r + (r + aper_left) * _np.cos(theta), 0.0])

                entrance_up, _, exit_up, _ = compute_face_angles(width=aper_left + pipe_thickness)

                thetas_up = _np.linspace(
                    reference_angle - omega_e - entrance_up,
                    reference_angle - omega_s + exit_up,
                    points_in_polar_paths)

                for theta in thetas_up[::-1]:
                    pts.append([(r + aper_left + pipe_thickness) * _np.sin(theta),
                                -r + (r + aper_left + pipe_thickness) * _np.cos(theta), 0.0])

                add_svg_path(_np.array(pts), reference_frame=reference_frame, color=e.PIPE_COLOR)
                pts = []

                _, entrance_down, _, exit_down = compute_face_angles(width=aper_right)
                thetas_up = _np.linspace(
                    reference_angle - omega_e + entrance_down,
                    reference_angle - omega_s - exit_down,
                    points_in_polar_paths)

                for theta in thetas_up:
                    pts.append(
                        [(r - aper_right) * _np.sin(theta), -r + (r - aper_right) * _np.cos(theta), 0.0])

                _, entrance_down, _, exit_down = compute_face_angles(width=aper_right + pipe_thickness)

                thetas_down = _np.linspace(
                    reference_angle - omega_e + entrance_down,
                    reference_angle - omega_s - exit_down,
                    points_in_polar_paths)

                for theta in thetas_down[::-1]:
                    pts.append([(r - aper_right - pipe_thickness) * _np.sin(theta),
                                -r + (r - aper_right - pipe_thickness) * _np.cos(theta), 0.0])

                add_svg_path(_np.array(pts), reference_frame=reference_frame, color=e.PIPE_COLOR)

        def plot_polar_map():
            # Plot the map
            thetas = _np.linspace(0, total_angle, points_in_polar_paths)
            pts = []
            for theta in thetas:
                pts.append([(r + width / 2) * _np.sin(theta), -r + (r + width / 2) * _np.cos(theta), 0.0])
            pts.append([0, -r, 0.0])
            add_svg_path(_np.array(pts), reference_frame=reference_frame, opacity=0.2)
            pts = []
            x1 = (r + width / 2) * _np.sin(e.AT.m_as('radian') * 0.5)
            y1 = -r + (r + width / 2) * _np.cos(e.AT.m_as('radian') * 0.5)
            pts.append([0, -r, 0.0])
            pts.append([x1, y1, 0.0])
            add_svg_path(_np.array(pts), reference_frame=reference_frame, opacity=1.0)

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
                    r = e.RM.m_as('m')
                    print(e.entrance_field_boundary_linear_extent_up, e.entrance_field_boundary_linear_radius_up)
                    for i in range(0, e.n_magnets):
                        # width = e.entrance_field_boundary_linear_extent_up[i].m_as('m')
                        reference_angle = e.reference_angles[i].m_as('radian')
                        omega_e = e.entrance_efb[i].m_as('radian')
                        omega_s = e.exit_efb[i].m_as('radian')
                        total_angle = e.angular_opening.m_as('radians')
                        entrance_face_angle = e.entrance_field_boundary_wedge_angle[i].m_as('radians')
                        exit_face_angle = e.exit_field_boundary_wedge_angle[i].m_as('radians')
                        entrance_efb_extent_up = e.entrance_field_boundary_linear_extent_up[i].m_as('m')
                        entrance_efb_radius_up = e.entrance_field_boundary_linear_radius_up[i].m_as('m')
                        entrance_efb_extent_down = e.entrance_field_boundary_linear_extent_down[i].m_as('m')
                        entrance_efb_radius_down = e.entrance_field_boundary_linear_radius_down[i].m_as('m')

                        plot_polar_magnet()
                        if with_frames:
                            width = e.POLE_WIDTH.m_as('m')
                            plot_polar_map()

                else:
                    if with_magnet_poles:
                        add_svg_path(_np.array([
                            [0.0, -width / 2, 0.0],
                            [0.0, width / 2, 0.0],
                            [e.length.m_as('m'), width / 2, 0.0],
                            [e.length.m_as('m'), -width / 2, 0.0],
                        ]))

                    if with_apertures:
                        add_svg_path(_np.array([
                            [0.0, -aper_left, 0.0],
                            [0.0, -aper_left - pipe_thickness, 0.0],
                            [e.length.m_as('m'), -aper_left - pipe_thickness, 0.0],
                            [e.length.m_as('m'), -aper_left, 0.0],
                        ]), reference_frame=reference_frame, color=e.PIPE_COLOR)
                        add_svg_path(_np.array([
                            [0.0, aper_right, 0.0],
                            [0.0, aper_right + pipe_thickness, 0.0],
                            [e.length.m_as('m'), aper_right + pipe_thickness, 0.0],
                            [e.length.m_as('m'), aper_right, 0.0],
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
