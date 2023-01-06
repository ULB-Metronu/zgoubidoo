from typing import Callable, Union

from . import Q_ as _Q
from . import ureg as _ureg  # noqa: F401


def parse_quantity(f: Callable):
    """Decorator to convert argument 'q' from a string to a quantity."""

    def parse_arg(q: Union[str, _Q]):
        """Converts string to a Pint quantity."""
        if isinstance(q, str):
            q: _Q = _Q(q)
        return f(q)

    return parse_arg


@parse_quantity
def _m(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [LENGTH] to meters.
    >>> _m(1 * _ureg.km)
    1000.0

    Args:
        q: the quantity of dimension [LENGTH]

    Returns: the magnitude in meters.

    """
    return float(q.to("m").magnitude)


@parse_quantity
def _cm(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [LENGTH] to centimeters.
    >>> _cm(1 * _ureg.km)
    100000.

    Args:
        q: the quantity of dimension [LENGTH]

    Returns: the magnitude in centimeters.

    """
    return float(q.to("cm").magnitude)


@parse_quantity
def _mm(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [LENGTH] to millimeters.
    >>> _mm(1 * _ureg.km)
    1000000.0

    Args:
        q: the quantity of dimension [LENGTH]

    Returns: the magnitude in millimeters.

    """
    return float(q.to("mm").magnitude)


@parse_quantity
def _degree(q: Union[str, _Q]) -> float:
    """
    Convert a quantity to degree.
    >>> _degree(1 * _ureg.degree)
    1.0
    >>> _degree(10.0 * _ureg.degree)
    10.0

    Args:
        q: the quantity

    Returns: the magnitude in degrees.

    """
    return float(q.to("degree").magnitude)


@parse_quantity
def _radian(q: Union[str, _Q]) -> float:
    """
    Convert a quantity to radians.
    >>> _radian(180 * _ureg.degree)

    Args:
        q: the quantity

    Returns: the magnitude in degrees.
    """
    return float(q.to("radian").magnitude)


@parse_quantity
def _tesla(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [GAUSS] to tesla.

    Args:
        q: the quantity of dimension [GAUSS]

    Returns: the magnitude in Tesla.

    """
    return float(q.to("tesla").magnitude)


@parse_quantity
def _gauss(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [GAUSS] to gauss.

    Args:
        q: the quantity of dimension [GAUSS]

    Returns: the magnitude in Gauss.

    """
    return float(q.to("gauss").magnitude)


@parse_quantity
def _kilogauss(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [GAUSS] to kilogauss.

    Args:
        q: the quantity of dimension [GAUSS]

    Returns: the magnitude in kilogauss.

    """
    return float(q.to("kilogauss").magnitude)


@parse_quantity
def _ampere(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [AMPERE] to ampere.

    Args:
        q: the quantity of dimension [AMPERE]

    Returns: the magnitude in ampere.

    """
    return float(q.to("ampere").magnitude)


@parse_quantity
def _mev(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [length]**2 * [mass] * [time]**-2.0 to meters.
    >>> _mev(1 * _ureg.MeV)

    Args:
        q: the quantity of dimension [length]**2 * [mass] * [time]**-2.0

    Returns: the magnitude in MeV.

    """
    return float(q.to("MeV").magnitude)


@parse_quantity
def _gev(q: Union[str, _Q]) -> float:
    """
    Convert a quantity of dimension [length]**2 * [mass] * [time]**-2.0 to meters.
    >>> _mev(1 * _ureg.MeV)

    1.0
    Args:
        q: the quantity of dimension [length]**2 * [mass] * [time]**-2.0

    Returns: the magnitude in MeV.

    """
    return float(q.to("GeV").magnitude)


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
    return float(q.to("MeV_c").magnitude)


@parse_quantity
def _gev_c(q: _Q) -> float:
    """Convert a quantity of dimension [LENGTH] to meters.

    Examples:
        >>> _m(1 * _ureg.km)
        1000.0

    Args:
        q: the quantity of dimension [LENGTH]

    Returns:
        the magnitude in meters.
    """
    return float(q.to("GeV_c").magnitude)
