from .commands import Command, ZgoubidoException
import matplotlib.patches as patches
from .. import ureg, Q_


class AGSMainMagnet(Command):
    """AGS main magnet."""
    KEYWORD = 'AGSMM'


class AGSQuadrupole(Command):
    """AGS quadrupole."""
    KEYWORD = 'AGSQUAD'


class Aimant(Command):
    """Generation of dipole mid-plane 2-D map, polar frame."""
    KEYWORD = 'AIMANT'


class Bend(Command):
    """Bending magnet, Cartesian frame.
    Parameters:
        IL:
        XL (cm): magnet length (distance between EFB)

    """
    KEYWORD = 'BEND'

    PARAMETERS = {
        'IL': 2,
        'XL': (0.0 * ureg.centimeter, "Magnet length (straight reference frame)."),
        'SK': 0.0,
        'B1': 0.0,
        'X_E': 0.0,
        'LAM_E': 0.0,
        'W_E': 0.0,
        'C0_E': 0.0,
        'C1_E': 1.0,
        'C2_E': 0.0,
        'C3_E': 0.0,
        'C4_E': 0.0,
        'C5_E': 0.0,
        'X_S': 0.0,
        'LAM_S': 0.0,
        'W_S': 0.0,
        'C0_S': 0.0,
        'C1_S': 1.0,
        'C2_S': 0.0,
        'C3_S': 0.0,
        'C4_S': 0.0,
        'C5_S': 0.0,
        'XPAS': 0.0,
        'KPOS': 3,
        'XCE': 0.0,
        'YCE': 0.0,
        'ALE': 0.0,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IL}
        {s.XL.to('cm').magnitude:.12e} {s.SK:.12e} {s.B1:.12e}
        {s.X_E:.12e} {s.LAM_E:.12e} {s.W_E:.12e}
        0 {s.C0_E} {s.C1_E} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e}
        {s.X_S:.12e} {s.LAM_S:.12e} {s.W_S:.12e}
        0 {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e}
        {s.XPAS:.12e}
        {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
        """

    def plot(self, ax):
        return ax


class Decapole(Command):
    """Decapole magnet."""
    KEYWORD = 'DECAPOLE'


class Dipole(Command):
    """Dipole magnet, polar frame."""
    KEYWORD = 'DIPOLE'

    PARAMETERS = {
        'IL': (2, 'Print field and coordinates along trajectories'),
        'AT': (0 * ureg.degree, 'Total angular extent of the dipole'),
        'RM': (0 * ureg.kilogauss, 'Reference radius'),
        'ACENT': (0 * ureg.degree, 'Azimuth for positioning of EFBs'),
        'B0': (0 * ureg.kilogauss, 'Reference field'),
        'N': (0, 'Field index (radial quadrupolar)'),
        'B': (0, 'Field index (radial sextupolar)'),
        'G': (0, 'Field index (radial octupolar)'),
        'LAM_E': (0 * ureg.centimeter, 'Entrance fringe field extent (normally ≃ gap size)'),
        'C0_E': 0,
        'C1_E': 1,
        'C2_E': 0,
        'C3_E': 0,
        'C4_E': 0,
        'C5_E': 0,
        'SHIFT_E': (0 * ureg.centimeter, 'Shift of the EFB'),
        'OMEGA_E': 0,
        'THETA_E': 0,
        'R1_E': (1e9 * ureg.centimeter, 'Entrance EFB radius'),
        'U1_E': (1e9 * ureg.centimeter, 'Entrance EFB linear extent'),
        'U2_E': (1e9 * ureg.centimeter, 'Entrance EFB linear extent'),
        'R2_E': (1e9 * ureg.centimeter, 'Entrance EFB radius'),
        'LAM_S': (0 * ureg.centimeter, 'Exit fringe field extent (normally ≃ gap size)'),
        'C0_S': 0,
        'C1_S': 1,
        'C2_S': 0,
        'C3_S': 0,
        'C4_S': 0,
        'C5_S': 0,
        'SHIFT_S': (0 * ureg.centimeter, 'Shift of the EFB'),
        'OMEGA_S': 0,
        'THETA_S': 0,
        'R1_S': (1e9 * ureg.centimeter, 'Exit EFB radius'),
        'U1_S': (1e9 * ureg.centimeter, 'Exit EFB linear extent'),
        'U2_S': (1e9 * ureg.centimeter, 'Exit EFB linear extent'),
        'R2_S': (1e9 * ureg.centimeter, 'Exit EFB radius'),
        'LAM_L': (0 * ureg.centimeter, 'Lateral fringe field extent (normally ≃ gap size)'),
        'XI_L': (0.0, 'Flag to activate/deactivate the lateral EFB (0 to deactivate)'),
        'C0_L': 0,
        'C1_L': 1,
        'C2_L': 0,
        'C3_L': 0,
        'C4_L': 0,
        'C5_L': 0,
        'SHIFT_L': (0 * ureg.centimeter, 'Shift of the EFB'),
        'OMEGA_L': 0,
        'THETA_L': 0,
        'R1_L': (1e9 * ureg.centimeter, 'Lateral EFB radius'),
        'U1_L': (1e9 * ureg.centimeter, 'Lateral EFB linear extent'),
        'U2_L': (1e9 * ureg.centimeter, 'Lateral EFB linear extent'),
        'R2_L': (1e9 * ureg.centimeter, 'Lateral EFB radius'),
        'RM3': (1e9 * ureg.centimeter, 'Reference radius of the lateral EFB'),
        'IORDRE': 2,
        'Resol': 10,
        'XPAS': (1 * ureg.millimeter, 'Integration step'),
        'KPOS': 2,
        'RE': 0,
        'TE': 0,
        'RS': 0,
        'TS': 0,
        'DP': 0,
    }

    def __str__(s):
        liste = []
        f = f"""
        {super().__str__().rstrip()}
        {s.IL}
        {s.AT.to('degree').magnitude:.12e} {s.RM.to('centimeter').magnitude:.12e}
        {s.ACENT.to('degree').magnitude:.12e} {s.B0.to('kilogauss').magnitude:.12e} {s.N:.12e} {s.B:.12e} {s.G:.12e}
        {s.LAM_E.to('centimeter').magnitude:.12e} 0.0
        0 {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e} {s.SHIFT_E.to('centimeter').magnitude:.12e}
        {s.OMEGA_E:.12e} {s.THETA_E:.12e} {s.R1_E.to('centimeter').magnitude:.12e} {s.U1_E.to('centimeter').magnitude:.12e} {s.U2_E.to('centimeter').magnitude:.12e} {s.R2_E.to('centimeter').magnitude:.12e}
        {s.LAM_S.to('centimeter').magnitude:.12e} 0.0
        0 {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e} {s.SHIFT_S.to('centimeter').magnitude:.12e}
        {s.OMEGA_S:.12e} {s.THETA_S:.12e} {s.R1_S.to('centimeter').magnitude:.12e} {s.U1_S.to('centimeter').magnitude:.12e} {s.U2_S.to('centimeter').magnitude:.12e} {s.R2_S.to('centimeter').magnitude:.12e}
        {s.LAM_L.to('centimeter').magnitude:.12e} {s.XI_L}
        0 {s.C0_L:.12e} {s.C1_L:.12e} {s.C2_L:.12e} {s.C3_L:.12e} {s.C4_L:.12e} {s.C5_L:.12e} {s.SHIFT_L.to('centimeter').magnitude:.12e}
        {s.OMEGA_L:.12e} {s.THETA_L:.12e} {s.R1_L.to('centimeter').magnitude:.12e} {s.U1_L.to('centimeter').magnitude:.12e} {s.U2_L.to('centimeter').magnitude:.12e} {s.R2_L.to('centimeter').magnitude:.12e} {s.RM3.to('centimeter').magnitude:.12e}
        {s.IORDRE} {s.Resol}
        {s.XPAS.to('centimeter').magnitude:.12e}"""
        liste.append(f)
        if s.KPOS == 2:
            g = f"""
        {s.KPOS}
        {s.RE.to('centimeter').magnitude:.12e} {s.TE:.12e} {s.RS.to('centimeter').magnitude:.12e} {s.TS:.12e}
        """
            liste.append(g)
        elif s.KPOS == 1:
            g = f"""
        {s.KPOS}
        {s.DP:.12e}
        """
            liste.append(g)
        somme = ''
        for l in range(0, len(liste)):
            somme += liste[l]
        return somme

    def plot(self, ax, offset={}):
        offset = {
            'X': offset.get('X', 0),
            'Y': offset.get('Y', 0),
            'R': offset.get('R', 0),
        }
        w = patches.Wedge(
            (offset['X'], offset['Y']),
            0.2,
            0.0,
            0.0 + self.AT.to('degree').magnitude,
            width=0.4,
            alpha=1,
            facecolor='r',
            ec='r'
        )
        ax.add_patch(w)


class DipoleM(Command):
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
                {s.DP:.12e}"""
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Dipoles(Command):
    """Dipole magnet N-tuple, polar frame."""
    KEYWORD = 'DIPOLES'

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

        if int(s.KIRD) == 0:
            command.append(f"""
            {s.KIRD}.{s.n} {s.Resol:.12e}
            """)
        else:
            command.append(f"""
            {s.KIRD} {s.Resol:.12e}
            """)

        command.append(f"""{s.XPAS:.12e}""")

        if int(s.KPOS) == 2:
            c = f"""
            {s.KPOS}
            {s.RE:.12e} {s.TE:.12e} {s.RS:.12e} {s.TS:.12e}
            """
            command.append(c)
        elif int(s.KPOS) == 1:
            c = f"""
            {s.KPOS}
            {s.DP:.12e}"""
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command))


