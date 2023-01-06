# Zgoubidoo: a modern Python 3 interface to the Zgoubi particle tracking code

[![ci](https://github.com/ULB-Metronu/zgoubidoo/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/ULB-Metronu/georges-core/actions/workflows/ci.yml)
[![documentation](https://github.com/ULB-Metronu/zgoubidoo/actions/workflows/documentation.yml/badge.svg?branch=master)](https://github.com/ULB-Metronu/zgoubidoo/actions/workflows/documentation.yml)
![Python](docs/_static/python_versions.svg)
![version](https://img.shields.io/badge/version-2022.1-blue)

[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=ULB-Metronu_zgoubidoo&metric=bugs)](https://sonarcloud.io/summary/new_code?id=ULB-Metronu_zgoubidoo)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ULB-Metronu_zgoubidoo&metric=coverage)](https://sonarcloud.io/summary/new_code?id=ULB-Metronu_zgoubidoo)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=ULB-Metronu_zgoubidoo&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=ULB-Metronu_zgoubidoo)

[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Gitter](https://badges.gitter.im/ULB-Metronu/zgoubidoo.svg)](https://gitter.im/ULB-Metronu/zgoubidoo?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

<img src="docs/_static/zgoubidoo.png" style="float: right; width: 150px;">

Zgoubidoo is a Python 3 interface for [Zgoubi](https://sourceforge.net/projects/zgoubi/), a ray-tracing code for beam
dynamics simulations. Zgoubido is intended to follow a modern Python design and aims at being easy to use. Interactive
use with iPython or Jupyter Notebook is supported and encouraged. As such Zgoubidoo can be viewed as a 'Zgoubi for the
mere mortal' interface.

Zgoubi is a ray-tracing (tracking) code for beam dynamics simulations. Many magnetic and electric elements are
supported, as well as multiple other features, such as spin tracking. It is maintained by François Méot on
[SourceForge](https://sourceforge.net/projects/zgoubi/).


## Documentation

[**Zgoubidoo's documentation**](https://ulb-metronu.github.io/zgoubidoo/) is hosted on Github Pages.


## Design goals

- **Fully featured interface to Zgoubi**: all functionalities of Zgoubi are supported through the Python interface;
- **Ease of use**: a simple tracking study and its visualization can be set up in just a few lines of code;
- Written in **high-quality Python 3 with type-hints**;
- The library interface and use-n-feel must be **Jupyter notebook friendly**;
- Decoupling between a low-level use (simple Python interface to generate Zgoubi input files and run the executable)
  and high-level interfaces with more abstraction (`sequences`, etc.);
- Strong support and enforcement of physical units: **no units conversion nightmare**, you can freely use whatever units
  set you like, the conversion into Zgoubi's default units is automatically handled.
