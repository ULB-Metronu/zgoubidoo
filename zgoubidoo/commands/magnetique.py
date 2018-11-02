from typing import NoReturn
from .commands import Command, ZgoubidoException
from .. import ureg, Q_
from ..frame import Frame
from ..vis import ZgoubiPlot
from .patchable import Patchable
from .plotable import Plotable
from ..units import _cm, _radian, _kilogauss


class Magnet(Command, Patchable, Plotable):
    """Base class for all magnetic elements."""
    PARAMETERS = {
        'HEIGHT': 20 * ureg.cm,
    }

    def __init__(self, label1='', label2='', *params, **kwargs):
        super().__init__(label1, label2, Magnet.PARAMETERS, self.PARAMETERS, *params, **kwargs)


class CartesianMagnet(Magnet):
    """Base class for magnetic elements in cartesian coordinates"""
    PARAMETERS = {
        'WIDTH': 50 * ureg.cm,
        'COLOR': 'gray',
    }

    def __init__(self, label1='', label2='', *params, **kwargs):
        super().__init__(label1, label2, CartesianMagnet.PARAMETERS, self.PARAMETERS, *params, **kwargs)

    @property
    def rotation(self) -> Q_:
        return self.ALE or 0.0 * ureg.degree

    @property
    def length(self) -> Q_:
        return self.XL or 0.0 * ureg.cm

    @property
    def x_offset(self) -> Q_:
        return self.XCE or 0.0 * ureg.cm

    @property
    def y_offset(self) -> Q_:
        return self.YCE or 0.0 * ureg.cm

    @property
    def entry_patched(self) -> Frame:
        if self._entry_patched is None:
            self._entry_patched = Frame(self.entry)
            self._entry_patched.translate_x(-(self.X_E or 0.0 * ureg.cm))
            self._entry_patched.translate_x(self.x_offset)
            self._entry_patched.translate_y(self.y_offset)
            self._entry_patched.rotate_z(-self.rotation)
        return self._entry_patched

    @property
    def exit(self) -> Frame:
        if self._exit is None:
            self._exit = Frame(self.entry_patched)
            self._exit.translate_x(self.length + (self.X_E or 0.0 * ureg.cm) + (self.X_S or 0.0 * ureg.cm))
        return self._exit

    @property
    def exit_patched(self) -> Frame:
        if self._exit_patched is None:
            if self.KPOS is None or self.KPOS == 1:
                self._exit_patched = Frame(self.exit)
                self._exit_patched.translate_x(-(self.X_S or 0.0 * ureg.cm))
            elif self.KPOS == 0 or self.KPOS == 2:
                self._exit_patched = Frame(self.entry)
                self._exit_patched.translate_x(self.XL or 0.0 * ureg.cm)
        return self._exit_patched

    def plot(self, artist=None) -> NoReturn:
        if artist is None:
            return
        getattr(artist, CartesianMagnet.__name__.lower())(self)

    def plot_tracks(self, artist=None, tracks=None) -> NoReturn:
        if artist is None or tracks is None:
            return
        getattr(artist, f"tracks_{CartesianMagnet.__name__.lower()}")(self, tracks)


class PolarMagnet(Magnet):
    """Base class for magnetic elements in polar coordinates"""
    PARAMETERS = {
        'WIDTH': 50 * ureg.cm,
    }

    def __init__(self, label1: str='', label2: str='', *params, **kwargs):
        super().__init__(label1, label2, PolarMagnet.PARAMETERS, self.PARAMETERS, *params, **kwargs)

    @property
    def angular_opening(self):
        return self.AT or 0 * ureg.degree

    @property
    def radius(self) -> Q_:
        return self.RM or 0 * ureg.cm

    @property
    def length(self) -> Q_:
        return self.angular_opening * self.radius

    @property
    def entry_patched(self):
        if self._entry_patched is None:
            self._entry_patched = Frame(self.entry)
        return self._entry_patched

    @property
    def center(self):
        if self._center is None:
            self._center = Frame(self.entry_patched)
            self._center.translate_y(-self.radius)
        return self._center

    @property
    def exit(self) -> Frame:
        if self._exit is None:
            self._exit = Frame(self.center)
            self._exit.translate_y(self.radius)
            self._exit.rotate_z(-self.angular_opening)
        return self._exit

    @property
    def exit_patched(self) -> Frame:
        if self._exit_patched is None:
            self._exit_patched = Frame(self.exit)
        return self._exit_patched

    def plot(self, artist: ZgoubiPlot):
        getattr(artist, PolarMagnet.__name__.lower())(self)

    def plot_tracks(self, artist=None, tracks=None):
        if artist is None or tracks is None:
            return
        getattr(artist, f"tracks_{PolarMagnet.__name__.lower()}")(self, tracks)


class AGSMainMagnet(Magnet):
    """AGS main magnet."""
    KEYWORD = 'AGSMM'


class AGSQuadrupole(Magnet):
    """AGS quadrupole."""
    KEYWORD = 'AGSQUAD'

    PARAMETERS = {

    }


