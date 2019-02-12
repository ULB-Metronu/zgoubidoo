"""

"""
from ..commands.radiation import SRLoss, SRPrint
from ..commands.commands import Marker as _Marker
from ..commands.objet import Objet2 as _Objet2
from ..input import Input as _Input


def srloss(sequence, bunch=None, debug=False):
    """

    Args:
        sequence: the input sequence
        bunch:
        debug: verbose output on the results of the Zgoubi run

    Returns:

    """
    if bunch is None:
        bunch = _Objet2('BUNCH', BORO=sequence.kinematics.brho)
        for i in range(2):
            bunch.add([[0., 0., 0., 0., 0., 1., 1.]])
    zi = _Input(
        name=f'SRLOSS_COMPUTATION_FOR_{sequence.name}',
        line=[
                 bunch,
                 sequence.particle,
                 SRLoss(),
             ] + sequence.sequence + [
            SRPrint(),
            SRLoss().off(),
            _Marker('__END__'),
             ]
    )
    _ = sequence.zgoubi(zi).collect()
    if debug:
        _.print()
    return _.srloss
