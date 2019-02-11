"""

"""
from .. import ureg as _ureg
from ..commands.radiation import SRLoss, SRPrint
from ..commands.commands import Marker as _Marker
from ..commands.objet import Objet2 as _Objet2
from ..input import Input as _Input


def srloss(sequence, bunch=None):
    """

    Args:
        sequence:
        bunch:

    Returns:

    """
    if bunch is None:
        bunch = _Objet2('BUNCH', BORO=-169 * _ureg.tesla * _ureg.m)
        for i in range(10):
            bunch.add([[0., 0., 0., 0., 0., 1., 1.]])
    zi = _Input(
        name='CLOSED_ORBIT_FINDER',
        line=[
                 bunch,
                 sequence.particle,
                 SRLoss(),
             ]
             + sequence.sequence
             + [
                SRPrint(),
                _Marker('__END__'),
            ]
    )