"""
Commands controlling Zgoubi's control flow, geometry, tracking options, etc.

TODO
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Mapping, Union

import pandas as _pd

from .. import Q_ as _Q
from .actions import Action as _Action

if TYPE_CHECKING:
    from ..input import Input as _Input


class SynchrotronRadiationLosses(_Action):
    """Synchrotron radiation loss.

    .. rubric:: Zgoubi manual description

    The keyword SRLOSS allows activating or stopping (option KSR = 1, 0 respectively) stepwise tracking of energy loss
    by stochastic emission of photons in magnetic fields, following the method described in section 3.1.

    It can be chosen to allow radiation in the sole dipole fields, or in all types of fields regardless of their
    multipole composition. It can also be chosen to allow for the radiation induced transverse kick.

    SRLOSS must be preceded by PARTICUL for defining mass and charge values as they enter in the definition of SR
    parameters.

    Statistics on SR parameters are computed and updated while tracking, the results of which can be obtained by means
    of the keyword SRPRNT.
    """

    KEYWORD = "SRLOSS"
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        "KSR": (1, "Switch (0: SR switched off, 1: SR switched on)."),
        "I": (1, "Output SRLOSS information to file."),
        "KEYWORDS": ("ALL", ""),
        "SCALING": ("", 'If "scale" then scale magnetic field based on energy loss from synchrotron radiation.'),
        "OPTION": (2, "1: effect on DP only, 2 : effect on dp and kick angle."),
        "SEED": (123456, "Random seed."),
    }
    """Parameters of the command, with their default value, their description and optionally an index used by other
    commands (e.g. fit)."""

    def __str__(self):
        return f"""
        {super().__str__().rstrip()}
        {self.KSR}.{self.I} {'PRINT' if self.I else ''}
        {self.KEYWORDS} {self.SCALING}
        {self.OPTION} {self.SEED}
        """

    def switch(self, value: bool = True):
        """Switches on or off the synchrotron radiation losses.

        Args:
            value: value of the switch.
        """
        self.KSR = int(value)
        return self

    def on(self):
        """Switches on the synchrotron radiation losses."""
        self.switch()
        return self

    def off(self):
        """Switches off the synchrotron radiation losses."""
        self.switch(False)
        return self


SRLoss = SynchrotronRadiationLosses


class SynchrotronRadiationPrint(_Action):
    """Print SR loss statistics."""

    KEYWORD = "SRPRNT"
    """Keyword of the command used for the Zgoubi input data."""

    def process_output(
        self,
        output: List[str],
        parameters: Mapping[str, Union[_Q, float]],
        zgoubi_input: _Input,
    ) -> bool:
        """

        Args:
            output:
            parameters:
            zgoubi_input:

        Returns:

        """
        self._results.append(
            (
                parameters,
                _Action.CommandResult(success=True, results=_pd.DataFrame()),
            ),
        )
        return True


SRPrint = SynchrotronRadiationPrint


class SynchrotronRadiationSpectral(_Action):
    """Synchrotron radiation spectral-angular densities."""

    KEYWORD = "SYNRAD"
    """Keyword of the command used for the Zgoubi input data."""
