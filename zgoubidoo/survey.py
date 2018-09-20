from .input import Input
from .frame import Frame


def survey(beamline: Input=None, reference_frame: Frame=None) -> Input:
    """
    Survey a Zgoubidoo input and provides a line with all the elements being placed in space.
    :param beamline: a Zgoubidoo Input object acting as a beamline
    :param reference_frame: a Zgoubidoo Frame object acting as the initial reference frame
    :return: a Zgoubidoo Input object
    """
    surveyed_line: Input = Input(name=beamline.name, line=beamline.line)
    frame: Frame = reference_frame or Frame()
    for e in beamline.line:
        if not e.patchable:
            continue
        e.PLACEMENT = frame
        frame = e.sortie
    return surveyed_line
