"""Loaders and converters for a variety of formats (MAD-X, etc.).

The `converters` module is a collection of

- **converters**: read external data table (e.g. a MAD-X Twiss table) onto a standard Pandas format (DataFrame or Series);
- **converters**: convert 'commands' to Zgoubidoo commands (e.g. read a MAD-X drift and convert it to Zgoubidoo).

This module is meant to be extensible to handle a wide variety of formats. To allow for maximal flexibility and to
encourage the development of converters even for exotic cases, no specific configuration is in place: we favor convention.
The MAD-X converters and converters are to be considered as typical examples and conventions that other modules should
follow.


"""
