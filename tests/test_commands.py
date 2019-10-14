import pytest
from zgoubidoo.commands import Drift


@pytest.fixture()
def foo():
    pass


def test_drift_input():
    drift = Drift()
    assert isinstance(str(drift), str)
