import numpy as np
from .commands import Command, ZgoubidoException
from .. import ureg, Q_


class Objet(Command):
    """Generation of an object."""
    KEYWORD = 'OBJET'

    PARAMETERS = {
        'BORO': 1.0 * ureg.kilogauss * ureg.cm,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.BORO.to("kilogauss * cm").magnitude:.12e}
        """

    def __init__(self, label1='', label2='', *params, **kwargs):
        super().__init__(label1, label2, Objet.PARAMETERS, self.PARAMETERS, *params, **kwargs)


class Objet1(Objet):
    """Objet with initial coordinates drawn from a regular grid"""
    PARAMETERS = {
        'KOBJ': 1,
        'K2': 0,
        'IY': (1, 'Total number of points in +- Y'),
        'IT': (1, 'Total number of points in +- T'),
        'IZ': (1, 'Total number of points in +- Z (or +Z only if K2=01)'),
        'IP': (1, 'Total number of points in +- P (or +P only if K2=01)'),
        'IX': (1, 'Total number of points in +- X'),
        'ID': (1, 'Total number of points in +- D'),
        'PY': (0.1 * ureg.centimeter, 'Step size in Y'),
        'PT': (0.1 * ureg.milliradian, 'Step size in T'),
        'PZ': (0.1 * ureg.centimeter, 'Step size in Z'),
        'PP': (0.1 * ureg.milliradian, 'Step size in P'),
        'PX': (0.1 * ureg.centimeter, 'Step size in X'),
        'PD': (0.1, 'Step size in Delta(BRHO)/BORO'),
        'YR': (0.0 * ureg.centimeter, 'Reference Y'),
        'TR': (0.0 * ureg.milliradian, 'Reference T'),
        'ZR': (0.0 * ureg.centimeter, 'Reference Z'),
        'PR': (0.0 * ureg.milliradian, 'Reference P'),
        'XR': (0.0 * ureg.centimeter, 'Reference X'),
        'DR': (1.0, 'Reference D'),
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.KOBJ}.0{s.K2}
        {s.IY} {s.IT} {s.IZ} {s.IP} {s.IX} {s.ID}
        {s.PY.to('centimeter').magnitude:.12e} {s.PT.to('milliradian').magnitude:.12e} {s.PZ.to('centimeter').magnitude:.12e} {s.PP.to('milliradian').magnitude:.12e} {s.PX.to('centimeter').magnitude:.12e} {s.PD:.12e}
        {s.YR.to('centimeter').magnitude:.12e} {s.TR.to('milliradian').magnitude:.12e} {s.ZR.to('centimeter').magnitude:.12e} {s.PR.to('milliradian').magnitude:.12e} {s.XR.to('centimeter').magnitude:.12e} {s.DR:.12e}
        """


class Objet2(Objet):
    """Objet with all initial coordinates entered explicitely."""
    PARAMETERS = {
        'KOBJ': 2,
        'K2': 0,
        'IDMAX': 1,
        '_PARTICULES': None,
    }

    @property
    def IMAX(self):
        return self.PARTICULES.shape[0]

    @property
    def IEX(self):
        return self._PARTICULES[:, 6]

    @property
    def PARTICULES(self):
        if self._PARTICULES is None:
            self._PARTICULES = np.zeros((1, 7))
            self._PARTICULES[:, 5] = 1.0  # D = 1
            self._PARTICULES[:, 6] = 1  # IEX
        return self._PARTICULES

    def clear(self):
        self.PARTICULES = np.zeros((1, 7))
        return self

    def add(self, p):
        if self._PARTICULES is None:
            self._PARTICULES = p
        else:
            self._PARTICULES = np.append(self._PARTICULES, p)
        return self

    def __str__(s):
        c = f"""
        {super().__str__().rstrip()}
        {s.KOBJ}.0{s.K2}
        {s.IMAX} {s.IDMAX}
        """
        for p in s.PARTICULES[:, 0:6]:
            c += f"""
        {p[0]} {p[1]} {p[2]} {p[3]} {p[4]} {p[5]} A
        """.lstrip()
        c += " ".join(map(lambda x: f"{int(x):d}", s.IEX)) + "\n"
        return c


