"""*Zgoubidoo: a modern Python 3 interface to particle tracking codes: Zgoubi and MAD-X.*

Zgoubidoo was born as a Python 3 interface for `Zgoubi`_, a ray-tracing code for beam dynamics simulations. Zgoubido is
intended to follow a modern Python design and aims at being easy to use. Interactive use with iPython or Jupyter
Notebook is supported and encouraged. As such Zgoubidoo can be viewed as a 'Zgoubi for the mere mortal' interface. More
recently, Zgoubidoo learned how to drive MAD-X, in a similar fashion as it runs Zgoubi. This is intended to promote
more systematic comparisons between the codes (in the few corner cases where it is possible) and to allow the user to
built a complete workflow with a single unified libary: indeed, the optical design of new machines typically starts
with MAD-X for which Zgoubidoo provides a complete interface (survey, Twiss and tracking modules, as well as the
equivalent PTC modules).

Zgoubi
------

Zgoubi is a ray-tracing (tracking) code for beam dynamics simulations. Many magnetic and electric elements are
supported, as well as multiple other features, such as spin tracking. It is maintained by François Méot on SourceForge
(`Zgoubi SourceForge repository`_).

.. _Zgoubi: https://sourceforge.net/projects/zgoubi/
.. _Zgoubi SourceForge repository: https://sourceforge.net/projects/zgoubi/

MAD-X and PTC
-------------

.. _MADX: http://mad.web.cern.ch

Design goals
------------

.. image:: _static/zgoubi_logo.png
   :width: 150 px
   :alt: Zgoubi's logo
   :align: right

- **Fully featured interface to Zgoubi**: all functionalities of Zgoubi are supported through the Python interface;
- **Fully featuted interface to MAD-X and PTC**: all functionalities are supported through the Python interface;
- **Ease of use**: a simple tracking study and its visualization can be set up in just a few lines of code;
- Written in **high-quality Python 3 with type-hints**;
- **Built-in support for multi-core machines**: it is possible and easy to run multiple simulations in parallel and to
  collect the final results;
- The library interface and use-n-feel is **Jupyter notebook friendly**;
- **Decoupling between low-level and high-level use cases**: the low-level support provides a simple Python interface to
  generate Zgoubi (or MAD-X) input files and run the executable while the high-level support provides interfaces with
  more abstraction (`sequences`, etc.);
- Strong support and enforcement of the **systematic use of physical units**: **no units conversion nightmare**, you can
  freely use whatever units set you like, the conversion into Zgoubi's or MAD-X's default units is automatically
  handled.

Publications
------------

- Coming soon.

"""
__version__ = "2019.4"

try:
    from georges_core import ureg, Q_
except ModuleNotFoundError:
    # TODO error handling
    # Manipulation of physical quantities (with units, etc.)
    # https://pint.readthedocs.io/en/latest/
    from pint import UnitRegistry
    ureg = UnitRegistry()
    Q_ = ureg.Quantity
    ureg.define('electronvolt = e * volt = eV')
    ureg.define('electronvolt_per_c = eV / c = eV_c')
    ureg.define('electronvolt_per_c2 = eV / c**2 = eV_c2')

try:
    from georges_core import sequences
    from georges_core import Kinematics, ZgoubiKinematicsException
    from georges_core.frame import Frame, FrameException
except ModuleNotFoundError:
    # TODO error handling
    pass

from . import commands
from . import converters
from . import fieldmaps
from . import physics
from . import vis
from . import twiss
from .input import Input, ZgoubiInputValidator, ZgoubiInputException
from .outputs import read_fai_file, read_matrix_file, read_optics_file, read_plt_file, read_srloss_file, \
    read_srloss_steps_file
from .mappings import ParametricMapping, ParametersMappingType
from .zgoubi import Zgoubi, ZgoubiResults, ZgoubiException
from .surveys import survey, clear_survey, survey_reference_trajectory
from .polarity import HorizontalPolarity, VerticalPolarity
