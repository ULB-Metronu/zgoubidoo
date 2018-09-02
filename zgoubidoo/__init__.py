__version__ = "2018.1"

# Manipulation of physical quantities (with units, etc.)
# https://pint.readthedocs.io/en/latest/
from pint import UnitRegistry
ureg = UnitRegistry()
Q_ = ureg.Quantity

from . import commands
from . import plotting
from .input import Input
from .output import read_fai_file, read_plt_file
from .zgoubi import Zgoubi, ZgoubiException