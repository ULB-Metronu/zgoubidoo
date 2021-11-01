# Zgoubidoo: a modern Python 3 interface to the Zgoubi particle tracking code

[![develop](https://github.com/ULB-Metronu/zgoubidoo/actions/workflows/develop.yaml/badge.svg)](https://github.com/ULB-Metronu/zgoubidoo/actions/workflows/develop.yaml)

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
