"""Zgoubidoo survey module.

The module performs a 3D global survey of the beamline. Zgoubi is *not* used for this purpose, the positionning is
infered by Zgoubidoo based on the inputs.
"""
from typing import Optional, Union
import numpy as _np
import pandas as _pd
import zgoubidoo.zgoubi
from .input import Input as _Input
from georges_core.frame import Frame as _Frame
from georges_core.frame import FrameFrenet as _FrameFrenet
from .commands.patchable import Patchable as _Patchable
from .commands.objet import Objet2 as _Objet2
from .commands.particules import Particule as _Particule
from .commands.particules import ParticuleType as _ParticuleType
from .commands.particules import Proton as _Proton
from . import Kinematics as _Kinematics
from . units import _ureg as _


def clear_survey(beamline: _Input):
    """

    Args:
        beamline:

    Returns:

    """
    for e in beamline[_Patchable]:
        e.clear_placement()


def survey(beamline: _Input,
           reference_frame: Optional[_Frame] = None,
           with_reference_trajectory: bool = False,
           reference_particle: Optional[Union[_Particule, _ParticuleType]] = None,
           reference_kinematics: Optional[_Kinematics] = None,
           reference_closed_orbit: Optional[_np.ndarray] = None,
           output: bool = False) -> Union[_Input, _pd.DataFrame]:
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
        reference_closed_orbit: TODO
        output:

    Returns:
        the surveyed line.
    """
    sref = 0 * _.m
    for e in beamline[_Patchable]:
        e.entry_sref = sref
        sref += e.optical_ref_length
        e.exit_sref = sref

    frenet: _FrameFrenet = _FrameFrenet()
    for e in beamline[_Patchable]:
        e.place(frenet)
        frenet = e.frenet_orientation
    clear_survey(beamline)
    frame: _Frame = reference_frame or _Frame()
    for e in beamline[_Patchable]:
        e.place(frame)
        frame = e.exit_patched
    if with_reference_trajectory:
        survey_reference_trajectory(beamline, reference_kinematics, reference_particle, reference_closed_orbit)
        beamline.set_valid_survey()
    if output:
        return process_survey_output(beamline)
    else:
        return beamline


def process_survey_output(beamline: _Input) -> _pd.DataFrame:
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
                                closed_orbit: Optional[_np.ndarray] = None,
                                debug: bool = False,
                                ):
    """
    TODO
    Args:
        beamline: TODO
        reference_kinematics:
        reference_particle:
        closed_orbit:
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
    if closed_orbit is not None:
        objet.add(closed_orbit)
    zi = _Input(name='SURVEY_REFERENCE', line=[objet, reference_particle] + list(sequence))
    zi.KINEMATICS = reference_kinematics
    zi.IL = 2
    z = zgoubidoo.Zgoubi()
    tracks = z(zi, debug=debug).collect().tracks
    if len(tracks) > 0:
        for e in sequence:
            e.reference_trajectory = tracks.query(f"LABEL1 == '{e.LABEL1}'")
    z.cleanup()
    return beamline
