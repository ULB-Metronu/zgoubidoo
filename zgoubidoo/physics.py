"""Zgoubidoo relativistic physics module.

This module provides a collection of functions and classes to deal with relativistic physics computations. This mainly
concerns conversions between kinematic quantities. Full support for units (via ``pint``) is provided. Additionnally, a
helper class (``Kinematics``) provides automatic construction and conversion of kinematics quantities.

Examples:
    >>> 1 + 1
    TODO

"""
from typing import Union, Optional
from functools import partial as _partial
import numpy as _np
from . import ureg as _ureg
from . import _Q
from .commands import ParticuleType as _ParticuleType
from .commands import Proton as _Proton


class ZgoubiPhysicsException(Exception):
    """Exception raised for errors in the Zgoubidoo physics module."""

    def __init__(self, m):
        self.message = m


class Kinematics:
    """

    """
    def __init__(self, q: Union[float, _Q], particle: _ParticuleType = _Proton, kinetic: bool = True):
        """

        Args:
            q:
            particle:
            kinetic:
        """
        self._q: Union[float, _Q] = q
        self._p: _ParticuleType = particle
        self._type: Optional[str] = None

        if _Q(q).dimensionality == _ureg.cm.dimensionality:
            self._type = 'range'
        elif _Q(q).dimensionality == _ureg.eV.dimensionality:
            if kinetic:
                self._type = 'energy'
            else:
                self._type = 'etot'
        elif _Q(q).dimensionality == _ureg.eV_c.dimensionality:
            self._type = 'momentum'
        elif _Q(q).dimensionality == (_ureg.tesla * _ureg.m).dimensionality:
            self._type = 'brho'
        elif _Q(q).dimensionless:
            if q < 1:
                self._type = 'beta'
            else:
                self._type = 'gamma'
        else:
            raise ZgoubiPhysicsException("Invalid kinematic quantity.")

    def to(self, quantity: str) -> Union[float, _Q]:
        """

        Args:
            quantity:

        Returns:

        """
        if self._type == quantity:
            return self._q
        else:
            c = f"{self._type}_to_{quantity}"
            try:
                return globals()[c](self._q)
            except KeyError:
                raise ZgoubiPhysicsException(f"Invalid conversion attempted: {c}.")

    def to_range(self, magnitude: bool = False):
        """

        Args:
            magnitude:

        Returns:

        """
        _ = self.to('range')
        if magnitude:
            return _.to('cm').magnitude
        else:
            return _

    range = property(to_range)
    """TODO"""

    range_ = property(_partial(to_range, magnitude=True))
    """TODO"""

    def to_energy(self, magnitude: bool = False) -> Union[float, _Q]:
        """

        Args:
            magnitude:

        Returns:

        """
        _ = self.to('energy')
        if magnitude:
            return _.to('MeV').magnitude
        else:
            return _

    energy = property(to_energy)
    """TODO"""

    energy_ = property(_partial(to_energy, magnitude=True))
    """TODO"""

    def to_etot(self, magnitude: bool = False) -> Union[float, _Q]:
        """

        Args:
            magnitude:

        Returns:

        """
        _ = self.to('etot')
        if magnitude:
            return _.to('MeV').magnitude
        else:
            return _

    etot = property(to_etot)
    """TODO"""

    etot_ = property(_partial(to_etot, magnitude=True))
    """TODO"""

    def to_momentum(self, magnitude: bool = False) -> Union[float, _Q]:
        """

        Args:
            magnitude:

        Returns:

        """
        _ = self.to('momentum')
        if magnitude:
            return _.to('MeV_c').magnitude
        else:
            return _

    momentum = property(to_momentum)
    """Provides the *momentum*."""

    momentum_ = property(_partial(to_momentum, magnitude=True))
    """Provides the *momentum* (magnitude only)."""

    def to_brho(self, magnitude: bool = False) -> Union[float, _Q]:
        """

        Args:
            magnitude:

        Returns:

        """
        _ = self.to('brho')
        if magnitude:
            return _.to('tesla meter').magnitude
        else:
            return _

    brho = property(to_brho)
    """Provides *brho*."""

    brho_ = property(_partial(to_brho, magnitude=True))
    """Provides *brho* (magnitude only)."""

    def to_beta(self) -> Union[float, _Q]:
        """

        Returns:

        """
        return self.to('beta')

    beta = property(to_beta)
    """Provides *beta*."""

    def to_gamma(self) -> Union[float, _Q]:
        """

        Returns:

        """
        return self.to('gamma')

    gamma = property(to_gamma)
    """Provides *gamma*."""


