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
        self._ref_frame: ReferenceFrame = f
        self._ref_origin: Point = o
        self._frame: ReferenceFrame = f.orientnew(f"FRAME_{id(self)}", 'Quaternion', [1, 0, 0, 0])  # Identity
        self._origin: Point = o.locatenew(f"ORIGIN_{id(self)}", 0 * f.x)

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
            return self.origin.pos_from(self.ref_origin).to_matrix(self.ref_frame)
        else:
            return self.origin.pos_from(reference.origin).to_matrix(reference.frame)

    offset = property(offset_ref)

    def offset_x(self, reference) -> float:
        return self.offset_ref(reference)[0, 0]

    def offset_y(self, reference) -> float:
        return self.offset_ref(reference)[1, 0]

    def offset_z(self, reference) -> float:
        return self.offset_ref(reference)[2, 0]

    def rotate(self, axis: str, angle: float) -> None:
        self.frame.orient(self.ref_frame, "Axis", [angle, getattr(self.ref_frame, axis.lower())])

    def rotate_x(self, angle: float) -> None:
        self.rotate('X', angle)

    def rotate_y(self, angle: float) -> None:
        self.rotate('Y', angle)

    def rotate_z(self, angle: float) -> None:
        self.rotate('Z', angle)

    def translate(self, axis: str, offset: float) -> None:
        self.origin.set_pos(self.ref_origin, offset * getattr(self.frame, axis.lower()))

    def translate_x(self, offset: float) -> None:
        self.translate('X', offset)

    def translate_y(self, offset: float) -> None:
        self.translate('Y', offset)

    def translate_z(self, offset: float) -> None:
        self.translate('Z', offset)