class Dodecapole(Command):
    """Dodecapole magnet."""
    KEYWORD = 'DODECAPO'


class Drift(Command):
    """Field free drift space."""
    KEYWORD = 'DRIFT'

    PARAMETERS = {
        'XL': (0.0 * ureg.centimeter, "Drift length."),
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.XL.to('centimeter').magnitude}
        """


class Emma(Command):
    """2-D Cartesian or cylindrical mesh field map for EMMA FFAG."""
    KEYWORD = 'EMMA'


class FFAG(Command):
    """FFAG magnet, N-tuple."""
    KEYWORD = 'FFAG'


class FFAGSpirale(Command):
    """Spiral FFAG magnet, N-tuple."""
    KEYWORD = 'FFAG-SPI'


class Multipole(Command):
    """Magnetic multipole."""
    KEYWORD = 'MULTIPOL'


class Octupole(Command):
    """Octupole magnet."""
    KEYWORD = 'OCTUPOLE'


class PS170(Command):
    """Simulation of a round shape dipole magnet."""
    KEYWORD = 'PS170'


class Quadisex(Command):
    """Sharp edge magnetic multipoles."""
    KEYWORD = 'QUADISEX'


class Quadrupole(Command):
    """Quadrupole magnet."""
    KEYWORD = 'QUADRUPO'

    PARAMETERS = {
        'IL': 2,
        'XL': 0,
        'R0': 1.0,
        'B0': 0,
        'XE': 0,
        'LAM_E': 0,
        'NCE': 0,
        'NCS': 0,
        'C0': 0,
        'C1': 0,
        'C2': 0,
        'C3': 0,
        'C4': 0,
        'C5': 0,
        'XS': 0,
        'LAM_S': 0,
        'XPAS': 0.1,
        'KPOS': 0,
        'XCE': 0,
        'YCE': 0,
        'ALE': 0,
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.IL}
        {s.XL:.12e} {s.R0:.12e} {s.B0:.12e}
        {s.XE:.12e} {s.LAM_E:.12e}
        {s.NCE} {s.C0:.12e} {s.C1:.12e} {s.C2:.12e} {s.C3:.12e} {s.C4:.12e} {s.C5:.12e}
        {s.XS:.12e} {s.LAM_S:.12e}
        {s.NCS} {s.C0:.12e} {s.C1:.12e} {s.C2:.12e} {s.C3:.12e} {s.C4:.12e} {s.C5:.12e}
        {s.XPAS}
        {s.KPOS} {s.XCE:.12e} {s.YCE:.12e} {s.ALE:.12e}
        """

    def plot(self, ax, width=0.4, coords=None):
        if coords is None:
            coords = [0, 0, 0, 0, 0, 0]
        w = patches.Rectangle(
            (
                coords[0] - width / 2,
                coords[1],
            ),
            width,
            self.XL,
            angle=coords[3],
            alpha=1.0,
            facecolor='b',
            ec='b',
            hatch=''
        )
        ax.add_patch(w)
        w = patches.Rectangle(
            (
                coords[0] - width / 2,
                coords[1],
            ),
            width/10,
            self.XL,
            angle=coords[3],
            alpha=0.5,
            facecolor='k',
            ec='k',
            hatch=''
        )
        ax.add_patch(w)


class SexQuad(Command):
    """Sharp edge magnetic multipole."""
    KEYWORD = 'SEXQUAD'


class Sextupole(Command):
    """Sextupole magnet."""
    KEYWORD = 'SEXTUPOL'


class Solenoid(Command):
    """Solenoid."""
    KEYWORD = 'SOLENOID'


class Undulator(Command):
    """Undulator magnet."""
    KEYWORD = 'UNDULATOR'


class Venus(Command):
    """Simulation of a rectangular shape dipole magnet."""
    KEYWORD = 'VENUS'
