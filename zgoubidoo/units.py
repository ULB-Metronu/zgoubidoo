from . import ureg, Q_


def _m(q: Q_) -> float:
    """
    Convert a quantity of dimension [LENGTH] to meters.

    >>> _m(1 * ureg.km)
    1000.0

    :param q: the quantity of dimension [LENGTH]
    :return: the magnitude in meters.
    """
    return float(q.to('m').magnitude)


def _cm(q: Q_) -> float:
    """
    Convert a quantity of dimension [LENGTH] to centimeters.

    >>> _cm(1 * ureg.km)
    100000.0

    :param q: the quantity of dimension [LENGTH]
    :return: the magnitude in centimeters.
    """
    return float(q.to('cm').magnitude)


def _mm(q: Q_) -> float:
    """
    Convert a quantity of dimension [LENGTH] to millimeters.

    >>> _mm(1 * ureg.km)
    1000000.0

    :param q: the quantity of dimension [LENGTH]
    :return: the magnitude in millimeters.
    """
    return float(q.to('mm').magnitude)


def _degree(q: Q_) -> float:
    """
    Convert a quantity to degrees.

    >>> _degree(1 * ureg.degree)
    1.0
    >>> _degree(10.0 * ureg.degree)
    10.0

    :param q: the quantity
    :return: the magnitude in degrees.
    """
    return float(q.to('degree').magnitude)


def _radian(q: Q_) -> float:
    """
    Convert a quantity to radians.

    >>> _radian(180 * ureg.degree) #doctest: +ELLIPSIS
    3.14159...

    :param q: the quantity
    :return: the magnitude in degrees.
    """
    return float(q.to('radian').magnitude)


def _tesla(q: Q_) -> float:
    """
    Convert a quantity of dimension [LENGTH] to meters.

    >>> _m(1 * ureg.km)
    1000.0

    :param q: the quantity of dimension [LENGTH]
    :return: the magnitude in meters.
    """
    return float(q.to('tesla').magnitude)


def _gauss(q: Q_) -> float:
    """
    Convert a quantity of dimension [LENGTH] to meters.

    >>> _m(1 * ureg.km)
    1000.0

    :param q: the quantity of dimension [LENGTH]
    :return: the magnitude in meters.
    """
    return float(q.to('gauss').magnitude)


def _kilogauss(q: Q_) -> float:
    """
    Convert a quantity of dimension [LENGTH] to meters.

    >>> _m(1 * ureg.km)
    1000.0

    :param q: the quantity of dimension [LENGTH]
    :return: the magnitude in meters.
    """
    return float(q.to('kilogauss').magnitude)


def _mev(q: Q_) -> float:
    """
    Convert a quantity of dimension [length]**2 * [mass] * [time]**-2.0 to meters.

    >>> _mev(1 * ureg.MeV)
    1.0

    :param q: the quantity of dimension [length]**2 * [mass] * [time]**-2.0
    :return: the magnitude in MeV.
    """
    return float(q.to('MeV').magnitude)


def _mev_c(q: Q_) -> float:
    """
    Convert a quantity of dimension [LENGTH] to meters.

    >>> _m(1 * ureg.km)
    1000.0

    :param q: the quantity of dimension [LENGTH]
    :return: the magnitude in meters.
    """
    return float(q.to('MeV_c').magnitude)
