"""Zgoubidoo beam.

"""
from __future__ import annotations
from typing import Optional, Union
import os
from random import randint
import numpy as np
import pandas as pd
from zgoubidoo import _Q
from zgoubidoo.commands import CommandType as _CommandType
from zgoubidoo.commands import Command as _Command
from zgoubidoo.commands import Comment as _Comment
from zgoubidoo.commands import ParticuleType as _ParticuleType
from zgoubidoo.commands import Proton as _Proton
from zgoubidoo.commands import Objet2 as _Objet2
from zgoubidoo.commands import Objet5 as _Objet5
from zgoubidoo.commands import MCObjet3 as _MCObjet3
from zgoubidoo.commands import ObjetType as _ObjetType
from zgoubidoo.kinematics import Kinematics as _Kinematics
from ..input import ParametricMapping as _ParametricMapping
from ..input import MappedParametersListType as _MappedParametersListType
from .. import ureg as _ureg


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


class BeamZgoubiDistribution(Beam):
    """
    TODO
    """
    PARAMETERS = {
        'SLICE': (0, "Active slice identifier. *Note*: this is not the number of slices, but the active slice number."),
        'ALPHA_Y': (0.0, 'Horizontal (Y) alpha function'),
        'BETA_Y': (1.0 * _ureg.m, 'Horizontal (Y) beta function'),
        'EMIT_Y': (1e-9 * _ureg.m * _ureg.radian, 'Horizontal (Y) normalized emittance'),
        'DY': (0.0 * _ureg.m, 'Horizontal (Y) dispersion'),
        'DPY': (0.0, 'Horizontal (Y) dispersion prime'),
        'N_CUTOFF_Y': (10, 'Cut-off value for the horizontal distribution'),
        'N_CUTOFF2_Y': (0, 'Secondary cut-off value for the horizontal distribution'),
        'ALPHA_Z': (0.0, 'Vertical (Z) alpha function'),
        'BETA_Z': (1.0 * _ureg.m, 'Vertical (Z) beta function'),
        'EMIT_Z': (1e-9 * _ureg.m * _ureg.radian, 'Vertical (Z) normalized emittance'),
        'DZ': (0.0 * _ureg.m, 'Vertical (Z) dispersion'),
        'DPZ': (0.0, 'Vertical (Z) dispersion prime'),
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
                  slices: int = 1,
                  *args,
                  **kwargs):
        """

        Args:
            objet_type:
            slices:
            *args:
            **kwargs:

        Returns:

        """
        self._slices: int = slices

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
                                IMAX=10,
                                KY=2,
                                KT=2,
                                KZ=2,
                                KP=2,
                                ALPHA_Y=self.ALPHA_Y,
                                BETA_Y=self.BETA_Y,
                                DY=self.DY,
                                DPY=self.DPY,
                                EMIT_Y=self.EMIT_Z,
                                ALPHA_Z=self.ALPHA_Z,
                                BETA_Z=self.BETA_Z,
                                DZ=self.DZ,
                                DPZ=self.DPZ,
                                EMIT_Z=self.EMIT_Z,
                                ALPHA_X=self.ALPHA_X,
                                BETA_X=self.BETA_X,
                                EMIT_X=self.EMIT_X,
                                I1=randint(0, 1e6),
                                I2=randint(0, 1e6),
                                I3=randint(0, 1e6),
                                )


class BeamTwiss(Beam):
    """
    A beam to be used for transfer map and Twiss computations.
    """
    PARAMETERS = {
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
                  objet_type: _ObjetType = _Objet5,
                  *args,
                  **kwargs):
        """

        Args:
            objet_type:
            *args:
            **kwargs:

        Returns:

        """
        pass

    def generate_object(self):
        """
        TODO

        Return:

        """
        return self._objet_type(self.LABEL1,
                                BORO=self._kinematics.brho,
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


class BeamDistribution(Beam):
    """
    A beam using an explicit beam distribution.
    """

    PARAMETERS = {
        'SLICE': (0, "Active slice identifier. Note: this is not the number of slices, but the active slice number."),
        'REFERENCE': (0, ""),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def post_init(self,
                  distribution: Optional[pd.DataFrame] = None,
                  slices: int = 1,
                  *args,
                  **kwargs):
        """

        Args:
            distribution:
            particle:
            objet_type:
            kinematics:
            slices:
            *args:
            **kwargs:

        Returns:

        """
        self._slices: int = slices
        self._distribution: Optional[Union[pd.DataFrame, np.array]] = None
        self._initialize_distribution(distribution, **kwargs)

    def _initialize_distribution(self, distribution: Union[pd.DataFrame, np.array] = None, **kwargs):
        """Try setting the internal pandas.DataFrame with a distribution.

        Args:
            distribution:
        """
        if distribution is not None:
            try:
                self._distribution = distribution.values
            except AttributeError:
                self._distribution = distribution
        else:
            try:
                try:
                    self._distribution = distribution.values
                except AttributeError:
                    self._distribution = distribution
            except (IndexError, ValueError):
                if kwargs.get("filename") is not None:
                    self._distribution = Beam.generate_from_file(kwargs.get('filename'), path=kwargs.get('path', '.'))
                else:
                    return
        if self._distribution is not None and self._distribution.shape[0] == 0:
            raise ZgoubidooBeamException("Trying to initialize a beam distribution with invalid number of particles.")

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
            return [{f"{self.LABEL1}.REFERENCE": 1}]
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

    def create_statistics(self, n: int = 1):
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
        self._initialize_distribution(Beam.generate_from_file(file, path, n))
        return self

    def from_5d_sigma_matrix(self, n, **kwargs) -> Beam:
        """
        Initialize a beam with a 5D particle distribution from a Sigma matrix.

        Args:
            n:
            **kwargs:

        Returns:

        """
        distribution = Beam.generate_from_5d_sigma_matrix(n, **kwargs)
        self._initialize_distribution(distribution)
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
        return pd.read_csv(os.path.join(path, file))[:n]

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
