Installation
============

Installation the `Zgoubidoo` Python library requires a working Python 3.7 environment. The easiest way is to proceed
with `Conda` to set it up. In case you already have a Python 3.7 environment available, you can simply install
`Zgoubidoo` with `pip`. `Zgoubidoo` has a relatively small number of dependencies, and no non-Python dependencies,
except of course for `Zgoubi` itself.

Compiling and installing Zgoubi
-------------------------------

Creating a Python 3.7 environment with Conda
--------------------------------------------


Installation Zgoubidoo using pip
--------------------------------
The first step is to activate your Python 3.7 environment (only needed if you don't use a global
instalaltion of Python. On Mac OS if you use the Python `brew` installation you should already have Python 3.7 widely
available). With `Conda` proceed like this::
    conda activate py37

where `py37` is the name of the environment created by default if you used the `requirement.txt` file.

Zgoubidoo can then be installed::
    cd path_to_zgoubidoo
    pip install .

Upgrading Zgoubidoo::
    pip install . --upgrade

Alternatively if you intend to develop `Zgoubidoo` you can install it in editable mode::
    pip install -e .

The second method allows any change to be reflected directly to your Zgoubidoo package (only a symlink is created in
site-packages).

