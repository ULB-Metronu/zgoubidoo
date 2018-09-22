from ..frame import Frame


class Patchable:
    _entry: Frame
    _entry_patched: Frame
    _exit: Frame
    _exit_patched: Frame
    _center: Frame

    def place(self, frame) -> None:
        self.clear_placement()
        self._entry = frame

    def clear_placement(self) -> None:
        self._entry = None
        self._entry_patched = None
        self._exit = None
        self._entry_patched = None
        self._center = None

    @property
    def entry(self) -> Frame:
        return self._entry

    @property
    def entry_patched(self) -> Frame:
        if self._entry_patched is None:
            self._entry_patched = Frame(self.entry)
        return self._entry_patched

    @property
    def exit(self) -> Frame:
        if self._exit is None:
            self._exit = Frame(self.entry_patched)
        return self._exit

    @property
    def exit_patched(self) -> Frame:
        if self._exit_patched is None:
            self._exit_patched = Frame(self.exit)
        return self._exit_patched
