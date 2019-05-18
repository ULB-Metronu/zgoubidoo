"""Patchable elements module."""
from typing import Optional
from .. import ureg as _ureg
from .. import _Q
from ..frame import Frame as _Frame


class Patchable:
    """Patchable elements are Zgoubi commands that affect the placement of the reference frame.

    A default implementation of the placement methods is provided for subclasses. It only places the entrance frame
    at the location of the placement frame and all other frames are set to the entrance frame ('point-like' element).
    """

    def __init__(self):
        """Initializes a un-patched patchable element."""
        self._entry: Optional[_Frame] = None
        self._entry_patched: Optional[_Frame] = None
        self._exit: Optional[_Frame] = None
        self._exit_patched: Optional[_Frame] = None
        self._center: Optional[_Frame] = None

    def place(self, frame: _Frame):
        """Place the element with a reference frame.

        All the frames of the element are reset and the entrance frame is then placed with respect to the reference
        frame.

        Args:
            frame: the reference frame for the placement of the entrance frame.
        """
        self._clear_placement()
        self._entry = _Frame(frame)

    def _clear_placement(self):
        """Clears all the frames."""
        self._entry = None
        self._entry_patched = None
        self._exit = None
        self._exit_patched = None
        self._center = None

    @property
    def length(self) -> _Q:
        """Length of the element.

        Returns:
            the length of the element with units.
        """
        return 0.0 * _ureg.cm

    @property
    def entry(self) -> _Frame:
        """Entrance frame.

        Returns:
            the frame of the entrance of the element.
        """
        return self._entry

    @property
    def entry_patched(self) -> _Frame:
        """Entrance patched frame.

        Returns:
            the frame of the entrance of the element with the patch applied.
        """
        if self._entry_patched is None:
            self._entry_patched = _Frame(self.entry)
        return self._entry_patched

    @property
    def exit(self) -> _Frame:
        """Exit frame.

        Returns:
            the frame of the exit of the element.
        """
        if self._exit is None:
            self._exit = _Frame(self.entry_patched)
        return self._exit

    @property
    def exit_patched(self) -> _Frame:
        """Exit patched frame.

        Returns:
            the frame of the exit of the element with the patch applied.
        """
        if self._exit_patched is None:
            self._exit_patched = _Frame(self.exit)
        return self._exit_patched

    @property
    def center(self) -> _Frame:
        """Center frame.

        Returns:
            the frame of the center of the element.
        """
        if self._center is None:
            self._center = _Frame(self.entry)
        return self._center
