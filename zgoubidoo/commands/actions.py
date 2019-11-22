"""
TODO
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Union, Tuple, Iterable, Mapping
import pandas as _pd
from .commands import CommandType as _CommandType
from .commands import Command as _Command
from .commands import ZgoubidooException as _ZgoubidooException
from georges_core.utils import fortran_float
from .. import Q_ as _Q
if TYPE_CHECKING:
    from ..input import Input as _Input


class ActionType(_CommandType):
    """TODO"""
    pass


class Action(_Command, metaclass=ActionType):
    """TODO"""
    pass


class End(Action):
    """End of input data list.

    .. rubric:: Zgoubi manual description

    The end of a problem, or of a set of several problems stacked in the data file, should be stated by means of the
    keywords FIN or END.

    Any information following these keywords will be ignored.

    In some cases, these keywords may cause some information to be printed in zgoubi.res, for instance when the keyword
    PICKUPS is used.
    """
    KEYWORD = 'END'
    """Keyword of the command used for the Zgoubi input data."""


class Faisceau(Action):
    """Print coordinates.

    .. rubric:: Zgoubi manual description

    Print particle coordinates at the location where the keyword is introduced in the structure.
    """
    KEYWORD = 'FAISCEAU'
    """Keyword of the command used for the Zgoubi input data."""


class Faiscnl(Action):
    """Store coordinates in file.

    .. rubric:: Zgoubi manual description

    Store particle coordinates in file FNAME.
    """
    KEYWORD = 'FAISCNL'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'FNAME': 'zgoubi.fai',
        'B_FNAME': 'b_zgoubi.fai',
        'binary': (False, 'Binary storage format.'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.B_FNAME if self.binary else self.FNAME}
        """


class Fin(Action):
    """End of input data list.

    The end of a problem, or of a set of several problems stacked in the data file, should be stated by means of the
    keywords FIN or END.

    Any information following these keywords will be ignored.

    In some cases, these keywords may cause some information to be printed in zgoubi.res, for instance when the keyword
    PICKUPS is used.
    """
    KEYWORD = 'FIN'
    """Keyword of the command used for the Zgoubi input data."""


class FitType(ActionType):
    """Type for fit commands."""
    pass


