"""High-level interface (API) for Zgoubi.

The high-level API adds a level of abstraction on top of low-level API (using `Input` and `Command`).
"""
from .sequence import Sequence, ZgoubidooSequenceException
from .srloss import srloss
