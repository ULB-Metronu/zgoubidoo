"""Zgoubidoo's interfaces to spin tracking commands.

More details here.
"""
from .commands import Command as _Command
from .commands import ZgoubidooException as _ZgoubidooException


class SpinRotation(_Command):
    """Spin rotation."""
    KEYWORD = 'SPINR'


class Spnprnl(_Command):
    """Store spin coordinates into file FNAME."""
    KEYWORD = 'SPNPRNL'


class SpinStore(_Command):
    """Store spin coordinates every IP other pass at labeled elements."""
    KEYWORD = 'SPNSTORE'


class SpnPrt(_Command):
    """Print spin coordinates."""


SpinPrint = SpnPrt


class SpnTrk(_Command):
    """Spin tracking."""

    PARAMETERS = {
        'KSO': (1, ''),
        'IR': (1, 'Random sequence seed.')
    }

    def __str__(self) -> str:
        if self.KSO not in (1, 2, 3, 4, 4.1, 5):
            raise _ZgoubidooException("KPOS must be in (0, 1, 2, 3, 4, 4.1, 5).")
        return f"""
        {super().__str__().rstrip()}
        {self.KSO:d}
        {int(self.IR):d}
        """


SpinTracking = SpnTrk
