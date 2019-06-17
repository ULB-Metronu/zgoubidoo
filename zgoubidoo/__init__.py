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
__version__ = "2019.3"

# Manipulation of physical quantities (with units, etc.)
# https://pint.readthedocs.io/en/latest/
from pint import UnitRegistry
ureg = UnitRegistry()
_Q = ureg.Quantity
ureg.define('electronvolt = e * volt = eV')
ureg.define('electronvolt_per_c = eV / c = eV_c')
ureg.define('electronvolt_per_c2 = eV / c**2 = eV_c2')

from . import commands
from . import converters
from . import fieldmaps
from . import output
from . import physics
from . import sequences
from .sequences import ZgoubidooSequenceException, SequenceMetadata, Sequence, Element
from . import vis
from . import twiss
from .input import Input, MadInput, ZgoubiInputValidator, ZgoubiInputException, ParametricMapping
from .zgoubi import Zgoubi, ZgoubiResults, ZgoubiException
from .surveys import survey, survey_reference_trajectory, clear_survey, transform_tracks
from .frame import Frame, ZgoubidooFrameException
from .polarity import HorizontalPolarity, VerticalPolarity
from .kinematics import ZgoubiKinematicsException, Kinematics
