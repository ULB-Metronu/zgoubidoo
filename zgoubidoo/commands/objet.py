"""Zgoubi commands for the generation of Objet's.

The description of the object, i.e., initial coordinates of the ensemble of particles, must be the first procedure
in the zgoubi input data file, zgoubi.dat.

Several types of automatically generated objects are available, they are described in the following pages and
include:

    - non-random object, with various distributions : individual particles, grids, object for MATRIX, etc.
    - Monte Carlo distribution (see MCObjet), with various distributions as well : 6-D window, ellipsoids, etc.

A recurrent quantity appearing in these procedures is IMAX, the number of particles to be ray-traced.
The maximum value allowed for IMAX can be changed at leisure in the include file `MAXTRA.H` where it is defined
(that requires re-compiling zgoubi).
"""

import numpy as _np

from .. import ureg as _ureg
from .commands import Command as _Command
from .commands import CommandType as _CommandType
from .commands import ZgoubidooException as _ZgoubidooException


class ObjetType(_CommandType):
    """Type system for Objet types."""

    pass


class Objet(_Command, metaclass=ObjetType):
    """Generation of an object."""

    KEYWORD = "OBJET"
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        "BORO": (1.0 * _ureg.kilogauss * _ureg.cm, "Reference magnetic rigidity."),
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.BORO.to("kilogauss * cm").magnitude:.12e}
        """

    def __init__(self, label1="", label2="", *params, **kwargs):
        super().__init__(label1, label2, Objet.PARAMETERS, self.PARAMETERS, *params, **kwargs)


class Objet1(Objet):
    """Objet with initial coordinates drawn from a regular grid"""

    PARAMETERS = {
        "KOBJ": 1,
        "K2": 0,
        "IY": (1, "Total number of points in +- Y"),
        "IT": (1, "Total number of points in +- T"),
        "IZ": (1, "Total number of points in +- Z (or +Z only if K2=01)"),
        "IP": (1, "Total number of points in +- P (or +P only if K2=01)"),
        "IX": (1, "Total number of points in +- X"),
        "ID": (1, "Total number of points in +- D"),
        "PY": (1.0 * _ureg.centimeter, "Step size in Y"),
        "PT": (1.0 * _ureg.milliradian, "Step size in T"),
        "PZ": (1.0 * _ureg.centimeter, "Step size in Z"),
        "PP": (1.0 * _ureg.milliradian, "Step size in P"),
        "PX": (1.0 * _ureg.centimeter, "Step size in X"),
        "PD": (0.1, "Step size in Delta(BRHO)/BORO"),
        "YR": (0.0 * _ureg.centimeter, "Reference Y"),
        "TR": (0.0 * _ureg.milliradian, "Reference T"),
        "ZR": (0.0 * _ureg.centimeter, "Reference Z"),
        "PR": (0.0 * _ureg.milliradian, "Reference P"),
        "XR": (0.0 * _ureg.centimeter, "Reference X"),
        "DR": (1.0, "Reference D"),
    }

    def __str__(s) -> str:
        return f"""
        {super().__str__().rstrip()}
        {s.KOBJ}.0{s.K2}
        {s.IY} {s.IT} {s.IZ} {s.IP} {s.IX} {s.ID}
        {s.PY.to('centimeter').magnitude:.12e} {s.PT.to('milliradian').magnitude:.12e} {s.PZ.to('centimeter').magnitude:.12e} {s.PP.to('milliradian').magnitude:.12e} {s.PX.to('centimeter').magnitude:.12e} {s.PD:.12e}
        {s.YR.to('centimeter').magnitude:.12e} {s.TR.to('milliradian').magnitude:.12e} {s.ZR.to('centimeter').magnitude:.12e} {s.PR.to('milliradian').magnitude:.12e} {s.XR.to('centimeter').magnitude:.12e} {s.DR:.12e}
        """


class Objet2(Objet):
    """Objet with all initial coordinates entered explicitely.

    This object type can be used to simulate a bunch with an explicit list of coordinates. That's the method Zgoubidoo
    uses when tracking bunches.

    Examples:
        >>> zi = Input()
        >>> objet = Objet2()
        >>> objet.add()
        >>> zi += objet
        >>> zi
        >>> objet.clear()
        >>> objet
    """

    PARAMETERS = {
        "KOBJ": (2, ""),
        "K2": (0, ""),
        "IDMAX": (1, ""),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other
    commands (e.g. fit)."""

    Y_ = 30
    T_ = 31
    Z_ = 32
    P_ = 33
    # Used for FIT

    def post_init(
        self,
        reference_y: float = 0.0,
        reference_t: float = 0.0,
        reference_z: float = 0.0,
        reference_p: float = 0.0,
        reference_x: float = 0.0,
        reference_d: float = 1.0,
        **kwargs,
    ):
        """Post initialization routine."""
        self._PARTICULES = None
        self._reference_y = reference_y
        self._reference_t = reference_t
        self._reference_z = reference_z
        self._reference_p = reference_p
        self._reference_x = reference_x
        self._reference_d = reference_d

    @property
    def IMAX(self):
        """

        Returns:

        """
        return self.PARTICULES.shape[0]

    @property
    def IEX(self):
        """

        Returns:

        """
        return self.PARTICULES[:, 6]

    @property
    def PARTICULES(self):
        """The particles list."""
        if self._PARTICULES is None:
            self.add_references()
        return self._PARTICULES

    def clear(self):
        """Reset the object's content, remove all particles."""
        self._PARTICULES = None
        return self

    def __iadd__(self, other):
        self.add(other)
        return self

    def add(self, p):
        """

        Args:
            p:

        Returns:

        """
        if p is None:
            return self
        assert isinstance(p, _np.ndarray), "The particles container must be a numpy array."
        assert p.ndim == 2, "Invalid dimensions for the array of particles (must be 2)."
        if p.shape[1] == 4:  # Y T Z P
            x = _np.zeros((p.shape[0], 1))
            d = _np.ones((p.shape[0], 1))
            iex = _np.ones((p.shape[0], 1))
            distribution = _np.concatenate((p, x, d, iex), axis=1)
        elif p.shape[1] == 5:  # Y T Z P D
            x = _np.zeros((p.shape[0], 1))
            iex = _np.ones((p.shape[0], 1))
            distribution = _np.concatenate((p[:, :-1], x, p[:, -1:], iex), axis=1)
        elif p.shape[1] == 6:  # Y T Z P X D
            iex = _np.ones((p.shape[0], 1))
            distribution = _np.concatenate((p, iex), axis=1)
        elif p.shape[1] == 7:  # Y T Z P X D IEX
            distribution = p
        else:
            raise _ZgoubidooException("Invalid dimensions for particles vectors.")
        if self._PARTICULES is None:
            self._PARTICULES = distribution
        else:
            self._PARTICULES = _np.append(self._PARTICULES, distribution, axis=0)
        return self

    def add_references(self, n: int = 1):
        """
        Add a reference particle to the Objet.

        Args:
            n: the number of reference particles to add

        Returns:
            the object itself.
        """
        p = _np.zeros((n, 7))
        p[:, 0] = self._reference_y
        p[:, 1] = self._reference_t
        p[:, 2] = self._reference_z
        p[:, 3] = self._reference_p
        p[:, 4] = self._reference_x
        p[:, 5] = self._reference_d
        p[:, 6] = 1.0  # IEX
        self.add(p)
        return self

    def __str__(self) -> str:
        c = f"""
        {super().__str__().strip()}
        {self.KOBJ}.0{self.K2}
        {self.IMAX} {self.IDMAX}
        """
        p = self.PARTICULES[0, 0:6]
        c += f"""
        {p[0]:.12e} {p[1]:.12e} {p[2]:.12e} {p[3]:.12e} {p[4]:.12e} {p[5]:.12e} O
        """.lstrip()
        for p in self.PARTICULES[1:, 0:6]:
            c += f"""
        {p[0]:.12e} {p[1]:.12e} {p[2]:.12e} {p[3]:.12e} {p[4]:.12e} {p[5]:.12e} A
        """.lstrip()
        c += " ".join(map(lambda x: f"{int(x):d}", self.IEX)) + "\n"
        return c


