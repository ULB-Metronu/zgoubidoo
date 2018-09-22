__version__ = "2018.1"

# Manipulation of physical quantities (with units, etc.)
# https://pint.readthedocs.io/en/latest/
from pint import UnitRegistry
ureg = UnitRegistry()
Q_ = ureg.Quantity

from . import commands
from . import plotting
from . import twiss
from .input import Input
from .output import read_fai_file, read_plt_file, read_matrix_file
from .zgoubi import Zgoubi, ZgoubiException
from .survey import survey
from .frame import Frame


def _cm(q: Q_) -> float:
    return q.to('cm').magnitude


def _degree(q: Q_) -> float:
    return q.to('degree').magnitude
