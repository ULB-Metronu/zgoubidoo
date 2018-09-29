from __future__ import annotations
import numpy as _np
import quaternion as _quaternion
from typing import Optional, List
from . import ureg
from .units import _m, _radian

_X = 0
_Y = 1
_Z = 2


class Frame:
    """
    A Frame object represents a reference frame for affine geometry transformations (rotations and translations).
    It has full support for transformation chaining through the notion of 'parent frame' and is able to provide
    rotation angles and translation offsets with respect to any parent among the linked list of parents.

    Additionnally Frames are unit-aware through the use of 'pint quantities'. The internal representations use the
    'quaternion-numpy' module with the base units being radians and meters. This is transparent to the public interface
    which can use arbitrary units for the representations of lengths and angles.

    Frame handles quaternion rotations via `quaternion-numpy`: https://github.com/moble/quaternion .

    >>> f1 = Frame()
    >>> f1.translate_y(10 * ureg.cm) #doctest: +ELLIPSIS
    <zgoubidoo.frame.Frame object at 0x...>
    >>> f2 = Frame(parent=f1)
    >>> f2.parent == f1
    True
    >>> f2.translate_x(1 * ureg.cm) #doctest: +ELLIPSIS
    <zgoubidoo.frame.Frame object at 0x...>
    >>> f2.get_origin(f1)
    [<Quantity(0.01, 'meter')>, <Quantity(0.0, 'meter')>, <Quantity(0.0, 'meter')>]
    >>> f2.o == f2.origin == f2.get_origin(None)
    True
    """
    def __init__(self, parent: Optional[Frame] = None):
        """
        Initialize a Frame with respect to a parent frame. If no parent is provided the newly created frame
        is considered to be a global reference frame. The frame is create with no rotation or translate with
        respect to its parent frame.
        :param parent: parent frame, if None then the frame is considered as a global reference frame.
        """
        self._p: Optional[Frame] = parent
        self._q: _np.quaternion = _np.quaternion(1, 0, 0, 0)
        self._o: _np.ndarray = _np.zeros(3)
        self._flips: _np.ndarray = _np.ones(3)

    @property
    def parent(self) -> Optional[Frame]:
        """
        Provides the parent frame.

        >>> f1 = Frame()
        >>> f1.parent is None
        True
        >>> f2 = Frame(parent=f1)
        >>> f2.parent == f1
        True

        :return: parent frame, None in case the frame is a global reference frame.
        """
        return self._p

    @parent.setter
    def parent(self, _):
        raise Exception("Setting the parent is not allowed.")

    def get_quaternion(self, ref: Optional[Frame] = None) -> _np.quaternion:
        """
        Provides the quaternion representation of the rotation of the frame with respect to another reference frame.
        :param ref: reference frame with respect to which the rotation quaternion is returned.
        If None then the rotation is provided with respect to the global reference frame.
        :return: the quaternion representing the rotation with respect to a given reference frame.
        """
        if self._p == ref:
            return self._q
        elif ref == self:
            return _np.quaternion(1, 0, 0, 0)  # Identity rotation with respect to oneself
        else:
            return self._q * self._p.get_quaternion(ref)  # Recursion

    quaternion = property(get_quaternion)
    q = property(get_quaternion)

    def _get_origin(self, ref: Optional[Frame] = None) -> _np.ndarray:
        """
        Provides the offset representing the translation of the frame with respect to another reference frame.
        This method works in the internal unit representation of the class `Frame`.
        :param ref: reference frame with respect to which the origin is returned.
        If None then the translation is provided with respect to the global reference frame.
        :return: the offset (numpy array, no units) representing the translation with respect to
        a given reference frame.
        """
        if self._p == ref:
            return self._o
        elif ref == self:
            return _np.zeros(3)  # Identity translation with respect to oneself
        else:
            m = _quaternion.as_rotation_matrix(self.get_quaternion(ref))
            return self._p._get_origin(ref) + _np.matmul(m, self._o)

    def get_origin(self, ref: Optional[Frame] = None) -> List[ureg.Quantity]:
        """
        Provides the offset representing the translation of the frame with respect to another reference frame.
        This method supports units and returns `pint` quantities with dimensions of [LENGTH].
        :param ref: reference frame with respect to which the origin is returned.
        If None then the translation is provided with respect to the global reference frame.
        :return: the offset (list of quantities with dimensions of [LENGTH]) representing the translation
        with respect to a given reference frame.
        """
        return list(map(lambda _: _ * ureg.meter, self._get_origin(ref)))

    o = property(get_origin)
    origin = property(get_origin)

    def _get_x(self, ref: Optional[Frame] = None) -> float:
        return self.get_origin(ref)[_X]

    def get_x(self, ref: Optional[Frame] = None) -> ureg.Quantity:
        """

        :param ref: reference frame with respect to which the origin is returned.
        If None then the translation offset is provided with respect to the global reference frame.
        :return:
        """
        return self._get_x(ref)

    x = property(get_x)

    def _get_y(self, ref: Optional[Frame] = None) -> float:
        return self.get_origin(ref)[_Y]

    def get_y(self, ref: Optional[Frame] = None) -> ureg.Quantity:
        """

        :param ref: reference frame with respect to which the origin is returned.
        If None then the translation offset is provided with respect to the global reference frame.
        :return:
        """
        return self._get_y(ref)

    y = property(get_y)

    def _get_z(self, ref: Optional[Frame] = None) -> float:
        return self.get_origin(ref)[_Z]

    def get_z(self, ref: Optional[Frame] = None) -> ureg.Quantity:
        """

        :param ref: reference frame with respect to which the origin is returned.
        If None then the translation offset is provided with respect to the global reference frame.
        :return:
        """
        return self._get_z(ref)

    z = property(get_z)

    def _get_angles(self, ref: Optional[Frame] = None) -> _np.ndarray:
        return _np.array([_np.arccos(e) for e in _np.diag(_quaternion.as_rotation_matrix(self.get_quaternion(ref)))])

    def get_angles(self, ref: Optional[Frame] = None) -> List[ureg.Quantity]:
        return list(map(lambda _: _ * ureg.radian , self._get_angles(ref)))

    angles = property(get_angles)

    def _get_tx(self, ref: Optional[Frame] = None) -> float:
        return self._get_angles(ref)[_X]

    def get_tx(self, ref: Optional[Frame] = None) -> ureg.Quantity:
        return self._get_tx(ref) * ureg.radian

    tx = property(get_tx)

    def _get_ty(self, ref: Optional[Frame] = None) -> float:
        return self._get_angles(ref)[_Y]

    def get_ty(self, ref: Optional[Frame] = None) -> ureg.Quantity:
        return self._get_ty(ref) * ureg.radian

    ty = property(get_ty)

    def _get_tz(self, ref: Optional[Frame] = None) -> float:
        return self._get_angles(ref)[_Z]

    def get_tz(self, ref: Optional[Frame] = None) -> ureg.Quantity:
        return self._get_tz(ref) * ureg.radian

    tz = property(get_tz)

    def _rotate(self, angles: _np.array) -> Frame:
        self._q *= _quaternion.from_rotation_vector(angles)
        return self

    def rotate(self, angles: List[ureg.Quantity]) -> Frame:
        return self._rotate(_np.array(list(map(lambda _: _radian(_), angles))))

    def _rotate_x(self, angle: float) -> Frame:
        self._rotate([angle, 0, 0])
        return self

    def rotate_x(self, angle: ureg.Quantity) -> Frame:
        return self._rotate_x(_radian(angle))

    def _rotate_y(self, angle: float) -> Frame:
        self._rotate([0, angle, 0])
        return self

    def rotate_y(self, angle: ureg.Quantity) -> Frame:
        return self._rotate_y(_radian(angle))

    def _rotate_z(self, angle: float) -> Frame:
        self._rotate([0, 0, angle])
        return self

    def rotate_z(self, angle: ureg.Quantity) -> Frame:
        return self._rotate_z(_radian(angle))

    def rotate_axis(self, axis: str, angle: float) -> Frame:
        if axis.lower() not in "xyz" or len(axis) > 1:
            raise Exception("Invalid rotation axis for 'translate_axis'")
        return getattr(self, f"rotate_{axis.lower()}")(angle)

    def _translate(self, offset: _np.ndarray) -> Frame:
        self._o += offset
        return self

    def translate(self, offset: List[ureg.Quantity]) -> Frame:
        return self._translate(_np.array(_np.array(list(map(lambda _: _m(_), offset)))))

    def _translate_x(self, offset: float) -> Frame:
        self._o[_X] += offset
        return self

    def translate_x(self, offset: ureg.Quantity) -> Frame:
        return self._translate_x(_m(offset))

    def _translate_y(self, offset: float) -> Frame:
        self._o[_Y] += offset
        return self

    def translate_y(self, offset: ureg.Quantity) -> Frame:
        return self._translate_y(_m(offset))

    def _translate_z(self, offset: float) -> Frame:
        self._o[_Z] += offset
        return self

    def translate_z(self, offset: ureg.Quantity) -> Frame:
        return self._translate_z(_m(offset))

    def _translate_axis(self, axis: str, offset: float) -> Frame:
        if axis.lower() not in "xyz" or len(axis) > 1:
            raise Exception("Invalid rotation axis for 'translate_axis'")
        return getattr(self, f"translate_{axis.lower()}")(offset)

    def translate_axis(self, axis: str, offset: ureg.Quantity) -> Frame:
        return self._translate_axis(axis, _m(offset))

    def reset(self) -> Frame:
        """
        Reset the frame (rotation and translation) with respect to the parent.

        >>> f1 = Frame().rotate_x(1 * ureg.radian)
        >>> f1.get_angles()
        [<Quantity(0.0, 'radian')>, <Quantity(0.9999999999999999, 'radian')>, <Quantity(0.9999999999999999, 'radian')>]
        >>> f1.reset().get_angles()
        [<Quantity(0.0, 'radian')>, <Quantity(0.0, 'radian')>, <Quantity(0.0, 'radian')>]

        :return: the frame itself (to allow method chaining)
        """
        self._q: _np.quaternion = _np.quaternion(1, 0, 0, 0)
        self._o: _np.ndarray = _np.zeros(3)
        return self
