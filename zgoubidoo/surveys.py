"""Zgoubidoo survey module.

The module performs a 3D global survey of the beamline. Zgoubi is *not* used for this purpose, the positionning is
infered by Zgoubidoo based on the inputs.
"""
from typing import Optional, Union
import numpy as _np
import pandas as _pd
import quaternion
import zgoubidoo.zgoubi
from .input import Input as _Input
from georges_core.frame import Frame as _Frame
from .commands.patchable import Patchable as _Patchable
from .commands.magnetique import PolarMagnet as _PolarMagnet
from .commands.objet import Objet2 as _Objet2
from .commands.particules import Particule as _Particule
from .commands.particules import ParticuleType as _ParticuleType
from .commands.particules import Proton as _Proton
from . import Kinematics as _Kinematics
from . import ureg as _ureg


def clear_survey(beamline: _Input):
    """

    Args:
        beamline:

    Returns:

    """
    beamline.reset_optical_lenght()
    for e in beamline[_Patchable]:
        e.clear_placement()


def survey(beamline: _Input,
           reference_frame: Optional[_Frame] = None,
           with_reference_trajectory: bool = False,
           reference_particle: Optional[Union[_Particule, _ParticuleType]] = None,
           reference_kinematics: Optional[_Kinematics] = None,
           output: bool = False) -> Optional[_pd.DataFrame]:
    """
    Survey a Zgoubidoo input and provides a line with all the elements being placed in space.

    Examples:
        >>> import zgoubidoo
        >>> from zgoubidoo.commands import *
        >>> _ = zgoubidoo.ureg
        >>> di = zgoubidoo.Input('test-line')
        >>> di += Objet2('BUNCH', BORO=2149 * _.kilogauss * _.cm).add([[10.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]])
        >>> di += Proton()
        >>> di += Ymy()
        >>> di += Dipole('DIPOLE_1', RM= 200 * _.cm, AT = -180 * _.degree)
        >>> di += Drift('DRIFT', XL = 20 * _.centimeter)
        >>> zgoubidoo.survey(beamline=di, reference_frame=Frame())

    Args:
        beamline: a Zgoubidoo Input object acting as a beamline
        reference_frame: a Zgoubidoo Frame object acting as the global reference frame
        with_reference_trajectory: TODO
        reference_particle: TODO
        reference_kinematics: TODO
        output:

    Returns:
        the surveyed line.
    """
    frame: _Frame = reference_frame or _Frame()
    for e in beamline[_Patchable]:
        e.place(frame)
        frame = e.exit_patched
    if with_reference_trajectory:
        survey_reference_trajectory(beamline, reference_kinematics, reference_particle)
    if output:
        return survey_output(beamline)
    else:
        return beamline


def survey_output(beamline: _Input) -> _pd.DataFrame:
    """

    Args:
        beamline:

    Returns:

    """
    bl = beamline[_Patchable]
    _ = []
    for e in bl:
        element_entry = e.entry.o_
        element_entry_patched = e.entry_patched.o_
        element_exit = e.exit.o_
        element_exit_patched = e.exit_patched.o_
        _.append(
            {
                'LABEL1': e.LABEL1,
                'KEYWORD': e.KEYWORD,
                'entry_s': e.entry_s,
                'exit_s': e.exit_s,
                'entry_x': element_entry[0],
                'entry_y': element_entry[1],
                'entry_z': element_entry[2],
                'entry_patched_x': element_entry_patched[0],
                'entry_patched_y': element_entry_patched[1],
                'entry_patched_z': element_entry_patched[2],
                'exit_x': element_exit[0],
                'exit_y': element_exit[1],
                'exit_z': element_exit[2],
                'exit_patched_x': element_exit_patched[0],
                'exit_patched_y': element_exit_patched[1],
                'exit_patched_z': element_exit_patched[2],
                'entry_tx': e.entry.tx.m_as('degree'),
                'entry_ty': e.entry.ty.m_as('degree'),
                'entry_tz': e.entry.tz.m_as('degree'),
                'entry_patched_tx': e.entry_patched.tx.m_as('degree'),
                'entry_patched_ty': e.entry_patched.ty.m_as('degree'),
                'entry_patched_tz': e.entry_patched.tz.m_as('degree'),
                'exit_tx': e.exit.tx.m_as('degree'),
                'exit_ty': e.exit.ty.m_as('degree'),
                'exit_tz': e.exit.tz.m_as('degree'),
                'exit_patched_tx': e.exit_patched.tx.m_as('degree'),
                'exit_patched_ty': e.exit_patched.ty.m_as('degree'),
                'exit_patched_tz': e.exit_patched.tz.m_as('degree'),
            }
        )
    output = _pd.DataFrame(_, index=bl.labels1)
    return output


