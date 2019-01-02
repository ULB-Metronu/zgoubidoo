"""Zgoubidoo survey module.

"""
from typing import Optional
from .input import Input
from .frame import Frame
from .commands.patchable import Patchable


def survey(beamline: Input, reference_frame: Optional[Frame] = None) -> Input:
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

    Returns:
        a Zgoubidoo Input object
    """
    surveyed_line: Input = Input(name=beamline.name, line=beamline.line.copy())
    frame: Frame = reference_frame or Frame()
    for e in beamline[Patchable].line:
        e.place(frame)
        surveyed_line.increase_optical_length(e.length)
        frame = e.exit_patched
    return surveyed_line
