"""TODO"""
from ..commands import Command as _Command
from ..commands import CommandType as _CommandType


class MadCommandType(_CommandType):
    """
    Dark magic.
    Be careful.

    TODO
    """
    pass


class MadCommand(_Command, metaclass=MadCommandType):
    """MAD Command.

    """
    PARAMETERS: dict = {
        'LABEL1': (None, 'Primary label for the Zgoubi command (default: auto-generated hash).'),
        'LABEL2': (None, 'Secondary label for the Zgoubi command.'),
    }

    def post_init(self, **kwargs):
        """Remove unnecessary labels."""
        self.LABEL1 = None
        self.LABEL2 = None

    def __str__(self) -> str:
        """
        Provides the string representation of the command in the MAD-X input format.

        Returns:
            The string representation.

        """
        cmd = f"{self.KEYWORD}, "
        for p in self.PARAMETERS.keys():
            if p is not 'LABEL1':
                cmd += f"{p}={getattr(self, p)}, " if getattr(self, p) else ''
        cmd = cmd.rstrip(', ')
        cmd += ';'
        return cmd


class Beam(MadCommand):
    """
    TODO
    """
    KEYWORD = 'BEAM'
    """Keyword of the command used for the MAD-X input data."""

    PARAMETERS = {
        'PARTICLE': ('PROTON', ''),
        'MASS': (None, ''),
        'CHARGE': (None, ''),
        'ENERGY': (None, ''),
        'PC': (None, ''),
        'GAMMA': (None, ''),
        'BETA': (None, ''),
        'BRHO': (None, ''),
        'EX': (None, ''),
        'EXN': (None, ''),
        'EY': (None, ''),
        'EYN': (None, ''),
        'ET': (None, ''),
        'SIGT': (None, ''),
        'SIGE': (None, ''),
        'KBUNCH': (None, 'The number of particle bunches in the machine (default: 1).'),
        'NPART': (None, 'The number of particles per bunch (default: 0).'),
        'BCURRENT': (None, ''),
        'BUNCHED': (False, 'A logical flag. If set, the beam is treated as bunched whenever this makes sense.'),
        'RADIATE': (False, 'A logical flag. If set, synchrotron radiation is considered in all dipole magnets.'),
        'BV': (None, 'An integer specifying the direction of the particle movement in a beam line; either +1 (default),'
                     ' or -1.'),
        'SEQUENCE': (None, 'Attaches the defined beam to the named sequence; if the name is omitted, the BEAM command '
                           'refers to the default beam which is always present. Sequences without attached beam use '
                           'this default beam. When updating a beam with a corresponding sequence name, tye sequence '
                           'name must always be mentioned.')
    }
    """Parameters of the command, with their default value and their description."""


class Call(MadCommand):
    """
    TODO
    """
    KEYWORD = ' CALL'

    def __str__(self) -> str:
        return f"{self.KEYWORD}, FILE={self.FILE};"


class Exit(MadCommand):
    """ends the execution of MAD-X."""
    KEYWORD = 'EXIT'
    """Keyword of the command used for the MAD-X input data."""


class Help(MadCommand):
    """The HELP command prints all parameters, and their defaults values, for the statement given; this includes basic
    element types."""
    KEYWORD = 'HELP'
    """Keyword of the command used for the MAD-X input data."""


class MakeThin(MadCommand):
    """
    TODO
    """
    pass


class Option(MadCommand):
    """
    TODO
    """
    KEYWORD = 'OPTION'


class Quit(MadCommand):
    """ends the execution of MAD-X."""
    KEYWORD = 'QUIT'
    """Keyword of the command used for the MAD-X input data."""


class SaveBeta(MadCommand):
    """
    TODO
    """
    KEYWORD = 'SAVEBETA'

    def __str__(self) -> str:
        return f"{self.KEYWORD}, LABEL={self.LABEL}, PLACE={self.PLACE};"


class Show(MadCommand):
    """The SHOW command prints the command (typically beam, beam%sequ, or an element name), with the actual value of all
    its parameters."""
    KEYWORD = 'SHOW'

    def __str__(self) -> str:
        return f"{self.KEYWORD}, {self.WHAT};"


class Stop(MadCommand):
    """ends the execution of MAD-X."""
    KEYWORD = 'STOP'
    """Keyword of the command used for the MAD-X input data."""


class Survey(MadCommand):
    """
    TODO
    """
    KEYWORD = 'SURVEY'

    def __str__(self) -> str:
        return f"{self.KEYWORD}, FILE={self.FILE};"


