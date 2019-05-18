"""TODO"""
import numpy as _np
from .... import Kinematics as _Kinematics
from ...particules import Electron as _Electron
from ...magnetique import Solenoid as _Solenoid
from ...magnetique import Multipol as _Multipol
from ...commands import Marker as _Marker
from ...commands import ChangeRef as _ChangeRef
from .... import ureg as _ureg

lhec_database = {
    'KIN': _Kinematics(50 * _ureg.GeV_c, particle=_Electron),
    'IP': _Marker('IP'),
    'S0_L': _Solenoid('S0_L',
                      XL=4 * _ureg.m,
                      R0=1.08 * _ureg.m,
                      B0=-3.5 * _ureg.tesla,
                      XPAS=1 * _ureg.m,
                      KPOS=1,
                      ),
    'S0_R': _Solenoid('S0_R',
                      XL=2 * _ureg.m,
                      R0=1.08 * _ureg.m,
                      B0=-3.5 * _ureg.tesla,
                      XPAS=1 * _ureg.m,
                      KPOS=1,
                      ),
    'B0_L': _Multipol('B0_L',
                      XL=6 * _ureg.m,
                      R0=20 * _ureg.cm,
                      B1=5 * _ureg.tesla,
                      KPOS=1,
                      WIDTH=200 * _ureg.cm,
                      ),
    'B0_R': _Multipol('B0_R',
                      XL=4 * _ureg.m,
                      R0=20 * _ureg.cm,
                      B1=-5 * _ureg.tesla,
                      KPOS=1,
                      WIDTH=200 * _ureg.cm,
                      ),
    'B1_L': _Multipol('B1_L',
                      XL=9 * _ureg.m,
                      R0=20 * _ureg.cm,
                      B1=1 * _ureg.tesla,
                      KPOS=1,
                      WIDTH=200 * _ureg.cm),
    'B1_R': _Multipol('B1_R',
                      XL=11 * _ureg.m,
                      R0=20 * _ureg.cm,
                      B1=-1 * _ureg.tesla,
                      KPOS=1,
                      WIDTH=200 * _ureg.cm),

}
lhec_database['CR_L'] = _ChangeRef(
    TRANSFORMATIONS=[
        [
            'ZR',
            -2 * _np.arcsin((lhec_database['B0_L'].XL * lhec_database['B0_L'].B1) / (2 * lhec_database['KIN'].brho))
        ]
    ]
)

lhec_database['CR_R'] = _ChangeRef(
    TRANSFORMATIONS=[
        [
            'ZR',
            -2 * _np.arcsin((lhec_database['B0_R'].XL * lhec_database['B0_R'].B1) / (2 * lhec_database['KIN'].brho))
        ]
    ]
)


class LHeC:
    pass