class Fit(Action, metaclass=FitType):
    """Fitting procedure.

    TODO
    """
    KEYWORD = 'FIT'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'PARAMS': ([], 'Physical parameters to be varied'),
        'CONSTRAINTS': ([], 'Constraints'),
        'PENALTY': (1.0e-10, 'Penalty'),
        'ITERATIONS': (50000, 'Iterations'),
        'FINAL': (True, 'If true, Zgoubi will do an extra pass with the variables set with the fit results'),
        'SAVE': (True, 'If true, Zgoubi will save the results to file'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    class FitCoordinates:
        """Zgoubi coordinates."""
        DP = 1
        Y = 2
        T = 3
        Z = 4
        P = 5

    class Parameter:
        """
        TODO
        """
        def __init__(self,
                     line: _Input,
                     place: Union[str, _Command],
                     parameter: Union[int, Iterable],
                     parameter_range: Optional[Union[float, Tuple[float]]] = None):
            """

            Args:
                line:
                place:
                parameter:
                parameter_range:
            """
            self.IR: int = line.zgoubi_index(place)
            try:
                self.IP: int = parameter[2]
            except TypeError:
                self.IP: int = parameter
            self.XC: int = 0
            self.DV: Union[float, Tuple[float]] = parameter_range if parameter_range is not None else [-100.0, 100.0]

        def __getitem__(self, item):
            return getattr(self, item)

    class Constraint:
        """Generic constraint."""
        def __getitem__(self, item):
            return getattr(self, item)

    class SigmaMatrixConstraint(Constraint):
        """Constraint on the coefficients of the sigma matrix."""
        def __init__(self,
                     line: _Input,
                     place: Union[str, _Command],
                     i: int,
                     j: int,
                     value: float = 0.0,
                     weight: float = 1.0,
                     ):
            """

            Args:
                line:
                place:
                i:
                j:
                value:
                weight:
            """
            self.IC: float = 0
            self.I: int = i
            self.J: int = j
            self.IR: int = line.zgoubi_index(place)
            self.V: float = value
            self.WV: float = weight
            self.NP: int = 0

    class FirstOrderTransportCoefficientsConstraint(Constraint):
        """Constraint on the coefficients of the transfer matrix."""
        def __init__(self,
                     line: _Input,
                     place: Union[str, _Command],
                     i: int,
                     j: int,
                     value: float = 0.0,
                     weight: float = 1.0,
                     ):
            """

            Args:
                line:
                place:
                i:
                j:
                value:
                weight:
            """
            self.IC: float = 1
            self.I: int = i
            self.J: int = j
            self.IR: int = line.zgoubi_index(place)
            self.V: float = value
            self.WV: float = weight
            self.NP: int = 0

    class SecondOrderTransportCoefficientsConstraint(Constraint):
        """Constraint on the coefficients of the second-order transport tensor."""
        def __init__(self,
                     line: _Input,
                     place: Union[str, _Command],
                     i: int,
                     j: int,
                     value: float = 0.0,
                     weight: float = 1.0,
                     ):
            """

            Args:
                line:
                place:
                i:
                j:
                value:
                weight:
            """
            self.IC: float = 2
            self.I: int = i
            self.J: int = j
            self.IR: int = line.zgoubi_index(place)
            self.V: float = value
            self.WV: float = weight
            self.NP: int = 0

    class EllipseParametersConstraint(Constraint):
        """Constraint on the beam ellipse."""
        pass

    class EqualityConstraint(Constraint):
        """Equality constraint on the trajectories."""
        def __init__(self,
                     line: _Input,
                     place: Union[str, _Command],
                     variable: int,
                     value: float = 0.0,
                     weight: float = 1.0,
                     particle: int = 1
                     ):
            """

            Args:
                line:
                place:
                variable:
                value:
                weight:
            """
            self.IC: float = 3
            self.I: int = particle
            self.J: int = variable
            self.IR: int = place if place == '#End' else line.zgoubi_index(place)
            self.V: float = value
            self.WV: float = weight
            self.NP: int = 0

    class DifferenceEqualityConstraint(EqualityConstraint):
        """Equality constraint on the difference between current and initial coordinates."""
        def __init__(self,
                     line: _Input,
                     place: Union[str, _Command],
                     variable: int,
                     value: float = 0.0,
                     weight: float = 1.0,
                     particle: int = 1
                     ):
            super().__init__(line, place, variable, value, weight, particle)
            self.IC = 3.1

    class SumEqualityConstraint(EqualityConstraint):
        """Equality constraint on the difference between current and initial coordinates."""
        def __init__(self,
                     line: _Input,
                     place: Union[str, _Command],
                     variable: int,
                     value: float = 0.0,
                     weight: float = 1.0,
                     particle: int = 1
                     ):
            super().__init__(line, place, variable, value, weight, particle)
            self.IC = 3.2

    class MaxEqualityConstraint(EqualityConstraint):
        """Equality constraint on the difference between current and initial coordinates."""
        def __init__(self,
                     line: _Input,
                     place: Union[str, _Command],
                     variable: int,
                     value: float = 0.0,
                     weight: float = 1.0,
                     particle: int = 1
                     ):
            super().__init__(line, place, variable, value, weight, particle)
            self.IC = 3.3
            self.NP = 2

    class MinEqualityConstraint(EqualityConstraint):
        """Equality constraint on the difference between current and initial coordinates."""
        def __init__(self,
                     line: _Input,
                     place: Union[str, _Command],
                     variable: int,
                     value: float = 0.0,
                     weight: float = 1.0,
                     particle: int = 1
                     ):
            super().__init__(line, place, variable, value, weight, particle)
            self.IC = 3.3
            self.NP = 1

    def __str__(self):
        command = list()
        command.append(super().__str__().rstrip())
        command.append(f"""
        {len(self.PARAMS) - list(self.PARAMS).count(None)} {'nofinal' if not self.FINAL else ''} {'save' if self.SAVE else ''}
        """)
        for p in self.PARAMS:
            if p is None:
                continue
            if isinstance(p['IP'], (list, tuple)):
                ip = p['IP'][2]
            else:
                ip = p['IP']
            if isinstance(p['DV'], (list, tuple)):
                command.append(f"""
        {p['IR']} {ip} {p['XC']} [{p['DV'][0]}, {p['DV'][1]}]
        """)
            else:
                command.append(f"""
        {p['IR']} {ip} {p['XC']} {p['DV']}
        """)
        command.append(f"""
        {len(self.CONSTRAINTS) - list(self.PARAMS).count(None)} {self.PENALTY:.12e} {int(self.ITERATIONS):d}
        """)
        for c in self.CONSTRAINTS:
            if c is None:
                continue
            command.append(f"""
        {c['IC']} {c['I']} {c['J']} {c['IR']} {c['V']} {c['WV']} {c['NP']}
        """)
        return ''.join(map(lambda x: x.rstrip(), command))

    def process_output(self,
                       output: List[str],
                       parameters: Mapping[str, Union[_Q, float]],
                       zgoubi_input: _Input
                       ) -> bool:
        """

        Args:
            output: the output from a Zgoubi run to be processed by the command.
            parameters: TODO
            zgoubi_input: the Input sequence (required and some cases by the command output processor).

        Returns:
            a flag indicating if the processing is valid.
        """

        def find_parameter_by_id(command: int, parameter: int) -> str:
            """

            Args:
                command:
                parameter:

            Returns:

            """
            k = None
            for k, v in zgoubi_input[command - (1 if zgoubi_input.beam is None else 0)].__class__.PARAMETERS.items():
                if v is None:
                    continue
                try:
                    if v[2] == parameter:
                        break
                except (TypeError, IndexError):
                    continue
            return k

        def find_dimension_by_id(command: int, parameter: int):
            """

            Args:
                command:
                parameter:

            Returns:

            """
            for k, v in zgoubi_input[command - 1].__class__.PARAMETERS.items():
                if v is None:
                    continue
                try:
                    if v[2] == parameter:
                        return _Q(v[0]).units
                except (TypeError, IndexError):
                    continue
            return _Q(1)

        grab: bool = False
        status: list = []
        data: list = []
        for line in output:
            if line.strip().startswith('Lmnt'):
                status.append(line)
            if line.strip().startswith('LMNT'):
                grab = True
                continue
            if line.strip().startswith('STATUS OF'):
                grab = False
            if grab:
                values = line.split()
                d = {
                        'element_id': int(values[0]),
                        'variable_id': int(values[1]),
                        'parameter_id': int(values[2]),
                        'parameter': find_parameter_by_id(int(values[0]), int(values[2])),
                        'min': fortran_float(values[3]),
                        'initial': fortran_float(values[4]),
                        'final': fortran_float(values[5]) * find_dimension_by_id(int(values[0]), int(values[2])),
                        'max': fortran_float(values[6]),
                        'stepsize': fortran_float(values[7]),
                }
                if len(values) >= 9:
                    d['name'] = values[8]
                    d['label1'] = values[9]
                    d['label2'] = values[10]
                data.append(d)
        success = False if len(data) == 0 or len(status) > 0 else True
        try:
            try:
                _ = _pd.DataFrame(data).set_index('variable_id')
            except KeyError:
                _ = _pd.DataFrame(data)
            self._results.append(
                (
                    parameters,
                    _Command.CommandResult(success=success, results=_)
                )
            )
        except KeyError:
            raise _ZgoubidooException(f"Results from fit {self.LABEL1} could not be processed.")
        return success


class Fit2(Fit, metaclass=FitType):
    """Fitting procedure.

    Alternative fitting procedure implemented in Zgoubi, see manual.
    """
    KEYWORD = 'FIT2'
    """Keyword of the command used for the Zgoubi input data."""


class Goto(Action):
    """
    TODO
    """
    pass


class Include(Action):
    """
    TODO
    """
    pass


class Options(Action):
    """
    TODO
    """
    KEYWORD = 'OPTIONS'
    """Keyword of the command used for the Zgoubi input data."""

    def post_init(self, write: bool = True, consty: bool = False):
        """

        Args:
            write:
            consty:

        Returns:

        """
        self.LABEL1 = ' '
        self._write = write
        self._consty = consty

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        1 2
        CONSTY {'ON' if self._consty else 'OFF'}
        WRITE {'ON' if self._write else 'OFF'}
        """
