import doctest
import zgoubidoo

VERBOSITY = False

doctest.testmod(zgoubidoo, verbose=VERBOSITY)
doctest.testmod(zgoubidoo.frame, verbose=VERBOSITY)
doctest.testmod(zgoubidoo.input, verbose=VERBOSITY)
doctest.testmod(zgoubidoo.physics, verbose=VERBOSITY)
