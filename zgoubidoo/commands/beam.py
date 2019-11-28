"""Zgoubidoo beam.

"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union
import os
from random import randint
import numpy as np
import pandas as pd
from zgoubidoo import Q_ as _Q
from zgoubidoo.commands import CommandType as _CommandType
from zgoubidoo.commands import Command as _Command
from zgoubidoo.commands import Comment as _Comment
from zgoubidoo.commands import particules as _particules
from zgoubidoo.commands import ParticuleType as _ParticuleType
from zgoubidoo.commands import Proton as _Proton
from zgoubidoo.commands import Objet2 as _Objet2
from zgoubidoo.commands import Objet5 as _Objet5
from zgoubidoo.commands import MCObjet3 as _MCObjet3
from zgoubidoo.commands import ObjetType as _ObjetType
from zgoubidoo.commands import ZgoubidooAttributeException as _ZgoubidooAttributeException
from zgoubidoo.commands import ZgoubidooException as _ZgoubidooException
from .. import Kinematics as _Kinematics
from ..mappings import ParametricMapping as _ParametricMapping
from ..mappings import MappedParametersListType as _MappedParametersListType
from .. import ureg as _ureg
if TYPE_CHECKING:
    from georges_core.sequences import BetaBlock as _BetaBlock
    from georges_core.sequences import TwissSequence as _TwissSequence
    from georges_core.sequences import Sequence as _Sequence


class ZgoubidooBeamException(Exception):
    """Exception raised for errors when running Zgoubi."""

    def __init__(self, m):
        self.message = m


class BeamType(_CommandType):
    """Type system for Objet types."""
    pass


class Beam(_Command, metaclass=BeamType):
    """
    Beam
    """
    def __str__(self) -> str:
        return str(_Comment(f"Definition of {self.__class__.__name__}")) \
               + str(self.generate_object()) \
               + str(self._particle)

    def post_init(self,
                  objet_type: _ObjetType,
                  kinematics: Union[_Kinematics, float, _Q],
                  particle: _ParticuleType = _Proton,
                  *args,
                  **kwargs):
        """

        Args:
            objet_type:
            kinematics:
            particle:
            *args:
            **kwargs:

        Returns:

        """
        self._particle: _ParticuleType = particle
        self._objet_type: _ObjetType = objet_type
        if not isinstance(kinematics, _Kinematics):
            kinematics = _Kinematics(kinematics)
        self._kinematics: _Kinematics = kinematics

    @property
    def particle(self) -> _ParticuleType:
        """The beam's particle type."""
        return self._particle

    @property
    def kinematics(self):
        """The beam's kinematics properties."""
        return self._kinematics

    @property
    def mappings(self) -> _MappedParametersListType:
        """TODO"""
        return [{}]

    def generate_object(self):
        """
        TODO

        Return:

        """
        return self._objet_type(self.LABEL1, BORO=self._kinematics.brho)

    def _set_from_betablock(self, betablock: _BetaBlock):
        """

        Args:
            betablock:

        Returns:

        """
        try:
            self.ALPHA_Y = betablock.alpha11
            self.BETA_Y = betablock.beta11
            self.ALPHA_Z = betablock.alpha22
            self.BETA_Z = betablock.beta22
            self.D_Y = betablock.disp1
            self.D_YP = betablock.disp2
            self.D_Z = betablock.disp3
            self.D_ZP = betablock.disp4
        except _ZgoubidooAttributeException:
            pass


