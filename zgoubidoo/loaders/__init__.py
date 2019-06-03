"""Loaders and converters for a variety of formats (MAD-X, etc.).

The `loaders` module is a collection of

- **loaders**: read external data table (e.g. a MAD-X Twiss table) onto a standard Pandas format (DataFrame or Series);
- **converters**: convert 'commands' to Zgoubidoo commands (e.g. read a MAD-X drift and convert it to Zgoubidoo).

This module is meant to be extensible to handle a wide variety of formats. To allow for maximal flexibility and to
encourage the development of loaders even for exotic cases, no specific configuration is in place: we favor convention.
The MAD-X loaders and converters are to be considered as typical examples and conventions that other modules should
follow.


"""
from .madx import load_madx_twiss_headers, load_madx_twiss_table, from_madx_twiss, get_twiss_values
from .transport import load_transport_input, from_transport_input
