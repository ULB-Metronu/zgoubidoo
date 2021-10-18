"""Patchable elements module."""
from typing import Optional
import pandas as _pd
from .. import ureg as _ureg
from georges_core.frame import Frame as _Frame
from georges_core.patchable import Patchable as _Patchable


class Patchable(_Patchable):
    """Patchable elements are Zgoubi commands that affect the placement of the reference frame.

    A default implementation of the placement methods is provided for subclasses. It only places the entrance frame
    at the location of the placement frame and all other frames are set to the entrance frame ('point-like' element).
    """

    def __init__(self):
        """Initializes a un-patched patchable element."""
        super().__init__()
        self.LABEL1 = None
        self._entry_efb: Optional[_Frame] = None
        self._exit_efb: Optional[_Frame] = None
        self._frenet: Optional[_Frame] = None
        self._reference_trajectory: Optional[_pd.DataFrame] = None

    def adjust_tracks_variables(self, tracks: _pd.DataFrame):
        t = tracks[tracks.LABEL1 == self.LABEL1]
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'SREF'] = t['X'] + self.entry_sref.m_as('m')
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT'] = t['Y']
        try:
            tracks.loc[tracks.LABEL1 == self.LABEL1, 'YT0'] = t['Yo']
        except KeyError:
            pass
        tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT'] = t['Z']
        try:
            tracks.loc[tracks.LABEL1 == self.LABEL1, 'ZT0'] = t['Zo']
        except KeyError:
            pass

    def clear_placement(self):
        self._entry = None
        self._entry_patched = None
        self._exit = None
        self._exit_patched = None
        self._center = None
        self._entry_efb = None
        self._exit_efb = None
        self._frenet = None
        self._reference_trajectory = None

    @property
    def entry_efb(self) -> _Frame:
        """Entrance field boundary patched frame.

        Returns:

        """
        return self._entry_efb

    @property
    def exit_efb(self) -> _Frame:
        """Entrance field boundary patched frame.

        Returns:

        """
        if self._exit_efb is None:
            self._exit_efb = self.entry_patched.__class__(self.entry_patched)
        return self._exit_efb

    @property
    def frenet_orientation(self) -> Optional[_Frame]:
        if self._frenet is None:
            self._frenet = self.entry_patched.__class__(self.entry_patched)
        return self._frenet

    @property
    def entry_s(self) -> Optional[_ureg.Quantity]:
        """

        Returns:

        """
        if self.reference_trajectory is not None:
            return self.reference_trajectory['S'].min() * _ureg.m
        else:
            return 0.0 * _ureg.m

    @property
    def exit_s(self) -> Optional[_ureg.Quantity]:
        """

        Returns:

        """
        if self.reference_trajectory is not None:
            return self.reference_trajectory['S'].max() * _ureg.m
        else:
            return 0.0 * _ureg.m

    @property
    def optical_length(self) -> Optional[_ureg.Quantity]:
        """

        Returns:

        """
        if self.reference_trajectory is not None:
            return (self.reference_trajectory['S'].max() - self.reference_trajectory['S'].min()) * _ureg.m
        else:
            return 0.0 * _ureg.m

    @property
    def optical_ref_length(self) -> Optional[_ureg.Quantity]:
        """

        Returns:

        """
        if self.reference_trajectory is not None:
            return (self.reference_trajectory['S'].max() - self.reference_trajectory['S'].min()) * _ureg.m
        else:
            return 0.0 * _ureg.m
