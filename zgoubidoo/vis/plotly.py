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
            if isinstance(e, (_Quadrupole, _Sextupole)):
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
                      apertures: bool = True,
                      body: bool = False,
                      with_drifts: bool = False,
                      points_in_polar_paths: int = 20,
                      opacity: float = 0.5,
                      magnet_poles: int = 0.0,
                      start: Optional[Union[str, _Command]] = None,
                      stop: Optional[Union[str, _Command]] = None,
                      ) -> None:
        """
        Use a `ZgoubiPlot` artist to perform the rendering of the beamline with elements and tracks.

        The `Input` must be surveyed first so that all the placements are taken into account for the plotting.

        Args:
            beamline:
            apertures:
            body:
            with_drifts:
            points_in_polar_paths:
            opacity:
            magnet_poles:
            start:
            stop:
        """
        def add_svg_path(points, reference_frame: str = 'entry_patched'):
            points = points.dot(_np.linalg.inv(e.entry_patched.get_rotation_matrix())) + _np.array([
                getattr(e, reference_frame).x_, getattr(e, reference_frame).y_, 0.0
            ])
            path = f"M{points[0, 0]},{points[0, 1]} "
            for p in points[1:]:
                path += f"L{p[0]},{p[1]} "
            path += "Z"
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
                if isinstance(e, _PolarMultiMagnet):
                    r = e.RM.m_as('m')
                    re = e.RE.m_as('m')
                    for i in range(0, e.N):
                        if magnet_poles == 0:
                            pts = []
                            thetas = _np.linspace(
                                e.AT.m_as('radian') / 2 + e.ACN[i].m_as('radian') - e.OMEGA_E[i].m_as('radian'),
                                e.AT.m_as('radian') / 2 + e.ACN[i].m_as('radian') - e.OMEGA_S[i].m_as('radian'),
                                points_in_polar_paths)
                            for theta in thetas:
                                pts.append([(r + 0.1) * _np.sin(theta), -re + (r + 0.1) * _np.cos(theta), 0.0])
                            for theta in thetas[::-1]:
                                pts.append([(r + 0.2) * _np.sin(theta), -re + (r + 0.2) * _np.cos(theta), 0.0])
                            add_svg_path(_np.array(pts))
                            pts = []
                            for theta in thetas:
                                pts.append([(r - 0.1) * _np.sin(theta), -re + (r - 0.1) * _np.cos(theta), 0.0])
                            for theta in thetas[::-1]:
                                pts.append([(r - 0.2) * _np.sin(theta), -re + (r - 0.2) * _np.cos(theta), 0.0])
                            add_svg_path(_np.array(pts))
                        else:
                            pts = []
                            thetas = _np.linspace(
                                e.AT.m_as('radian') / 2 + e.ACN[i].m_as('radian') - e.OMEGA_E[i].m_as('radian'),
                                e.AT.m_as('radian') / 2 + e.ACN[i].m_as('radian') - e.OMEGA_S[i].m_as('radian'),
                                points_in_polar_paths)
                            for theta in thetas:
                                pts.append([(r + magnet_poles/4) * _np.sin(theta), -re + (r + magnet_poles/4) * _np.cos(theta), 0.0])
                            for theta in thetas[::-1]:
                                pts.append([(r - magnet_poles) * _np.sin(theta), -re + (r - magnet_poles) * _np.cos(theta), 0.0])
                            add_svg_path(_np.array(pts), reference_frame='entry')
                elif isinstance(e, _PolarMagnet):
                    r = e.RM.m_as('m')
                    thetas = _np.linspace(0, e.AT.m_as('radian'), points_in_polar_paths)
                    if apertures:
                        pts = []
                        for theta in thetas:
                            pts.append([(r+0.1) * _np.sin(theta), -r + (r+0.1) * _np.cos(theta), 0.0])
                        for theta in thetas[::-1]:
                            pts.append([(r+0.2) * _np.sin(theta), -r + (r+0.2) * _np.cos(theta), 0.0])
                        add_svg_path(_np.array(pts))
                        pts = []
                        for theta in thetas:
                            pts.append([(r - 0.1) * _np.sin(theta), -r + (r - 0.1) * _np.cos(theta), 0.0])
                        for theta in thetas[::-1]:
                            pts.append([(r - 0.2) * _np.sin(theta), -r + (r - 0.2) * _np.cos(theta), 0.0])
                        add_svg_path(_np.array(pts))
                    if magnet_poles > 0:
                        pts = []
                        for theta in thetas:
                            pts.append([(r + 0.1) * _np.sin(theta), -r + (r + 0.1) * _np.cos(theta), 0.0])
                        for theta in thetas[::-1]:
                            pts.append([(r + 0.2) * _np.sin(theta), -r + (r - 0.1) * _np.cos(theta), 0.0])
                        add_svg_path(_np.array(pts))
                else:
                    if apertures:
                        add_svg_path(_np.array([
                            [0.0, -e.APERTURE_LEFT.m_as('m') - 0.1, 0.0],
                            [0.0, -e.APERTURE_LEFT.m_as('m'), 0.0],
                            [e.length.m_as('m'), -e.APERTURE_LEFT.m_as('m'), 0.0],
                            [e.length.m_as('m'), -e.APERTURE_LEFT.m_as('m') - 0.1, 0.0],
                        ]))
                        add_svg_path(_np.array([
                            [0.0, e.APERTURE_LEFT.m_as('m'), 0.0],
                            [0.0, e.APERTURE_LEFT.m_as('m') + 0.1, 0.0],
                            [e.length.m_as('m'), e.APERTURE_LEFT.m_as('m') + 0.1, 0.0],
                            [e.length.m_as('m'), e.APERTURE_LEFT.m_as('m'), 0.0],
                        ]))
                    if magnet_poles > 0:
                        add_svg_path(_np.array([
                            [0.0, -e.APERTURE_LEFT.m_as('m'), 0.0],
                            [0.0, e.APERTURE_LEFT.m_as('m'), 0.0],
                            [e.length.m_as('m'), e.APERTURE_LEFT.m_as('m'), 0.0],
                            [e.length.m_as('m'), -e.APERTURE_LEFT.m_as('m'), 0.0],
                        ]))

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
                    marker={'color': 'green', 'symbol': 'cross-thin', 'size': 5, 'line': {'width': 1, 'color': 'green'}},
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
                    marker={'color': 'green', 'symbol': 'cross-thin', 'size': 5, 'line': {'width': 1, 'color': 'green'}},
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
