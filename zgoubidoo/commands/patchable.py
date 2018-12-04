from typing import NoReturn
from .. import ureg as _ureg
from .. import _Q
from ..frame import Frame


class Patchable:
    """Patchable elements are Zgoubi commands that affect the placement of the reference frame.

    TODO
    """
    _entry: Frame
    _entry_patched: Frame
    _exit: Frame
    _exit_patched: Frame
    _center: Frame

    def place(self, frame: Frame) -> NoReturn:
        """

        Args:
            frame:

        Returns:

        """
        self._clear_placement()
        self._entry = frame

    def _clear_placement(self) -> NoReturn:
        self._entry = None
        self._entry_patched = None
        self._exit = None
        self._entry_patched = None
        self._center = None

    @property
    def length(self) -> _Q:
        """

        Returns:

        """
        return 0.0 * _ureg.cm

    @property
    def entry(self) -> Frame:
        """

        Returns:

        """
        return self._entry

    @property
    def entry_patched(self) -> Frame:
        """

        Returns:

        """
        if self._entry_patched is None:
            self._entry_patched = Frame(self.entry)
        return self._entry_patched

    @property
    def exit(self) -> Frame:
        """

        Returns:

        """
        if self._exit is None:
            self._exit = Frame(self.entry_patched)
        return self._exit

    @property
    def exit_patched(self) -> Frame:
        """

        Returns:

        """
        if self._exit_patched is None:
            self._exit_patched = Frame(self.exit)
        return self._exit_patched

    @property
    def center(self) -> Frame:
        """

        Returns:

        """
        if self._center is None:
            self._center = Frame(self.entry)
        return self._center
