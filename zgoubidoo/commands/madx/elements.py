from ... import ureg as _ureg
from ..commands import Command as _Command
from ..commands import CommandType as _CommandType


class MadElementCommandType(_CommandType):
    """
    Dark magic.
    Be careful.

    TODO
    """
    pass


class MadElementCommand(_Command, metaclass=MadElementCommandType):
    """MAD Command.

    """
    def __str__(self) -> str:
        """
        Provides the string representation of the command in the MAD-X input format.

        Returns:
            The string representation.
        """
        cmd = f"{self.LABEL1}: {self.KEYWORD}, "
        for p, v in self.PARAMETERS.items():
            if p is not 'LABEL1':
                try:
                    value = getattr(self, p).m_as(v[0].units)
                except (ValueError, AttributeError):
                    value = getattr(self, p)
                cmd += f"{p}={value}, " if getattr(self, p) else ''
        cmd = cmd.rstrip(', ')
        cmd += ';'
        return cmd


class MadInstance(_Command, metaclass=MadElementCommandType):
    """A class is the name of an element (or basic type) from which other elements have been derived."""
    PARAMETERS = {
        'CLASS': ('', '')
    }

    def __str__(self) -> str:
        """
        Provides the string representation of the command in the MAD-X input format.

        Returns:
            The string representation.
        """
        return f"{self.LABEL1}: {self.CLASS};"


class Sequence(MadElementCommand):
    """A MAD-X sequence."""
    KEYWORD = 'SEQUENCE'
    """Keyword of the command used for the MAD-X input data."""

    PARAMETERS = {
        'L': (0 * _ureg.m, 'The total length of the sequence in meters.'),
    }
    """Parameters of the command, with their default value and their description."""

    def post_init(self, elements=None, **kwargs):
        """Post-initialization of the sequence"""
        self._elements = elements or []

    def add(self, element, at):
        """Add an element or a class to the sequence."""
        self._elements.append((element, at))
        return self

    def __str__(self) -> str:
        cmd = f"{self.LABEL1}: {self.KEYWORD}, "
        for p, v in self.PARAMETERS.items():
            if p is not 'LABEL1':
                try:
                    value = getattr(self, p).m_as(v[0].units)
                except (ValueError, AttributeError):
                    value = getattr(self, p)
                cmd += f"{p}={value}, " if getattr(self, p) else ''
        cmd = cmd.rstrip(', ')
        cmd += ';\n'
        for e in self._elements:
            cmd += f"    {str(e[0]).rstrip(';')}, AT={e[1].m_as('m')};\n"
        cmd += 'ENDSEQUENCE;'
        return cmd


class Drift(MadElementCommand):
    """
    A drift space.

    The straight reference system for a drift space is a Cartesian coordinate system.
    """
    KEYWORD = 'DRIFT'
    """Keyword of the command used for the MAD-X input data."""

    PARAMETERS = {
        'L': (0 * _ureg.m, 'The drift length (Default: 0 m).'),
    }
    """Parameters of the command, with their default value and their description."""


class Marker(MadElementCommand):
    """
    The simplest element which can occur in a beam line is a MARKER. It has zero length and has no effect on the beam,
    but it allows one to identify a position in the beam line, for example to apply a matching constraint.
    """
    KEYWORD = 'MARKER'
    """Keyword of the command used for the MAD-X input data."""


class BendType(MadElementCommandType):
    pass


