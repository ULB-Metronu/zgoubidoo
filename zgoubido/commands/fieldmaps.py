from .commands import Command


class Brevol(Command):
    """1-D uniform mesh magnetic field map."""
    KEYWORD = 'BREVOL'


class CartesianMesh(Command):
    """"2-D Cartesian uniform mesh magnetic field map."""
    KEYWORD = 'CARTEMES'


class Map2D(Command):
    """2-D Cartesian uniform mesh field map - arbitrary magnetic field."""
    KEYWORD = 'MAP2D'


class Map2DElectric(Command):
    """2-D Cartesian uniform mesh field map - arbitrary electric field."""
    KEYWORD = 'MAP2D-E'


class Poisson(Command):
    """Read magnetic field data from POISSON output."""
    KEYWORD = 'POISSON'


class PolarMesh(Command):
    """2-D polar mesh magnetic field map."""
    KEYWORD = 'POLARMES'


class Tosca(Command):
    """2-D and 3-D Cartesian or cylindrical mesh field map."""
    KEYWORD = 'TOSCA'
