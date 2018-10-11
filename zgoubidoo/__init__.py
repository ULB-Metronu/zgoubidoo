__version__ = "2018.1"

# Manipulation of physical quantities (with units, etc.)
# https://pint.readthedocs.io/en/latest/
from pint import UnitRegistry
ureg = UnitRegistry()
Q_ = ureg.Quantity
ureg.define('electronvolt = e * volt = eV')
ureg.define('electronvolt_per_c = eV / c = eV_c')
ureg.define('electronvolt_per_c2 = eV / c**2 = eV_c2')
ureg.define('[momentum] = [ev] / [c]')
ureg.define('[energy] = [ev] / [c]**2 ')

from . import physics
from . import commands
from . import vis
from . import twiss
from .input import Input
from .output import read_fai_file, read_plt_file, read_matrix_file
from .zgoubi import Zgoubi, ZgoubiRun, ZgoubiException
from .survey import survey
from .frame import Frame, ZgoubidooFrameException
from .beam import Beam, ZgoubidooBeamException