class System(MadCommand):
    """Transfers the quoted string to the operating system for execution. The quotes are stripped and no check of the
    return status is performed by MAD-X."""
    KEYWORD = 'SYSTEM'
    """Keyword of the command used for the MAD-X input data."""


class Title(MadCommand):
    """Defines a string that is inserted as title in various table outputs and plot results."""
    KEYWORD = 'TITLE'
    """Keyword of the command used for the MAD-X input data."""


class Track(MadCommand):
    """
    TODO
    """
    pass


class Twiss(MadCommand):
    """
    TODO
    """
    KEYWORD = 'TWISS'
    """Keyword of the command used for the MAD-X input data."""

    PARAMETERS = {
        'SEQUENCE': (None, 'The name of a valid sequence for which the calculation of optical functions should be '
                           'performed. SEQUENCE and LINE are mutually exclusive. (Default: sequence or beam line '
                           'defined in the latest USE command)'),
        'LINE': (None, 'the name of a valid beamline for which the calculation of optical functions should be '
                       'performed. SEQUENCE and LINE are mutually exclusive. (Default: sequence or beam line defined '
                       'in the latest USE command)'),
        'RANGE': (None, '(Default: #S/#E). The TWISS calculation is restricted to the specified range.'),
        'DELTAP': (None, 'The relative energy error DELTAP may be entered in one of the two forms above. The first '
                         'form lists several numbers, which may be general expressions, sepa- rated by commas. The '
                         'second form specifies an initial value, a final value, and a step, which must be constant '
                         'expressions, separated by colons. For example, DELTAP=0.001 defines a single value, '
                         'DELTAP=0.001,0.005 de- fines two values and DELTAP=0.001:0.007:0.002 defines four values.'),
        'CHROM': (None, 'A logical flag to trigger computation of the chromatic functions as well as the radiation '
                        'synchrotron integrals.'),
        'CENTRE': (None, 'A logical flag to enforce the calculation of the linear lattice functions at the center of '
                         'the element instead of the end of the element. The values in the tables and in the output '
                         'files are affected by this flag. (Default: false)'),
        'TOLERANCE': (None, 'The maximum closed orbit error, for all six orbit components, that can be tolerated '
                            'during the closed orbit search. The value given in the TWISS command is only valid for '
                            'the current calculation; the COGUESS command allows to change the default value for '
                            'all subsequent closed orbit search calculations. (Default: 1.e-6)'),
        'FILE': ('twiss.outx', 'Causes MAD-X to write a TFS Twiss table to the file specified. (Default: “twiss”) '
                               'The columns of the table can be selected using the SELECT command with the '
                               'FLAG=twiss attribute.'),
        'TABLE': (None, 'The name of the table where linear lattice functions as well as chromatic functions are '
                        'stored. (Default: “twiss”)'),
        'NOTABLE': (None, 'Logical flag to prevent the creation of the internal twiss table. Consequently, no output '
                          'file is created either.'),
        'RMATRIX': (None, 'If this flag is used the the one-turn map at the location of every element is calculated '
                          'and prepared for storage in the twiss table. Using the SELECT command and using the column '
                          'RE, RE11 ...RE16 ...RE61 ...RE66 these components will be added to the twiss table, i.e. '
                          'with "COLUMN, RE" and "COLUMN, REij" one gets all or the component ”ij” respectively.'),
    }
    """Parameters of the command, with their default value and their description."""


class Use(MadCommand):
    """
    MAD-X operates on beamlines that must be loaded and expanded in memory before other commands can be invoked.
    The USE command allows this loading and expansion.

    Note that reloading a sequence with the USE command reloads a bare sequence and that any
ERROR or orbit correction previously assigned or associated to the sequence are discarded. A mechanism to select a
sequence without this side effect of the USE command is provided with the SET, SEQUENCE=... command.
    """
    KEYWORD = 'USE'
    """Keyword of the command used for the MAD-X input data."""

    PARAMETERS = {
        'SEQUENCE': (None, 'Name of the sequence to be loaded and expanded.'),
        'PERIOD': (None, 'Name of the sequence to be loaded and expanded. PERIOD is an alias to SEQUENCE that was kept '
                         'for backwards compatibility with MAD-8 and only one of them should be specified in a USE '
                         'statement.'),
        'RANGE': (None, 'Specifies a range. Restriction so that only the specified part of the named sequence is '
                        'loaded and expanded.'),
        'SURVEY': (None, 'Option to plug the survey data into the sequence elements nodes on the first pass '
                         '(see SURVEY).'),
    }
    """Parameters of the command, with their default value and their description."""
