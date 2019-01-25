"""*Zgoubidoo: a modern Python 3 interface to the Zgoubi particle tracking code.*

Zgoubidoo is a Python 3 interface for `Zgoubi`_, a ray-tracing code for beam dynamics simulations. Zgoubido is intended to
follow a modern Python design and aims at being easy to use. Interactive use with iPython or Jupyter Notebook is
supported and encouraged. As such Zgoubidoo can be viewed as a 'Zgoubi for the mere mortal' interface.

Zgoubi is a ray-tracing (tracking) code for beam dynamics simulations. Many magnetic and electric elements are
supported, as well as multiple other features, such as spin tracking. It is maintained by François Méot on SourceForge
(`Zgoubi SourceForge repository`_).

.. _Zgoubi: https://sourceforge.net/projects/zgoubi/
.. _Zgoubi SourceForge repository: https://sourceforge.net/projects/zgoubi/

Design goals
------------

- **Fully featured interface to Zgoubi**: all functionalities of Zgoubi are supported through the Python interface;
- **Ease of use**: a simple tracking study and its visualization can be set up in just a few lines of code;
- Written in **high-quality Python 3 with type-hints**;
- The library interface and use-n-feel must be **Jupyter notebook friendly**;
- Decoupling between a low-level use (simple Python interface to generate Zgoubi input files and run the executable)
  and high-level interfaces with more abstraction (`sequences`, etc.);
- Strong support and enforcement of physical units: **no units conversion nightmare**, you can freely use whatever units
  set you like, the conversion into Zgoubi's default units is automatically handled.

Publications
------------

- Coming soon.

"""
__version__ = "2019.3"

# Manipulation of physical quantities (with units, etc.)
# https://pint.readthedocs.io/en/latest/
from pint import UnitRegistry
ureg = UnitRegistry()
_Q = ureg.Quantity
ureg.define('electronvolt = e * volt = eV')
ureg.define('electronvolt_per_c = eV / c = eV_c')
ureg.define('electronvolt_per_c2 = eV / c**2 = eV_c2')
ureg.define('[momentum] = [ev] / [c]')
ureg.define('[energy] = [ev] / [c]**2 ')

from . import commands
from . import physics
from . import vis
from . import twiss
from . import sequence
from .input import Input, InputValidator, ZgoubiInputException, ParametricMapping
from .output import read_fai_file, read_plt_file, read_matrix_file
from .zgoubi import Zgoubi, ZgoubiResults, ZgoubiException
from .survey import survey
from .frame import Frame, ZgoubidooFrameException
from .beam import Beam, ZgoubidooBeamException
from .polarity import HorizontalPolarity, VerticalPolarity