class Objet3(Objet):
    """NN=00 (default) : [b_]zgoubi.fai like data file FORMAT"""
    PARAMETERS = {
        'KOBJ': 3,
        'NN': 1,  # 00 to store the file as '[b_]zgoubi.fai'
        'IT1': 1,
        'IT2': 1,
        'ITSTEP': 1,
        'IP1': 1,
        'IP2': 1,
        'IPSTEP': 1,
        'YF': 0,
        'TF': 0,
        'ZF': 0,
        'PF': 0,
        'XF': 0,
        'DF': 0,
        'TF': 0,
        'TAG': '*',  # No effect if '*'
        'YR': 0,
        'TR': 0,
        'ZR': 0,
        'PR': 0,
        'XR': 0,
        'DR': 0,
        'TR': 0,
        'InitC': 0,
        'FNAME': 'zgoubi.fai',  # (NN in KOBJ=3.NN determines storage FORMAT)
    }

    def __str__(s):
        if s.NN == 1:
            return f"""
            {super().__str__().rstrip()}
            {s.KOBJ}.{s.NN}
            {s.IT1} {s.IT2} {s.ITSTEP}
            {s.IP1} {s.IP2} {s.IPSTEP}
            {s.YF:.12e} {s.TF:.12e} {s.ZF:.12e} {s.PF:.12e} {s.XF:.12e} {s.DF:.12e} {s.TF:.12e} {s.TAG:.12e}
            {s.YR:.12e} {s.TR:.12e} {s.ZR:.12e} {s.PR:.12e} {s.XR:.12e} {s.DR:.12e} {s.TR:.12e}
            {s.InitC}
            {s.FNAME}
           """
        else:
            raise ZgoubidoException("NN != 1 not supported")


class Objet4(Objet):
    pass


class Objet5(Objet):
    """Generation of 11 particles, or 11*NN if I ≥ 2 (for use with MATRIX, IORD = 1)"""

    PARAMETERS = {
        'KOBJ': 5,
        'NN': 1,
        'PY': 0,
        'PT': 0,
        'PZ': 0,
        'PP': 0,
        'PX': 0,
        'PD': 0,
        'YR': 0,
        'TR': 0,
        'ZR': 0,
        'PR': 0,
        'DR': 1,
        'ALPHA_Y': 0,
        'BETA_Y': 0,
        'ALPHA_Z': 0,
        'BETA_Z': 0,
        'ALPHA_X': 0,
        'BETA_X': 0,
        'D_Y': 0,
        'D_YP': 0,
        'D_Z': 0,
        'D_ZP': 0,
    }

    def __str__(s):
        command = []
        c = f"""
        {super().__str__().rstrip()}
        {s.KOBJ}.{s.NN}
        {s.PY:.12e} {s.PT:.12e} {s.PZ:.12e} {s.PP:.12e} {s.PX:.12e} {s.PD:.12e}
        {s.YR:.12e} {s.TR:.12e} {s.ZR:.12e} {s.PR:.12e} {s.XR:.12e} {s.DR:.12e}
        {s.YF:.12e} {s.TF:.12e} {s.ZF:.12e} {s.PF:.12e} {s.XF:.12e} {s.DF:.12e} {s.TF:.12e} {s.TAG:.12e}
        {s.YR:.12e} {s.TR:.12e} {s.ZR:.12e} {s.PR:.12e} {s.XR:.12e} {s.DR:.12e} {s.TR:.12e}
        """
        command.append(c)
        if s.NN == 1:
            c = f"""
            {s.ALPHA_Y:.12e} {s.BETA_Y:.12e} {s.ALPHA_Z:.12e} {s.BETA_Z:.12e} {s.ALPHA_X:.12e} {s.BETA_X:.12e}
            {s.D_Y:.12e} {s.D_YP:.12e} {s.D_Z:.12e} {s.D_ZP:.12e}
            """
            command.append(c)
        elif s.NN in range(2, 99):
            c = f"""
            {s.YR:.12e} {s.TR:.12e} {s.ZR:.12e} {s.PR:.12e} {s.XR:.12e} {s.DR:.12e}
            """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Objet6(Objet):
    pass


class Objet7(Objet):
    pass


class Objet8(Objet):
    pass


class ObjetA(Command):
    """Object from Monte-Carlo simulation of decay reaction."""
    KEYWORD = 'OBJETA'
