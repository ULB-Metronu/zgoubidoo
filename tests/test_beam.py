import numpy as _np
import pandas as _pd
from zgoubidoo import ureg as _ureg
from zgoubidoo.commands.beam import BeamInputDistribution


def test_empty_constructor():
    b = BeamInputDistribution('BEAM', kinematics=1 * _ureg.GeV)
    assert b._distribution is None
    assert b.SLICE == 0
    assert b.REFERENCE == 0


def test_distribution_constructor():
    d = _np.array([
        [5.0, 0.0, 0.0, 0.0, 1.0],
        [7.0, 7.0, 0.0, 0.0, 1.0],
    ])
    b = BeamInputDistribution('BEAM', distribution=d, kinematics=1 * _ureg.GeV)
    assert b._distribution == d
    assert b.SLICE == 0
    assert b.REFERENCE == 0
