"""

"""
from dataclasses import dataclass
import pandas as _pd
from ..commands.radiation import SRLoss, SRPrint
from ..commands.commands import Marker as _Marker
from ..commands.objet import Objet2 as _Objet2
from .sequence import Sequence as _Sequence
from .results import PhysicsResults as _PhysicsResults
from ..input import Input as _Input


@dataclass
class SynchrotronRadiationLosses(_PhysicsResults):
    """
    TODO
    """
    srloss: _pd.DataFrame
    zi: _Input


def srloss(sequence: _Sequence, bunch=None, statistics: int = 1000, debug: bool = False) -> SynchrotronRadiationLosses:
    """

    Args:
        sequence: the input physics
        bunch:
        statistics:
        debug: verbose output on the results of the Zgoubi run

    Returns:

    """
    if bunch is None:
        bunch = _Objet2('BUNCH', BORO=sequence.kinematics.brho)
        for i in range(statistics):
            bunch.add([[0., 0., 0., 0., 0., 1., 1.]])
    zi = _Input(
        name=f'SRLOSS_COMPUTATION_FOR_{sequence.name}',
        line=[
                 bunch,
                 sequence.particle,
                 SRLoss(),
             ] + sequence.sequence + [
            SRPrint(),
            _Marker('__END__'),
             ]
    )
    _ = sequence.zgoubi(zi).collect()
    r = SynchrotronRadiationLosses(srloss=_.srloss, zi=zi)
    if debug:
        _.print()
    return r
