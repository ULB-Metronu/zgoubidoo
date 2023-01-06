"""Zgoubidoo's interfaces to purefly electric Zgoubi commands.

More details here.
"""
from .. import ureg as _ureg
from .commands import Command as _Command
from .patchable import Patchable as _Patchable
from .plotable import Plotable as _Plotable


class Cavite(_Command, _Patchable, _Plotable):
    """Accelerating cavity."""

    KEYWORD = "CAVITE"
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        "IOPT": (0, "Model."),
        "FREQ": (0.0 * _ureg.Hz, "RF frequency"),
        "V": (0.0 * _ureg.volt, "RF voltage"),
        "PHI_S": (0.0 * _ureg.radian, "Phase"),
        "XL": (0.0 * _ureg.cm, "Cavity length"),
        "CHAMBERS": ("+1", "Use Chambers' model."),
        "COLOR": "yellow",
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other
        commands (e.g. fit)."""

    def __str__(s):
        return f"""
            {super().__str__().rstrip()}
            {int(s.IOPT):d}   PRINT
            {s.XL.m_as('m'):.12e} {s.FREQ.to('Hz').magnitude:.12e}
            {s.V.m_as('volt'):.12e} {s.PHI_S.m_as('radian'):.12e} {s.CHAMBERS}
            """


# Alias
Cavity = Cavite


class EBMult(_Command):
    r"""Electro-magnetic multipole.

    ``EBMULT`` simulates an electro-magnetic multipole, by addition of electric (:math:`\vec{E}`) and
    magnetic (:math:`\vec{B}`) multipole components (dipole to 20-pole). :math:`\vec{E}` and its derivatives
    :math:`\frac{\partial^{i+j+k} \vec{E}}{\partial X^i \partial Y^j \partial Z^k} (i + j + k \le 4)` are derived from
    the general expression of the multipole scalar potential (eq. 1.3.5), followed by a :math:`\frac{\pi}{2n}`
    rotation (n = 1, 2, 3, ...) (see also ``ELMULT``). :math:`\vec{B}` and its derivatives are derived from the same
    general potential, as described in section 1.3.7 (see also ``MULTIPOL``).

    The entrance and exit fringe fields of the :math:`\vec{E}` and :math:`\vec{B}` components are treated separately,
    in the same way as described under ``ELMULT`` and ``MULTIPOL``, for each one of these two fields. Wedge angle
    correction is applied in sharp edge field model if :math:`\vec{B_1}` is non zero, as in ``MULTIPOL``. Any of the
    :math:`\vec{E}` or :math:`\vec{B}` multipole field component can be X-rotated independently of the others.

    Use ``PARTICUL`` prior to ``EBMULT``, for the definition of particle mass and charge.
    """
    KEYWORD = "EBMULT"
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        "IL": (0, "Print field and coordinates along trajectories"),
        # Electric poles
        "XL_El": (0.0 * _ureg.centimeter, "Length of element"),
        "R0_El": (10.0 * _ureg.centimeter, "Radius at pole tip"),
        "PHI1": (0.0 * _ureg.volt, "potential at pole tip for dipole electric component"),
        "PHI2": (0.0 * _ureg.volt, "potential at pole tip for quadrupole electric component"),
        "PHI3": (0.0 * _ureg.volt, "potential at pole tip for sextupole electric component"),
        "PHI4": (0.0 * _ureg.volt, "potential at pole tip for octupole electric component"),
        "PHI5": (0.0 * _ureg.volt, "potential at pole tip for decapole electric component"),
        "PHI6": (0.0 * _ureg.volt, "potential at pole tip for dodecapole electric component"),
        "PHI7": (0.0 * _ureg.volt, "potential at pole tip for 14-pole electric component"),
        "PHI8": (0.0 * _ureg.volt, "potential at pole tip for 16-pole electric component"),
        "PHI9": (0.0 * _ureg.volt, "potential at pole tip for 18-pole electric component"),
        "PHI10": (0.0 * _ureg.volt, "potential at pole tip for 20-pole electric component"),
        "X_E_El": (0.0 * _ureg.cm, "Entrance face integration zone for the fringe field."),
        "LAM_E_El": (0.0 * _ureg.cm, "Entrance face dipole fringe field extent"),
        "E2_El": (1.0, "Quadrupole entrance fringe field extent (E_2 * LAM_E)."),
        "E3_El": (1.0, "Sextupolar entrance fringe field extent (E_3 * LAM_E)."),
        "E4_El": (1.0, "Octupolar entrance fringe field extent (E_4 * LAM_E)."),
        "E5_El": (1.0, "Decapolar entrance fringe field extent (E_5 * LAM_E)."),
        "E6_El": (1.0, "Dodecapolar entrance fringe field extent (E_6 * LAM_E)."),
        "E7_El": (1.0, "14-polar entrance fringe field extent (E_7 * LAM_E)."),
        "E8_El": (1.0, "16-polar entrance fringe field extent (E_8 * LAM_E)."),
        "E9_El": (1.0, "18-polar entrance fringe field extent (E_9 * LAM_E)."),
        "E10_El": (1.0, "20-polar entrance fringe field extent (E_10 * LAM_E)."),
        # 'NCE': (6, 'UNUSED'),
        "C0_E_El": (0.0, "Fringe field coefficient C0"),
        "C1_E_El": (1.0, "Fringe field coefficient C1"),
        "C2_E_El": (0.0, "Fringe field coefficient C2"),
        "C3_E_El": (0.0, "Fringe field coefficient C3"),
        "C4_E_El": (0.0, "Fringe field coefficient C4"),
        "C5_E_El": (0.0, "Fringe field coefficient C5"),
        "X_S_El": (0.0 * _ureg.centimeter, "Exit face integration zone for the fringe field"),
        "LAM_S_El": (0.0 * _ureg.centimeter, "Exit face fringe field extent"),
        "S2_El": (1.0, "Quadrupole exit fringe field extent (E_2 * LAM_S)."),
        "S3_El": (1.0, "Sextupolar exit fringe field extent (E_3 * LAM_S)."),
        "S4_El": (1.0, "Octupolar exit fringe field extent (E_4 * LAM_S)."),
        "S5_El": (1.0, "Decapolar exit fringe field extent (E_5 * LAM_S)."),
        "S6_El": (1.0, "Dodecapolar exit fringe field extent (E_6 * LAM_S)."),
        "S7_El": (1.0, "14-polar exit fringe field extent (E_7 * LAM_S)."),
        "S8_El": (1.0, "16-polar exit fringe field extent (E_8 * LAM_S)."),
        "S9_El": (1.0, "18-polar exit fringe field extent (E_9 * LAM_S)."),
        "S10_El": (1.0, "20-polar exit fringe field extent (E_10 * LAM_S)."),
        # 'NCS': (6, 'UNUSED'),
        "C0_S_El": (0.0, "Fringe field coefficient C0"),
        "C1_S_El": (1.0, "Fringe field coefficient C1"),
        "C2_S_El": (0.0, "Fringe field coefficient C2"),
        "C3_S_El": (0.0, "Fringe field coefficient C3"),
        "C4_S_El": (0.0, "Fringe field coefficient C4"),
        "C5_S_El": (0.0, "Fringe field coefficient C5"),
        "R1_El": (0.0 * _ureg.radian, "Skew angle of the dipolar elecric field component"),
        "R2_El": (0.0 * _ureg.radian, "Skew angle of the quadrupolar elecric field component"),
        "R3_El": (0.0 * _ureg.radian, "Skew angle of the sextupolar elecric field component"),
        "R4_El": (0.0 * _ureg.radian, "Skew angle of the octupolar elecric field component"),
        "R5_El": (0.0 * _ureg.radian, "Skew angle of the decapolar elecric field component"),
        "R6_El": (0.0 * _ureg.radian, "Skew angle of the dodecapolar elecric field component"),
        "R7_El": (0.0 * _ureg.radian, "Skew angle of the 14-polar elecric field component"),
        "R8_El": (0.0 * _ureg.radian, "Skew angle of the 16-polar elecric field component"),
        "R9_El": (0.0 * _ureg.radian, "Skew angle of the 18-polar elecric field component"),
        "R10_El": (0.0 * _ureg.radian, "Skew angle of the 20-polar elecric field component"),
        # Magnetic poles
        "XL": (0.0 * _ureg.centimeter, "Length of element"),
        "R0": (10.0 * _ureg.centimeter, "Radius at pole tip"),
        "B1": (0 * _ureg.kilogauss, "Field at pole tip for dipolar component."),
        "B2": (0 * _ureg.kilogauss, "Field at pole tip for quadrupolar component."),
        "B3": (0 * _ureg.kilogauss, "Field at pole tip for sextupolar component."),
        "B4": (0 * _ureg.kilogauss, "Field at pole tip for octupolar component."),
        "B5": (0 * _ureg.kilogauss, "Field at pole tip for decapolar component."),
        "B6": (0 * _ureg.kilogauss, "Field at pole tip for dodecapolar component."),
        "B7": (0 * _ureg.kilogauss, "Field at pole tip for 14-polar component."),
        "B8": (0 * _ureg.kilogauss, "Field at pole tip for 16-polar component."),
        "B9": (0 * _ureg.kilogauss, "Field at pole tip for 18-polar component."),
        "B10": (0 * _ureg.kilogauss, "Field at pole tip for 20-polar component."),
        "X_E": (0.0 * _ureg.cm, "Entrance face integration zone for the fringe field."),
        "LAM_E": (0.0 * _ureg.cm, "Entrance face dipole fringe field extent"),
        "E2": (1.0, "Quadrupole entrance fringe field extent (E_2 * LAM_E)."),
        "E3": (1.0, "Sextupolar entrance fringe field extent (E_3 * LAM_E)."),
        "E4": (1.0, "Octupolar entrance fringe field extent (E_4 * LAM_E)."),
        "E5": (1.0, "Decapolar entrance fringe field extent (E_5 * LAM_E)."),
        "E6": (1.0, "Dodecapolar entrance fringe field extent (E_6 * LAM_E)."),
        "E7": (1.0, "14-polar entrance fringe field extent (E_7 * LAM_E)."),
        "E8": (1.0, "16-polar entrance fringe field extent (E_8 * LAM_E)."),
        "E9": (1.0, "18-polar entrance fringe field extent (E_9 * LAM_E)."),
        "E10": (1.0, "20-polar entrance fringe field extent (E_10 * LAM_E)."),
        # 'NCE': (6, 'UNUSED'),
        "C0_E": (0.0, "Fringe field coefficient C0"),
        "C1_E": (1.0, "Fringe field coefficient C1"),
        "C2_E": (0.0, "Fringe field coefficient C2"),
        "C3_E": (0.0, "Fringe field coefficient C3"),
        "C4_E": (0.0, "Fringe field coefficient C4"),
        "C5_E": (0.0, "Fringe field coefficient C5"),
        "X_S": (0.0 * _ureg.centimeter, "Exit face integration zone for the fringe field"),
        "LAM_S": (0.0 * _ureg.centimeter, "Exit face fringe field extent"),
        "S2": (1.0, "Quadrupole exit fringe field extent (E_2 * LAM_S)."),
        "S3": (1.0, "Sextupolar exit fringe field extent (E_3 * LAM_S)."),
        "S4": (1.0, "Octupolar exit fringe field extent (E_4 * LAM_S)."),
        "S5": (1.0, "Decapolar exit fringe field extent (E_5 * LAM_S)."),
        "S6": (1.0, "Dodecapolar exit fringe field extent (E_6 * LAM_S)."),
        "S7": (1.0, "14-polar exit fringe field extent (E_7 * LAM_S)."),
        "S8": (1.0, "16-polar exit fringe field extent (E_8 * LAM_S)."),
        "S9": (1.0, "18-polar exit fringe field extent (E_9 * LAM_S)."),
        "S10": (1.0, "20-polar exit fringe field extent (E_10 * LAM_S)."),
        # 'NCS': (6, 'UNUSED'),
        "C0_S": (0.0, "Fringe field coefficient C0"),
        "C1_S": (1.0, "Fringe field coefficient C1"),
        "C2_S": (0.0, "Fringe field coefficient C2"),
        "C3_S": (0.0, "Fringe field coefficient C3"),
        "C4_S": (0.0, "Fringe field coefficient C4"),
        "C5_S": (0.0, "Fringe field coefficient C5"),
        "R1": (0.0 * _ureg.radian, "Skew angle of the dipolar magnetic field component"),
        "R2": (0.0 * _ureg.radian, "Skew angle of the quadrupolar magnetic field component"),
        "R3": (0.0 * _ureg.radian, "Skew angle of the sextupolar magnetic field component"),
        "R4": (0.0 * _ureg.radian, "Skew angle of the octupolar magnetic field component"),
        "R5": (0.0 * _ureg.radian, "Skew angle of the decapolar magnetic field component"),
        "R6": (0.0 * _ureg.radian, "Skew angle of the dodecapolar magnetic field component"),
        "R7": (0.0 * _ureg.radian, "Skew angle of the 14-polar magnetic field component"),
        "R8": (0.0 * _ureg.radian, "Skew angle of the 16-polar magnetic field component"),
        "R9": (0.0 * _ureg.radian, "Skew angle of the 18-polar magnetic field component"),
        "R10": (0.0 * _ureg.radian, "Skew angle of the 20-polar magnetic field component"),
        "XPAS": (1.0 * _ureg.cm, "Integration step."),
        "KPOS": (1, "Alignment parameter: 1 (element aligned) or 2 (misaligned)"),
        "XCE": (0.0 * _ureg.centimeter, "X shift"),
        "YCE": (0.0 * _ureg.centimeter, "Y shift"),
        "ALE": (0.0 * _ureg.radian, "Tilt"),
    }


# Aliases
EBMultipole = EBMult


class EL2Tub(_Command):
    r"""Two-tube electrostatic lens.

    The lens is cylindrically symmetric about the X-axis.
    The length and potential of the first (resp. second) electrode are X1 and V1 (X2 and V2). The distance between the
    two electrodes is D, and their inner radius is :math:`R_0` (Fig. 26). The model for the electrostatic potential
    along the axis is [50]

    .. math::

    V(X) = \frac{V_2 − V_1}{2} th{ωx􏰊}{R_0}(+\frac{V_1 + V_2}{2}) \quad if D = 0
    V(X) = \frac{V_2 − V_1}{2} \frac{1}{2ωD/R_0} ln \frac{ch ω \frac{x+D}{R_0}}{ch ω \frac{x-D}{R_0}}(+\frac{V_1 + V_2}{2}) \quad if D \ne 0

    (x = distance from half-way between the electrodes ; ω = 1.318 ; th = hyperbolic tangent ; ch = hyperbolic cosine)
    from which the field :math:`\vec{E}(X, Y, Z)` and its derivatives are derived following the procedure described in
    section 1.3.1 (note that they don’t depend on the constant term 􏰊 :math:`\frac{V_1 + V_2}{2}` which disappears when
    differentiating).
    Use ``PARTICUL`` prior to ``EL2TUB``, for the definition of particle mass and charge.
    """
    KEYWORD = "EL2TUB"
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        "IL": (0, "Print field and coordinates along trajectories"),
        "X1": (0.0 * _ureg.meter, "Length of first tube"),
        "D": (0.0 * _ureg.meter, "distance between tubes"),
        "X2": (0.0 * _ureg.meter, "length of second tube"),
        "R0": (0.0 * _ureg.centimeter, "inner radius"),  # check units
        "V1": (0.0 * _ureg.volt, "Potential"),
        "V2": (0.0 * _ureg.volt, "Potential"),
        "XPAS": (1.0 * _ureg.cm, "Integration step."),
        "KPOS": (1, "Alignment parameter: 1 (element aligned) or 2 (misaligned)"),
        "XCE": (0.0 * _ureg.centimeter, "X shift"),
        "YCE": (0.0 * _ureg.centimeter, "Y shift"),
        "ALE": (0.0 * _ureg.radian, "Tilt"),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other
        commands (e.g. fit)."""


class ELMir(_Command):
    """Electrostatic N-electrode mirror/lens,straight slits."""

    KEYWORD = "ELMIR"
    """Keyword of the command used for the Zgoubi input data."""


class ELMirCircular(_Command):
    """Electrostatic N-electrode mirror/lens, circular slits."""

    KEYWORD = "ELMIRC"
    """Keyword of the command used for the Zgoubi input data."""


class ELMulti(_Command):
    """Electric multipole."""

    KEYWORD = "ELMULT"
    """Keyword of the command used for the Zgoubi input data."""


class ELRevol(_Command):
    """1-D uniform mesh electric field map."""

    KEYWORD = "ELREVOL"
    """Keyword of the command used for the Zgoubi input data."""


class Unipot(_Command):
    """Unipotential cylindrical electrostatic lens."""

    KEYWORD = "UNIPOT"
    """Keyword of the command used for the Zgoubi input data."""
