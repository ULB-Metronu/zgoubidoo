import pytest
from zgoubidoo import ureg as _ureg
from zgoubidoo import Kinematics


def test_proton_total_energy():
    kin = Kinematics(1 * _ureg.GeV)
    assert kin.etot.m_as('GeV') == pytest.approx(1)
    assert kin.ekin.m_as('MeV') == pytest.approx(61.72797)
    assert kin.momentum.m_as('GeV_c') == pytest.approx(0.34589824763892485)
    assert kin.brho.m_as('meter * tesla') == pytest.approx(1.153792360043043)
    assert kin.range.m_as('cm') == pytest.approx(3.23758370)
    assert kin.beta == pytest.approx(0.345898)
    assert kin.gamma == pytest.approx(1.0657889)


def test_proton_kinetic_energy():
    kin = Kinematics(61.72797 * _ureg.MeV)
    assert kin.etot.m_as('GeV') == pytest.approx(1)
    assert kin.ekin.m_as('MeV') == pytest.approx(61.72797)
    assert kin.momentum.m_as('GeV_c') == pytest.approx(0.34589824763892485)
    assert kin.brho.m_as('meter * tesla') == pytest.approx(1.153792360043043)
    assert kin.range.m_as('cm') == pytest.approx(3.23758370)
    assert kin.beta == pytest.approx(0.345898)
    assert kin.gamma == pytest.approx(1.0657889)


def test_proton_momentum():
    kin = Kinematics(200 * _ureg.MeV)
    assert kin.ekin.m_as('MeV') == pytest.approx(200)


def test_proton_range():
    kin = Kinematics(200 * _ureg.MeV)
    assert kin.ekin.m_as('MeV') == pytest.approx(200)


def test_proton_beta():
    kin = Kinematics(200 * _ureg.MeV)
    assert kin.ekin.m_as('MeV') == pytest.approx(200)


def test_kinematics_gamma():
    kin = Kinematics(200 * _ureg.MeV)
    assert kin.ekin.m_as('MeV') == pytest.approx(200)