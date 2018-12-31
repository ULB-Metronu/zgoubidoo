from typing import Optional, List
from ..input import Input
from ..commands.particules import Proton, ParticuleType
from ..commands.commands import Command, Fit2, Marker, FitType
from ..commands.objet import Objet2
import zgoubidoo


class ZgoubidooSequenceException(Exception):
    """Exception raised for errors when using zgoubidoo.Sequence"""

    def __init__(self, m):
        self.message = m


class Sequence:
    """

    """

    def __init__(self, sequence: Optional[List[Command]] = None, particle: Optional[ParticuleType] = Proton):
        """

        Args:
            sequence:
            particle:
        """
        self._sequence: List[Command] = sequence
        self._particle = particle()
        self._closed_orbit = None
        self._z: zgoubidoo.Zgoubi = zgoubidoo.Zgoubi()

    def __getitem__(self, item) -> Command:
        """

        Args:
            item:

        Returns:

        """
        return self._sequence[item]

    def is_valid(self) -> bool:
        """

        Returns:

        Raises:

        """
        if len(self[zgoubidoo.commands.Particule]) > 0:
            raise ZgoubidooSequenceException("A valid sequence should not contain any Particule")

        if len(self[zgoubidoo.commands.Objet]) > 0:
            raise ZgoubidooSequenceException("A valid sequence should not contain any Objet")

        return True

    def find_closed_orbit(self, guess: Optional[List] = None, tolerance: float = 1e-8, method: FitType = Fit2):
        if guess is None:
            guess = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        zi = Input(
            name='CLOSED_ORBIT_FINDER',
            line=[
                     self._particle,
                     Objet2('BUNCH', BORO=2149 * _.kilogauss * _.cm).add([guess])
                 ] + self._sequence + [Marker('__END__')]
        )
        #objet_index = [i for i, x in enumerate(zi) if isinstance(x, Objet2)][0]
        #last_magnet_index = [i for i, x in enumerate(zi) if isinstance(x, Magnet)][-1]
        fit = method(
            PENALTY=tolerance,
            PARAMS=[
                {
                    'IR': objet_index + 1,
                    'IP': 30,  # Y
                    'XC': 0,
                    'DV': [-50, 50],
                },
                {
                    'IR': objet_index + 1,
                    'IP': 31,  # T
                    'XC': 0,
                    'DV': [-50, 50],
                },
                {
                    'IR': objet_index + 1,
                    'IP': 32,  # Z
                    'XC': 0,
                    'DV': [-50, 50],
                },
                {
                    'IR': objet_index + 1,
                    'IP': 33,  # P
                    'XC': 0,
                    'DV': [-50, 50],
                },
            ],
            CONSTRAINTS=[
                {
                    'IC': 3.1,  # F(I, J) - F0(I, J)
                    'I': 1,
                    'J': 2,  # Y
                    'IR': last_magnet_index + 1,
                    'V': 0.0,
                    'WV': 1.0,
                    'NP': 0,
                },
                {
                    'IC': 3.1,  # F(I, J) - F0(I, J)
                    'I': 1,
                    'J': 3,  # T
                    'IR': last_magnet_index + 1,
                    'V': 0.0,
                    'WV': 1.0,
                    'NP': 0,
                },
                {
                    'IC': 3.1,  # F(I, J) - F0(I, J)
                    'I': 1,
                    'J': 4,  # Z
                    'IR': last_magnet_index + 1,
                    'V': 0.0,
                    'WV': 1.0,
                    'NP': 0,
                },
                {
                    'IC': 3.1,  # F(I, J) - F0(I, J)
                    'I': 1,
                    'J': 5,  # P
                    'IR': last_magnet_index + 1,
                    'V': 0.0,
                    'WV': 1.0,
                    'NP': 0,
                }
            ]
        )
        zi.line.append(fit)
        zi.IL = 0
        out = self._z(zi)
        co = out.tracks.query("LABEL1 == '__END__'").iloc[0][['Yo', 'To', 'Zo', 'Po', 'Do-1']].values
        co1 = out.tracks.query("LABEL1 == '__END__'").iloc[0][['Y-DY', 'T', 'Z', 'P', 'D-1']].values
        assert ((co - co1).all() < tolerance)
        self._closed_orbit = co
        return self._closed_orbit

    def track_closed_orbit(self):
        zi = zgoubidoo.Input(
            name='TEST',
            line=[
                     self._particle,
                     Objet2('BUNCH', BORO=2149 * _.kilogauss * _.cm).add([[100 * self._closed_orbit[0],
                                                                           1000 * self._closed_orbit[1],
                                                                           100 * self._closed_orbit[2],
                                                                           1000 * self._closed_orbit[3],
                                                                           0.0,
                                                                           self._closed_orbit[4] + 1,
                                                                           0.0]])
                 ] + self._sequence
        )
        zi.IL = 2
        out = self._z(zi)
        return out.tracks

    def twiss(self):
        """

        Returns:

        """
        pass






