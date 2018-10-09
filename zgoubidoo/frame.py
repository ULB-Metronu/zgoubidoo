from __future__ import annotations
import numpy as _np
import quaternion as _quaternion
from typing import Optional, List, NoReturn
from . import ureg
from .units import _m, _radian

_X = 0
_Y = 1
_Z = 2

_AXES = {
    'X': 0,
    'Y': 1,
    'Z': 2
}


class ZgoubidooFrameException(Exception):
    """Exception raised for errors in the Frame module."""

    def __init__(self, m):
        self.message = m


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
    def __init__(self, parent: Optional[Frame] = None, reference: Optional[Frame] = None):
        """
        Initialize a Frame with respect to a parent frame. If no parent is provided the newly created frame
        is considered to be a global reference frame. The frame is create with no rotation or translate with
        respect to its parent frame.

        :param parent: parent frame, if None then the frame itself is considered as a global reference frame.
        :param reference: reference frame, all quantities are provided by default with respect to this frame.
        This allows to use the properties easily but can be modified on a case-by-case basis for each function.
        Alternatively the reference frame can be modified after the object creation.
        """
        self._p: Optional[Frame] = parent
        self._r: Optional[Frame] = reference
        self._q: _np.quaternion = _np.quaternion(1, 0, 0, 0)
        self._o: _np.ndarray = _np.zeros(3)

    def __eq__(self, o: Frame) -> bool:
        """
        Equality comparison with another Frame.

        >>> f1 = Frame()
        >>> f2 = Frame()
        >>> f1.rotate_x(10 * ureg.degree) #doctest: +ELLIPSIS
        <zgoubidoo.frame.Frame object at 0x...>
        >>> f1 == f2
        False
        >>> f2.rotate_x(10 * ureg.degree) #doctest: +ELLIPSIS
        <zgoubidoo.frame.Frame object at 0x...>
        >>> f1 == f2
        True

        :param o: other frame to be compared with
        :return: True if the two frames are strictly equal (same parent and equal rotation and origin) else otherwise
        """
        return self._p == o._p and self._q == o._q and _np.all(self._o == o._o)

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

        The 'parent' property can also be set:

        >>> f1 = Frame()
        >>> f1.parent is None
        True
        >>> f2 = Frame()
        >>> f2.parent is None
        True
        >>> f2.parent = f1
        >>> f2.parent is f1
        True
        >>> f2.parent == f1
        True
        >>> f2.parent = None
        >>> f2.parent is None
        True

        :return: parent frame, None in case the frame is a global reference frame.
        """
        return self._p

    @parent.setter
    def parent(self, p) -> NoReturn:
        """
        Modifies the parent frame on the fly.

        :param p: the new parent frame
        :return: NoReturn
        """
        self._p = p

    @property
    def reference(self) -> Optional[Frame]:
        """
        Provides the reference frame with respect to which the quantities will be provided. None if not set.

        >>> f1 = Frame(parent=None, reference=None)
        >>> f1.reference is None
        True
        >>> f2 = Frame(parent=f1, reference=f1)
        >>> f2.reference is f1
        True
        >>> f2.reference == f1
        True
        >>> f2.reference = None
        >>> f2.reference is None
        True

        :return: a frame serving as reference frame for the current frame (None if not set)
        """
        return self._r

    @reference.setter
    def reference(self, r) -> NoReturn:
        """
        Modifies the reference frame with respect to which the quantities are provided by default.

        :param r: the new reference frame.
        :return: NoReturn.
        """
        self._r = r

    def get_quaternion(self, ref: Optional[Frame] = None) -> _np.quaternion:
        """
        Provides the quaternion representation of the rotation of the frame with respect to another reference frame.

        >>> f1 = Frame().rotate_z(20 * ureg.degree)
        >>> f1.get_quaternion()
        quaternion(0.984807753012208, 0, 0, 0.17364817766693)
        >>> f2 = Frame(f1)
        >>> f2.rotate_x(10 * ureg.degree).get_quaternion() #doctest: +ELLIPSIS
        quaternion(0.981060..., 0.085831..., 0.015134..., 0.172987...)
        >>> f2.get_quaternion(f1) #doctest: +ELLIPSIS
        quaternion(0.996194..., 0.087155..., 0, 0)

        :param ref: reference frame with respect to which the rotation quaternion is returned.
        If None then the rotation is provided with respect to the current reference frame.
        :return: the quaternion representing the rotation with respect to a given reference frame.
        """
        ref = ref or self._r
        if self._p is ref:
            return self._q
        elif ref is self:
            return _np.quaternion(1, 0, 0, 0)  # Identity rotation with respect to oneself
        else:
            # Caution: this one DOES NOT commute
            return self._p.get_quaternion(ref) * self._q   # Recursion

    quaternion = property(get_quaternion)
    q = property(get_quaternion)

    def _get_origin(self, ref: Optional[Frame] = None) -> _np.ndarray:
        """
        Provides the offset representing the translation of the frame with respect to another reference frame.
        This method works in the internal unit representation of the class `Frame`.

        >>> f1 = Frame().translate_x(10 * ureg.cm)
        >>> f1._get_origin()
        array([0.1, 0. , 0. ])
        >>> f2 = Frame(f1).translate_y(100 * ureg.cm)
        >>> f2._get_origin()
        array([0.1, 1. , 0. ])
        >>> f2._get_origin(f1)
        array([0., 1., 0.])

        :param ref: reference frame with respect to which the origin is returned.
        If None then the translation is provided with respect to the current reference frame.
        :return: the offset (numpy array, no units) representing the translation with respect to
        a given reference frame.
        """
        ref = ref or self._r
        if self._p is ref:
            return self._o
        elif ref is self:
            return _np.zeros(3)  # Identity translation with respect to oneself
        else:
            m = _quaternion.as_rotation_matrix(self.get_quaternion(ref))
            return self._p._get_origin(ref) + _np.matmul(m, self._o)

    def get_origin(self, ref: Optional[Frame] = None) -> List[ureg.Quantity]:
        """
        Provides the offset representing the translation of the frame with respect to another reference frame.
        This method supports units and returns `pint` quantities with dimensions of [LENGTH].

        >>> f1 = Frame().translate_x(10 * ureg.cm)
        >>> f1.get_origin()
        [<Quantity(0.1, 'meter')>, <Quantity(0.0, 'meter')>, <Quantity(0.0, 'meter')>]
        >>> f2 = Frame(f1).translate_y(100 * ureg.cm)
        >>> f2.get_origin()
        [<Quantity(0.1, 'meter')>, <Quantity(1.0, 'meter')>, <Quantity(0.0, 'meter')>]
        >>> f2.get_origin(f1)
        [<Quantity(0.0, 'meter')>, <Quantity(1.0, 'meter')>, <Quantity(0.0, 'meter')>]

        :param ref: reference frame with respect to which the origin is returned.
        If None then the translation is provided with respect to the global reference frame.
        :return: the offset (list of quantities with dimensions of [LENGTH]) representing the translation
        with respect to a given reference frame.
        """
        return list(map(lambda _: _ * ureg.meter, self._get_origin(ref)))

    o = property(get_origin)
    origin = property(get_origin)

    def _get_x(self, ref: Optional[Frame] = None) -> float:
        """
        Provides the X axis offset representing the translation of the frame with respect to another reference frame.
        This method works in the internal unit representation of the class `Frame`.

        >>> f1 = Frame().translate_x(10 * ureg.cm)
        >>> f1._get_x()
        0.1
        >>> f2 = Frame(f1).translate_y(100 * ureg.cm)
        >>> f2._get_x()
        0.1
        >>> f2._get_x(f1)
        0.0

        :param ref: reference frame with respect to which the origin is returned.
        If None then the translation is provided with respect to the current reference frame.
        :return: the X axis offset (float, no units) representing the X axis translation with respect to
        a given reference frame.
        """
        return self._get_origin(ref)[_X]

    def get_x(self, ref: Optional[Frame] = None) -> ureg.Quantity:
        """
        Provides the X axis offset representing the translation of the frame with respect to another reference frame.
        This method works with full support of pint units.

        >>> f1 = Frame().translate_x(10 * ureg.cm)
        >>> f1.get_x()
        <Quantity(0.1, 'meter')>
        >>> f2 = Frame(f1).translate_y(100 * ureg.cm)
        >>> f2.get_x()
        <Quantity(0.1, 'meter')>
        >>> f2.get_x(f1)
        <Quantity(0.0, 'meter')>

        :param ref: reference frame with respect to which the origin is returned.
        If None then the translation is provided with respect to the current reference frame.
        :return: the X axis offset (with units, pint quantity) representing the X axis translation with respect to
        a given reference frame.
        """
        return self.get_origin(ref)[_X]

    x = property(get_x)

    def _get_y(self, ref: Optional[Frame] = None) -> float:
        """
        Provides the Y axis offset representing the translation of the frame with respect to another reference frame.
        This method works in the internal unit representation of the class `Frame`.

        >>> f1 = Frame().translate_y(10 * ureg.cm)
        >>> f1._get_y()
        0.1
        >>> f2 = Frame(f1).translate_x(100 * ureg.cm)
        >>> f2._get_y()
        0.1
        >>> f2._get_y(f1)
        0.0

        :param ref: reference frame with respect to which the origin is returned.
        If None then the translation is provided with respect to the current reference frame.
        :return: the Y axis offset (float, no units) representing the Y axis translation with respect to
        a given reference frame.
        """
        return self._get_origin(ref)[_Y]

    def get_y(self, ref: Optional[Frame] = None) -> ureg.Quantity:
        """
        Provides the Y axis offset representing the translation of the frame with respect to another reference frame.
        This method works with full support of pint units.

        >>> f1 = Frame().translate_y(10 * ureg.cm)
        >>> f1.get_y()
        <Quantity(0.1, 'meter')>
        >>> f2 = Frame(f1).translate_x(100 * ureg.cm)
        >>> f2.get_y()
        <Quantity(0.1, 'meter')>
        >>> f2.get_y(f1)
        <Quantity(0.0, 'meter')>

        :param ref: reference frame with respect to which the origin is returned.
        If None then the translation is provided with respect to the current reference frame.
        :return: the Y axis offset (with units, pint quantity) representing the Y axis translation with respect to
        a given reference frame.
        """
        return self.get_origin(ref)[_Y]

    y = property(get_y)

    def _get_z(self, ref: Optional[Frame] = None) -> float:
        """
        Provides the Z axis offset representing the translation of the frame with respect to another reference frame.
        This method works in the internal unit representation of the class `Frame`.

        >>> f1 = Frame().translate_z(10 * ureg.cm)
        >>> f1._get_z()
        0.1
        >>> f2 = Frame(f1).translate_x(100 * ureg.cm)
        >>> f2._get_z()
        0.1
        >>> f2._get_z(f1)
        0.0

        :param ref: reference frame with respect to which the origin is returned.
        If None then the translation is provided with respect to the current reference frame.
        :return: the Z axis offset (float, no units) representing the Z axis translation with respect to
        a given reference frame.
        """
        return self._get_origin(ref)[_Z]

    def get_z(self, ref: Optional[Frame] = None) -> ureg.Quantity:
        """
        Provides the Z axis offset representing the translation of the frame with respect to another reference frame.
        This method works with full support of pint units.

        >>> f1 = Frame().translate_z(10 * ureg.cm)
        >>> f1.get_z()
        <Quantity(0.1, 'meter')>
        >>> f2 = Frame(f1).translate_x(100 * ureg.cm)
        >>> f2.get_z()
        <Quantity(0.1, 'meter')>
        >>> f2.get_z(f1)
        <Quantity(0.0, 'meter')>

        :param ref: reference frame with respect to which the origin is returned.
        If None then the translation is provided with respect to the current reference frame.
        :return: the Z axis offset (with units, pint quantity) representing the Z axis translation with respect to
        a given reference frame.
        """
        return self.get_origin(ref)[_Z]

    z = property(get_z)

    def _get_angles(self, ref: Optional[Frame] = None) -> _np.ndarray:
        """

        >>> f1 = Frame() # TODO

        :param ref:
        :return:
        """
        m = _quaternion.as_rotation_matrix(self.get_quaternion(ref))
        return _np.array([
            -_np.pi / 2 + _np.arctan2(m[0, 0], m[1, 0]),
            _np.arccos(m[1, 1]),
            _np.arccos(m[2, 2]),
        ])

    def get_angles(self, ref: Optional[Frame] = None, units: ureg.Unit = ureg.radian) -> List[ureg.Quantity]:
        """

        >>> f1 = Frame() # TODO

        :param ref:
        :param units:
        :return:
        """
        return list(map(lambda _: (_ * ureg.radian).to(units), self._get_angles(ref)))

    angles = property(get_angles)

    def _get_tx(self, ref: Optional[Frame] = None) -> float:
        """

        >>> f1 = Frame() # TODO

        :param ref:
        :return:
        """
        return self._get_angles(ref)[_X]

    def get_tx(self, ref: Optional[Frame] = None) -> ureg.Quantity:
        """

        >>> f1 = Frame() # TODO

        :param ref:
        :return:
        """
        return self._get_tx(ref) * ureg.radian

    tx = property(get_tx)

    def _get_ty(self, ref: Optional[Frame] = None) -> float:
        """

        >>> f1 = Frame() # TODO

        :param ref:
        :return:
        """
        return self._get_angles(ref)[_Y]

    def get_ty(self, ref: Optional[Frame] = None) -> ureg.Quantity:
        """

        >>> f1 = Frame() # TODO

        :param ref:
        :return:
        """
        return self._get_ty(ref) * ureg.radian

    ty = property(get_ty)

    def _get_tz(self, ref: Optional[Frame] = None) -> float:
        """

        >>> f1 = Frame() # TODO

        :param ref:
        :return:
        """
        return self._get_angles(ref)[_Z]

    def get_tz(self, ref: Optional[Frame] = None) -> ureg.Quantity:
        """

        >>> f1 = Frame() # TODO

        :param ref:
        :return:
        """
        return self._get_tz(ref) * ureg.radian

    tz = property(get_tz)

    def __mul__(self, q: _np.quaternion) -> Frame:
        """
        Provide a simple way to rotate the Frame in a generic way, by multiplying directly with a quaternion.

        >>> f = Frame()
        >>> q = _quaternion.from_rotation_vector([0, 0, 0.5])
        >>> (f * q).tx
        <Quantity(-0.5, 'radian')>

        :param q: a quaternion by which the frame is multiplied representing the rotation
        :return: the rotated frame (in place), allows method chaining
        """
        self._q *= q
        return self

    def _rotate(self, angles: _np.array) -> Frame:
        """

        :param angles:
        :return: the rotated frame (in place), allows method chaining
        """
        return self * _quaternion.from_rotation_vector(angles)

    def rotate(self, angles: List[ureg.Quantity]) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param angles:
        :return: the rotated frame (in place), allows method chaining
        """
        return self._rotate(_np.array(list(map(lambda _: _radian(_), angles))))

    def _rotate_x(self, angle: float) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param angle:
        :return:
        """
        return self._rotate([angle, 0, 0])

    def rotate_x(self, angle: ureg.Quantity) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param angle:
        :return:
        """
        return self._rotate_x(_radian(angle))

    def _rotate_y(self, angle: float) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param angle:
        :return:
        """
        return self._rotate([0, angle, 0])

    def rotate_y(self, angle: ureg.Quantity) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param angle:
        :return:
        """
        return self._rotate_y(_radian(angle))

    def _rotate_z(self, angle: float) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param angle:
        :return:
        """
        return self._rotate([0, 0, angle])

    def rotate_z(self, angle: ureg.Quantity) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param angle:
        :return:
        """
        return self._rotate_z(_radian(angle))

    def rotate_axis(self, axis: str, angle: float) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param axis:
        :param angle:
        :return:
        """
        if axis.lower() not in "xyz" or len(axis) > 1:
            raise ZgoubidooFrameException("Invalid rotation axis for 'translate_axis'")
        return getattr(self, f"rotate_{axis.lower()}")(angle)

    def __add__(self, offset: List[ureg.Quantity]) -> Frame:
        """
        Provide a simple way to translate the Frame in a generic way, by adding an offset directly.
        This method is unit-aware and the offset must be provided as a list of pint Quantities.

        >>> f = Frame()
        >>> offset = [1.0 * ureg.cm, 2.0 * ureg.cm, 3.0 * ureg.cm]
        >>> (f + offset).x
        <Quantity(0.01, 'meter')>
        >>> (f + offset).y
        <Quantity(0.04, 'meter')>
        >>> (f + offset).z
        <Quantity(0.09, 'meter')>

        :param offset: a list representing the offset (elements of the list must be quantities of dimension [LENGTH])
        :return: the translated frame (in place)
        """
        return self.translate(offset)

    def _translate(self, offset: _np.ndarray) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param offset:
        :return:
        """
        self._o += offset
        return self

    def translate(self, offset: List[ureg.Quantity]) -> Frame:
        """
        Translates the origin of the Frame with respect to the parent reference frame.
        The translations are extrinsic (done with respect to the axes of the parent frame).

        >>> f1 = Frame()
        >>> f1.translate([1.0 * ureg.meter, 2.0 * ureg.meter, 3.0 * ureg.meter]).o
        [<Quantity(1.0, 'meter')>, <Quantity(2.0, 'meter')>, <Quantity(3.0, 'meter')>]
        >>> f2 = Frame(parent=f1)
        >>> f2.translate([-1.0 * ureg.meter, -2.0 * ureg.meter, -3.0 * ureg.meter]).o
        [<Quantity(0.0, 'meter')>, <Quantity(0.0, 'meter')>, <Quantity(0.0, 'meter')>]
        >>> f2.get_origin(f1)
        [<Quantity(-1.0, 'meter')>, <Quantity(-2.0, 'meter')>, <Quantity(-3.0, 'meter')>]
        >>> f2.rotate_x(180 * ureg.degree).o
        [<Quantity(0.0, 'meter')>, <Quantity(4.0, 'meter')>, <Quantity(6.0, 'meter')>]
        >>> f2.get_origin(f1)
        [<Quantity(-1.0, 'meter')>, <Quantity(-2.0, 'meter')>, <Quantity(-3.0, 'meter')>]

        :param offset: a list representing the offset (elements of the list must be quantities of dimension [LENGTH])
        :return: the translated frame (in place), allows method chaining
        """
        if len(offset) != 3:
            raise ZgoubidooFrameException("The offset must be of length 3.")
        return self._translate(_np.array(list(map(lambda _: _m(_), offset))))

    def _translate_x(self, offset: float) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param offset:
        :return:
        """
        self._o[_X] += offset
        return self

    def translate_x(self, offset: ureg.Quantity) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param offset:
        :return:
        """
        return self._translate_x(_m(offset))

    def _translate_y(self, offset: float) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param offset:
        :return:
        """
        self._o[_Y] += offset
        return self

    def translate_y(self, offset: ureg.Quantity) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param offset:
        :return:
        """
        return self._translate_y(_m(offset))

    def _translate_z(self, offset: float) -> Frame:
        """

        >>> f1 = Frame() # TODO


        :param offset:
        :return:
        """
        self._o[_Z] += offset
        return self

    def translate_z(self, offset: ureg.Quantity) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param offset:
        :return:
        """
        return self._translate_z(_m(offset))

    def _translate_axis(self, axis: str, offset: float) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param axis:
        :param offset:
        :return:
        """
        if axis.lower() not in "xyz" or len(axis) > 1:
            raise ZgoubidooFrameException("Invalid rotation axis for 'translate_axis'")
        return getattr(self, f"_translate_{axis.lower()}")(offset)

    def translate_axis(self, axis: str, offset: ureg.Quantity) -> Frame:
        """

        >>> f1 = Frame() # TODO

        :param axis:
        :param offset:
        :return:
        """
        return self._translate_axis(axis, _m(offset))

    def reset(self) -> Frame:
        """
        Reset the frame (rotation and translation) with respect to the parent.

        >>> f1 = Frame().rotate_x(1 * ureg.radian)
        >>> f1.get_angles() #doctest: +ELLIPSIS
        [<Quantity(0.0, 'radian')>, <Quantity(0.999..., 'radian')>, <Quantity(0.999..., 'radian')>]
        >>> f1.reset().get_angles()
        [<Quantity(0.0, 'radian')>, <Quantity(0.0, 'radian')>, <Quantity(0.0, 'radian')>]

        :return: the frame itself (to allow method chaining)
        """
        self._q: _np.quaternion = _np.quaternion(1, 0, 0, 0)
        self._o: _np.ndarray = _np.zeros(3)
        return self

