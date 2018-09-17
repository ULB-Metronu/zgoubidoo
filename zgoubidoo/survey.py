from .input import Input
from .frame import Frame


def survey(beamline=None, reference_frame=None):
    """
    Survey a Zgoubidoo input and provides a line with all the elements being placed in space.
    :param beamline: a Zgoubidoo Input object acting as a beamline
    :param reference_frame: a Zgoubidoo Frame object acting as the initial reference frame
    :return: a Zgoubidoo Input object
    """
    if beamline is None or not isinstance(beamline, Input):
        raise Exception("'line' must be a Zgoubi input object.")
    if reference_frame is not None and not isinstance(reference_frame, Frame):
        raise Exception("'reference' must be a valid Frame object or None.")

    surveyed_line = Input(name=beamline.name, line=beamline.line)
    frame = reference_frame or Frame()
    for e in beamline.line:
        if not e.patchable:
            continue
        e.PLACEMENT = frame
        frame = e.sortie
    return surveyed_line
