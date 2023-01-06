import os

import numpy as _np
import pandas as _pd
from georges_core import twiss
from georges_core.sequences import TwissSequence

import zgoubidoo
from zgoubidoo import ureg as _
from zgoubidoo.commands import BeamTwiss, Dipole


def check_optics(twiss_madx: _pd.DataFrame, twiss_zgoubi: _pd.DataFrame):
    s_madx = twiss_madx["S"].apply(lambda e: e.m_as("m")).values
    betx_madx = twiss_madx["BETX"].values
    bety_madx = twiss_madx["BETY"].values
    alfx_madx = twiss_madx["ALFX"].values
    alfy_madx = twiss_madx["ALFY"].values
    dispx_madx = twiss_madx["DX"].values
    dispxp_madx = twiss_madx["DPX"].values

    s_zgoubi = twiss_zgoubi["S"].values

    betx_zgoubi = twiss_zgoubi["BETA11"].values
    bety_zgoubi = twiss_zgoubi["BETA22"].values
    alfx_zgoubi = twiss_zgoubi["ALPHA11"].values
    alfy_zgoubi = twiss_zgoubi["ALPHA22"].values
    dispx_zgoubi = twiss_zgoubi["DISP1"].values
    dispxp_zgoubi = twiss_zgoubi["DISP2"].values

    betx_zgoubi_madx = _np.interp(s_madx, s_zgoubi, betx_zgoubi)
    bety_zgoubi_madx = _np.interp(s_madx, s_zgoubi, bety_zgoubi)
    alfx_zgoubi_madx = _np.interp(s_madx, s_zgoubi, alfx_zgoubi)
    alfy_zgoubi_madx = _np.interp(s_madx, s_zgoubi, alfy_zgoubi)
    dispx_zgoubi_madx = _np.interp(s_madx, s_zgoubi, dispx_zgoubi)
    dispxp_zgoubi_madx = _np.interp(s_madx, s_zgoubi, dispxp_zgoubi)

    _np.testing.assert_allclose(betx_madx, betx_zgoubi_madx, rtol=1e-2)
    _np.testing.assert_allclose(bety_madx, bety_zgoubi_madx, rtol=5e-2)
    _np.testing.assert_allclose(alfx_madx, alfx_zgoubi_madx, rtol=1)
    _np.testing.assert_allclose(alfy_madx, alfy_zgoubi_madx, rtol=1)
    _np.testing.assert_allclose(dispx_madx, dispx_zgoubi_madx, atol=5e-2)
    _np.testing.assert_allclose(dispxp_madx, dispxp_zgoubi_madx, atol=5e-2)

    # Test more precisely the IP
    ip_position = twiss_madx.loc["IP"]["S"].m_as("m")
    betx_zgoubi_ip = _np.interp(ip_position, s_zgoubi, betx_zgoubi)
    bety_zgoubi_ip = _np.interp(ip_position, s_zgoubi, bety_zgoubi)
    alfx_zgoubi_ip = _np.interp(ip_position, s_zgoubi, alfx_zgoubi)
    alfy_zgoubi_ip = _np.interp(ip_position, s_zgoubi, alfy_zgoubi)
    dispx_zgoubi_ip = _np.interp(ip_position, s_zgoubi, dispx_zgoubi)
    dispxp_zgoubi_ip = _np.interp(ip_position, s_zgoubi, dispxp_zgoubi)

    _np.testing.assert_allclose(twiss_madx.loc["IP"]["BETX"], betx_zgoubi_ip, atol=1e-3)
    _np.testing.assert_allclose(twiss_madx.loc["IP"]["BETY"], bety_zgoubi_ip, atol=1e-3)
    _np.testing.assert_allclose(twiss_madx.loc["IP"]["ALFX"], alfx_zgoubi_ip, atol=1e-2)
    _np.testing.assert_allclose(twiss_madx.loc["IP"]["ALFY"], alfy_zgoubi_ip, atol=1e-2)
    _np.testing.assert_allclose(twiss_madx.loc["IP"]["DX"], dispx_zgoubi_ip, atol=1e-3)
    _np.testing.assert_allclose(twiss_madx.loc["IP"]["DPX"], dispxp_zgoubi_ip, atol=1e-3)


def test_lhec():
    # Convert file from MAD-X
    input_madx = TwissSequence(path=f"{os.getcwd()}/tests", filename="test45degspreader.outx")
    zi = zgoubidoo.Input.from_sequence(
        sequence=input_madx,
        beam=BeamTwiss(kinematics=input_madx.kinematics),
        with_survey=True,
        with_survey_reference=True,
        converters={
            "sbend": zgoubidoo.converters.sbend_to_zgoubi,
            "quadrupole": zgoubidoo.converters.quadrupole_to_zgoubi,
        },
        options={
            "sbend": {"command": Dipole},
        },
    )
    zi.XPAS = 10 * _.cm

    # Check if the survey is the same
    survey_zgoubi = zi.survey(output=True, with_reference_trajectory=True, reference_kinematics=input_madx.kinematics)[
        "exit_s"
    ]
    survey_zgoubi = survey_zgoubi.apply(lambda e: e.m_as("m"))
    survey_madx = input_madx.df["S"].apply(lambda e: e.m_as("m"))
    survey = _pd.merge(survey_zgoubi, survey_madx, left_index=True, right_index=True)
    _np.testing.assert_allclose(survey["exit_s"].values, survey["S"].values, rtol=1e-3)

    # Ensure plotting is working
    artist = zgoubidoo.vis.ZgoubidooPlotlyArtist(width=1200)
    artist.fig["layout"]["xaxis"]["title"] = "X (m)"
    artist.fig["layout"]["yaxis"]["title"] = "Y (m)"
    artist.plot_beamline(beamline=zi, with_frames=True, with_apertures=True, with_map=True)

    # Compute the Twiss
    zr_twiss = zgoubidoo.Zgoubi()(zi).collect()
    tm = zgoubidoo.twiss.compute_transfer_matrix(
        beamline=zi,
        tracks=zr_twiss.tracks_frenet,
    )
    results_twiss = twiss.Twiss(twiss_init=input_madx.betablock)(matrix=tm)

    # Validation with MAD-X
    check_optics(input_madx.df, results_twiss)

    # Plot the comparison
    artist = zgoubidoo.vis.ZgoubidooPlotlyArtist(width=1200).plot_twiss(
        beamline=zi,
        twiss=results_twiss,
        twiss_madx=input_madx.df,
    )
    artist.plot_twiss(beamline=zi, twiss=results_twiss, twiss_madx=input_madx.df)
