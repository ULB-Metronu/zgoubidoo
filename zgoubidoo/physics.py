from typing import Union
from functools import partial
import numpy as _np
from pint import DimensionalityError
from . import ureg, Q_
from .commands import Particule, Proton


class ZgoubiPhysicsException(Exception):
    """Exception raised for errors in the Zgoubidoo physics module."""

    def __init__(self, m):
        self.message = m


class Kinematic:
    def __init__(self, q: Q_, particle: Particule=Proton()):
        self._q = q
        self._p = particle
        self._range = None
        self._energy = None
        self._momentum = None
        self._brho = None
        self._beta = None
        self._gamma = None

    def to(self, ):

        try:
            self._q = momentum_to_energy(q, self._p)
        except DimensionalityError:
            pass

    def to_range(self):
        pass

    range = property(to_range)
    range_ = property(partial(to_range, magnitude=True))

    def to_energy(self, magnitude: bool=False) -> Union[float, Q_]:
        pass

    energy = property(to_energy)
    energy_ = property(partial(to_energy, magnitude=True))

    def to_momentum(self, magnitude: bool=False) -> Union[float, Q_]:
        pass

    momentum = property(to_momentum)
    momentum_ = property(partial(to_momentum, magnitude=True))

    def to_brho(self, magnitude: bool=False) -> Union[float, Q_]:
        pass

    brho = property(to_brho)
    brho_ = property(partial(to_brho, magnitude=True))

    def to_beta(self, magnitude: bool=False) -> Union[float, Q_]:
        pass

    beta = property(to_beta)
    beta_ = property(partial(to_beta, magnitude=True))

    def to_gamma(self, magnitude: bool=False) -> Union[float, Q_]:
        pass

    gamma = property(to_gamma)
    gamma_ = property(partial(to_gamma, magnitude=True))


def energy_to_momentum(e: Q_, particle: Particule=Proton()) -> Q_:
    """
    Converts momentum to kinetic energy.

    >>> energy_to_momentum(100 * ureg.MeV).to('MeV_c')
    <Quantity(444.58340724772927, 'megaelectronvolt_per_c')>
    >>> energy_to_momentum(230 * ureg.MeV).to('MeV_c')
    <Quantity(696.064029957015, 'megaelectronvolt_per_c')>

    :param e: kinetic energy
    :param particle: the particle type (default: proton)
    :return: relativistic momentum
    """
    return _np.sqrt((particle.mass * ureg.c**2 + e) ** 2 - particle.mass ** 2 * ureg.c ** 4) / ureg.c


def energy_to_brho(e: Q_, particle: Particule=Proton()) -> Q_:
    """
    Converts kinetic energy to magnetic rigidity (brho).

    >>> energy_to_momentum(100 * ureg.MeV).to('MeV_c')
    <Quantity(444.58340724772927, 'megaelectronvolt_per_c')>
    >>> energy_to_momentum(230 * ureg.MeV).to('MeV_c')
    <Quantity(696.064029957015, 'megaelectronvolt_per_c')>

    :param e: kinetic energy
    :param particle: the particle type (default: proton)
    :return: magnetic rigidity
    """
    return momentum_to_brho(energy_to_momentum(e, particle), particle)


def energy_to_range(e: Q_, particle: Particule=Proton()) -> Q_:
    """
    Converts kinetic energy to proton range in water; following IEC60601.

    >>> energy_to_range(100 * ureg.MeV).to('cm')
    <Quantity(7.7269636143698905, 'centimeter')>
    >>> energy_to_range(230 * ureg.MeV).to('cm')
    <Quantity(32.9424672323197, 'centimeter')>

    :param e: kinetic energy
    :param particle: the particle type (default: proton)
    :return: proton range in water
    """
    if not isinstance(particle, Proton):
        raise ZgoubiPhysicsException("Conversion to range only works for protons.")

    b = 0.008539
    c = 0.5271
    d = 3.4917
    e = e.to('MeV').magnitude
    return _np.exp((-c + _np.sqrt(c ** 2 - 4 * b * (d - _np.log(e)))) / (2 * b)) * ureg.cm


def energy_to_pv(e: Q_, particle: Particule=Proton()) -> Q_:
    """
    Converts kinetic energy to relativistic pv.

    >>> energy_to_pv(230 * ureg.MeV)
    <Quantity(414.71945005821937, 'megaelectronvolt')>

    :param e: kinetic energy
    :param particle: the particle type (default: proton)
    :return: relativistic pv
    """
    return ((e + particle.mass * ureg.c**2)**2 - (particle.mass * ureg.c**2)**2) / (e + particle.mass * ureg.c**2)


