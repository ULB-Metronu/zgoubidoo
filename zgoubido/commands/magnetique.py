from .commands import Command


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
    """Bending magnet, Cartesian frame."""
    KEYWORD = 'BEND'


class Decapole(Command):
    """Decapole magnet."""
    KEYWORD = 'DECAPOLE'


class Dipole(Command):
    """Dipole magnet, polar frame."""
    KEYWORD = 'DIPOLE'

    PARAMETERS = {
        'IL': 2,
        'AT': 0,
        'RM': 0,
        'ACENT': 0,
        'B0': 0,
        'N': 0,
        'B': 0,
        'G': 0,
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
        'R1_E': 0,
        'U1_E': 0,
        'U2_E': 0,
        'R2_E': 0,
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
        'R1_S': 0,
        'U1_S': 0,
        'U2_S': 0,
        'R2_S': 0,
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
        'R1_L': 0,
        'U1_L': 0,
        'U2_L': 0,
        'R2_L': 0,
        'RM3': 0,
        'IORDRE': 2,
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
        liste = []
        f = f"""
        {super().__str__().rstrip()}
        {s.IL}
        {s.AT:.12e} {s.RM:.12e}
        {s.ACENT} {s.B0:.12e} {s.N:.12e} {s.B:.12e} {s.G:.12e}
        {s.LAM_E:.12e} {s.XI_E:.12e}
        {s.NCE} {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e} {s.SHIFT_E:.12e}
        {s.OMEGA_E:.12e} {s.THETA_E:.12e} {s.R1_E:.12e} {s.U1_E:.12e} {s.U2_E:.12e} {s.R2_E:.12e}
        {s.LAM_S:.12e} {s.XI_S:.12e}
        {s.NCS} {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e} {s.SHIFT_S:.12e}
        {s.OMEGA_S:.12e} {s.THETA_S:.12e} {s.R1_S:.12e} {s.U1_S:.12e} {s.U2_S:.12e} {s.R2_S:.12e}
        {s.LAM_L:.12e} {s.XI_L:.12e}
        {s.NCL} {s.C0_L:.12e} {s.C1_L:.12e} {s.C2_L:.12e} {s.C3_L:.12e} {s.C4_L:.12e} {s.C5_L:.12e} {s.SHIFT_L:.12e}
        {s.OMEGA_L:.12e} {s.THETA_L:.12e} {s.R1_L:.12e} {s.U1_L:.12e} {s.U2_L:.12e} {s.R2_L:.12e} {s.RM3:.12e}
        {s.IORDRE} {s.Resol}
        {s.XPAS}"""
        liste.append(f)
        if s.KPOS == 2:
            g = f"""
            {s.KPOS}
            {s.RE:.12e} {s.TE:.12e} {s.RS:.12e} {s.TS:.12e}"""
            liste.append(g)
        elif s.KPOS == 1:
            g = f"""
            {s.KPOS}
            {s.DP:.12e}"""
            liste.append(g)
        somme = ''
        for l in range(0, len(liste)):
            somme += liste[l]
        return somme


class DipoleM(Command):
    KEYWORD = 'DIPOLEM'

    PARAMETERS = {
        'NFACE': 3,
        'IC': 0,
        'IL': 0,
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
        'R1_E': 0,
        'U1_E': 0,
        'U2_E': 0,
        'R2_E': 0,
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
        'R1_S': 0,
        'U1_S': 0,
        'U2_S': 0,
        'R2_S': 0,
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
        'R1_L': 0,
        'U1_L': 0,
        'U2_L': 0,
        'R2_L': 0,
        'RM3': 0,
        'NBS': 0,
        'R0': 0,
        'DELTAB': 0,
        'THETA_0': 0,
        'IORDRE': 0,
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
        liste = []
        if s.NFACE != 3:
            print('Error : Zgoubido does not support NFACE =', s.NFACE)
        elif s.NFACE == 3:
            f = f"""
            {super().__str__().rstrip()}
            {s.NFACE} {s.IC} {s.IL}
            {s.IAMAX} {s.IRMAX}
            {s.B0:.12e} {s.N:.12e} {s.B:.12e} {s.G:.12e}
            {s.AT} {s.ACENT:.12e} {s.RM:.12e} {s.RMIN:.12e} {s.RMAX:.12e}
            {s.LAM_E:.12e} {s.XI_E:.12e}
            {s.NCE} {s.C0_E:.12e} {s.C1_E:.12e} {s.C2_E:.12e} {s.C3_E:.12e} {s.C4_E:.12e} {s.C5_E:.12e} {s.SHIFT_E:.12e}
            {s.OMEGA_E:.12e} {s.THETA_E:.12e} {s.R1_E:.12e} {s.U1_E:.12e} {s.U2_E:.12e} {s.R2_E:.12e}
            {s.LAM_S:.12e} {s.XI_S:.12e}
            {s.NCS} {s.C0_S:.12e} {s.C1_S:.12e} {s.C2_S:.12e} {s.C3_S:.12e} {s.C4_S:.12e} {s.C5_S:.12e} {s.SHIFT_S:.12e}
            {s.OMEGA_S:.12e} {s.THETA_S:.12e} {s.R1_S:.12e} {s.U1_S:.12e} {s.U2_S:.12e} {s.R2_S:.12e}
            {s.LAM_L:.12e} {s.XI_L:.12e}
            {s.NCL} {s.C0_L:.12e} {s.C1_L:.12e} {s.C2_L:.12e} {s.C3_L:.12e} {s.C4_L:.12e} {s.C5_L:.12e} {s.SHIFT_L:.12e}
            {s.OMEGA_L:.12e} {s.THETA_L:.12e} {s.R1_L:.12e} {s.U1_L:.12e} {s.U2_L:.12e} {s.R2_L:.12e} {s.RM3:.12e}"""
            liste.append(f)
            if NBS == 0:
                g = f"""
                {s.NBS}
                {s.IORDRE}
                {s.XPAS:.12e}"""
                liste.append(g)
            elif s.NBS == -2:
                g = f"""
                {s.NBS}
                {s.R0:.12e} {s.DELTAB:.12e}
                {s.IORDRE}
                {s.XPAS:.12e}"""
                liste.append(g)
            elif s.NBS == -1:
                g = f"""
                {s.NBS}
                {s.THETA_0:.12e} {s.DELTAB:.12e}
                {s.IORDRE}
                {s.XPAS:.12e}"""
                liste.append(g)
            elif s.NBS>=1:
                g = f"""
                {s.NBS}"""
                list.append(g)
                shim_r1 = len(s.SHIM_R1)
                shim_r2 = len(s.SHIM_R2)
                shim_theta1 = len(s.SHIM_THETA1)
                shim_theta2 = len(s.SHIM_THETA2)
                shim_LAMBDA = len(s.SHIM_LAMBDA)
                shim_GAMMA = len(s.SHIM_GAMMA)
                shim_ALPHA = len(s.SHIM_ALPHA)
                shim_BETA = len(s.SHIM_BETA)
                shim_MU = len(s.SHIM_MU)
                if shim_r1 == shim_r2 == shim_theta1 == shim_theta2 == shim_LAMBDA == shim_GAMMA == shim_ALPHA == shim_BETA ==  shim_MU:
                    for i in range (1,s.SHIM_R1):
                        for i, j, k, l in zip(s.SHIM_R1, s.SHIM_R2, s.SHIM_THETA1, s.SHIM_LAMBDA):
                            d1 = f"{i:.12e} {j:.12e} {k:.12e} {l:.12e}"
                            liste.append(d1)
                        for i, j, k, l in zip(s.GAMMA, s.ALPHA, s.MU, s.BETA):
                            d2 = f"{i:.12e} {j:.12e} {k:.12e} {l:.12e}"
                            liste.append(d2)
                    j = f"""
                    {s.IORDRE}
                    {s.XPAS:.12e}"""
                    liste.append(j)
                    if s.KPOS == 2:
                        k = f"""
                        {s.KPOS}
                        {s.RE:.12e} {s.TE:.12e} {s.RS:.12e} {s.TS:.12e}"""
                        liste.append(j)
                    elif s.KPOS == 1:
                        k = f"""
                        {s.KPOS}
                        {s.DP:.12e}"""
                        liste.append(j)
                else:
                    print('Error : The given lists have not the same lenghts')
        somme = ''
        for l in range(0,len(liste)):
            somme += liste[l]
        return somme


class Dipoles(Command):
    """Dipole magnet N-tuple, polar frame."""
    KEYWORD = 'DIPOLES'

    PARAMETERS = {
        'IL': 2,
        'N': 2,
        'AT': 0,
        'RM': 0,
        'ACN': 0,
        'DELTA_RM': 0,
        'B0': 0,
        'IND': 0,
        'bi': 0,
        'G0_E': 0,
        'K_E': 0,
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
        'R1_E': 0,
        'U1_E': 0,
        'U2_E': 0,
        'R2_E': 0,
        'G0_S': 0,
        'K_S': 0,
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
        'R1_S': 0,
        'U1_S': 0,
        'U2_S': 0,
        'R2_S': 0,
        'G0_L': 0,
        'K_L': 0,
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
        'R1_L': 0,
        'U1_L': 0,
        'U2_L': 0,
        'R2_L': 0,
        'R3': 0,
        'KIRD': 2,
        'n': 2,
        'Resol': 2,
        'XPAS': 0.1,
        'KPOS': 2,
        'RE': 0,
        'TE': 0,
        'RS': 0,
        'TS': 0,
        'DP': 0,
    }

    def __init__(self, label1='', label2='', *params, **kwargs):
        super().__init__(label1, label2, Dipoles.PARAMETERS, self.PARAMETERS, *params, **kwargs)
        for i in range(1, self.IND + 1):
            setattr(self, f"b{i}", 0.0)

    def __str__(s):
        c = []
        f = f"""
        {super().__str__().rstrip()}
        {s.IL}
        {s.N} {s.AT:.12e} {s.RM:.12e}"""
        c.append(f)
        liste_bi = []
        for i in range (1,s.N +1):
            g = f"""
                {s.ACN:.12e} {s.DELTA_RM:.12e} {s.B0:.12e} {s.IND:.12e}"""
            for j in range (1, s.IND + 1):
                h = f"{s.bi:.12e}"
        c.append(g)
        if s.KPOS == 2:
            g = f"""
            {s.RE:.12e}
            {s.KIRD:.12e} {s.n:.12e}
            {s.KPOS}
            {s.RE:.12e} {s.TE:.12e} {s.RS:.12e} {s.TS:.12e}"""
            c.append(g)
        elif s.KPOS == 1:
            g = f"""
            {s.KPOS}
            {s.DP:.12e}"""
            c.append(g)
        somme = ''
        for l in range(0, len(c)):
            somme += c[l]
        return somme


class Dodecapole(Command):
    """Dodecapole magnet."""
    KEYWORD = 'DODECAPO'


class Drift(Command):
    """Field free drift space."""
    KEYWORD = 'DRIFT'

    PARAMETERS = {
        'XL': 0.0
    }

    def __str__(s):
        return f"""
        '{s.KEYWORD}' {s.LABEL1} {s.LABEL2}
        {s.XL}
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
        'R0': 0,
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
