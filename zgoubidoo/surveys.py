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
from .frame import Frame as _Frame
from .commands.patchable import Patchable as _Patchable
from .commands.objet import Objet2 as _Objet2
from .commands.particules import Particule as _Particule
from .commands.particules import ParticuleType as _ParticuleType
from .commands.particules import Proton as _Proton
from .kinematics import Kinematics as _Kinematics


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
           reference_particle: Optional[_Objet2] = None,
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
        reference_particle: TODO
        reference_kinematics: TODO
        output:

    Returns:
        the surveyed line.
    """
    frame: _Frame = reference_frame or _Frame()
    beamline.reset_optical_lenght()
    for e in beamline[_Patchable]:
        e.place(frame)
        beamline.increase_optical_length(e.length)
        frame = e.exit_patched
    if output:
        return survey_output(beamline)


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
            }
        )
    output = _pd.DataFrame(_, index=bl.labels1)
    return output


def survey_reference_trajectory(beamline: _Input,
                                reference_kinematics: _Kinematics,
                                reference_particle: Optional[Union[_Particule, _ParticuleType]] = None,
                                ):
    """
    TODO
    Args:
        beamline: TODO
        reference_particle:
        reference_kinematics:

    Returns:

    """
    sequence = beamline[_Patchable].line
    reference_particle = reference_particle or _Proton()
    if isinstance(reference_particle, _ParticuleType):
        reference_particle = reference_particle()
    objet = _Objet2(BORO=reference_kinematics.brho)
    zi = _Input(name='SURVEY_REFERENCE', line=[objet, reference_particle] + sequence)
    zi.KINEMATICS = reference_kinematics
    z = zgoubidoo.Zgoubi()
    tracks = z(zi).collect().tracks
    if len(tracks) > 0:
        for e in sequence:
            e.reference_trajectory = tracks.query(f"LABEL1 == '{e.LABEL1}'")
    return beamline


def construct_rays(tracks: _pd.DataFrame, length: float = 1.0):
    """

    Args:
        tracks:
        length:

    Returns:

    """
    for label in tracks.LABEL1.unique():
        coordinates = tracks.query(f"LABEL1 == '{label}'")

        _ = _np.zeros((coordinates.shape[0], 3))
        _[:, 2] = -coordinates['T'].values
        q1 = quaternion.from_rotation_vector(_)
        _[:, 2] = 0
        _[:, 1] = coordinates['P'].values
        q2 = quaternion.from_rotation_vector(_)
        q = q2 * q1
        end_points = _np.matmul(_np.linalg.inv(quaternion.as_rotation_matrix(q)), _np.array([1.0, 0.0, 0.0]))
        tracks.loc[tracks.LABEL1 == label, 'XR'] = coordinates['X'] + length * end_points[:, 0]
        tracks.loc[tracks.LABEL1 == label, 'YR'] = coordinates['Y'] + length * end_points[:, 1]
        tracks.loc[tracks.LABEL1 == label, 'ZR'] = coordinates['Z'] + length * end_points[:, 2]


def transform_tracks(beamline: _Input, tracks: _pd.DataFrame):
    """

    Args:
        beamline:
        tracks:
    """
    for label in tracks.LABEL1.unique():
        element_rotation = _np.linalg.inv(getattr(beamline, label).entry_patched.get_rotation_matrix())

        # Transform (rotate and translate) all particle coordinates to the global reference frame
        v = _np.dot(tracks.query(f"LABEL1 == '{label}'")[['X', 'Y', 'Z']].values, element_rotation)
        origin = getattr(beamline, label).entry_patched.origin
        tracks.loc[tracks.LABEL1 == label, 'XG'] = v[:, 0] + origin[0].m_as('m')
        tracks.loc[tracks.LABEL1 == label, 'YG'] = v[:, 1] + origin[1].m_as('m')
        tracks.loc[tracks.LABEL1 == label, 'ZG'] = v[:, 2] + origin[2].m_as('m')

        # Transform (rotate and translate) all rays coordinates to the global reference frame
        w = _np.dot(tracks.query(f"LABEL1 == '{label}'")[['XR', 'YR', 'ZR']].values, element_rotation)
        tracks.loc[tracks.LABEL1 == label, 'XRG'] = w[:, 0] + origin[0].m_as('m')
        tracks.loc[tracks.LABEL1 == label, 'YRG'] = w[:, 1] + origin[1].m_as('m')
        tracks.loc[tracks.LABEL1 == label, 'ZRG'] = w[:, 2] + origin[2].m_as('m')

        # Transform the angles in the global reference frame
        u = w - v
        tracks.loc[tracks.LABEL1 == label, 'TG'] = _np.arcsin(u[:, 1])
        tracks.loc[tracks.LABEL1 == label, 'PG'] = _np.arcsin(u[:, 2])
