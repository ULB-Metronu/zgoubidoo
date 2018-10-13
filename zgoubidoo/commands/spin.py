from .commands import Command, ZgoubidoException


class SpinRotation(Command):
    """Spin rotation."""
    KEYWORD = 'SPINR'


class Spnprnl(Command):
    """Store spin coordinates into file FNAME."""
    KEYWORD = 'SPNPRNL'


class SpinStore(Command):
    """Store spin coordinates every IP other pass at labeled elements."""
    KEYWORD = 'SPNSTORE'


class SpinPrint(Command):
    """Print spin coordinates."""
    KEYWORD = 'SPNPRT'


spnprt = SpinPrint


class SpinTracking(Command):
    """Spin tracking."""
    KEYWORD = 'SPNTRK'

    PARAMETERS = {
        'KSO': (1, ''),
        'IR': (1, 'Random sequence seed.')
    }

    def __str__(self) -> str:
        if self.KSO not in (1, 2, 3, 4, 4.1, 5):
            raise ZgoubidoException("KPOS must be in (0, 1, 2, 3, 4, 4.1, 5).")
        return f"""
        {super().__str__().rstrip()}
        {self.KSO:d}
        {int(self.IR):d}
        """
