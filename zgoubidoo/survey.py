import copy
from .input import Input
from .frame import Frame
from .commands.patchable import Patchable


def survey(beamline: Input=None, reference_frame: Frame=None) -> Input:
    """
    Survey a Zgoubidoo input and provides a line with all the elements being placed in space.
    :param beamline: a Zgoubidoo Input object acting as a beamline
    :param reference_frame: a Zgoubidoo Frame object acting as the initial reference frame
    :return: a Zgoubidoo Input object
    """
    surveyed_line: Input = Input(name=beamline.name, line=beamline.line.copy())
    frame: Frame = reference_frame or Frame()
    angle = 0
    for e in beamline[Patchable].line:
        e.place(frame)
        print('Angle tx en entrée: ', e.entry_patched.tx(frame)+angle)
        frame = e.exit_patched
        print('Angle tx en sortie: ', e.entry_patched.tx(frame)+angle)
        angle += e.entry_patched.tx(frame)
    return surveyed_line
