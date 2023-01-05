Installation
============

Installing and using the :code:`Zgoubidoo` Python library requires a working Python 3.8.1+ environment.

The easiest way is to proceed with ``poetry`` to set it up. In case you already have a Python environment available,
you can simply install ``Zgoubidoo`` with ``poetry`` directly. ``Zgoubidoo`` has a relatively small number of
dependencies, and no non-Python dependencies, except of course for ``Zgoubi`` itself. Detailed step-by-step
instructions are provided in the following sections.

Compiling and installing Zgoubi
-------------------------------

Zgoubi can be obtained from the official SourceForge repository, although we do not explicitly support the
compilation and installation of Zgoubi with that method. Indeed, no platform-independent build system is provided and
it is difficult to support compilation over a variety of platforms. A selection of ``Makefile``s is provided. In case
one of them suits your needs, a brief description of the build process is given in the next section.

A non-official ``git`` repository, tracking the SVN repository (using ``git svn``) is maintained in parallel with
Zgoubidoo. You can contact us to obtain access. That repository provides a build system using ``cmake``, which allow to
compile over a variety of platforms and compilers.

In particular, the build process for recent versions of ``gfortran`` on Mac OS is actively supported. The dependencies
are ``cmake`` and ``gfortran``. They can be installed using your package manager, ``brew`` on Mac OS works just fine.

The following steps are recommended on a Mac::

    # Install cmake on Mac OS
    brew install cmake
    # Install gfortran on Mac OS
    brew install gcc
    # Clone the git repository in a source directory
    git clone https://github.com/ulb-metronu/zgoubi.git zgoubi-source
    cd zgoubi-source
    git checkout develop
    cd ..
    mkdir zgoubi-build
    cd zgoubi-build
    cmake ../zgoubi-source
    make

The Zgoubi executable is then available in the ``bin`` directory. No specific step is required to "install" Zgoubi, but
a symbolic link can be a good idea::

    ln -s ./bin/zgoubi /usr/local/bin/zgoubi

Compiling Zgoubi from the official SourceForge repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Zgoubi can be obtained from SourceForge (download or ``svn checkout``). A Fortran compiler is required: both ``ifort``
and ``gfortran`` are supported ('Makefile's are provided).

After the compilation the ``zgoubi`` executable will be available in the `zgoubi` directory. Depending on the Makefile
you use, `zpop` will also be built. `zpop` is *not* used by Zgoubidoo.

Zgoubidoo needs to be able to locate the ``zgoubi`` executable. The easiest way is to have it somewhere in your `$PATH`
so that ``which`` (via Python `shutil.which`) is able to find it. Alternatively, it is possible to provide the path
at runtime (see the ``zgoubidoo.Zgoubi`` class).

Obtaining Zgoubidoo
-------------------
``Zgoubidoo`` is hosted on github (see Zgoubidoo's Github repository). To obtain the code using ``git`` do::

    git clone --recurse-submodules https://github.com/ULB-Metronu/zgoubidoo.git

The default branch (`master`) should be clean at all time, with all the development happening in the `develop` branch.
It should thus be safe to `pull` from the master branch to get the latest version. Only the released and tagged
versions are merged onto the master branch.

To stay on a released (tagged) revision::

    git clone --recurse-submodules --branch 'tag_name' https://github.com/ULB-Metronu/zgoubidoo.git

The releases `CHANGELOG` follows.

.. note::
    .. include:: ../CHANGELOG

To update later on you'll need to execute the following commands, from the top-level repository (not from within any of the submodules)::

    git pull --recurse-submodules

In case the .gitmodules file changes after pulling from upstream (this should be relatively rare, for example if one of the submodule change its remote), it might be necessary to first run the following::

    git submodule sync --recursive

Installation Zgoubidoo using ``poetry``
--------------------------------------------

Assuming you have :code:`poetry` and :code:`python` installed on your system, go to the location of the library and simply use
these commands::

    cd path/to/zgoubidoo
    poetry install --without dev,docs

.. note::

    Zgoubidoo uses python version >=3.8.1 and < 3.11

Zgoubidoo can be subsequently updated by running the following::

    git pull origin master
    poetry update

.. note::

    You can install a independent python environment with :code:`pyenv` (https://github.com/pyenv/pyenv) and
    :code:`pyenv-virtualenv` (https://github.com/pyenv/pyenv-virtualenv) ::

        pyenv install 3.8.13
        pyenv virtualenv 3.8.13 py38

    Then, activate your Python environment and install :code:`zgoubidoo` with Poetry ::

        pyenv local py38
        poetry install --without dev,docs


If you would like to have extra-dependencies such as sphinx or pytest, you can use ::

    poetry install --with dev,docs

Creating a Python environment with Conda
----------------------------------------
The Zgoubidoo repository contains a ``conda`` environment file that can be used to create a complete Python 3.7
environment suitable for Zgoubidoo::

    cd path_to_zgoubidoo
    conda env create --file environment.yml

or you can give a custom name to the environment with::

    conda env create --file environment.yml --name your_custom_name

Installation Zgoubidoo using :code:`poetry`
-------------------------------------------
The first step is to activate your Python environment (only needed if you do not use a global
installation of Python. On Mac OS if you use the Python ``brew`` installation you should already have Python
available from your path). With ``conda`` proceed like this::

    conda activate zgoubidoo

where `zgoubidoo` is the name of the environment created by default.

Zgoubidoo can then be installed using :code:`poetry` as described in the above section.

Using Zgoubidoo with Jupyter Lab
--------------------------------
A working installation of :code:`jupyter lab` is directly include when you install :code:`zgoubidoo`.
Depending where your python is coming from (:code:`pyenv` or :code:`conda`), you can activate your
environment::

    conda activate zgoubidoo
    pyenv shell py38

You can now simply launch::

    jupyter-lab

From there you can create a new notebook and simply import Zgoubidoo::

    import zgoubidoo

