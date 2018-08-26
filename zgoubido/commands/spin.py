from .commands import Command


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


class SpinTracking(Command):
    """Spin tracking."""
    KEYWORD = 'SPNTRK'
