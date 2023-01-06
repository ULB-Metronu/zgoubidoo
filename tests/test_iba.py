"""Test of IBA code."""

from zgoubidoo.commands.contrib.iba import B3G, CGTR
from zgoubidoo.units import _ureg


def test_cgtr():
    cgtr = CGTR(
        b3g=B3G(
            magnet_opening=70 * _ureg.degree,
            poles_opening=60 * _ureg.degree,
            entrance_pole_trim=1.125 * _ureg.degree,
            exit_pole_trim=1.125 * _ureg.degree,
            entrance_fringe_lambda=9 * _ureg.cm,
            exit_fringe_lambda=9 * _ureg.cm,
        ),
    )
    cgtr.q1g.current = 1
    cgtr.q2g.current = 1
    cgtr.q3g.current = 1
    cgtr.q4g.current = 1
    cgtr.q5g.current = 1
    cgtr.q6g.current = 1
    cgtr.q7g.current = 1
    # spots = cgtr.spots([(0.0, 0.0), (-20.0, 2.0), (20.0, 2.0)])
    cgtr.line.cleanup()