class Objet3(Objet):
    """

    Examples:
        Test
    """

    PARAMETERS = {
        "KOBJ": 3,
        "NN": 1,  # 00 to store the file as '[b_]zgoubi.fai'
        "IT1": 1,
        "IT2": 1,
        "ITSTEP": 1,
        "IP1": 1,
        "IP2": 1,
        "IPSTEP": 1,
        "YF": 0,
        "TF": 0,
        "ZF": 0,
        "PF": 0,
        "XF": 0,
        "DF": 0,
        "TAG": "*",  # No effect if '*'
        "YR": 0,
        "ZR": 0,
        "PR": 0,
        "XR": 0,
        "DR": 0,
        "InitC": 0,
        "FNAME": "zgoubi.fai",  # (NN in KOBJ=3.NN determines storage FORMAT)
    }

    def __str__(s) -> str:
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
            raise _ZgoubidooException("NN != 1 not supported")


class Objet4(Objet):
    pass

    PARAMETERS = {
        "KOBJ": 3,
        "NN": 1,  # 00 to store the file as '[b_]zgoubi.fai'
        "IT1": 1,
        "IT2": 1,
        "ITSTEP": 1,
        "IP1": 1,
        "IP2": 1,
        "IPSTEP": 1,
        "YF": 0,
        "TF": 0,
        "ZF": 0,
        "PF": 0,
        "XF": 0,
        "DF": 0,
        "TF": 0,
        "TAG": "*",  # No effect if '*'
        "YR": 0,
        "TR": 0,
        "ZR": 0,
        "PR": 0,
        "XR": 0,
        "DR": 0,
        "TR": 0,
        "InitC": 0,
        "FNAME": "zgoubi.fai",  # (NN in KOBJ=3.NN determines storage FORMAT)
    }

    def __str__(s) -> str:
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
            raise _ZgoubidooException("NN != 1 not supported")


