"""

"""
from dataclasses import dataclass
import pandas as _pd
from ..commands.radiation import SRLoss, SRPrint
from ..commands.commands import Marker as _Marker
from ..commands.objet import Objet2 as _Objet2
from ..sequence import Sequence as _Sequence
from .results import PhysicsResults as _PhysicsResults
from ..input import Input as _Input
from ..zgoubi import ZgoubiResults as _ZgoubiResults
from .. import ureg as _ureg


@dataclass
class SynchrotronRadiationLosses(_PhysicsResults):
    """
    TODO
    """
    srloss: _pd.DataFrame
    srprint: SRPrint
    zi: _Input


def srloss(sequence: _Sequence, bunch=None, statistics: int = 1000, debug: bool = False) -> SynchrotronRadiationLosses:
    """

    Args:
        sequence: the input sequence
        bunch:
        statistics: the number of particles to tracks to collect enough statistics
        debug: verbose output on the results of the Zgoubi run

    Returns:

    """
    if bunch is None:
        bunch = _Objet2('BUNCH', BORO=sequence.kinematics.brho)
        for i in range(statistics):
            bunch.add([[0., 0., 0., 0., 0., 1., 1.]])
    srprint = SRPrint()
    zi = _Input(
        name=f'SRLOSS_COMPUTATION_FOR_{sequence.name}',
        line=[
                 bunch,
                 sequence.particle,
                 SRLoss(),
             ] + sequence.sequence + [
                 srprint,
                 _Marker('__END__'),
             ]
    )
    zi.XPAS = 1 * _ureg.cm
    _ = sequence.zgoubi(zi).collect()
    r = SynchrotronRadiationLosses(srloss=_.srloss, zi=zi, srprint=srprint)
    if debug:
        _.print()
    return r
