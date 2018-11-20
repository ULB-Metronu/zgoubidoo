Installation
============

Installation the `Zgoubidoo` Python library requires a working Python 3.7 environment. The easiest way is to proceed
with `Conda` to set it up. In case you already have a Python 3.7 environment available, you can simply install
`Zgoubidoo` with `pip`. `Zgoubidoo` has a relatively small number of dependencies, and no non-Python dependencies,
except of course for `Zgoubi` itself.

Compiling and installing Zgoubi
-------------------------------

Obtaining Zgoubidoo
-------------------


Creating a Python 3.7 environment with Conda
--------------------------------------------
The Zgoubidoo repository contains a ``conda`` environment file that can be used to create a complete Python 3.7
environment suitable for Zgoubidoo::

    cd path_to_zgoubidoo
    conda env create --file environment.yml

Installation Zgoubidoo using ``pip``
------------------------------------
The first step is to activate your Python 3.7 environment (only needed if you do not use a global
instalaltion of Python. On Mac OS if you use the Python ``brew`` installation you should already have Python 3.7
available from your path). With ``conda`` proceed like this::

    conda activate py37

where `py37` is the name of the environment created by default if you used the `requirement.txt` file as described
above.

Zgoubidoo can then be installed using ``pip``::

    cd path_to_zgoubidoo
    pip install .

Upgrading Zgoubidoo::

    pip install . --upgrade

Alternatively if you intend to develop `Zgoubidoo` you can install it in editable mode::

    pip install -e .

The second method allows any change to be reflected directly to your Zgoubidoo package (only a symlink is created in
site-packages).

Using Zgoubidoo with Jupyter Notebook
-------------------------------------
Any installation of Jupyter would work as long as the Python 3.7 kernel from the ``conda`` installation can be selected.
For that it is best to install the extension ``nb_conda_kernels``. The ``conda`` environment already contains a working
installation of ``jupyter`` with the ``conda`` extensions::

    conda activate py37
    jupyter notebook

From there you can create a new notebook and simply import Zgoubidoo::

    import zgoubidoo
