"""Zgoubidoo survey module.

The module performs a 3D global survey of the beamline. Zgoubi is *not* used for this purpose, the positionning is
infered by Zgoubidoo based on the inputs.
"""
from typing import Optional, Union
from .input import Input as _Input
from .frame import Frame as _Frame
from .zgoubi import Zgoubi as _Zgoubi
from .kinematics import Kinematics as _Kinematics
from .commands.patchable import Patchable as _Patchable
from .commands.objet import Objet2 as _Objet2
from .commands.particules import Particule as _Particule
from .commands.particules import ParticuleType as _ParticuleType
from .commands.particules import Proton as _Proton


def survey(beamline: _Input,
           reference_frame: Optional[_Frame] = None,
           reference_particle: Optional[_Objet2] = None,
           reference_kinematics: Optional[_Kinematics] = None) -> _Input:
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

    Returns:
        the surveyed line.
    """
    frame: _Frame = reference_frame or _Frame()
    beamline.reset_optical_lenght()
    for e in beamline[_Patchable]:
        e.place(frame)
        beamline.increase_optical_length(e.length)
        frame = e.exit_patched
    return beamline


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
    z = _Zgoubi()
    tracks = z(zi).collect().tracks
    if len(tracks) > 0:
        for e in sequence:
            e.reference_trajectory = tracks.query(f"LABEL1 == '{e.LABEL1}'")
    return beamline
