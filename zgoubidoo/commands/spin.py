"""Zgoubidoo's interfaces to spin tracking commands.

More details here.
"""
from .commands import Command as _Command
from .commands import ZgoubidooException as _ZgoubidooException


class SpinRotation(_Command):
    """Spin rotation."""
    KEYWORD = 'SPINR'
    """Keyword of the command used for the Zgoubi input data."""


class Spnprnl(_Command):
    """Store spin coordinates into file FNAME."""
    KEYWORD = 'SPNPRNL'
    """Keyword of the command used for the Zgoubi input data."""


class SpinStore(_Command):
    """Store spin coordinates every IP other pass at labeled elements."""
    KEYWORD = 'SPNSTORE'
    """Keyword of the command used for the Zgoubi input data."""


class SpnPrt(_Command):
    """Print spin coordinates."""
    KEYWORD = 'SPNPRT'
    """Keyword of the command used for the Zgoubi input data."""


SpinPrint = SpnPrt


class SpnTrk(_Command):
    """Spin tracking."""
    KEYWORD = 'SPNTRK'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'KSO': (1, ''),
        'IR': (1, 'Random sequence seed.')
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
        commands (e.g. fit)."""

    def __str__(self) -> str:
        if self.KSO not in (1, 2, 3, 4, 4.1, 5):
            raise _ZgoubidooException("KPOS must be in (0, 1, 2, 3, 4, 4.1, 5).")
        return f"""
        {super().__str__().rstrip()}
        {self.KSO:d}
        {int(self.IR):d}
        """


SpinTracking = SpnTrk