def energy_to_momentum(e: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts momentum to kinetic energy.

    >>> energy_to_momentum(100 * _ureg.MeV).to('MeV_c')
    <Quantity(444.58340724772927, 'megaelectronvolt_per_c')>
    >>> energy_to_momentum(230 * _ureg.MeV).to('MeV_c')
    <Quantity(696.064029957015, 'megaelectronvolt_per_c')>

    :param e: kinetic energy
    :param particle: the particle type (default: proton)
    :return: relativistic momentum
    """
    return _np.sqrt((particle.M * _ureg.c ** 2 + e) ** 2 - particle.M ** 2 * _ureg.c ** 4) / _ureg.c


def energy_to_brho(e: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts kinetic energy to magnetic rigidity (brho).

    >>> energy_to_momentum(100 * _ureg.MeV).to('MeV_c')
    <Quantity(444.58340724772927, 'megaelectronvolt_per_c')>
    >>> energy_to_momentum(230 * _ureg.MeV).to('MeV_c')
    <Quantity(696.064029957015, 'megaelectronvolt_per_c')>

    :param e: kinetic energy
    :param particle: the particle type (default: proton)
    :return: magnetic rigidity
    """
    return momentum_to_brho(energy_to_momentum(e, particle), particle)


def energy_to_range(e: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts kinetic energy to proton range in water; following IEC60601.

    >>> energy_to_range(100 * _ureg.MeV).to('cm')
    <Quantity(7.7269636143698905, 'centimeter')>
    >>> energy_to_range(230 * _ureg.MeV).to('cm')
    <Quantity(32.9424672323197, 'centimeter')>

    :param e: kinetic energy
    :param particle: the particle type (default: proton)
    :return: proton range in water
    """
    if particle is not _Proton:
        raise ZgoubiPhysicsException("Conversion to range only works for protons.")

    b = 0.008539
    c = 0.5271
    d = 3.4917
    e = e.to('MeV').magnitude
    return _np.exp((-c + _np.sqrt(c ** 2 - 4 * b * (d - _np.log(e)))) / (2 * b)) * _ureg.cm


def energy_to_pv(e: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts kinetic energy to relativistic pv.

    >>> energy_to_pv(230 * _ureg.MeV)
    <Quantity(414.71945005821937, 'megaelectronvolt')>

    :param e: kinetic energy
    :param particle: the particle type (default: proton)
    :return: relativistic pv
    """
    return ((e + particle.M * _ureg.c ** 2) ** 2 - (particle.M * _ureg.c ** 2) ** 2) / (e + particle.M * _ureg.c ** 2)


def energy_to_beta(e: _Q, particle: _ParticuleType = _Proton) -> float:
    """
    Converts the kinetic energy to relativistic beta.

    >>> 1 + 1
    2

    :param e: kinetic energy
    :param particle: the particle type (default: proton)
    :return: relativistic beta
    """
    gamma = (particle.M * _ureg.c ** 2 + e) / (particle.M * _ureg.c ** 2)
    return (_np.sqrt((gamma ** 2 - 1) / gamma ** 2)).magnitude


def energy_to_gamma(e: _Q, particle: _ParticuleType = _Proton) -> float:
    """
    Converts the kinetic energy to relativistic gamma.

    >>> 1 + 1
    2

    :param e: kinetic energy
    :param particle: the particle type (default: proton)
    :return: relativistic gamma
    """
    return ((particle.M * _ureg.c ** 2 + e) / (particle.M * _ureg.c ** 2)).magnitude


def momentum_to_energy(p: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts momentum to kinetic energy.

    >>> momentum_to_energy(100 * _ureg.MeV_c).to('MeV')
    <Quantity(5.313897343302641, 'megaelectronvolt')>

    :param p: relativistic momentum
    :param particle: the particle type (default: proton)
    :return:
    """
    return _np.sqrt((p ** 2 * _ureg.c ** 2) + ((particle.M * _ureg.c ** 2) ** 2)) - particle.M * _ureg.c ** 2


def momentum_to_brho(p: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts momentum to magnetic rigidity (brho).

    >>> momentum_to_brho(100 * _ureg.MeV_c).to('tesla * meter')
    <Quantity(0.33356409519815206, 'meter * tesla')>

    :param p: relativistic momentum
    :param particle: the particle type (default: proton)
    :return:
    """
    return p / particle.Q


def momentum_to_range(p: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts momentum to proton range in water; following IEC60601.

    >>> momentum_to_range(696 * _ureg.MeV_c).to('cm')
    <Quantity(32.93315610400117, 'centimeter')>

    :param p: relativistic momentum
    :param particle: the particle type (default: proton)
    :return:
    """
    return energy_to_range(momentum_to_energy(p, particle), particle)


def momentum_to_pv(p: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts momentum to proton range in water; following IEC60601.

    >>> momentum_to_range(696 * _ureg.MeV_c).to('cm')
    <Quantity(32.93315610400117, 'centimeter')>

    :param p: relativistic momentum
    :param particle: the particle type (default: proton)
    :return:
    """
    return energy_to_range(momentum_to_energy(p, particle), particle)


def momentum_to_beta(p: _Q, particle: _ParticuleType = _Proton) -> float:
    """
    Converts momentum to proton range in water; following IEC60601.

    >>> momentum_to_range(696 * _ureg.MeV_c).to('cm')
    <Quantity(32.93315610400117, 'centimeter')>

    :param p: relativistic momentum
    :param particle: the particle type (default: proton)
    :return:
    """
    return energy_to_range(momentum_to_energy(p, particle), particle)


def momentum_to_gamma(p: _Q, particle: _ParticuleType = _Proton) -> float:
    """
    Converts momentum to proton range in water; following IEC60601.

    >>> momentum_to_range(696 * _ureg.MeV_c).to('cm')
    <Quantity(32.93315610400117, 'centimeter')>

    :param p: relativistic momentum
    :param particle: the particle type (default: proton)
    :return:
    """
    return energy_to_range(momentum_to_energy(p, particle), particle)


def brho_to_energy(brho: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts magnetic rigidity (brho) to momentum.

    >>> momentum_to_brho(100 * _ureg.MeV_c).to('tesla * meter')
    <Quantity(0.33356409519815206, 'meter * tesla')>

    :param brho: magnetic rigidity
    :param particle: the particle type (default: proton)
    :return:
    """
    return momentum_to_energy(brho_to_momentum(brho, particle))


def brho_to_momentum(brho: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts magnetic rigidity (brho) to momentum.

    >>> momentum_to_brho(100 * _ureg.MeV_c).to('tesla * meter')
    <Quantity(0.33356409519815206, 'meter * tesla')>

    :param brho: magnetic rigidity
    :param particle: the particle type (default: proton)
    :return:
    """
    return brho * particle.Q


def brho_to_range(brho: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts magnetic rigidity (brho) to momentum.

    >>> momentum_to_brho(100 * _ureg.MeV_c).to('tesla * meter')
    <Quantity(0.33356409519815206, 'meter * tesla')>

    :param brho: magnetic rigidity
    :param particle: the particle type (default: proton)
    :return:
    """
    return brho * particle.Q


def brho_to_pv(brho: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts magnetic rigidity (brho) to momentum.

    >>> momentum_to_brho(100 * _ureg.MeV_c).to('tesla * meter')
    <Quantity(0.33356409519815206, 'meter * tesla')>

    :param brho: magnetic rigidity
    :param particle: the particle type (default: proton)
    :return:
    """
    return brho * particle.Q


def brho_to_beta(brho: _Q, particle: _ParticuleType = _Proton) -> float:
    """
    Converts magnetic rigidity (brho) to momentum.

    >>> momentum_to_brho(100 * _ureg.MeV_c).to('tesla * meter')
    <Quantity(0.33356409519815206, 'meter * tesla')>

    :param brho: magnetic rigidity
    :param particle: the particle type (default: proton)
    :return:
    """
    return brho * particle.Q


def brho_to_gamma(brho: _Q, particle: _ParticuleType = _Proton) -> float:
    """
    Converts magnetic rigidity (brho) to momentum.

    >>> momentum_to_brho(100 * _ureg.MeV_c).to('tesla * meter')
    <Quantity(0.33356409519815206, 'meter * tesla')>

    :param brho: magnetic rigidity
    :param particle: the particle type (default: proton)
    :return:
    """
    return brho * particle.charge


def range_to_energy(r: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts proton range in water to kinetic energy following IEC60601.

    Examples:
        >>> range_to_energy(32 * _ureg.cm).to('MeV')
        <Quantity(226.12911179644985, 'megaelectronvolt')>

    Args:
        r: proton range in water
        particle: the particle type (default: proton)

    Returns:
        the kinetic energy of the particle.
    """
    if not isinstance(particle, _Proton):
        raise ZgoubiPhysicsException("Conversion from range only works for protons.")

    a = 0.00169
    b = -0.00490
    c = 0.56137
    d = 3.46405
    r = r.to('cm').magnitude
    return _np.exp(
        a * _np.log(r) ** 3 + b * _np.log(r) ** 2 + c * _np.log(r) + d
    ) * _ureg.MeV


def range_to_momentum(r: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts proton range in water to kinetic energy following IEC60601.

    >>> range_to_energy(32 * _ureg.cm).to('MeV')
    <Quantity(226.12911179644985, 'megaelectronvolt')>

    :param r: proton range in water
    :param particle: the particle type (default: proton)
    :return:
    """
    if not isinstance(particle, _Proton):
        raise ZgoubiPhysicsException("Conversion from range only works for protons.")

    a = 0.00169
    b = -0.00490
    c = 0.56137
    d = 3.46405
    r = r.to('cm').magnitude
    return _np.exp(
        a * _np.log(r) ** 3 + b * _np.log(r) ** 2 + c * _np.log(r) + d
    ) * _ureg.MeV


def range_to_brho(r: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts proton range in water to kinetic energy following IEC60601.

    >>> range_to_energy(32 * _ureg.cm).to('MeV')
    <Quantity(226.12911179644985, 'megaelectronvolt')>

    :param r: proton range in water
    :param particle: the particle type (default: proton)
    :return:
    """
    if not isinstance(particle, _Proton):
        raise ZgoubiPhysicsException("Conversion from range only works for protons.")

    a = 0.00169
    b = -0.00490
    c = 0.56137
    d = 3.46405
    r = r.to('cm').magnitude
    return _np.exp(
        a * _np.log(r) ** 3 + b * _np.log(r) ** 2 + c * _np.log(r) + d
    ) * _ureg.MeV


def range_to_pv(r: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts proton range in water to kinetic energy following IEC60601.

    >>> range_to_energy(32 * _ureg.cm).to('MeV')
    <Quantity(226.12911179644985, 'megaelectronvolt')>

    :param r: proton range in water
    :param particle: the particle type (default: proton)
    :return:
    """
    if not isinstance(particle, _Proton):
        raise ZgoubiPhysicsException("Conversion from range only works for protons.")

    a = 0.00169
    b = -0.00490
    c = 0.56137
    d = 3.46405
    r = r.to('cm').magnitude
    return _np.exp(
        a * _np.log(r) ** 3 + b * _np.log(r) ** 2 + c * _np.log(r) + d
    ) * _ureg.MeV


def range_to_beta(r: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts proton range in water to kinetic energy following IEC60601.

    >>> range_to_energy(32 * _ureg.cm).to('MeV')
    <Quantity(226.12911179644985, 'megaelectronvolt')>

    :param r: proton range in water
    :param particle: the particle type (default: proton)
    :return:
    """
    if not isinstance(particle, _Proton):
        raise ZgoubiPhysicsException("Conversion from range only works for protons.")

    a = 0.00169
    b = -0.00490
    c = 0.56137
    d = 3.46405
    r = r.to('cm').magnitude
    return _np.exp(
        a * _np.log(r) ** 3 + b * _np.log(r) ** 2 + c * _np.log(r) + d
    ) * _ureg.MeV


def range_to_gamma(r: _Q, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts proton range in water to kinetic energy following IEC60601.

    >>> range_to_energy(32 * _ureg.cm).to('MeV')
    <Quantity(226.12911179644985, 'megaelectronvolt')>

    :param r: proton range in water
    :param particle: the particle type (default: proton)
    :return:
    """
    if not isinstance(particle, _Proton):
        raise ZgoubiPhysicsException("Conversion from range only works for protons.")

    a = 0.00169
    b = -0.00490
    c = 0.56137
    d = 3.46405
    r = r.to('cm').magnitude
    return _np.exp(
        a * _np.log(r) ** 3 + b * _np.log(r) ** 2 + c * _np.log(r) + d
    ) * _ureg.MeV


def beta_to_energy(beta: float, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts relativistic beta to kinetic energy.

    >>> 1 + 1
    2

    :param beta: relativistic beta (dimensionless)
    :param particle: the particle type (default: proton)
    :return: kinetic energy
    """
    return beta_to_gamma(beta) * (particle.M * _ureg.c ** 2) - (particle.M * _ureg.c ** 2)


def beta_to_momentum(beta: float, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts relativistic beta to kinetic energy.

    >>> 1 + 1
    2

    :param beta: relativistic beta (dimensionless)
    :param particle: the particle type (default: proton)
    :return: kinetic energy
    """
    return beta_to_gamma(beta) * (particle.M * _ureg.c ** 2) - (particle.M * _ureg.c ** 2)


def beta_to_brho(beta: float, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts relativistic beta to kinetic energy.

    >>> 1 + 1
    2

    :param beta: relativistic beta (dimensionless)
    :param particle: the particle type (default: proton)
    :return: kinetic energy
    """
    return beta_to_gamma(beta) * (particle.M * _ureg.c ** 2) - (particle.M * _ureg.c ** 2)


def beta_to_range(beta: float, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts relativistic beta to kinetic energy.

    >>> 1 + 1
    2

    :param beta: relativistic beta (dimensionless)
    :param particle: the particle type (default: proton)
    :return: kinetic energy
    """
    return beta_to_gamma(beta) * (particle.M * _ureg.c ** 2) - (particle.M * _ureg.c ** 2)


def beta_to_pv(beta: float, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts relativistic beta to kinetic energy.

    >>> 1 + 1
    2

    :param beta: relativistic beta (dimensionless)
    :param particle: the particle type (default: proton)
    :return: kinetic energy
    """
    return beta_to_gamma(beta) * (particle.M * _ureg.c ** 2) - (particle.M * _ureg.c ** 2)


def beta_to_gamma(beta: float) -> float:
    """
    Converts relativistic beta to relativistic gamma.

    >>> 1 + 1
    2

    :param beta: relativistic beta
    :return:
    """
    return 1/(_np.sqrt(1 - beta ** 2))


def gamma_to_energy(gamma: float, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts relativistic gamma to kinetic energy.

    >>> gamma_to_energy(100.0).to('MeV')
    <Quantity(92888.93096999999, 'megaelectronvolt')>

    :param gamma: relativistic gamma (dimensionless)
    :param particle: the particle type (default: proton)
    :return: kinetic energy
    """
    return gamma * (particle.M * _ureg.c ** 2) - (particle.M * _ureg.c ** 2)


def gamma_to_momentum(gamma: float, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts relativistic gamma to kinetic energy.

    >>> gamma_to_energy(100.0).to('MeV')
    <Quantity(92888.93096999999, 'megaelectronvolt')>

    :param gamma: relativistic gamma (dimensionless)
    :param particle: the particle type (default: proton)
    :return: kinetic energy
    """
    return gamma * (particle.M * _ureg.c ** 2) - (particle.M * _ureg.c ** 2)


def gamma_to_brho(gamma: float, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts relativistic gamma to kinetic energy.

    >>> gamma_to_energy(100.0).to('MeV')
    <Quantity(92888.93096999999, 'megaelectronvolt')>

    :param gamma: relativistic gamma (dimensionless)
    :param particle: the particle type (default: proton)
    :return: kinetic energy
    """
    return gamma * (particle.M * _ureg.c ** 2) - (particle.M * _ureg.c ** 2)


def gamma_to_range(gamma: float, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts relativistic gamma to kinetic energy.

    >>> gamma_to_energy(100.0).to('MeV')
    <Quantity(92888.93096999999, 'megaelectronvolt')>

    :param gamma: relativistic gamma (dimensionless)
    :param particle: the particle type (default: proton)
    :return: kinetic energy
    """
    return gamma * (particle.M * _ureg.c ** 2) - (particle.M * _ureg.c ** 2)


def gamma_to_pv(gamma: float, particle: _ParticuleType = _Proton) -> _Q:
    """
    Converts relativistic gamma to kinetic energy.

    >>> gamma_to_energy(100.0).to('MeV')
    <Quantity(92888.93096999999, 'megaelectronvolt')>

    :param gamma: relativistic gamma (dimensionless)
    :param particle: the particle type (default: proton)
    :return: kinetic energy
    """
    return gamma * (particle.M * _ureg.c ** 2) - (particle.M * _ureg.c ** 2)


def gamma_to_beta(gamma: float, particle: _ParticuleType = _Proton) -> float:
    """
    Converts relativistic gamma to kinetic energy.

    >>> gamma_to_energy(100.0).to('MeV')
    <Quantity(92888.93096999999, 'megaelectronvolt')>

    :param gamma: relativistic gamma (dimensionless)
    :param particle: the particle type (default: proton)
    :return: kinetic energy
    """
    return gamma * (particle.M * _ureg.c ** 2) - (particle.M * _ureg.c ** 2)
