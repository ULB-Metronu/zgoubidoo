class Objet():
    KEYWORD = 'OBJET'
    
    def __init__(self):
        self._boro = 0
        pass
    
    def __str__(self):
        return f"""
        '{self.KEYWORD}'
        {self._boro}
        {self._kobj}.{self._k2}
        """
    
class Objet1(Objet):
    pass

class Objet2(Objet):
    pass

class Objet3(Objet):
    pass

class Objet4(Objet):
    pass
    
class Objet5(Objet):
    def __init__(self):
        pass

class Objet6(Objet):
    pass

class Objet7(Objet):
    pass

class Objet8(Objet):
    pass


class Command:
    PARAMETERS = {
        'VALID': True,
        'LABEL2': '',
    }
    
    def __init__(self, *params, **kwargs):
        name = params[0] if (len(params) > 0 and isinstance(params[0], str)) else ''
        self._attributes = {
            'LABEL1': name,
        }
        for p in (Command.PARAMETERS, self.PARAMETERS, ) + (params[1] if (len(params) > 1 and isinstance(params[0], str)) else params):
            self._attributes = dict(self._attributes, **p)
        self._attributes = dict(self._attributes, **kwargs)
        
    def __getattr__(self, a):
        return self._attributes[a]
    
    def __setattr__(self, a, v):
        if a == '_attributes':
            self.__dict__[a] = v
        else:
            self._attributes[a] = v
            
    def __repr__(s):
        return f"""
        '{s.KEYWORD}' {s.LABEL1} {s.LABEL2}
        """
    
    def __str__(s):
        return s.__repr__()

class Drift(Command):
    KEYWORD = 'DRIFT'
    PARAMETERS = {
        'XL': 0.0
    }
    
    def __repr__(s):
        return f"""
        '{s.KEYWORD}' {s.LABEL1} {s.LABEL2}
        {s.XL}
        """
            
class MCObjet(Command):
    PARAMETERS = {
        'BORO': 1.0,
        'IMAX': 1,
        'KY': 1,
    }
        
class MCObjet1(MCObjet):
    pass


class MCObjet2(MCObjet):
    pass


class MCObjet3(MCObjet):
    KEYWORD = 'MCOBJET'
    PARAMETERS = {
        'KY': 2,
        'KT': 1,
        'KZ': 1,
        'KP': 1,
        'KX': 1,
        'KD': 1,
        'Y0': 1,
        'T0': 1.0,
        'Z0': 1.0,
        'P0': 1.0,
        'X0': 1.0,
        'D0': 1.0,
        'ALPHA_Y': 0.0,
        'BETA_Y': 1.0,
        'EMIT_Y': 1e-9,
        'N_CUTOFF_Y': 0,
        'N_CUTOFF2_Y': 0,
        'ALPHA_Z': 0.0,
        'BETA_Z': 1.0,
        'EMIT_Z': 1e-9,
        'N_CUTOFF_Z': 0,
        'N_CUTOFF2_Z': 0,
        'ALPHA_X': 0.0,
        'BETA_X': 1.0,
        'EMIT_X': 1e-9,
        'N_CUTOFF_X': 0,
        'N_CUTOFF2_X': 0,
        'I1': 1,
        'I2': 2,
        'I3': 3,
    }
    
    def __str__(s):
        return f"""
        '{s.KEYWORD}' {s.LABEL1} {s.LABEL2}
        3
        {s.KY} {s.KT} {s.KZ} {s.KP} {s.KX} {s.KD}
        {s.Y0} {s.T0} {s.Z0} {s.P0} {s.X0} {s.D0}
        {s.ALPHA_Y} {s.BETA_Y} {s.EMIT_Y} {s.N_CUTOFF_Y} {s.N_CUTOFF2_Y if s.N_CUTOFF_Y < 0 else ''}
        {s.ALPHA_Z} {s.BETA_Z} {s.EMIT_Z} {s.N_CUTOFF_Z} {s.N_CUTOFF2_Z if s.N_CUTOFF_Z < 0 else ''}
        {s.ALPHA_X} {s.BETA_X} {s.EMIT_X} {s.N_CUTOFF_X} {s.N_CUTOFF2_X if s.N_CUTOFF_X < 0 else ''}
        {s.I1} {s.I2} {s.I3}
    """
    
class Particul(Command):
    KEYWORD = 'PARTICUL'
    PARAMETERS = {
        'M': 0,
        'Q': 0,
        'G': 0,
        'tau': 0,
        'X': 0,
    }
    
    def __init__(self, *params, **kwargs):
        super().__init__(Particul.PARAMETERS, self.PARAMETERS, *params, **kwargs)
        
    def __repr__(s):
        return f"""
        '{s.KEYWORD}'
        {s.M} {s.Q} {s.G} {s.tau} {s.X}
        """
    
class Electron(Particul):
    PARAMETERS = {
        'M': 0.51099892e6,
        'Q': -1.60217653e-19,
        'G': (2.0023193043622 -2)/2,
    }
    
class Positron(Particul):
    PARAMETERS = {
        'M': 0.51099892e6,
        'Q': 1.60217653e-19,
        'G': (2.0023193043622 -2)/2,
    }
    
class Proton(Particul):
    PARAMETERS = {
        'M': 938.27203e6,
        'Q': 1.602176487e-19,
        'G': (5.585694701 -2)/2,
    }
    
class AntiProton(Particul):
    PARAMETERS = {
        'M': 938.27203e6,
        'Q': -1.602176487e-19,
        'G': (5.585694701 -2)/2,
    }
    
class Faiscnl(Command):
    KEYWORD = 'FAISCNL'
    PARAMETERS = {
        'FNAME': 'zgoubi.fai',
        'B_FNAME': 'b_zgoubi.fai',
        'binary': False,
    }
            
    def __repr__(s):
        return f"""
        '{s.KEYWORD}' {s.LABEL1} {s.LABEL2}
        {s.B_FNAME if s.binary else s.FNAME}
        """
    
class End(Command):
    KEYWORD = 'END'
    
class Quadrupo(Command):
    KEYWORD = 'QUADRUPOL'
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
        'XPAS': [0, 0, 0],
        'KPOS': 0,
        'XCE': 0,
        'YCE': 0,
        'ALE': 0,
    }
    
    def __repr__(s):
        return f"""
        {super().__repr__()}
        {s.IL}
        {s.XL} {s.R0} {s.B0}
        {s.XE} {s.LAM_E}
        {s.NCE} {s.C0} {s.C1} {s.C2} {s.C3} {s.C4} {s.C5}
        {s.XS} {s.LAM_S}
        {s.NCS} {s.C0} {s.C1} {s.C2} {s.C3} {s.C4} {s.C5}
        #{'|'.join(map(str, s.XPAS))}
        {s.KPOS} {s.XCE}
        {s.YCE} {s.ALE}
        """
