from .. import output
from ..input import Input
import zgoubidoo

class ZgoubidooSequenceException(Exception):
    pass


class Sequence:
    """

    """

    def __init__(self):
        """

        """
        pass

    def __getitem__(self, item):
        return self._input[item]

    def is_valid(self) -> bool:
        """

        Returns:

        Raises:

        """
        if len(self[zgoubidoo.commands.Particule]) > 0:
            raise ZgoubidooSequenceException("A valid sequence should not contain any Particule")

        if len(self[zgoubidoo.commands.Objet]) > 0:
            raise ZgoubidooSequenceException("A valid sequence should not contain any Objet")

    def find_closed_orbit(self):
        """

        Returns:

        """
        pass

    def twiss(self):
        """

        Returns:

        """
        pass