class BeamZgoubiDistribution(Beam):
    """
    TODO
    """
    PARAMETERS = {
        'SLICE': (0, "Active slice identifier. *Note*: this is not the number of slices, but the active slice number."),
        'IMAX': (1, 'Number of particles to be generated'),
        'ALPHA_Y': (0.0, 'Horizontal (Y) alpha function'),
        'BETA_Y': (1.0 * _ureg.m, 'Horizontal (Y) beta function'),
        'EMIT_Y': (1e-9 * _ureg.m * _ureg.radian, 'Horizontal (Y) normalized emittance'),
        'D_Y': (0.0 * _ureg.m, 'Horizontal (Y) dispersion'),
        'D_YP': (0.0, 'Horizontal (Y) dispersion prime'),
        'N_CUTOFF_Y': (10, 'Cut-off value for the horizontal distribution'),
        'N_CUTOFF2_Y': (0, 'Secondary cut-off value for the horizontal distribution'),
        'ALPHA_Z': (0.0, 'Vertical (Z) alpha function'),
        'BETA_Z': (1.0 * _ureg.m, 'Vertical (Z) beta function'),
        'EMIT_Z': (1e-9 * _ureg.m * _ureg.radian, 'Vertical (Z) normalized emittance'),
        'D_Z': (0.0 * _ureg.m, 'Vertical (Z) dispersion'),
        'D_ZP': (0.0, 'Vertical (Z) dispersion prime'),
        'N_CUTOFF_Z': (10, 'Cut-off value for the vertical distribution'),
        'N_CUTOFF2_Z': (0, 'Secondary cut-off value for the vertical distribution'),
        'ALPHA_X': (0.0, 'Longitudinal (X) alpha function'),
        'BETA_X': (1.0 * _ureg.m, 'Longitudinal (X) beta function'),
        'EMIT_X': (1e-9 * _ureg.m * _ureg.radian, 'Longitudinal (X) normalized emittance'),
        'N_CUTOFF_X': (10, 'Cut-off value for the longitudinal distribution'),
        'N_CUTOFF2_X': (0, 'Secondary cut-off value for the longitudinal distribution'),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def post_init(self,
                  objet_type: _ObjetType = _MCObjet3,
                  betablock: _BetaBlock = None,
                  slices: int = 1,
                  *args,
                  **kwargs):
        """

        Args:
            objet_type:
            betablock:
            slices:
            *args:
            **kwargs:

        Returns:

        """
        super().post_init(objet_type=objet_type, **kwargs)
        self._slices: int = slices
        if betablock is not None:
            self._set_from_betablock(betablock)

    @property
    def slices(self):
        """Number of slices."""
        return self._slices

    @slices.setter
    def slices(self, n):
        """(Re)set the number of slices."""
        self._slices = n

    @property
    def mappings(self) -> _MappedParametersListType:
        """TODO"""
        return _ParametricMapping(
            [
                {
                    f"{self.LABEL1}.SLICE": list(range(0, self._slices))
                }
            ]
        ).combinations

    def generate_object(self):
        """
        TODO

        Return:

        """
        return self._objet_type(self.LABEL1,
                                BORO=self._kinematics.brho,
                                IMAX=self.IMAX / self.slices,
                                KY=2,
                                KT=2,
                                KZ=2,
                                KP=2,
                                ALPHA_Y=self.ALPHA_Y,
                                BETA_Y=self.BETA_Y,
                                D_Y=self.D_Y,
                                D_YP=self.D_YP,
                                EMIT_Y=self.EMIT_Z,
                                ALPHA_Z=self.ALPHA_Z,
                                BETA_Z=self.BETA_Z,
                                D_Z=self.D_Z,
                                D_ZP=self.D_ZP,
                                EMIT_Z=self.EMIT_Z,
                                ALPHA_X=self.ALPHA_X,
                                BETA_X=self.BETA_X,
                                EMIT_X=self.EMIT_X,
                                I1=randint(0, 1e6),
                                I2=randint(0, 1e6),
                                I3=randint(0, 1e6),
                                )

    @classmethod
    def from_sequence(cls, sequence: _TwissSequence, statistics: Optional[int] = None, **kwargs):
        """

        Args:
            sequence:
            statistics:

        Returns:

        """
        b = cls('BUNCH',
                particle=getattr(_particules, sequence.particle.__name__),
                kinematics=sequence.kinematics,
                betablock=sequence.betablock,
                **kwargs,
                )
        b.IMAX = statistics or sequence.metadata.n_particles,
        b.EMIT_Y = sequence.metadata['EX'] * _ureg.m * _ureg.radian
        b.EMIT_Z = sequence.metadata['EY'] * _ureg.m * _ureg.radian
        return b


class BeamInputDistribution(Beam):
    """
    A beam using an explicit beam distribution.
    """

    PARAMETERS = {
        'SLICE': (0, "Active slice identifier. Note: this is not the number of slices, but the active slice number."),
        'REFERENCE': (0, "Setting to 1 will produce a beam with only the reference particle (the distribution is not "
                         "lost"),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def post_init(self,
                  objet_type: _ObjetType = _Objet2,
                  distribution: Optional[Union[pd.DataFrame, np.array, str]] = None,
                  slices: int = 1,
                  *args,
                  **kwargs):
        """

        Args:
            objet_type:
            kinematics:
            particle:
            distribution:
            slices:
            *args:
            **kwargs:

        Returns:

        """
        super().post_init(objet_type=objet_type, **kwargs)
        self._slices: int = slices
        self._distribution: Optional[np.array] = None
        self.initialize_distribution(distribution, **kwargs)

    def initialize_distribution(self, distribution: Optional[Union[pd.DataFrame, np.ndarray, str]] = None, **kwargs):
        """Try setting the internal pandas.DataFrame with a distribution.

        Args:
            distribution:
        """
        if isinstance(distribution, str):
            self.add(
                BeamInputDistribution.generate_from_file(
                    distribution,
                    path=kwargs.get('path', '.')
                )
            )
        elif isinstance(distribution, (np.ndarray, pd.DataFrame)):
            self.add(distribution)
        return self

    def add(self, distribution: Union[pd.DataFrame, np.ndarray, str], **kwargs):
        """

        Args:
            distribution:

        Returns:

        """
        distr = None
        if isinstance(distribution, str):
            distr = BeamInputDistribution.generate_from_file(
                distribution,
                path=kwargs.get('path', '.')
            )
        elif isinstance(distribution, pd.DataFrame):
            distr = distribution.values
        elif isinstance(distribution, np.ndarray):
            distr = distribution

        if distr is not None:
            assert isinstance(distr, np.ndarray), "The distribution container must be a numpy array."
            assert distr.ndim == 2, "Invalid dimensions for the array of particles (must be 2)."
            if distr.shape[1] == 4:  # Y T Z P
                x = np.zeros((distr.shape[0], 1))
                d = np.ones((distr.shape[0], 1))
                iex = np.ones((distr.shape[0], 1))
                distr = np.concatenate((distr, x, d, iex), axis=1)
            elif distr.shape[1] == 5:  # Y T Z P D
                x = np.zeros((distr.shape[0], 1))
                iex = np.ones((distr.shape[0], 1))
                distr = np.concatenate((distr[:, :-1], x, distr[:, -1:], iex), axis=1)
            elif distr.shape[1] == 6:  # Y T Z P X D
                iex = np.ones((distr.shape[0], 1))
                distr = np.concatenate((distr, iex), axis=1)
            elif distr.shape[1] == 7:  # Y T Z P X D IEX
                pass
            else:
                raise _ZgoubidooException("Invalid dimensions for particles vectors.")
            if self._distribution is None:
                self._distribution = distr
            else:
                self._distribution = np.append(self._distribution, distr, axis=0)
        return self

    @property
    def slices(self):
        """Number of slices."""
        return self._slices

    @slices.setter
    def slices(self, n):
        """(Re)set the number of slices."""
        self._slices = n

    @property
    def active_slice(self):
        """The index of the active (current) slice."""
        try:
            n_tot = self._distribution.shape[0]
        except TypeError:
            return None
        n_per_slices = int(np.floor(n_tot / self._slices))
        d = self._distribution[self.SLICE * n_per_slices:(self.SLICE + 1) * n_per_slices]
        if len(d) == 0:
            return None
        else:
            return d

    def generate_object(self):
        """
        TODO

        Return:

        """
        _ = self._objet_type(self.LABEL1, BORO=self._kinematics.brho)
        if self.REFERENCE == 0:
            _.add(self.active_slice)
        return _

    @property
    def mappings(self) -> _MappedParametersListType:
        """TODO"""
        if self.REFERENCE == 1:
            return [{f"{self.LABEL1}.SLICE": 0, f"{self.LABEL1}.REFERENCE": 1}]
        else:
            return _ParametricMapping(
                [
                    {
                        f"{self.LABEL1}.SLICE": list(range(0, self._slices))
                    },
                    {
                        f"{self.LABEL1}.REFERENCE": [0]
                    }
                ]
            ).combinations

    @property
    def distribution(self) -> pd.DataFrame:
        """The beam distribution."""
        return self._distribution

    def create_reference_statistics(self, n: int = 1):
        """

        Args:
            n:

        Returns:

        """
        o = self.generate_object().clear().add_references(n)
        self._distribution = np.array(o.PARTICULES)
        return self

    def clear(self) -> Beam:
        """

        Returns:

        """
        self._distribution = None
        self._slices = 1
        return self

    def from_file(self, file: str, n: int = None, path: str = '.') -> Beam:
        """

        Args:
            file:
            n:
            path:

        Returns:

        """
        self.initialize_distribution(BeamInputDistribution.generate_from_file(file, path, n))
        return self

    def from_5d_sigma_matrix(self, n, **kwargs) -> Beam:
        """
        Initialize a beam with a 5D particle distribution from a Sigma matrix.

        Args:
            n:
            **kwargs:

        Returns:

        """
        distribution = BeamInputDistribution.generate_from_5d_sigma_matrix(n, **kwargs)
        self.initialize_distribution(distribution)
        return self

    def from_twiss_parameters(self, n, **kwargs) -> Beam:
        """
        Initialize a beam with a 5D particle distribution from Twiss parameters.

        Args:
            n:
            **kwargs:

        Returns:

        """
        keys = {'X', 'PX', 'Y', 'PY', 'DPP', 'DPPRMS', 'BETAX', 'ALPHAX', 'BETAY', 'ALPHAY', 'EMITX', 'EMITY'}
        if any([k not in keys for k in kwargs.keys()]):
            raise ZgoubidooBeamException("Invalid argument for a twiss distribution.")
        betax = kwargs.get('BETAX', 1)
        alphax = kwargs.get('ALPHAX', 0)
        gammax = (1+alphax**2)/betax
        betay = kwargs.get('BETAY', 1)
        alphay = kwargs.get('ALPHAY', 0)
        gammay = (1 + alphay ** 2) / betay

        self.from_5d_sigma_matrix(n,
                                  x=kwargs.get('X', 0),
                                  px=kwargs.get('PX', 0),
                                  y=kwargs.get('Y', 0),
                                  py=kwargs.get('PY', 0),
                                  dpp=kwargs.get('DPP', 0),
                                  dpprms=kwargs.get('DPPRMS', 0),
                                  s11=betax * kwargs['EMITX'],
                                  s12=-alphax * kwargs['EMITX'],
                                  s22=gammax * kwargs['EMITX'],
                                  s33=betay * kwargs['EMITY'],
                                  s34=-alphay * kwargs['EMITY'],
                                  s44=gammay * kwargs['EMITY']
                                  )
        return self

    @classmethod
    def from_sequence(cls, sequence: _Sequence, **kwargs):
        """

        Args:
            sequence:
            kwargs:

        Returns:

        """
        return cls(
            particle=getattr(_particules, sequence.particle.__name__),
            kinematics=sequence.kinematics,
            **kwargs
        )

    @staticmethod
    def generate_from_file(file: str, path: str = '.', n: Optional[int] = None) -> pd.DataFrame:
        """
        Read a beam distribution from file.

        Args:
            file:
            path:
            n:

        Returns:

        """
        return pd.read_csv(os.path.join(path, file))[:n].values

    @staticmethod
    def generate_from_5d_sigma_matrix(n: int,
                                      x: float = 0,
                                      px: float = 0,
                                      y: float = 0,
                                      py: float = 0,
                                      dpp: float = 0,
                                      s11: float = 0,
                                      s12: float = 0,
                                      s13: float = 0,
                                      s14: float = 0,
                                      s15: float = 0,
                                      s22: float = 0,
                                      s23: float = 0,
                                      s24: float = 0,
                                      s25: float = 0,
                                      s33: float = 0,
                                      s34: float = 0,
                                      s35: float = 0,
                                      s44: float = 0,
                                      s45: float = 0,
                                      dpprms: float = 0,
                                      matrix=None,
                                      ):
        """

        Args:
            n:
            x:
            px:
            y:
            py:
            dpp:
            s11:
            s12:
            s13:
            s14:
            s15:
            s22:
            s23:
            s24:
            s25:
            s33:
            s34:
            s35:
            s44:
            s45:
            dpprms:
            matrix:

        Returns:

        """
        # For performance considerations, see
        # https://software.intel.com/en-us/blogs/2016/06/15/faster-random-number-generation-in-intel-distribution-for-python
        try:
            import numpy.random_intel
            generator = numpy.random_intel.multivariate_normal
        except ModuleNotFoundError:
            import numpy.random
            generator = numpy.random.multivariate_normal

        s21 = s12
        s31 = s13
        s32 = s23
        s41 = s14
        s42 = s24
        s43 = s34
        s51 = s15
        s52 = s25
        s53 = s35
        s54 = s45
        s55 = dpprms ** 2

        if matrix is not None:
            assert matrix.shape == (5, 5)
            return generator(
                [x, px, y, py, dpp],
                matrix,
                int(n)
            )
        else:
            return generator(
                [x, px, y, py, dpp],
                np.array([
                    [s11, s12, s13, s14, s15],
                    [s21, s22, s23, s24, s25],
                    [s31, s32, s33, s34, s35],
                    [s41, s42, s43, s44, s45],
                    [s51, s52, s53, s54, s55]
                ]),
                int(n)
            )


class BeamTwiss(Beam):
    """
    A beam to be used for transfer map and Twiss computations.
    """
    PARAMETERS = {
        'PY': 1e-3,
        'PT': 1e-3,
        'PZ': 1e-3,
        'PP': 1e-3,
        'PX': 1e-3,
        'PD': 1e-3,
        'ALPHA_Y': 0.0,
        'BETA_Y': 1.0 * _ureg.m,
        'ALPHA_Z': 0.0,
        'BETA_Z': 1.0 * _ureg.m,
        'ALPHA_X': 0.0,
        'BETA_X': 1.0 * _ureg.m,
        'D_Y': 0 * _ureg.m,
        'D_YP': 0,
        'D_Z': 0 * _ureg.m,
        'D_ZP': 0,
    }

    def post_init(self,
                  betablock: _BetaBlock = None,
                  sequence: _TwissSequence = None,
                  objet_type: _ObjetType = _Objet5,
                  *args,
                  **kwargs):
        """

        Args:
            betablock:
            sequence:
            objet_type:
            *args:
            **kwargs:

        Returns:

        """
        super().post_init(objet_type=objet_type, **kwargs)
        if betablock is not None and sequence is not None:
            raise ZgoubidooBeamException("Provide either betablock or sequence, not both.")
        if sequence is not None and betablock is None:
            betablock = sequence.betablock
        if betablock is not None:
            self._set_from_betablock(betablock)

    def generate_object(self):
        """
        TODO

        Return:

        """
        return self._objet_type(self.LABEL1,
                                BORO=self._kinematics.brho,
                                PY=self.PY,
                                PT=self.PT,
                                PZ=self.PZ,
                                PP=self.PP,
                                PX=self.PX,
                                PD=self.PD,
                                ALPHA_Y=self.ALPHA_Y,
                                BETA_Y=self.BETA_Y,
                                ALPHA_Z=self.ALPHA_Z,
                                BETA_Z=self.BETA_Z,
                                ALPHA_X=self.ALPHA_X,
                                BETA_X=self.BETA_X,
                                D_Y=self.D_Y,
                                D_YP=self.D_YP,
                                D_Z=self.D_Z,
                                D_ZP=self.D_ZP,
                                )

    @classmethod
    def from_sequence(cls, sequence: _TwissSequence, **kwargs):
        """

        Args:
            sequence:
            kwargs:

        Returns:

        """
        return cls(
            particle=getattr(_particules, sequence.particle.__name__),
            kinematics=sequence.kinematics,
            betablock=sequence.betablock,
            objet_type=_Objet5,
            **kwargs
        )
