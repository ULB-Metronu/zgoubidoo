import doctest
import zgoubidoo
import zgoubidoo.units

VERBOSITY = False

doctest.testmod(zgoubidoo, verbose=VERBOSITY)
doctest.testmod(zgoubidoo.frame, verbose=VERBOSITY)
doctest.testmod(zgoubidoo.input, verbose=VERBOSITY)
doctest.testmod(zgoubidoo.kinematics, verbose=VERBOSITY)
doctest.testmod(zgoubidoo.commands, verbose=VERBOSITY)
doctest.testmod(zgoubidoo.units, verbose=VERBOSITY)