class Objet5(Objet):
    """Generation of 11 particles, or 11*NN if I ≥ 2 (for use with MATRIX, IORD = 1).

    Examples:
        test
    """

    PARAMETERS = {
        "KOBJ": (5, "Generation of groups 13 particles."),
        "NN": (1, "Number of groups of 13 particles"),
        "PY": 1e-3,
        "PT": 1e-3,
        "PZ": 1e-3,
        "PP": 1e-3,
        "PS": 1e-3,
        "PD": 1e-3,
        "YR": ([0], "Y-coordinate of the reference trajectory"),
        "TR": ([0], "T-coordinate of the reference trajectory"),
        "ZR": ([0], "Z-coordinate of the reference trajectory"),
        "PR": ([0], "P-coordinate of the reference trajectory"),
        "SR": ([0], "X-coordinate of the reference trajectory"),
        "DR": ([1], "D-coordinate of the reference trajectory"),
        "ALPHA_Y": 0,
        "BETA_Y": 1 * _ureg.m,
        "ALPHA_Z": 0,
        "BETA_Z": 1 * _ureg.m,
        "ALPHA_S": 0,
        "BETA_S": 1 * _ureg.m,
        "D_Y": 0 * _ureg.m,
        "D_YP": 0,
        "D_Z": 0 * _ureg.m,
        "D_ZP": 0,
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other
    commands (e.g. fit)."""

    def __str__(s) -> str:
        assert len(s.YR) == len(s.TR) == len(s.ZR) == len(s.PR) == len(s.SR) == len(s.DR) == s.NN, "Invalid lengths"
        command = []
        c = f"""
        {super().__str__().strip()}
        {s.KOBJ}.{s.NN}
        {s.PY:.12e} {s.PT:.12e} {s.PZ:.12e} {s.PP:.12e} {s.PS:.12e} {s.PD:.12e}
        {s.YR[0]:.12e} {s.TR[0]:.12e} {s.ZR[0]:.12e} {s.PR[0]:.12e} {s.SR[0]:.12e} {s.DR[0]:.12e}
        """
        command.append(c)
        if s.NN == 1:
            c = f"""
        {s.ALPHA_Y:.12e} {s.BETA_Y.m_as('m'):.12e} {s.ALPHA_Z:.12e} {s.BETA_Z.m_as('m'):.12e} {s.ALPHA_S:.12e} {s.BETA_S.m_as('m'):.12e} {s.D_Y.m_as('m'):.12e} {s.D_YP:.12e} {s.D_Z.m_as('m'):.12e} {s.D_ZP:.12e}
            """
            command.append(c)
        elif 1 < s.NN < 99:
            for i in range(1, s.NN):
                c = f"""
        {s.YR[i]:.12e} {s.TR[i]:.12e} {s.ZR[i]:.12e} {s.PR[i]:.12e} {s.SR[i]:.12e} {s.DR[i]:.12e}
                    """
            command.append(c)

        return "".join(map(lambda _: _.rstrip(), command)) + "\n"


class Objet6(Objet):
    """Generation of 61 particles.

    Examples:
        >>> 1 + 1 # TODO
    """

    PARAMETERS = {
        "KOBJ": (6, "Generation of groups 61 particles."),
        "PY": 1e-3,
        "PT": 1e-3,
        "PZ": 1e-3,
        "PP": 1e-3,
        "PX": 1e-3,
        "PD": 1e-3,
        "YR": (0.0, "Y-coordinate of the reference trajectory"),
        "TR": (0.0, "T-coordinate of the reference trajectory"),
        "ZR": (0.0, "Z-coordinate of the reference trajectory"),
        "PR": (0.0, "P-coordinate of the reference trajectory"),
        "XR": (0.0, "X-coordinate of the reference trajectory"),
        "DR": (1.0, "D-coordinate of the reference trajectory"),
    }

    def __str__(self) -> str:
        command = []
        c = f"""
        {super().__str__().rstrip()}
        {self.KOBJ}
        {self.PY:.12e} {self.PT:.12e} {self.PZ:.12e} {self.PP:.12e} {self.PX:.12e} {self.PD:.12e}
        {self.YR:.12e} {self.TR:.12e} {self.ZR:.12e} {self.PR:.12e} {self.XR:.12e} {self.DR:.12e}
        """
        command.append(c)
        return "".join(map(lambda _: _.rstrip(), command)) + "\n"


class Objet7(Objet):
    """ """

    pass


class Objet8(Objet):
    """
    Generation of phase-space coordinates on ellipses
    """

    PARAMETERS = {
        "KOBJ": (8, "Generation of groups 61 particles."),
        "IY": (10, "Number of samples in each 2-D phase space if zero the central value (below) is assigned"),
        "IZ": (10, "Number of samples in each 2-D phase space if zero the central value (below) is assigned"),
        "IS": (10, "Number of samples in each 2-D phase space if zero the central value (below) is assigned"),
        "Y0": (0.0 * _ureg.m, "Central value Y0"),
        "T0": (0.0 * _ureg.rad, "Central value T0"),
        "Z0": (0.0 * _ureg.m, "Central value Z0"),
        "P0": (0.0 * _ureg.rad, "Central value P0"),
        "S0": (0.0 * _ureg.m, "Central value S0"),
        "D0": (1.0, "Central value D0"),
        "ALPHA_Y": (0.0, "Horizontal (Y) alpha function"),
        "BETA_Y": (1.0 * _ureg.m, "Horizontal (Y) beta function"),
        "EMIT_Y": (1e-9 * _ureg.m, "Horizontal (Y) emittance"),
        "ALPHA_Z": (0.0, "Vertical (Z) alpha function"),
        "BETA_Z": (1.0 * _ureg.m, "Vertical (Z) beta function"),
        "EMIT_Z": (1e-9 * _ureg.m, "Vertical (Z) emittance"),
        "ALPHA_S": (0.0, "Horizontal (S) alpha function"),
        "BETA_S": (1.0 * _ureg.m, "Horizontal (S) beta function"),
        "EMIT_S": (1e-9 * _ureg.m, "Horizontal (S) emittance"),
    }

    def __str__(self) -> str:
        command = []
        c = f"""
        {super().__str__().rstrip()}
        {self.KOBJ}
        {self.IY} {self.IZ} {self.IS}
        {self.Y0.m_as('m'):.12e} {self.T0.m_as('radians'):.12e} {self.Z0.m_as('m'):.12e} {self.P0.m_as('radians'):.12e} {self.S0.m_as('m'):.12e} {self.D0:.12e}
        {self.ALPHA_Y:.12e} {self.BETA_Y.m_as('m'):.12e} {self.EMIT_Y.m_as('m'):.12e}
        {self.ALPHA_Z:.12e} {self.BETA_Z.m_as('m'):.12e} {self.EMIT_Z.m_as('m'):.12e}
        {self.ALPHA_S:.12e} {self.BETA_S.m_as('m'):.12e} {self.EMIT_S.m_as('m'):.12e}
        """
        command.append(c)
        return "".join(map(lambda _: _.rstrip(), command)) + "\n"


class ObjetA(_Command):
    """Object from Monte-Carlo simulation of decay reaction.

    Examples:
        TODO
    """

    KEYWORD = "OBJETA"
    """Keyword of the command used for the Zgoubi input data."""