class Bend(MadElementCommand, metaclass=BendType):
    """A base class for the two kinds of BENDs in MAD-X: SBEND and RBEND."""
    PARAMETERS = {
        'L': (0 * _ureg.m, 'The length of the magnet (default: 0 m). For sector bends the declared length is the arc '
                           'length of the reference orbit. For rectangular bends the declared length is normally the '
                           'length of a straight line joining the entry and exit points, as in the Figure. Internally '
                           'MAD-X only uses the arc length of the reference orbit for both bend types. In order to '
                           'define RBEND’s with a declared length equal to the arc length of the reference orbit, the '
                           'option RBARC must be previously set to FALSE in MAD-X with Option, RBARC=false;'),
        'ANGLE': (0 * _ureg.radian, 'The bend angle (default: 0 rad). A positive bend angle represents a bend to the '
                                    'right, i.e. towards negative x values. Please notice that ANGLE is used to define '
                                    'bend strength, K0. To define the roll angle use TILT.'),
        'ADD_ANGLE': (None, 'An array of (maximum 5) bending angles for multiple passes. See ADD_PASS option of the '
                            'SEQUENCE command.'),
        'TILT': (0 * _ureg.radian, 'The roll angle about the longitudinal axis (default: 0 rad, i.e. a horizontal '
                                   'bend). A positive angle represents a clockwise rotation. An attribute TILT=pi/2 '
                                   'turns a horizontal into a vertical bend, and a positive ANGLE then denotes a '
                                   'downwards deflection.'),
        'K1': (None, 'The quadrupole coefficient (Default: 0 m−2) K1 = (1/Bρ)(∂By/∂x). A positive quadrupole strength '
                     'implies horizontal focussing of particles, irre- spective of their charge. K1 is taken into '
                     'account in thick bend transfer map. Only K0 and K1 are considered for think transfer map, not '
                     'any other strengths (like K2, K1S).'),
        'E1': (None, 'The rotation angle for the entrance pole face (Default: 0 rad).'),
        'E2': (None, 'The rotation angle for the exit pole face (Default: 0 rad).'),
        'FINT': (0, 'The fringe field integral at entrance and exit of the bend. (Default: 0).'),
        'FINTX': (None, 'If defined and positive, the fringe field integral at the exit of the element, overriding '
                        'FINT for the exit (Default: =FINT). This allows to set different fringe field integrals at '
                        'entrance (FINT) and exit (FINTX) of the element.'),
        'HGAP': (None, 'The half gap of the magnet (default: 0 m).'),
        'K2': (None, 'The sextupole coefficient. (Default: 0 m−3). Please note that K2 is not taken into account for '
                     'bend transfer map.'),
        'K1S': (None, 'The skew quadrupole coefficient. Ks = 1/(2Bρ)(∂Bx/∂x − ∂By/∂y) where (x,y) is a coordinate '
                      'system rotated by −45 degrees around s with respect to the normal one. The default is 0 m−2. '
                      'A positive skew quadrupole strength implies defocussing, irrespective of the charge of the '
                      'particles, in the (x,s) plane rotated by 45◦ around s (particles in this plane have x = y > 0). '
                      'Please note that K1S is not taken into account for bend transfer map.'),
        'H1': (None, 'The curvature of the entrance pole face. (Default: 0 m−1).'),
        'H2': (None, 'The curvature of the exit pole face. (Default: 0 m−1)'),
        'K0': (None, 'Please take note that K0 and K0S are left in the data base but are no longer used for the MAP of '
                     'the bends, instead ANGLE and TILT are used exclusively. However, K0 is assignment of relative '
                     'field errors to a bending magnet because K0 is used for the normalization instead of the ANGLE. '
                     '(see EFCOMP). With K0 = (1/Bρ)By, one gets K0 = ANGLE / arclength.'),
        'THICK': (None, 'If this logical flag is set to true the bending magnet is tracked through as a thick-element, '
                        'instead of being converted into thin-lenses. (Default: false)'),
        'KILL_ENT_FRINGE': (None, 'If this logical flag is set to true the fringe fields on the entrance of the '
                                  'element are not taken into account (not calculated). (Default: false).'),
        'KILL_EXT_FRINGE': (None, 'If this logical flag is set to true the fringe fields on the exit of the element '
                                  'are not taken into account (not calculated). (Deefault: false).')
    }
    """Parameters of the command, with their default value and their description."""


class RBend(Bend):
    """
    A drift space.

    The straight reference system for a drift space is a Cartesian coordinate system.
    """
    KEYWORD = 'RBEND'
    """Keyword of the command used for the MAD-X input data."""


class SBend(Bend):
    """
    Sector bending magnet.

    The planes of the pole faces intersect at the centre of curvature of the curved sbend reference system.
    """
    KEYWORD = 'SBEND'
    """Keyword of the command used for the MAD-X input data."""


class DipEdge(MadElementCommand):
    """
    A thin element describing the edge focusing of a dipole has been introduced in order to make it possible to track
    trajectories in the presence of dipoles with pole face angles. Only linear terms are considered since the higher
    order terms would make the tracking non-symplectic. The transformation of the machine elements into thin lenses
    leaves dipole edge (DIPEDGE) elements untouched and splits correctly the SBEND’s.

    It does not make sense to use a DIPEDGE alone. It can be specified at the entrance and the exit of a SBEND.
    """
    KEYWORD = 'DIPEDGE'
    """Keyword of the command used for the MAD-X input data."""


class Quadrupole(MadElementCommand):
    """A magnetic quadrupole."""
    KEYWORD = 'QUADRUPOLE'
    """Keyword of the command used for the MAD-X input data."""

    PARAMETERS = {
        'L': (0 * _ureg.m, 'The quadrupole length (default: 0 m).'),
        'K1': (0, 'The normal quadrupole coefficient: K1 = 1/(Bρ)(∂By/∂x). The default is 0 m−2. A positive normal '
                  'quadrupole strength implies horizontal focussing, irrespective of the charge of the particles.'),
        'K1S': (0, 'The skew quadrupole coefficient K1s = 1/(2Bρ)(∂Bx/∂x − ∂By/∂y) where (x,y) is now a coordinate '
                   'system rotated by −45◦ around s with respect to the normal one. The default is 0 m−2. '
                   'A positive skew quadrupole strength implies defocussing, irrespective of the charge of the '
                   'particles, in the (x,s) plane rotated by 45◦ around s (particles in this plane have x = y > 0).'),
        'TILT': (None, 'The roll angle about the longitudinal axis (default: 0 rad, i.e. a normal quadrupole). A '
                       'positive angle represents a clockwise rotation. A TILT=pi/4 turns a positive normal quadrupole '
                       'into a negative skew quadrupole.'),
        'THICK': (None, 'If this logical flag is set to true the quadrupole is tracked through as a thick- element, '
                        'instead of being converted into thin-lenses. (Default: false).')
    }
    """Parameters of the command, with their default value and their description."""