def survey_reference_trajectory(beamline: _Input,
                                reference_kinematics: _Kinematics,
                                reference_particle: Optional[Union[_Particule, _ParticuleType]] = None,
                                debug: bool = False,
                                ):
    """
    TODO
    Args:
        beamline: TODO
        reference_particle:
        reference_kinematics:
        debug:

    Returns:

    """
    sequence = beamline[_Patchable].line
    if reference_kinematics is None and beamline.beam is not None:
        reference_kinematics = beamline.beam.kinematics

    if reference_particle is None and beamline.beam is not None:
        reference_particle = beamline.beam.particle
    reference_particle = reference_particle or _Proton

    if isinstance(reference_particle, _ParticuleType):
        reference_particle = reference_particle()
    objet = _Objet2(BORO=reference_kinematics.brho)
    zi = _Input(name='SURVEY_REFERENCE', line=[objet, reference_particle] + list(sequence))
    zi.KINEMATICS = reference_kinematics
    zi.IL = 2
    z = zgoubidoo.Zgoubi()
    tracks = z(zi, debug=debug).collect().tracks
    if len(tracks) > 0:
        for e in sequence:
            e.reference_trajectory = tracks.query(f"LABEL1 == '{e.LABEL1}'")
    return beamline


def construct_rays(tracks: _pd.DataFrame):
    """

    Args:
        tracks:

    Returns:

    """
    for label in tracks.LABEL1.unique():
        coordinates = tracks.query(f"LABEL1 == '{label}'")

        for cset in (
                {'T': 'T', 'P': 'P', 'XR': 'XR', 'YR': 'YR', 'ZR': 'ZR'},
                {'T': 'To', 'P': 'Po', 'XR': 'XRo', 'YR': 'YRo', 'ZR': 'ZRo'},
        ):  # Transform the initial and final coordinates
            _ = _np.zeros((coordinates.shape[0], 3))
            _[:, 2] = -coordinates[cset['T']].values
            q1 = quaternion.from_rotation_vector(_)
            _[:, 2] = 0
            _[:, 1] = coordinates[cset['P']].values
            q2 = quaternion.from_rotation_vector(_)
            q = q2 * q1
            end_points = _np.matmul(_np.linalg.inv(quaternion.as_rotation_matrix(q)), _np.array([1.0, 0.0, 0.0]))
            tracks.loc[tracks.LABEL1 == label, cset['XR']] = end_points[:, 0]
            tracks.loc[tracks.LABEL1 == label, cset['YR']] = end_points[:, 1]
            tracks.loc[tracks.LABEL1 == label, cset['ZR']] = end_points[:, 2]


def transform_tracks(beamline: _Input,
                     tracks: _pd.DataFrame,
                     ref: str = 'entry_patched',
                     with_initial_coordinates: bool = True,
                     ):
    """

    Args:
        beamline:
        tracks:
        ref:
        with_initial_coordinates:
    """
    for label in tracks.LABEL1.unique():
        e = getattr(beamline, label)
        if isinstance(getattr(beamline, label), _PolarMagnet):
            # Convert from polar to cartesian coordinates
            raw = tracks.query(f"LABEL1 == '{label}'")[['X', 'Y']].values
            tracks.loc[tracks.LABEL1 == label, 'ANG'] = _np.degrees(100 * raw[:, 0])
            tracks.loc[tracks.LABEL1 == label, 'X'] = raw[:, 1] * _np.sin(100 * raw[:, 0])
            tracks.loc[tracks.LABEL1 == label, 'Y'] = raw[:, 1] * _np.cos(100 * raw[:, 0]) - e.RM.m_as('m')

        # Rotate all particle coordinates to the global reference frame
        element_rotation = _np.linalg.inv(getattr(e, ref).get_rotation_matrix())
        t = tracks.query(f"LABEL1 == '{label}'")
        u = _np.dot(t[['X', 'Y', 'Z']].values, element_rotation)
        if with_initial_coordinates:
            v = _np.dot(t[['X', 'Yo', 'Zo']].values, element_rotation)

        # Translate all particle coordinates to the global reference frame
        origin = getattr(e, ref).origin
        tracks.loc[tracks.LABEL1 == label, 'XG'] = u[:, 0] + origin[0].m_as('m')
        tracks.loc[tracks.LABEL1 == label, 'YG'] = u[:, 1] + origin[1].m_as('m')
        tracks.loc[tracks.LABEL1 == label, 'ZG'] = u[:, 2] + origin[2].m_as('m')
        if with_initial_coordinates:
            tracks.loc[tracks.LABEL1 == label, 'YGo'] = v[:, 1] + origin[1].m_as('m')
            tracks.loc[tracks.LABEL1 == label, 'ZGo'] = v[:, 2] + origin[2].m_as('m')

        # Transform (rotate and translate) all rays coordinates to the global reference frame
        if 'XR' in tracks.columns and 'YR' in tracks.columns and 'ZR' in tracks.columns:
            w = _np.dot(t[['XR', 'YR', 'ZR']].values, element_rotation)
            tracks.loc[tracks.LABEL1 == label, 'XRG'] = w[:, 0]
            tracks.loc[tracks.LABEL1 == label, 'YRG'] = w[:, 1]
            tracks.loc[tracks.LABEL1 == label, 'ZRG'] = w[:, 2]

            # Transform the angles in the global reference frame
            tracks.loc[tracks.LABEL1 == label, 'TG'] = _np.arcsin(w[:, 1])
            tracks.loc[tracks.LABEL1 == label, 'PG'] = _np.arcsin(w[:, 2])

            w = _np.dot(t[['XR', 'YRo', 'ZRo']].values, element_rotation)
            tracks.loc[tracks.LABEL1 == label, 'TGo'] = _np.arcsin(w[:, 1])
            tracks.loc[tracks.LABEL1 == label, 'PGo'] = _np.arcsin(w[:, 2])