def energy_to_beta(e: Q_, particle: Particule=Proton()) -> float:
    """
    Converts the kinetic energy to relativistic beta.

    >>> 1 + 1
    2

    :param e: kinetic energy
    :param particle: the particle type (default: proton)
    :return: relativistic beta
    """
    gamma = (particle.mass * ureg.c**2 + e) / (particle.mass * ureg.c**2)
    return _np.sqrt((gamma ** 2 - 1) / gamma ** 2)


def energy_to_gamma(e: Q_, particle: Particule=Proton()) -> float:
    """
    Converts the kinetic energy to relativistic gamma.

    >>> 1 + 1
    2

    :param e: kinetic energy
    :param particle: the particle type (default: proton)
    :return: relativistic gamma
    """
    return (particle.mass * ureg.c**2 + e) / (particle.mass * ureg.c**2)


def momentum_to_energy(p: Q_, particle: Particule=Proton()) -> Q_:
    """
    Converts momentum to kinetic energy.

    >>> momentum_to_energy(100 * ureg.MeV_c).to('MeV')
    <Quantity(5.313897343302641, 'megaelectronvolt')>

    :param p: relativistic momentum
    :param particle: the particle type (default: proton)
    :return:
    """
    return _np.sqrt((p ** 2 * ureg.c ** 2) + ((particle.mass * ureg.c ** 2) ** 2)) - particle.mass * ureg.c ** 2


def momentum_to_brho(p: Q_, particle: Particule=Proton()) -> Q_:
    """
    Converts momentum to magnetic rigidity (brho).

    >>> momentum_to_brho(100 * ureg.MeV_c).to('tesla * meter')
    <Quantity(0.33356409519815206, 'meter * tesla')>

    :param p: relativistic momentum
    :param particle: the particle type (default: proton)
    :return:
    """
    return p / particle.charge


def momentum_to_range(p: Q_, particle: Particule=Proton()) -> Q_:
    """
    Converts momentum to proton range in water; following IEC60601.

    >>> momentum_to_range(696 * ureg.MeV_c).to('cm')
    <Quantity(32.93315610400117, 'centimeter')>

    :param p: relativistic momentum
    :param particle: the particle type (default: proton)
    :return:
    """
    return energy_to_range(momentum_to_energy(p, particle), particle)


def brho_to_momentum(brho: Q_, particle: Particule=Proton()) -> Q_:
    """
    Converts magnetic rigidity (brho) to momentum.

    >>> momentum_to_brho(100 * ureg.MeV_c).to('tesla * meter')
    <Quantity(0.33356409519815206, 'meter * tesla')>

    :param brho: magnetic rigidity
    :param particle: the particle type (default: proton)
    :return:
    """
    return brho * particle.charge


def range_to_energy(r: Q_, particle: Particule=Proton()) -> Q_:
    """
    Converts proton range in water to kinetic energy following IEC60601.

    >>> range_to_energy(32 * ureg.cm).to('MeV')
    <Quantity(226.12911179644985, 'megaelectronvolt')>

    :param r: proton range in water
    :param particle: the particle type (default: proton)
    :return:
    """
    if not isinstance(particle, Proton):
        raise ZgoubiPhysicsException("Conversion from range only works for protons.")

    a = 0.00169
    b = -0.00490
    c = 0.56137
    d = 3.46405
    r = r.to('cm').magnitude
    return _np.exp(
        a * _np.log(r) ** 3 + b * _np.log(r) ** 2 + c * _np.log(r) + d
    ) * ureg.MeV


def beta_to_gamma(beta: float) -> float:
    """
    Converts relativistic beta to relativistic gamma.

    >>> 1 + 1
    2

    :param beta: relativistic beta
    :return:
    """
    return 1/(_np.sqrt(1 - beta ** 2))


def beta_to_energy(beta: float, particle: Particule=Proton()) -> Q_:
    """
    Converts relativistic beta to kinetic energy.

    >>> 1 + 1
    2

    :param beta: relativistic beta (dimensionless)
    :param particle: the particle type (default: proton)
    :return: kinetic energy
    """
    return beta_to_gamma(beta) * (particle.mass * ureg.c**2) - (particle.mass * ureg.c**2)


def gamma_to_energy(gamma: float, particle: Particule=Proton()) -> Q_:
    """
    Converts relativistic gamma to kinetic energy.

    >>> gamma_to_energy(100.0).to('MeV')
    <Quantity(92888.93096999999, 'megaelectronvolt')>

    :param gamma: relativistic gamma (dimensionless)
    :param particle: the particle type (default: proton)
    :return: kinetic energy
    """
    return gamma * (particle.mass * ureg.c**2) - (particle.mass * ureg.c**2)
