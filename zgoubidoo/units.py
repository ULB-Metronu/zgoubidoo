from typing import Union, Callable
from . import ureg as _ureg
from . import _Q


def parse_quantity(f: Callable):
    def parse_arg(q: Union[str, _Q]):
        if isinstance(q, str):
            q = _Q(q)
        return f(q)
    return parse_arg


@parse_quantity
def _m(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [LENGTH] to meters.

    >>> _m(1 * _ureg.km)
    1000.0

    :param q: the quantity of dimension [LENGTH]
    :return: the magnitude in meters.
    """
    if isinstance(q, str):
        q = _Q(q)
    return float(q.to('m').magnitude)


@parse_quantity
def _cm(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [LENGTH] to centimeters.

    >>> _cm(1 * _ureg.km)
    100000.0

    :param q: the quantity of dimension [LENGTH]
    :return: the magnitude in centimeters.
    """
    return float(q.to('cm').magnitude)


@parse_quantity
def _mm(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [LENGTH] to millimeters.

    >>> _mm(1 * _ureg.km)
    1000000.0

    :param q: the quantity of dimension [LENGTH]
    :return: the magnitude in millimeters.
    """
    return float(q.to('mm').magnitude)


@parse_quantity
def _degree(q: Union[str, _Q]) -> float:
    """
    Convert a quantity to degrees.

    >>> _degree(1 * _ureg.degree)
    1.0
    >>> _degree(10.0 * _ureg.degree)
    10.0

    :param q: the quantity
    :return: the magnitude in degrees.
    """
    return float(q.to('degree').magnitude)


@parse_quantity
def _radian(q: Union[str, _Q]) -> float:
    """
    Convert a quantity to radians.

    >>> _radian(180 * _ureg.degree) #doctest: +ELLIPSIS
    3.14159...

    :param q: the quantity
    :return: the magnitude in degrees.
    """
    return float(q.to('radian').magnitude)


@parse_quantity
def _tesla(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [LENGTH] to meters.

    >>> _m(1 * _ureg.km)
    1000.0

    :param q: the quantity of dimension [LENGTH]
    :return: the magnitude in meters.
    """
    return float(q.to('tesla').magnitude)


@parse_quantity
def _gauss(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [LENGTH] to meters.

    >>> _m(1 * _ureg.km)
    1000.0

    :param q: the quantity of dimension [LENGTH]
    :return: the magnitude in meters.
    """
    return float(q.to('gauss').magnitude)


@parse_quantity
def _kilogauss(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [LENGTH] to meters.

    >>> _m(1 * _ureg.km)
    1000.0

    :param q: the quantity of dimension [LENGTH]
    :return: the magnitude in meters.
    """
    return float(q.to('kilogauss').magnitude)


@parse_quantity
def _mev(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [length]**2 * [mass] * [time]**-2.0 to meters.

    >>> _mev(1 * _ureg.MeV)
    1.0

    :param q: the quantity of dimension [length]**2 * [mass] * [time]**-2.0
    :return: the magnitude in MeV.
    """
    return float(q.to('MeV').magnitude)


@parse_quantity
def _mev_c(q: _Q) -> float:
    """Convert a quantity of dimension [LENGTH] to meters.

    Examples:
        >>> _m(1 * _ureg.km)
        1000.0

    Args:
        q: the quantity of dimension [LENGTH]

    Returns:
        the magnitude in meters.
    """
    return float(q.to('MeV_c').magnitude)
