from ..frame import Frame


class Patchable:
    _entry: Frame
    _entry_patched: Frame
    _exit: Frame
    _exit_patched: Frame

    def place(self, frame) -> Frame:
        self._entry = frame

    @property
    def entry(self) -> Frame:
        print("Calling patchable 'entry'")
        return self._entry