class Aimant(Magnet):
    """Generation of dipole mid-plane 2-D map, polar frame."""
    PARAMETERS = {
        'NFACE': 2,
        'IC': 0,  # 1, 2: print field map
        'IL': 0,  # 1, 2: print field and coordinates on trajectores
        'IAMAX': 0,
        'IRMAX': 0,
        'B0': 0,
        'N': 0,
        'B': 0,
        'G': 0,
        'AT': 0,
        'ACENT': 0,
        'RM': 0,
        'RMIN': 0,
        'RMAX': 0,
        'LAM_E': 0,
        'XI_E': 0,
        'NCE': 0,
        'C0_E': 0,
        'C1_E': 0,
        'C2_E': 0,
        'C3_E': 0,
        'C4_E': 0,
        'C5_E': 0,
        'SHIFT_E': 0,
        'OMEGA_E': 0,
        'THETA_E': 0,
        'R1_E': 1e9,
        'U1_E': -1e9,
        'U2_E': 1e9,
        'R2_E': 1e9,
        'LAM_S': 0,
        'XI_S': 0,
        'NCS': 0,
        'C0_S': 0,
        'C1_S': 0,
        'C2_S': 0,
        'C3_S': 0,
        'C4_S': 0,
        'C5_S': 0,
        'SHIFT_S': 0,
        'OMEGA_S': 0,
        'THETA_S': 0,
        'R1_S': 1e9,
        'U1_S': -1e9,
        'U2_S': 1e9,
        'R2_S': 1e9,
        'LAM_L': 0,
        'XI_L': 0,
        'NCL': 0,
        'C0_L': 0,
        'C1_L': 0,
        'C2_L': 0,
        'C3_L': 0,
        'C4_L': 0,
        'C5_L': 0,
        'SHIFT_L': 0,
        'OMEGA_L': 0,
        'THETA_L': 0,
        'R1_L': 1e9,
        'U1_L': -1e9,
        'U2_L': 1e9,
        'R2_L': 1e9,
        'RM3': 0,
        'NBS': 0,
        'R0': 0,
        'DELTAB': 0,
        'THETA_0': 0,
        'IORDRE': 4,
        'XPAS': 0.1,
        'KPOS': 2,
        'RE': 0,
        'TE': 0,
        'RS': 0,
        'TS': 0,
        'DP': 0,
        'SHIM_R1': [],
        'SHIM_R2': [],
        'SHIM_THETA1': [],
        'SHIM_THETA2': [],
        'SHIM_LAMBDA': [],
        'SHIM_GAMMA': [],
        'SHIM_ALPHA': [],
        'SHIM_BETA': [],
        'SHIM_MU': [],
    }

    def __str__(s):
        command = []
        if s.NFACE not in (2, 3):
            raise ZgoubidoException(f"Error : Zgoubido does not support NFACE = {s.NFACE}")

        c = f"""
                {super().__str__().rstrip()}
                {s.NFACE} {s.IC} {s.IL}
                {s.IAMAX} {s.IRMAX}
                {s.B0:.12e} {s.N:.12e} {s.B:.12e} {s.G:.12e}
                {s.AT:.12e} {s.ACENT:.12e} {s.RM:.12e} {s.RMIN:.12e} {s.RMAX:.12e}
                {s.LAM_E:.12e} {s.XI_E:.12e}
                {s.NCE} {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e} {s.SHIFT_E:.12e}
                {s.OMEGA_E:.12e} {s.THETA_E:.12e} {s.R1_E:.12e} {s.U1_E:.12e} {s.U2_E:.12e} {s.R2_E:.12e}
                {s.LAM_S:.12e} {s.XI_S:.12e}
                {s.NCS} {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e} {s.SHIFT_S:.12e}
                {s.OMEGA_S:.12e} {s.THETA_S:.12e} {s.R1_S:.12e} {s.U1_S:.12e} {s.U2_S:.12e} {s.R2_S:.12e}
            """
        command.append(c)

        if s.NFACE == 3:
            c = f"""
                    {s.LAM_L:.12e} {s.XI_L:.12e}
                    {s.NCL} {s.C0_L:.12e} {s.C1_L:.12e} {s.C2_L:.12e} {s.C3_L:.12e} {s.C4_L:.12e} {s.C5_L:.12e} {s.SHIFT_L:.12e}
                    {s.OMEGA_L:.12e} {s.THETA_L:.12e} {s.R1_L:.12e} {s.U1_L:.12e} {s.U2_L:.12e} {s.R2_L:.12e} {s.RM3:.12e}
                """
            command.append(c)

        if s.NBS == 0:
            command.append(f"""
                {s.NBS}
                """)
        elif s.NBS == -2:
            c = f"""
                    {s.NBS}
                    {s.R0:.12e} {s.DELTAB:.12e}
                    """
            command.append(c)
        elif s.NBS == -1:
            c = f"""
                    {s.NBS}
                    {s.THETA_0:.12e} {s.DELTAB:.12e}
                    """
            command.append(c)
        elif s.NBS >= 1:
            command.append(f"""
                {s.NBS}""")

            shim_r1 = len(s.SHIM_R1)
            shim_r2 = len(s.SHIM_R2)
            shim_theta1 = len(s.SHIM_THETA1)
            shim_theta2 = len(s.SHIM_THETA2)
            shim_lambda = len(s.SHIM_LAMBDA)
            shim_gamma = len(s.SHIM_GAMMA)
            shim_alpha = len(s.SHIM_ALPHA)
            shim_beta = len(s.SHIM_BETA)
            shim_mu = len(s.SHIM_MU)
            if shim_r1 \
                    == shim_r2 \
                    == shim_theta1 \
                    == shim_theta2 \
                    == shim_lambda \
                    == shim_gamma \
                    == shim_alpha \
                    == shim_beta \
                    == shim_mu:
                for i, j, k, l in zip(s.SHIM_R1, s.SHIM_R2, s.SHIM_THETA1, s.SHIM_LAMBDA):
                    command.append(f"""
                        {i:.12e} {j:.12e} {k:.12e} {l:.12e}
                        """)

                for i, j, k, l in zip(s.GAMMA, s.ALPHA, s.MU, s.BETA):
                    command.append(f"""
                                       {i:.12e} {j:.12e} {k:.12e} {l:.12e}
                                       """)
            else:
                raise ZgoubidoException('Error : The shim parameters lists must have the same lenghts')

        c = f"""
                {s.IORDRE}
                {s.XPAS:.12e}
                """
        command.append(c)

        if s.KPOS not in (1, 2):
            raise ZgoubidoException("KPOS must be equal to 1 or 2.")

        if s.KPOS == 2:
            if s.RE == 0:
                s.RE = s.RM
            if s.RS == 0:
                s.RS = s.RM
            c = f"""
                    {s.KPOS}
                    {s.RE:.12e} {s.TE:.12e} {s.RS:.12e} {s.TS:.12e}
                    """
            command.append(c)
        elif s.KPOS == 1:
            c = f"""
                    {s.KPOS}
                    {s.DP:.12e}
                    """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Bend(CartesianMagnet):
    """Bending magnet, Cartesian frame.
    """
    PARAMETERS = {
        'IL': (2, "Print field and coordinates along trajectories"),
        'XL': (0.0 * ureg.centimeter, "Magnet length (straight reference frame)"),
        'SK': (0.0 * ureg.radian, "Skew angle"),
        'B1': (0.0 * ureg.kilogauss, "Dipole field"),
        'X_E': (0.0 * ureg.centimeter, "Integration zone extension (entrance face)"),
        'LAM_E': (0.0 * ureg.centimeter, "Fringe field extension (entrance face)"),
        'W_E': (0.0 * ureg.radian, "Wedge angle (entrance face)"),
        'C0_E': 0.0,
        'C1_E': 1.0,
        'C2_E': 0.0,
        'C3_E': 0.0,
        'C4_E': 0.0,
        'C5_E': 0.0,
        'X_S': (0.0 * ureg.centimeter, "Integration zone extension (exit face)"),
        'LAM_S': (0.0 * ureg.centimeter, "Fringe field extension (exit face)"),
        'W_S': (0.0 * ureg.radian, "Wedge angle (exit face)"),
        'C0_S': 0.0,
        'C1_S': 1.0,
        'C2_S': 0.0,
        'C3_S': 0.0,
        'C4_S': 0.0,
        'C5_S': 0.0,
        'XPAS': (1.0 * ureg.millimeter, "Integration step"),
        'KPOS': (2, "Alignment parameter"),
        'XCE': 0.0 * ureg.centimeter,
        'YCE': 0.0 * ureg.centimeter,
        'ALE': 0.0 * ureg.radian,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {int(s.IL):d}
        {s.XL.to('cm').magnitude:.12e} {s.SK.to('radian').magnitude:.12e} {_kilogauss(s.B1):.12e}
        {s.X_E.to('cm').magnitude:.12e} {s.LAM_E.to('cm').magnitude:.12e} {s.W_E.to('radian').magnitude:.12e}
        6 {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
        {s.X_S.to('cm').magnitude:.12e} {s.LAM_S.to('cm').magnitude:.12e} {s.W_S.to('radian').magnitude:.12e}
        6 {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
        {_cm(s.XPAS):.12e}
        {int(s.KPOS):d} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {_radian(s.ALE):.12e}
        """


class Decapole(CartesianMagnet):
    """Decapole magnet."""
    PARAMETERS = {
        'IL': 2,
        'XL': 0 * ureg.centimeter,
        'R0': 1.0 * ureg.centimeter,
        'B0': 0 * ureg.kilogauss,
        'XE': 0 * ureg.centimeter,
        'LAM_E': 0 * ureg.centimeter,
        'C0': 0,
        'C1': 1,
        'C2': 0,
        'C3': 0,
        'C4': 0,
        'C5': 0,
        'XS': 0 * ureg.centimeter,
        'LAM_S': 0 * ureg.centimeter,
        'XPAS': 0.1 * ureg.centimeter,
        'KPOS': 1,
        'XCE': 0 * ureg.centimeter,
        'YCE': 0 * ureg.centimeter,
        'ALE': 0 * ureg.radian,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {int(s.IL):d}
        {_cm(s.XL):.12e} {_cm(s.R0):.12e} {_kilogauss(s.B0):.12e}
        {_cm(s.XE):.12e} {_cm(s.LAM_E):.12e}
        6 {s.C0:.12e} {s.C1:.12e} {s.C2:.12e} {s.C3:.12e} {s.C4:.12e} {s.C5:.12e}
        {_cm(s.XS):.12e} {_cm(s.LAM_S):.12e}
        6 {s.C0:.12e} {s.C1:.12e} {s.C2:.12e} {s.C3:.12e} {s.C4:.12e} {s.C5:.12e}
        {_cm(s.XPAS)}
        {int(s.KPOS):d} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {_radian(s.ALE):.12e}
        """


class Dipole(PolarMagnet):
    """Dipole magnet, polar frame."""
    PARAMETERS = {
        'IL': (2, 'Print field and coordinates along trajectories', 1),
        'AT': (0 * ureg.degree, 'Total angular extent of the dipole', 2),
        'RM': (0 * ureg.centimeter, 'Reference radius', 3),
        'ACENT': (0 * ureg.degree, 'Azimuth for positioning of EFBs', 4),
        'B0': (0 * ureg.kilogauss, 'Reference field', 5),
        'N': (0, 'Field index (radial quadrupolar)', 6),
        'B': (0, 'Field index (radial sextupolar)', 7),
        'G': (0, 'Field index (radial octupolar)', 8),
        'LAM_E': (0 * ureg.centimeter, 'Entrance fringe field extent (normally ≃ gap size)', 9),
        'C0_E': (0, 'Fringe field coefficient C0', 12),
        'C1_E': (1, 'Fringe field coefficient C1', 13),
        'C2_E': (0, 'Fringe field coefficient C2', 14),
        'C3_E': (0, 'Fringe field coefficient C3', 15),
        'C4_E': (0, 'Fringe field coefficient C4', 16),
        'C5_E': (0, 'Fringe field coefficient C5', 17),
        'SHIFT_E': (0 * ureg.centimeter, 'Shift of the EFB'),
        'OMEGA_E': (0 * ureg.degree, ''),
        'THETA_E': 0,
        'R1_E': (1e9 * ureg.centimeter, 'Entrance EFB radius'),
        'U1_E': (1e9 * ureg.centimeter, 'Entrance EFB linear extent'),
        'U2_E': (1e9 * ureg.centimeter, 'Entrance EFB linear extent'),
        'R2_E': (1e9 * ureg.centimeter, 'Entrance EFB radius'),
        'LAM_S': (0 * ureg.centimeter, 'Exit fringe field extent (normally ≃ gap size)'),
        'C0_S': (0, 'Fringe field coefficient C0'),
        'C1_S': (1, 'Fringe field coefficient C1'),
        'C2_S': (0, 'Fringe field coefficient C2'),
        'C3_S': (0, 'Fringe field coefficient C3'),
        'C4_S': (0, 'Fringe field coefficient C4'),
        'C5_S': (0, 'Fringe field coefficient C5'),
        'SHIFT_S': (0 * ureg.centimeter, 'Shift of the EFB'),
        'OMEGA_S': (0 * ureg.degree, ''),
        'THETA_S': 0,
        'R1_S': (1e9 * ureg.centimeter, 'Exit EFB radius'),
        'U1_S': (1e9 * ureg.centimeter, 'Exit EFB linear extent'),
        'U2_S': (1e9 * ureg.centimeter, 'Exit EFB linear extent'),
        'R2_S': (1e9 * ureg.centimeter, 'Exit EFB radius'),
        'LAM_L': (0 * ureg.centimeter, 'Lateral fringe field extent (normally ≃ gap size)'),
        'XI_L': (0.0, 'Flag to activate/deactivate the lateral EFB (0 to deactivate)'),
        'C0_L': (0, 'Fringe field coefficient C0'),
        'C1_L': (1, 'Fringe field coefficient C1'),
        'C2_L': (0, 'Fringe field coefficient C2'),
        'C3_L': (0, 'Fringe field coefficient C3'),
        'C4_L': (0, 'Fringe field coefficient C4'),
        'C5_L': (0, 'Fringe field coefficient C5'),
        'SHIFT_L': (0 * ureg.centimeter, 'Shift of the EFB'),
        'OMEGA_L': (0 * ureg.degree, ''),
        'THETA_L': 0,
        'R1_L': (1e9 * ureg.centimeter, 'Lateral EFB radius'),
        'U1_L': (1e9 * ureg.centimeter, 'Lateral EFB linear extent'),
        'U2_L': (1e9 * ureg.centimeter, 'Lateral EFB linear extent'),
        'R2_L': (1e9 * ureg.centimeter, 'Lateral EFB radius'),
        'RM3': (1e9 * ureg.centimeter, 'Reference radius of the lateral EFB'),
        'IORDRE': 2,
        'RESOL': 10,
        'XPAS': (1 * ureg.millimeter, 'Integration step'),
        'KPOS': 1,
        'RE': 0 * ureg.millimeter,
        'TE': 0 * ureg.radian,
        'RS': 0 * ureg.millimeter,
        'TS': 0 * ureg.radian,
        'DP': 1.0,
    }

    def __str__(s):
        command = []
        c = f"""
        {super().__str__().rstrip()}
        {s.IL}
        {s.AT.to('degree').magnitude:.12e} {s.RM.to('centimeter').magnitude:.12e}
        {s.ACENT.to('degree').magnitude:.12e} {s.B0.to('kilogauss').magnitude:.12e} {s.N:.12e} {s.B:.12e} {s.G:.12e}
        {s.LAM_E.to('centimeter').magnitude:.12e} 0.0
        6 {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e} {s.SHIFT_E.to('centimeter').magnitude:.12e}
        {s.OMEGA_E.to('degree').magnitude:.12e} {s.THETA_E:.12e} {s.R1_E.to('centimeter').magnitude:.12e} {s.U1_E.to('centimeter').magnitude:.12e} {s.U2_E.to('centimeter').magnitude:.12e} {s.R2_E.to('centimeter').magnitude:.12e}
        {s.LAM_S.to('centimeter').magnitude:.12e} 0.0
        6 {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e} {s.SHIFT_S.to('centimeter').magnitude:.12e}
        {s.OMEGA_S.to('degree').magnitude:.12e} {s.THETA_S:.12e} {s.R1_S.to('centimeter').magnitude:.12e} {s.U1_S.to('centimeter').magnitude:.12e} {s.U2_S.to('centimeter').magnitude:.12e} {s.R2_S.to('centimeter').magnitude:.12e}
        {s.LAM_L.to('centimeter').magnitude:.12e} {s.XI_L}
        6 {s.C0_L:.12e} {s.C1_L:.12e} {s.C2_L:.12e} {s.C3_L:.12e} {s.C4_L:.12e} {s.C5_L:.12e} {s.SHIFT_L.to('centimeter').magnitude:.12e}
        {s.OMEGA_L.to('degree').magnitude:.12e} {s.THETA_L:.12e} {s.R1_L.to('centimeter').magnitude:.12e} {s.U1_L.to('centimeter').magnitude:.12e} {s.U2_L.to('centimeter').magnitude:.12e} {s.R2_L.to('centimeter').magnitude:.12e} {s.RM3.to('centimeter').magnitude:.12e}
        {s.IORDRE} {s.RESOL:.12e}
        {s.XPAS.to('centimeter').magnitude}"""
        command.append(c)

        if s.KPOS not in (1, 2):
            raise ZgoubidoException("KPOS must be equal to 1 or 2.")

        if s.KPOS == 2:
            if s.RE == 0:
                s.RE = s.RM
            if s.RS == 0:
                s.RS = s.RM
            c = f"""
        {s.KPOS}
        {s.RE.to('centimeter').magnitude:.12e} {s.TE.to('radian').magnitude:.12e} {s.RS.to('centimeter').magnitude:.12e} {s.TS.to('radian').magnitude:.12e}
                """
            command.append(c)
        elif s.KPOS == 1:
            c = f"""
        {s.KPOS}
        {s.DP:.12e}
                """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class DipoleM(Magnet):
    KEYWORD = 'DIPOLE-M'

    PARAMETERS = {
        'NFACE': 2,
        'IC': 0,  # 1, 2: print field map
        'IL': 0,  # 1, 2: print field and coordinates on trajectores
        'IAMAX': 0,
        'IRMAX': 0,
        'B0': 0 * ureg.kilogauss,
        'N': 0,
        'B': 0,
        'G': 0,
        'AT': 0,
        'ACENT': 0,
        'RM': 0,
        'RMIN': 0,
        'RMAX': 0,
        'LAM_E': 0,
        'XI_E': 0,
        'NCE': 0,
        'C0_E': 0,
        'C1_E': 0,
        'C2_E': 0,
        'C3_E': 0,
        'C4_E': 0,
        'C5_E': 0,
        'SHIFT_E': 0,
        'OMEGA_E': 0,
        'THETA_E': 0,
        'R1_E': 1e9,
        'U1_E': -1e9,
        'U2_E': 1e9,
        'R2_E': 1e9,
        'LAM_S': 0,
        'XI_S': 0,
        'NCS': 0,
        'C0_S': 0,
        'C1_S': 0,
        'C2_S': 0,
        'C3_S': 0,
        'C4_S': 0,
        'C5_S': 0,
        'SHIFT_S': 0,
        'OMEGA_S': 0,
        'THETA_S': 0,
        'R1_S': 1e9,
        'U1_S': -1e9,
        'U2_S': 1e9,
        'R2_S': 1e9,
        'LAM_L': 0,
        'XI_L': 0,
        'NCL': 0,
        'C0_L': 0,
        'C1_L': 0,
        'C2_L': 0,
        'C3_L': 0,
        'C4_L': 0,
        'C5_L': 0,
        'SHIFT_L': 0,
        'OMEGA_L': 0,
        'THETA_L': 0,
        'R1_L': 1e9,
        'U1_L': -1e9,
        'U2_L': 1e9,
        'R2_L': 1e9,
        'RM3': 0,
        'NBS': 0,
        'R0': 0,
        'DELTAB': 0,
        'THETA_0': 0,
        'IORDRE': 4,
        'XPAS': 0.1,
        'KPOS': 2,
        'RE': 0,
        'TE': 0,
        'RS': 0,
        'TS': 0,
        'DP': 0,
        'SHIM_R1': [],
        'SHIM_R2': [],
        'SHIM_THETA1': [],
        'SHIM_THETA2': [],
        'SHIM_LAMBDA': [],
        'SHIM_GAMMA': [],
        'SHIM_ALPHA': [],
        'SHIM_BETA': [],
        'SHIM_MU': [],
    }

    def __str__(s):
        command = []
        if s.NFACE not in (2, 3):
            raise ZgoubidoException(f"Error : Zgoubido does not support NFACE = {s.NFACE}")

        c = f"""
            {super().__str__().rstrip()}
            {s.NFACE} {s.IC} {s.IL}
            {s.IAMAX} {s.IRMAX}
            {s.B0.to('kilogauss').magnitude:.12e} {s.N:.12e} {s.B:.12e} {s.G:.12e}
            {s.AT:.12e} {s.ACENT:.12e} {s.RM:.12e} {s.RMIN:.12e} {s.RMAX:.12e}
            {s.LAM_E:.12e} {s.XI_E:.12e}
            {s.NCE} {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e} {s.SHIFT_E:.12e}
            {s.OMEGA_E:.12e} {s.THETA_E:.12e} {s.R1_E:.12e} {s.U1_E:.12e} {s.U2_E:.12e} {s.R2_E:.12e}
            {s.LAM_S:.12e} {s.XI_S:.12e}
            {s.NCS} {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e} {s.SHIFT_S:.12e}
            {s.OMEGA_S:.12e} {s.THETA_S:.12e} {s.R1_S:.12e} {s.U1_S:.12e} {s.U2_S:.12e} {s.R2_S:.12e}
        """
        command.append(c)

        if s.NFACE == 3:
            c = f"""
                {s.LAM_L:.12e} {s.XI_L:.12e}
                {s.NCL} {s.C0_L:.12e} {s.C1_L:.12e} {s.C2_L:.12e} {s.C3_L:.12e} {s.C4_L:.12e} {s.C5_L:.12e} {s.SHIFT_L:.12e}
                {s.OMEGA_L:.12e} {s.THETA_L:.12e} {s.R1_L:.12e} {s.U1_L:.12e} {s.U2_L:.12e} {s.R2_L:.12e} {s.RM3:.12e}
            """
            command.append(c)

        if s.NBS == 0:
            command.append(f"""
            {s.NBS}
            """)
        elif s.NBS == -2:
            c = f"""
                {s.NBS}
                {s.R0:.12e} {s.DELTAB:.12e}
                """
            command.append(c)
        elif s.NBS == -1:
            c = f"""
                {s.NBS}
                {s.THETA_0:.12e} {s.DELTAB:.12e}
                """
            command.append(c)
        elif s.NBS >= 1:
            command.append(f"""
            {s.NBS}""")

            shim_r1 = len(s.SHIM_R1)
            shim_r2 = len(s.SHIM_R2)
            shim_theta1 = len(s.SHIM_THETA1)
            shim_theta2 = len(s.SHIM_THETA2)
            shim_lambda = len(s.SHIM_LAMBDA)
            shim_gamma = len(s.SHIM_GAMMA)
            shim_alpha = len(s.SHIM_ALPHA)
            shim_beta = len(s.SHIM_BETA)
            shim_mu = len(s.SHIM_MU)
            if shim_r1\
                    == shim_r2 \
                    == shim_theta1 \
                    == shim_theta2 \
                    == shim_lambda \
                    == shim_gamma \
                    == shim_alpha \
                    == shim_beta \
                    == shim_mu:
                for i, j, k, l in zip(s.SHIM_R1, s.SHIM_R2, s.SHIM_THETA1, s.SHIM_LAMBDA):
                    command.append(f"""
                    {i:.12e} {j:.12e} {k:.12e} {l:.12e}
                    """)

                for i, j, k, l in zip(s.GAMMA, s.ALPHA, s.MU, s.BETA):
                    command.append(f"""
                                   {i:.12e} {j:.12e} {k:.12e} {l:.12e}
                                   """)
            else:
                raise ZgoubidoException('Error : The shim parameters lists must have the same lenghts')

        c = f"""
            {s.IORDRE}
            {s.XPAS:.12e}
            """
        command.append(c)

        if s.KPOS not in (1, 2):
            raise ZgoubidoException("KPOS must be equal to 1 or 2.")

        if s.KPOS == 2:
            if s.RE == 0:
                s.RE = s.RM
            if s.RS == 0:
                s.RS = s.RM
            c = f"""
                {s.KPOS}
                {s.RE:.12e} {s.TE:.12e} {s.RS:.12e} {s.TS:.12e}
                """
            command.append(c)
        elif s.KPOS == 1:
            c = f"""
                {s.KPOS}
                {s.DP:.12e}
                """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Dipoles(Magnet):
    """Dipole magnet N-tuple, polar frame."""
    PARAMETERS = {
        'IL': 2,
        'N': 1,
        'AT': 0,
        'RM': 0,

        'ACN': [0, ],
        'DELTA_RM': [0, ],
        'B0': [0, ],
        'IND': [0, ],
        'BI': [[0, ], ],
        'G0_E': [0, ],
        'K_E': [0, ],
        'NCE': [0, ],
        'C0_E': [0, ],
        'C1_E': [0, ],
        'C2_E': [0, ],
        'C3_E': [0, ],
        'C4_E': [0, ],
        'C5_E': [0, ],
        'SHIFT_E': [0, ],
        'OMEGA_E': [0, ],
        'THETA_E': [0, ],
        'R1_E': [1e9, ],
        'U1_E': [-1e9, ],
        'U2_E': [1e9, ],
        'R2_E': [1e9, ],
        'G0_S': [0, ],
        'K_S': [0, ],
        'NCS': [0, ],
        'C0_S': [0, ],
        'C1_S': [0, ],
        'C2_S': [0, ],
        'C3_S': [0, ],
        'C4_S': [0, ],
        'C5_S': [0, ],
        'SHIFT_S': [0, ],
        'OMEGA_S': [0, ],
        'THETA_S': [0, ],
        'R1_S': [1e9, ],
        'U1_S': [-1e9, ],
        'U2_S': [1e9, ],
        'R2_S': [1e9, ],
        'G0_L': [0, ],
        'K_L': [0, ],
        'NCL': [0, ],
        'C0_L': [0, ],
        'C1_L': [0, ],
        'C2_L': [0, ],
        'C3_L': [0, ],
        'C4_L': [0, ],
        'C5_L': [0, ],
        'SHIFT_L': [0, ],
        'OMEGA_L': [0, ],
        'THETA_L': [0, ],
        'R1_L': [1e9, ],
        'U1_L': [-1e9, ],
        'U2_L': [1e9, ],
        'R2_L': [1e9, ],
        'R3': [1e9, ],

        'KIRD': 0,
        'n': 0,
        'Resol': 2,
        'XPAS': 0.1,
        'KPOS': 2,
        'RE': 0,
        'TE': 0,
        'RS': 0,
        'TS': 0,
        'DP': 0,
    }

    def __str__(s):
        command = []
        c = f"""
        {super().__str__().rstrip()}
        {s.IL}
        {s.N} {s.AT:.12e} {s.RM:.12e}
        """
        command.append(c)

        for i in range(0, int(s.N)):
            c = f"{s.ACN[i]:.12e} {s.DELTA_RM[i]:.12e} {s.B0[i]:.12e} {s.IND[i]} "
            for bi in s.BI[i]:
                c += f"{bi} "
            command.append(c)

            c = f"""
                {s.G0_E[i]:.12e} {s.K_E[i]:.12e}
                {s.NCE[i]} {s.C0_E[i]:.12e} {s.C1_E[i]:.12e} {s.C2_E[i]:.12e} {s.C3_E[i]:.12e} {s.C4_E[i]:.12e} {s.C5_E[i]:.12e} {s.SHIFT_E[i]:.12e}
                {s.OMEGA_E[i]:.12e} {s.THETA_E[i]:.12e} {s.R1_E[i]:.12e} {s.U1_E[i]:.12e} {s.U2_E[i]:.12e} {s.R2_E[i]:.12e}
                {s.G0_S[i]:.12e} {s.K_S[i]:.12e}
                {s.NCS[i]} {s.C0_S[i]:.12e} {s.C1_S[i]:.12e} {s.C2_S[i]:.12e} {s.C3_S[i]:.12e} {s.C4_S[i]:.12e} {s.C5_S[i]:.12e} {s.SHIFT_S[i]:.12e}
                {s.OMEGA_S[i]:.12e} {s.THETA_S[i]:.12e} {s.R1_S[i]:.12e} {s.U1_S[i]:.12e} {s.U2_S[i]:.12e} {s.R2_S[i]:.12e}
                {s.G0_L[i]:.12e} {s.K_L[i]:.12e}
                {s.NCL[i]} {s.C0_L[i]:.12e} {s.C1_L[i]:.12e} {s.C2_L[i]:.12e} {s.C3_L[i]:.12e} {s.C4_L[i]:.12e} {s.C5_L[i]:.12e} {s.SHIFT_L[i]:.12e}
                {s.OMEGA_L[i]:.12e} {s.THETA_L[i]:.12e} {s.R1_L[i]:.12e} {s.U1_L[i]:.12e} {s.U2_L[i]:.12e} {s.R2_L[i]:.12e} {s.R3[i]:.12e}
                """
            command.append(c)

        if s.KIRD != 0 and s.KIRD != 2 and s.KIRD != 4 and s.KIRD != 25:
            raise ZgoubidoException("KIRD must be equal to 0,2,4 or 25")
        if (s.KIRD == 0 and s.n !=2) and (s.KIRD == 0 and s.n !=1):
            raise ZgoubidoException("n must be equal to 0 or 1 when KIRD = 0")
        if (s.KIRD == 0 and s.Resol !=2) and (s.KIRD == 0 and s.Resol !=4):
            raise ZgoubidoException("Resol must be equal to 2 or 4 when KIRD = 0")

        if s.KIRD == 0:
            command.append(f"""
            {s.KIRD}.{s.n} {s.Resol:.12e}
            """)
        else:
            command.append(f"""
            {s.KIRD} {s.Resol:.12e}
            """)

        command.append(f"""{s.XPAS:.12e}""")

        if int(s.KPOS) not in (1, 2):
            raise ZgoubidoException("KPOS must be equal to 1 or 2.")

        if s.KPOS == 2:
            if s.RE == 0:
                s.RE = s.RM
            if s.RS == 0:
                s.RS = s.RM
            c = f"""
                {s.KPOS}
                {s.RE:.12e} {s.TE:.12e} {s.RS:.12e} {s.TS:.12e}
                """
            command.append(c)
        elif int(s.KPOS) == 1:
            c = f"""
                {s.KPOS}
                {s.DP:.12e}
                """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Dodecapole(Command):
    """Dodecapole magnet."""
    KEYWORD = 'DODECAPO'

    PARAMETERS = {
        'IL': 2,
        'XL': 0 * ureg.centimeter,
        'R0': 1.0 * ureg.centimeter,
        'B0': 0 * ureg.kilogauss,
        'XE': 0 * ureg.centimeter,
        'LAM_E': 0 * ureg.centimeter,
        'C0': 0,
        'C1': 1,
        'C2': 0,
        'C3': 0,
        'C4': 0,
        'C5': 0,
        'XS': 0 * ureg.centimeter,
        'LAM_S': 0 * ureg.centimeter,
        'XPAS': 0.1 * ureg.centimeter,
        'KPOS': 1,
        'XCE': 0 * ureg.centimeter,
        'YCE': 0 * ureg.centimeter,
        'ALE': 0 * ureg.radian,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IL}
        {_cm(s.XL):.12e} {_cm(s.R0):.12e} {s.B0.to('kilogauss').magnitude:.12e}
        {s.XE.to('centimeter').magnitude:.12e} {s.LAM_E.to('centimeter').magnitude:.12e}
        6 {s.C0:.12e} {s.C1:.12e} {s.C2:.12e} {s.C3:.12e} {s.C4:.12e} {s.C5:.12e}
        {s.XS.to('centimeter').magnitude:.12e} {s.LAM_S.to('centimeter').magnitude:.12e}
        6 {s.C0:.12e} {s.C1:.12e} {s.C2:.12e} {s.C3:.12e} {s.C4:.12e} {s.C5:.12e}
        {_cm(s.XPAS)}
        {s.KPOS} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {_radian(s.ALE):.12e}
        """


class Drift(CartesianMagnet):
    """
    Field free drift space.

    >>> Drift()

    """
    PARAMETERS = {
        'XL': 0 * ureg.centimeter,
    }
    COLOR = 'yellow'

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {_cm(s.XL):.12e}
        """

    def plot(self, artist=None):
        if artist is None or not artist.with_drifts:
            return
        super().plot(artist)


class Emma(Command):
    """2-D Cartesian or cylindrical mesh field map for EMMA FFAG."""
    KEYWORD = 'EMMA'


class FFAG(Command):
    """FFAG magnet, N-tuple."""
    KEYWORD = 'FFAG'

    PARAMETERS = {
            'IL': 2,
            'N': 1,
            'AT': 0,
            'RM': 0,

            'ACN': [0, ],
            'DELTA_RM': [0, ],
            'BZ0': [0, ],
            'K': [0, ],
            'G0_E': [0, ],
            'K_E': [0, ],
            'NCE': [0, ],
            'C0_E': [0, ],
            'C1_E': [0, ],
            'C2_E': [0, ],
            'C3_E': [0, ],
            'C4_E': [0, ],
            'C5_E': [0, ],
            'SHIFT_E': [0, ],
            'OMEGA_E': [0, ],
            'THETA_E': [0, ],
            'R1_E': [1e9, ],
            'U1_E': [-1e9, ],
            'U2_E': [1e9, ],
            'R2_E': [1e9, ],
            'G0_S': [0, ],
            'K_S': [0, ],
            'NCS': [0, ],
            'C0_S': [0, ],
            'C1_S': [0, ],
            'C2_S': [0, ],
            'C3_S': [0, ],
            'C4_S': [0, ],
            'C5_S': [0, ],
            'SHIFT_S': [0, ],
            'OMEGA_S': [0, ],
            'THETA_S': [0, ],
            'R1_S': [1e9, ],
            'U1_S': [-1e9, ],
            'U2_S': [1e9, ],
            'R2_S': [1e9, ],
            'G0_L': [0, ],
            'K_L': [0, ],
            'NCL': [0, ],
            'C0_L': [0, ],
            'C1_L': [0, ],
            'C2_L': [0, ],
            'C3_L': [0, ],
            'C4_L': [0, ],
            'C5_L': [0, ],
            'SHIFT_L': [0, ],
            'OMEGA_L': [0, ],
            'THETA_L': [0, ],
            'R1_L': [1e9, ],
            'U1_L': [-1e9, ],
            'U2_L': [1e9, ],
            'R2_L': [1e9, ],

            'KIRD': 0,
            'Resol': 2,
            'XPAS': 0.1,
            'KPOS': 2,
            'RE': 0,
            'TE': 0,
            'RS': 0,
            'TS': 0,
            'DP': 0,
    }

    def __str__(s):
        command = []
        c = f"""
        {super().__str__().rstrip()}
        {s.IL}
        {s.N} {s.AT:.12e} {s.RM:.12e}
        """
        command.append(c)

        for i in range (0, s.N):
            c = f"""
            {s.ACN[i]:.12e} {s.DELTA_RM[i]:.12e} {s.BZ0[i]:.12e} {s.K[i]:.12e}
            {s.G0_E[i]:.12e} {s.K_E[i]:.12e}
            {s.NCE[i]} {s.C0_E[i]:.12e} {s.C1_E[i]:.12e} {s.C2_E[i]:.12e} {s.C3_E[i]:.12e} {s.C4_E[i]:.12e} {s.C5_E[i]:.12e} {s.SHIFT_E[i]:.12e}
            {s.OMEGA_E[i]:.12e} {s.THETA_E[i]:.12e} {s.R1_E[i]:.12e} {s.U1_E[i]:.12e} {s.U2_E[i]:.12e} {s.R2_E[i]:.12e}
            {s.G0_S[i]:.12e} {s.K_S[i]:.12e}
            {s.NCS[i]} {s.C0_S[i]:.12e} {s.C1_S[i]:.12e} {s.C2_S[i]:.12e} {s.C3_S[i]:.12e} {s.C4_S[i]:.12e} {s.C5_S[i]:.12e} {s.SHIFT_S[i]:.12e}
            {s.OMEGA_S[i]:.12e} {s.THETA_S[i]:.12e} {s.R1_S[i]:.12e} {s.U1_S[i]:.12e} {s.U2_S[i]:.12e} {s.R2_S[i]:.12e}
            {s.G0_L[i]:.12e} {s.K_L[i]:.12e}
            {s.NCL[i]} {s.C0_L[i]:.12e} {s.C1_L[i]:.12e} {s.C2_L[i]:.12e} {s.C3_L[i]:.12e} {s.C4_L[i]:.12e} {s.C5_L[i]:.12e} {s.SHIFT_L[i]:.12e}
            {s.OMEGA_L[i]:.12e} {s.THETA_L[i]:.12e} {s.R1_L[i]:.12e} {s.U1_L[i]:.12e} {s.U2_L[i]:.12e} {s.R2_L[i]:.12e}
            """
            command.append(c)

        if s.KIRD != 0 and s.KIRD != 2 and s.KIRD != 4 and s.KIRD != 25:
            raise ZgoubidoException("KIRD must be equal to 0,2,4 or 25")
        if (s.KIRD == 0 and s.Resol !=2) and (s.KIRD == 0 and s.Resol !=4):
            raise ZgoubidoException("Resol must be equal to 2 or 4 when KIRD = 0")

        command.append(f"""
        {s.KIRD} {s.Resol:.12e} 
        {s.XPAS:.12e}
        """)

        if s.KPOS not in (1, 2):
            raise ZgoubidoException("KPOS must be equal to 1 or 2.")

        if s.KPOS == 2:
            if s.RE == 0:
                s.RE = s.RM
            if s.RS == 0:
                s.RS = s.RM
            c = f"""
                {s.KPOS}
                {s.RE:.12e} {s.TE:.12e} {s.RS:.12e} {s.TS:.12e}
                """
            command.append(c)
        elif s.KPOS == 1:
            c = f"""
                {s.KPOS}
                {s.DP:.12e}
                """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class FFAGSpirale(Magnet):
    """Spiral FFAG magnet, N-tuple."""
    KEYWORD = 'FFAG-SPI'

    PARAMETERS = {
        'IL': 2,
        'N': 1,
        'AT': 0,
        'RM': 0,

        'ACN': [0, ],
        'DELTA_RM': [0, ],
        'BZ0': [0, ],
        'K': [0, ],
        'G0_E': [0, ],
        'K_E': [0, ],
        'NCE': [0, ],
        'C0_E': [0, ],
        'C1_E': [0, ],
        'C2_E': [0, ],
        'C3_E': [0, ],
        'C4_E': [0, ],
        'C5_E': [0, ],
        'SHIFT_E': [0, ],
        'OMEGA_E': [0, ],
        'XI_E': [0, ],
        'DUMMY1_E': 0,
        'DUMMY2_E': 0,
        'DUMMY3_E': 0,
        'DUMMY4_E': 0,
        'G0_S': [0, ],
        'K_S': [0, ],
        'NCS': [0, ],
        'C0_S': [0, ],
        'C1_S': [0, ],
        'C2_S': [0, ],
        'C3_S': [0, ],
        'C4_S': [0, ],
        'C5_S': [0, ],
        'SHIFT_S': [0, ],
        'OMEGA_S': [0, ],
        'XI_S': [0, ],
        'DUMMY1_S': 0,
        'DUMMY2_S': 0,
        'DUMMY3_S': 0,
        'DUMMY4_S': 0,
        'G0_L': [0, ],
        'K_L': [0, ],
        'NCL': [0, ],
        'C0_L': [0, ],
        'C1_L': [0, ],
        'C2_L': [0, ],
        'C3_L': [0, ],
        'C4_L': [0, ],
        'C5_L': [0, ],
        'SHIFT_L': [0, ],
        'OMEGA_L': [0, ],
        'THETA_L': [0, ],
        'R1_L': [1e9, ],
        'U1_L': [-1e9, ],
        'U2_L': [1e9, ],
        'R2_L': [1e9, ],

        'KIRD': 0,
        'Resol': 2,
        'XPAS': 0.1,
        'KPOS': 2,
        'RE': 0,
        'TE': 0,
        'RS': 0,
        'TS': 0,
        'DP': 0,
    }

    def __str__(s):
        command = []
        c = f"""
            {super().__str__().rstrip()}
            {s.IL}
            {s.N} {s.AT:.12e} {s.RM:.12e}
            """
        command.append(c)

        for i in range(0, s.N):
            c = f"""
                {s.ACN[i]:.12e} {s.DELTA_RM[i]:.12e} {s.BZ0[i]:.12e} {s.K[i]:.12e}
                {s.G0_E[i]:.12e} {s.K_E[i]:.12e}
                {s.NCE[i]} {s.C0_E[i]:.12e} {s.C1_E[i]:.12e} {s.C2_E[i]:.12e} {s.C3_E[i]:.12e} {s.C4_E[i]:.12e} {s.C5_E[i]:.12e} {s.SHIFT_E[i]:.12e}
                {s.OMEGA_E[i]:.12e} {s.XI_E[i]:.12e} {s.DUMMY1_E:.12e} {s.DUMMY2_E:.12e} {s.DUMMY3_E:.12e} {s.DUMMY4_E:.12e}
                {s.G0_S[i]:.12e} {s.K_S[i]:.12e}
                {s.NCS[i]} {s.C0_S[i]:.12e} {s.C1_S[i]:.12e} {s.C2_S[i]:.12e} {s.C3_S[i]:.12e} {s.C4_S[i]:.12e} {s.C5_S[i]:.12e} {s.SHIFT_S[i]:.12e}
                {s.OMEGA_S[i]:.12e} {s.XI_S[i]:.12e} {s.DUMMY1_S:.12e} {s.DUMMY2_S:.12e} {s.DUMMY3_S:.12e} {s.DUMMY4_S:.12e}
                {s.G0_L[i]:.12e} {s.K_L[i]:.12e}
                {s.NCL[i]} {s.C0_L[i]:.12e} {s.C1_L[i]:.12e} {s.C2_L[i]:.12e} {s.C3_L[i]:.12e} {s.C4_L[i]:.12e} {s.C5_L[i]:.12e} {s.SHIFT_L[i]:.12e}
                {s.OMEGA_L[i]:.12e} {s.THETA_L[i]:.12e} {s.R1_L[i]:.12e} {s.U1_L[i]:.12e} {s.U2_L[i]:.12e} {s.R2_L[i]:.12e}
                """
            command.append(c)

        if s.KIRD != 0 and s.KIRD != 2 and s.KIRD != 4 and s.KIRD != 25:
            raise ZgoubidoException("KIRD must be equal to 0,2,4 or 25")
        if (s.KIRD == 0 and s.Resol != 2) and (s.KIRD == 0 and s.Resol != 4):
            raise ZgoubidoException("Resol must be equal to 2 or 4 when KIRD = 0")

        command.append(f"""
            {s.KIRD} {s.Resol:.12e} 
            {s.XPAS:.12e}
            """)

        if s.KPOS not in (1, 2):
            raise ZgoubidoException("KPOS must be equal to 1 or 2.")

        if s.KPOS == 2:
            if s.RE == 0:
                s.RE = s.RM
            if s.RS == 0:
                s.RS = s.RM
            c = f"""
                {s.KPOS}
                {s.RE:.12e} {s.TE:.12e} {s.RS:.12e} {s.TS:.12e}
                """
            command.append(c)
        elif s.KPOS == 1:
            c = f"""
                {s.KPOS}
                {s.DP:.12e}
                """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Multipole(Magnet):
    """Magnetic multipole."""
    KEYWORD = 'MULTIPOL'

    PARAMETERS = {
            'IL': 2,
            'XL': 0,
            'R0': 0,
            'B1': 0,
            'B2': 0,
            'B3': 0,
            'B4': 0,
            'B5': 0,
            'B6': 0,
            'B7': 0,
            'B8': 0,
            'B9': 0,
            'B10': 0,
            'X_E': 0,
            'LAM_E': 0,
            'E_2': 0,
            'E_3': 0,
            'E_4': 0,
            'E_5': 0,
            'E_6': 0,
            'E_7': 0,
            'E_8': 0,
            'E_9': 0,
            'E_10': 0,
            'NCE': 0,
            'C0_E': 0,
            'C1_E': 0,
            'C2_E': 0,
            'C3_E': 0,
            'C4_E': 0,
            'C5_E': 0,
            'X_S': 0,
            'LAM_S': 0,
            'S_2': 0,
            'S_3': 0,
            'S_4': 0,
            'S_5': 0,
            'S_6': 0,
            'S_7': 0,
            'S_8': 0,
            'S_9': 0,
            'S_10': 0,
            'NCS': 0,
            'C0_S': 0,
            'C1_S': 0,
            'C2_S': 0,
            'C3_S': 0,
            'C4_S': 0,
            'C5_S': 0,
            'R1': 0,
            'R2': 0,
            'R3': 0,
            'R4': 0,
            'R5': 0,
            'R6': 0,
            'R7': 0,
            'R8': 0,
            'R9': 0,
            'R10': 0,
            'XPAS': 0.1,
            'KPOS': 1,
            'XCE': 0,
            'YCE': 0,
            'ALE': 0,
    }

    def __str__(s):
        command = []
        c = f"""
            {super().__str__().rstrip()}
            {s.IL}
            {s.XL:.12e} {s.R0:.12e} {s.B1:.12e} {s.B2:.12e} {s.B3:.12e} {s.B4:.12e} {s.B5:.12e} {s.B6:.12e} {s.B7:.12e} {s.B8:.12e} {s.B9:.12e} {s.B10:.12e}
            {s.X_E:.12e} {s.LAM_E:.12e} {s.E_2:.12e} {s.E_3:.12e} {s.E_4:.12e} {s.E_5:.12e} {s.E_6:.12e} {s.E_7:.12e} {s.E_8:.12e} {s.E_9:.12e} {s.E_10:.12e}
            {s.NCE} {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
            {s.X_S:.12e} {s.LAM_S:.12e} {s.S_2:.12e} {s.S_3:.12e} {s.S_4:.12e} {s.S_5:.12e} {s.S_6:.12e} {s.S_7:.12e} {s.S_8:.12e} {s.S_9:.12e} {s.S_10:.12e}
            {s.NCS} {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
            {s.R1:.12e} {s.R2:.12e} {s.R3:.12e} {s.R4:.12e} {s.R5:.12e} {s.R6:.12e} {s.R7:.12e} {s.R8:.12e} {s.R9:.12e} {s.R10:.12e}
            {s.XPAS:.12e}  
            """
        command.append(c)

        if s.KPOS not in (1, 3):
            raise ZgoubidoException("KPOS must be equal to 1,2 or 3.")

        if s.KPOS == 1:
            c = f"""
            {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
            """
            command.append(c)
        elif s.KPOS == 2:
            c = f"""
            {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
            """
            command.append(c)
        elif s.KPOS == 3:
            if s.B1 == 0:
                raise ZgoubidoException("B1 must be non-zero")
            c = f"""
            {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
            """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Octupole(Magnet):
    """Octupole magnet."""
    KEYWORD = 'OCTUPOLE'

    PARAMETERS = {
            'IL': 2,
            'XL': 0,
            'R0': 0,
            'B0': 0,
            'X_E': 0,
            'LAM_E': 0,
            'NCE': 0,
            'C0_E': 0,
            'C1_E': 0,
            'C2_E': 0,
            'C3_E': 0,
            'C4_E': 0,
            'C5_E': 0,
            'X_S': 0,
            'LAM_S': 0,
            'NCS': 0,
            'C0_S': 0,
            'C1_S': 0,
            'C2_S': 0,
            'C3_S': 0,
            'C4_S': 0,
            'C5_S': 0,
            'XPAS': 0.1,
            'KPOS': 1,
            'XCE': 0,
            'YCE': 0,
            'ALE': 0,
    }

    def __str__(s):
        command = []
        c = f"""
            {super().__str__().rstrip()}
            {s.IL}
            {s.XL:.12e} {s.R0:.12e} {s.B0:.12e}
            {s.X_E:.12e} {s.LAM_E:.12e}
            {s.NCE} {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
            {s.X_S:.12e} {s.LAM_S:.12e}
            {s.NCS} {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
            {s.XPAS:.12e}  
            """
        command.append(c)

        if s.KPOS not in (1, 2):
            raise ZgoubidoException("KPOS must be equal to 1 or 2")

        if s.KPOS == 1:
            c = f"""
            {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
            """
            command.append(c)
        elif s.KPOS == 2:
            c = f"""
            {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
            """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class PS170(Magnet):
    """
    Simulation of a round shape dipole magnet.

    >>> PS170('PS170', IL=2, XL=2 * ureg.m, R0 = 1.5 * ureg.m, B0 = 1 * ureg.tesla)
    """

    PARAMETERS = {
        'IL': (2, 'print field and coordinates along trajectories'),
        'XL': (1 * ureg.m, 'Length of the element'),
        'R0': (1 * ureg.m, ', radius of the circular dipole'),
        'B0': (0 * ureg.tesla, 'field'),
        'XPAS': (1.0 * ureg.mm, 'Integration step'),
        'KPOS': (0, ),
        'XCE': (0 * ureg.cm, ''),
        'YCE': (0 * ureg.cm, ''),
        'ALE': (0 * ureg.degree, ''),
    }
    COLOR = 'red'

    def __str__(s) -> str:
        if s.KPOS not in (0, 1, 2):
            raise ZgoubidoException("KPOS must be in (0, 1, 2)")
        return f"""
        {super().__str__().rstrip()}
        {int(s.IL):d}
        {_cm(s.XL):.12e} {_cm(s.R0):.12e} {_kilogauss(s.B0):.12e}
        {_cm(s.XPAS):.12e}  
        {int(s.KPOS):d} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {_radian(s.ALE):.12e}
        """


class Quadisex(Magnet):
    """Sharp edge magnetic multipoles."""
    PARAMETERS = {
        'IL': 2,
        'XL': 0,
        'R0': 0,
        'B0': 0,
        'N': 0,
        'EB1': 0,
        'EB2': 0,
        'EG1': 0,
        'EG2': 0,
        'XPAS': 0.1,
        'KPOS': 1,
        'XCE': 0,
        'YCE': 0,
        'ALE': 0,
    }

    def __str__(s):
        command = []
        c = f"""
                {super().__str__().rstrip()}
                {s.IL}
                {s.XL:.12e} {s.R0:.12e} {s.B0:.12e}
                {s.N:.12e} {s.EB1:.12e} {s.EB2:.12e} {s.EG1:.12e} {s.EG2:.12e} 
                {s.XPAS:.12e}  
                """
        command.append(c)

        if s.KPOS not in (1, 2):
            raise ZgoubidoException("KPOS must be equal to 1 or 2")

        if s.KPOS == 1:
            c = f"""
                {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
                """
            command.append(c)
        elif s.KPOS == 2:
            c = f"""
                {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
                """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Quadrupole(CartesianMagnet):
    """Quadrupole magnet."""
    KEYWORD = 'QUADRUPO'
    PARAMETERS = {
        'IL': (2, 'Print field and coordinates along trajectories'),
        'XL': (0 * ureg.centimeter, 'Magnet length'),
        'R0': (1.0 * ureg.centimeter, 'Radius of the pole tips'),
        'B0': (0 * ureg.kilogauss, 'Field at pole tips'),
        'XE': (0 * ureg.centimeter, 'Entrance face integration zone for the fringe field'),
        'LAM_E': (0 * ureg.centimeter, 'Entrance face fringe field extent'),
        'C0_E': 0,
        'C1_E': 1,
        'C2_E': 0,
        'C3_E': 0,
        'C4_E': 0,
        'C5_E': 0,
        'XS': (0 * ureg.centimeter, 'Exit face integration zone for the fringe field'),
        'LAM_S': (0 * ureg.centimeter, 'Exit face fringe field extent'),
        'C0_S': 0,
        'C1_S': 1,
        'C2_S': 0,
        'C3_S': 0,
        'C4_S': 0,
        'C5_S': 0,
        'XPAS': (0.1 * ureg.centimeter, 'Integration step'),
        'KPOS': 1,
        'XCE': 0 * ureg.centimeter,
        'YCE': 0 * ureg.centimeter,
        'ALE': 0 * ureg.radian,
    }
    COLOR = 'blue'

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IL}
        {_cm(s.XL):.12e} {_cm(s.R0):.12e} {s.B0.to('kilogauss').magnitude:.12e}
        {_cm(s.XE):.12e} {_cm(s.LAM_E):.12e}
        6 {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
        {_cm(s.XS):.12e} {_cm(s.LAM_S):.12e}
        6 {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
        {_cm(s.XPAS)}
        {s.KPOS} {_cm(s.XCE):.12e} {_cm(s.YCE):.12e} {s.ALE.to('radian').magnitude:.12e}
        """

    @property
    def gradient(self):
        return self.B0 / self.R0

    @gradient.setter
    def gradient(self, g):
        self.B0 = g * self.R0

    def align(self, mode=''):
        self.KPOS = 1
        self.XCE = 0.0 * ureg.centimeter
        self.YCE = 0.0 * ureg.centimeter
        self.ALE = 0.0 * ureg.radians
        return self


class SexQuad(Magnet):
    """Sharp edge magnetic multipole."""
    PARAMETERS = {
        'IL': 2,
        'XL': 0,
        'R0': 0,
        'N': 0,
        'EB1': 0,
        'EB2': 0,
        'EG1': 0,
        'EG2': 0,
        'XPAS': 0.1,
        'KPOS': 1,
        'XCE': 0,
        'YCE': 0,
        'ALE': 0,
    }

    def __str__(s):
        command = []
        c = f"""
                    {super().__str__().rstrip()}
                    {s.IL}
                    {s.XL:.12e} {s.R0:.12e} {s.B0:.12e}
                    {s.N:.12e} {s.EB1:.12e} {s.EB2:.12e} {s.EG1:.12e} {s.EG2:.12e} 
                    {s.XPAS:.12e}  
                    """
        # Coefficients for the calculation of B.
        # if Y > 0 : B = EB1 and G = EG1;
        # if Y < 0: B = EB2 and G = EG2.
        command.append(c)

        if s.KPOS not in (1, 2):
            raise ZgoubidoException("KPOS must be equal to 1 or 2")

        if s.KPOS == 1:  # XCE, YCE and ALE set to 0 and unused
            c = f"""
                    {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
                    """
            command.append(c)
        elif s.KPOS == 2:  # Elements are misaligned
            c = f"""
                    {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
                    """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Sextupole(Magnet):
    """Sextupole magnet."""
    KEYWORD = 'SEXTUPOL'

    PARAMETERS = {
        'IL': 2,
        'XL': 0,
        'R0': 0,
        'B0': 0,
        'X_E': 0,
        'LAM_E': 0,
        'NCE': 0,
        'C0_E': 0,
        'C1_E': 0,
        'C2_E': 0,
        'C3_E': 0,
        'C4_E': 0,
        'C5_E': 0,
        'X_S': 0,
        'LAM_S': 0,
        'NCS': 0,
        'C0_S': 0,
        'C1_S': 0,
        'C2_S': 0,
        'C3_S': 0,
        'C4_S': 0,
        'C5_S': 0,
        'XPAS': 0.1,
        'KPOS': 1,
        'XCE': 0,
        'YCE': 0,
        'ALE': 0,
    }

    def __str__(s):
        command = []
        c = f"""
                {super().__str__().rstrip()}
                {s.IL}
                {s.XL:.12e} {s.R0:.12e} {s.B0:.12e}
                {s.X_E:.12e} {s.LAM_E:.12e}
                {s.NCE} {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
                {s.X_S:.12e} {s.LAM_S:.12e}
                {s.NCS} {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
                {s.XPAS:.12e}  
                """
        command.append(c)

        if s.KPOS not in (1, 2):
            raise ZgoubidoException("KPOS must be equal to 1 or 2")

        if s.KPOS == 1:  # XCE, YCE and ALE set to 0 and unused
            c = f"""
                {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
                """
            command.append(c)
        elif s.KPOS == 2:  # Elements are misaligned
            c = f"""
                {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
                """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Solenoid(Magnet):
    """Solenoid."""
    PARAMETERS = {
        'IL': 2,
        'XL': 0,
        'R0': 0,
        'B0': 0,
        'X_E': 0,
        'X_S': 0,
        'XPAS': 0.1,
        'KPOS': 1,
        'XCE': 0,
        'YCE': 0,
        'ALE': 0,
    }

    def __str__(s):
        command = []
        c = f"""
                {super().__str__().rstrip()}
                {s.IL}
                {s.XL:.12e} {s.R0:.12e} {s.B0:.12e}
                {s.X_E:.12e} {s.X_S:.12e}
                {s.XPAS:.12e}  
                """
        command.append(c)

        if s.KPOS not in (1, 2):
            raise ZgoubidoException("KPOS must be equal to 1 or 2")

        if s.KPOS == 1:  # XCE, YCE and ALE set to 0 and unused
            c = f"""
                {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
                """
            command.append(c)
        elif s.KPOS == 2:  # Elements are misaligned
            c = f"""
                {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
                """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Undulator(Magnet):
    """Undulator magnet."""


class Venus(Command):
    """Simulation of a rectangular shape dipole magnet."""
    PARAMETERS = {
        'IL': (2, ),
        'XL': (100 * ureg.centimeter, ),
        'YL': (100 * ureg.centimeter, ),
        'B0': (10 * ureg.kilogauss, ),
        'XPAS': (0.1 * ureg.centimeter, ),
        'KPOS': 1,
        'XCE': (0 * ureg.centimeter, ),
        'YCE': (0 * ureg.centimeter, ),
        'ALE': (0 * ureg.radian, ),
    }

    def __str__(self) -> str:
        if self.KPOS not in (0, 1, 2):
            raise ZgoubidoException("KPOS must be in (0, 1, 2)")
        return f"""
        {super().__str__().rstrip()}
        {int(self.IL):d}
        {_cm(self.XL):.12e} {_cm(self.YL):.12e} {_kilogauss(self.B0):.12e}
        {_cm(self.XPAS):.12e}  
        {int(self.KPOS):d} {_cm(self.XCE):.12e} {_cm(self.YCE):.12e} {_radian(self.ALE):.12e}
        """
