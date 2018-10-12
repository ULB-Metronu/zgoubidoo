from typing import Union
from functools import partial
import numpy as _np
from pint import DimensionalityError
from . import ureg, Q_
from .commands import Particule, Proton


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

    :param e:
    :param particle:
    :return:
    """
    return _np.sqrt((particle.mass * ureg.c**2 + e) ** 2 - particle.mass ** 2 * ureg.c ** 4) / ureg.c


def energy_to_brho(e: Q_, particle: Particule=Proton()) -> Q_:
    """
    Converts momentum to kinetic energy.

    >>> energy_to_momentum(100 * ureg.MeV).to('MeV_c')
    <Quantity(444.58340724772927, 'megaelectronvolt_per_c')>
    >>> energy_to_momentum(230 * ureg.MeV).to('MeV_c')
    <Quantity(696.064029957015, 'megaelectronvolt_per_c')>

    :param e:
    :param particle:
    :return:
    """
    return momentum_to_brho(energy_to_momentum(e, particle), particle)


def momentum_to_energy(p: Q_, particle: Particule=Proton()) -> Q_:
    """
    Converts momentum to kinetic energy.

    >>> momentum_to_energy(100 * ureg.MeV_c).to('MeV')
    <Quantity(5.313897343302641, 'megaelectronvolt')>

    :param p:
    :param particle:
    :return:
    """
    return _np.sqrt((p ** 2 * ureg.c ** 2) + ((particle.mass * ureg.c ** 2) ** 2)) - particle.mass * ureg.c ** 2


def momentum_to_brho(p: Q_, particle: Particule=Proton()) -> Q_:
    """
    Converts momentum to magnetic rigidity (brho).

    >>> momentum_to_brho(100 * ureg.MeV_c).to('tesla * meter')
    <Quantity(0.33356409519815206, 'meter * tesla')>

    :param p:
    :param particle:
    :return:
    """
    return p / particle.charge


def brho_to_momentum(brho: Q_, particle: Particule=Proton()) -> Q_:
    """
    Converts magnetic rigidity (brho) to momentum.

    >>> momentum_to_brho(100 * ureg.MeV_c).to('tesla * meter')
    <Quantity(0.33356409519815206, 'meter * tesla')>

    :param brho:
    :param particle:
    :return:
    """
    return brho * particle.charge


def energy_to_beta(ekin):
    """Return beta relativistic from E [MeV/c^2] (proton)."""
    gamma = (PROTON_MASS + ekin) / PROTON_MASS
    return _np.sqrt((gamma ** 2 - 1) / gamma ** 2)


def beta_to_gamma(beta):
    """Return gamma relativistic from beta."""
    return 1/(_np.sqrt(1 - beta ** 2))


def gamma_to_energy(gamma):
    """Return relativistic energy from gamma."""
    return gamma * PROTON_MASS - PROTON_MASS


def beta_to_energy(beta):
    """Return relativistic energy from beta."""
    return beta_to_gamma(beta) * PROTON_MASS - PROTON_MASS


def energy_to_pv(energy):
    """Return relativistic factor 'pv' from kinetic energy (MeV)."""
    E = energy + PROTON_MASS
    return (E**2 - PROTON_MASS**2) / E


def range_to_energy(r):
    """Return the kinetic energy [MeV] from the range [g/cm^2]."""
    a = 0.00169; b = -0.00490; c = 0.56137; d = 3.46405
    return _np.exp(
        a * _np.log(r) ** 3 + b * _np.log(r) ** 2 + c * _np.log(r) + d
    )


def energy_to_range(e):
    """Return the range [g/cm^2] from the kinetic energy [MeV]."""
    """IEC60601 energy to range in water"""
    b = 0.008539; c = 0.5271; d = 3.4917
    return _np.exp((-c + _np.sqrt(c ** 2 - 4 * b * (d - _np.log(e)))) / (2 * b))
