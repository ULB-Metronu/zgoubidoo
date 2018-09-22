from sympy.physics.vector import ReferenceFrame, Point


class Frame:
    """

    """

    def __init__(self, reference=None):
        if reference is not None:
            f = reference.frame
            o = reference.origin
        else:
            f = ReferenceFrame(f"REF_FRAME_{id(self)}")
            o = Point(f"REF_ORIGIN_{id(self)}")
        self._ref_frame = f
        self._ref_origin = o
        self._frame = f.orientnew(f"FRAME_{id(self)}", 'Quaternion', [1, 0, 0, 0])
        self._origin = o.locatenew(f"ORIGIN_{id(self)}", 0 * f.x)

    def __copy__(self):
        return Frame(self)

    @property
    def frame(self) -> ReferenceFrame:
        return self._frame

    @property
    def origin(self) -> Point:
        return self._origin

    @property
    def ref_frame(self) -> ReferenceFrame:
        return self._ref_frame

    @property
    def ref_origin(self) -> Point:
        return self._ref_origin

    def dcm_ref(self, reference=None):
        if reference is None:
            return self.frame.dcm(self.ref_frame)
        else:
            return self.frame.dcm(reference.frame)

    dcm = property(dcm_ref)

    def offset_ref(self, reference=None):
        if reference is None:
            return self.origin.pos_from(self.ref_origin)
        else:
            return self.origin.pos_from(reference.origin)

    offset = property(offset_ref)

    def rotate(self, axis: str, angle: float) -> None:
        self.frame.orient(self.ref_frame, "Axis", [angle, getattr(self.ref_frame, axis.lower())])

    def translate(self, axis: str, offset: float) -> None:
        self.origin.set_pos(self.ref_origin, offset * getattr(self.frame, axis.lower()))
