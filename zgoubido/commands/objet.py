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
    PARAMETERS = {
        'KOBJ': 1,
        'NN': 1,
        'IY': 1,
        'IT': 1,
        'IZ': 1,
        'IP': 1,
        'IX': 1,
        'ID': 1,
        'PY': 0.1,
        'PT': 1.0,
        'PZ': 0.1,
        'PP': 1.0,
        'PX': 0.1,
        'PD': 0.1,
        'YR': 0.0,
        'TR': 0.0,
        'ZR': 0.0,
        'PR': 0.0,
        'XR': 0.0,
        'DR': 1.0,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.KOBJ}.{s.NN}
        {s.IY} {s.IT} {s.IZ} {s.IP} {s.IX} {s.ID}
        {s.PY} {s.PT} {s.PZ} {s.PP} {s.PX} {s.PD}
        {s.YR} {s.TR} {s.ZR} {s.PR} {s.XR} {s.DR}
        """


class Objet2(Objet):
    PARAMETERS = {
        'KOBJ': 2,
        'NN' : 1,
        'IMAX': 1,
        'IDMAX': 1,
        'Y': [0.0],
        'T': [0.0],
        'Z': [0.0],
        'P': [0.0],
        'X': [0.0],
        'D': [0.0],
        'LET': 1.0,
        'IEX': 1,
    }

    def __str__(s):
        c = f"""
        {super().__str__().rstrip()}
        {s.KOBJ}
        {s.IMAX} {s.IDMAX}
        """
        for p in zip(s.Y, s.T, s.Z, s.P, s.X, s.D):
            c += f"{p[0]} {p[1]} {p[2]} {p[3]} {p[4]} {p[5]}"
        c += f"{s.IEX}\n"
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

    PARAMETERS = {
        'KOBJ' : 3,
        'NN' : 1,  # 00 to store the file as '[b_]zgoubi.fai'
        'IT1' : 1,
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
        'TAG': '*', # No effect if '*'
        'YR': 0,
        'TR': 0,
        'ZR': 0,
        'PR': 0,
        'XR': 0,
        'DR': 0,
        'TR': 0,
        'InitC': 0,
        'FNAME': 'zgoubi.fai', #(NN in KOBJ=3.NN determines storage FORMAT)
    }

    def __str__(s):
        if s.NN == 1:
            return f"""
            {super().__str__().rstrip()}
            {s.IT1} {s.IT2} {s.ITSTEP}
            {s.IP1} {s.IP2} {s.IPSTEP}
            {s.YF:.12e} {s.TF:.12e} {s.ZF:.12e} {s.PF:.12e} {s.XF:.12e} {s.DF:.12e} {s.TF:.12e} {s.TAG:.12e}
            {s.YR:.12e} {s.TR:.12e} {s.ZR:.12e} {s.PR:.12e} {s.XR:.12e} {s.DR:.12e} {s.TR:.12e}
            {s.InitC}
            {s.FNAME}
           """
        else:
            raise ZgoubidoException("NN != 1 not supported")

class Objet5(Objet): # Generation of 11 particles, or 11*NN if I ≥ 2 (for use with MATRIX, IORD = 1)
    PARAMETERS = {
        'KOBJ' : 5,
        'NN' : 1,
        'PY' : 0,
        'PT' : 0,
        'PZ' : 0,
        'PP' : 0,
        'PX' : 0,
        'PD' : 0,
        'YR' : 0,
        'TR' : 0,
        'ZR' : 0,
        'PR' : 0,
        'DR' : 1,
        'ALPHA_Y' : 0,
        'BETA_Y' : 0,
        'ALPHA_Z' : 0,
        'BETA_Z' : 0,
        'ALPHA_X' : 0,
        'BETA_X' : 0,
        'D_Y' : 0,
        'D_YP' : 0,
        'D_Z' : 0,
        'D_ZP' : 0,
    }

    def __str__(s):
        objet = []
        ob =  f"""
        {super().__str__().rstrip()}
        {s.PY:.12e} {s.PT:.12e} {s.PZ:.12e} {s.PP:.12e} {s.PX:.12e} {s.PD:.12e}
        {s.YR:.12e} {s.TR:.12e} {s.ZR:.12e} {s.PR:.12e} {s.XR:.12e} {s.DR:.12e}
        {s.YF:.12e} {s.TF:.12e} {s.ZF:.12e} {s.PF:.12e} {s.XF:.12e} {s.DF:.12e} {s.TF:.12e} {s.TAG:.12e}
        {s.YR:.12e} {s.TR:.12e} {s.ZR:.12e} {s.PR:.12e} {s.XR:.12e} {s.DR:.12e} {s.TR:.12e}
        """
        objet.append(ob)
        if s.NN == 1:
            ob = f"""
            {s.ALPHA_Y:.12e} {s.BETA_Y:.12e} {s.ALPHA_Z:.12e} {s.BETA_Z:.12e} {s.ALPHA_X:.12e} {s.BETA_X:.12e}
            {s.D_Y:.12e} {s.D_YP:.12e} {s.D_Z:.12e} {s.D_ZP:.12e}
            """
            objet.append(ob)
        elif s.NN in range(2,99):
            ob = f"""
            {s.YR:.12e} {s.TR:.12e} {s.ZR:.12e} {s.PR:.12e} {s.XR:.12e} {s.DR:.12e}
            """
            objet.append(ob)

        return ''.join(map(lambda _: _.rstrip(), objet))


class Objet6(Objet):
    pass


class Objet7(Objet):
    pass


class Objet8(Objet):
    pass


class ObjetA(Command):
    """Object from Monte-Carlo simulation of decay reaction."""
    KEYWORD = 'OBJETA'
