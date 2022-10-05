"""

"""
from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as _np
import pandas as _pd
import quaternion
import zgoubidoo.commands
if TYPE_CHECKING:
    from .input import Input as _Input


class CoordinateTransformationType(type):
    def transform(self, tracks: _pd.DataFrame, beamline: _Input):
        pass


class CoordinateTranformation(metaclass=CoordinateTransformationType):
    @staticmethod
    def construct_rays(element: zgoubidoo.commands.Patchable,
                       element_tracks: _pd.DataFrame,
                       tracks: _pd.DataFrame,
                       norm: float = 1.0) -> _pd.DataFrame:
        """

        Args:
            element:
            element_tracks:
            tracks: a dataframe containing the raw tracking data (from a zgoubi.plt file)
            norm: the norm of the ray to be constructed

        Returns:
            the (transformed) tracks DataFrame
        """
        label = element.LABEL1
        _ = _np.zeros((element_tracks.shape[0], 3))
        _[:, 2] = -element_tracks['T'].values
        q1 = quaternion.from_rotation_vector(_)
        _[:, 2] = 0
        _[:, 1] = element_tracks['P'].values
        q2 = quaternion.from_rotation_vector(_)
        q = q2 * q1
        end_points = _np.matmul(_np.linalg.inv(quaternion.as_rotation_matrix(q)), _np.array([norm, 0.0, 0.0]))
        tracks.loc[tracks.LABEL1 == label, 'XR'] = end_points[:, 0]
        tracks.loc[tracks.LABEL1 == label, 'YR'] = end_points[:, 1]
        tracks.loc[tracks.LABEL1 == label, 'ZR'] = end_points[:, 2]

        return tracks

    @classmethod
    def transform(cls, tracks: _pd.DataFrame, beamline: _Input):
        pass


class GlobalCoordinateTransformation(CoordinateTranformation):
    @classmethod
    def transform(cls, tracks: _pd.DataFrame, beamline: _Input, reference_frame: str = 'entry_integration'):
        for label in tracks.LABEL1.unique():
            e = getattr(beamline, label)
            assert isinstance(e, zgoubidoo.commands.Patchable)
            label = e.LABEL1

            # Adjust the variables to a common set for all elements
            e.adjust_tracks_variables(tracks)

            # Compute rays
            t = tracks.query(f"LABEL1 == '{label}'")
            CoordinateTranformation.construct_rays(e, t, tracks)
            t = tracks.query(f"LABEL1 == '{label}'")

            # Rotate cartesian coordinates to the global reference frame
            element_rotation = _np.linalg.inv(getattr(e, reference_frame).get_rotation_matrix())
            u = _np.dot(t[['X', 'Y', 'Z']].values, element_rotation)

            # Translate all coordinates to the global reference frame
            origin = getattr(e, reference_frame).origin
            tracks.loc[tracks.LABEL1 == label, 'XG'] = u[:, 0] + origin[0].m_as('m')
            tracks.loc[tracks.LABEL1 == label, 'YG'] = u[:, 1] + origin[1].m_as('m')
            tracks.loc[tracks.LABEL1 == label, 'ZG'] = u[:, 2] + origin[2].m_as('m')

            # Transform (rotate and translate) all rays coordinates to the global reference frame
            v = _np.dot(t[['XR', 'YR', 'ZR']].values, element_rotation)
            tracks.loc[tracks.LABEL1 == label, 'XRG'] = v[:, 0]
            tracks.loc[tracks.LABEL1 == label, 'YRG'] = v[:, 1]
            tracks.loc[tracks.LABEL1 == label, 'ZRG'] = v[:, 2]

            # Transform the angles in the global reference frame
            tracks.loc[tracks.LABEL1 == label, 'TG'] = _np.arcsin(v[:, 1])
            tracks.loc[tracks.LABEL1 == label, 'PG'] = _np.arcsin(v[:, 2])

        return tracks


class FrenetCoordinateTransformation(CoordinateTranformation):
    @classmethod
    def transform(cls, tracks: _pd.DataFrame, beamline: _Input):
        for label in tracks.LABEL1.unique():
            e = getattr(beamline, label)
            assert isinstance(e, zgoubidoo.commands.Patchable)
            label = e.LABEL1

            # Adjust the variables to a common set for all elements
            e.adjust_tracks_variables(tracks)
            t = tracks.query(f"LABEL1 == '{label}'")

            # Rotate cartesian coordinates to the global reference frame
            element_rotation = _np.linalg.inv(getattr(e, 'frenet_orientation').get_rotation_matrix())
            u = _np.dot(t[['SREF', 'YT', 'ZT']].values, element_rotation)
            u0 = t[['SREF', 'YT0', 'ZT0']].values
            v = _np.dot(t[['SREF', 'T', 'P']].values, element_rotation)
            v0 = t[['SREF', 'To', 'Po']].values

            # Translate all coordinates to the global reference frame
            tracks.loc[tracks.LABEL1 == label, 'YT'] = u[:, 1]
            tracks.loc[tracks.LABEL1 == label, 'YT0'] = u0[:, 1]
            tracks.loc[tracks.LABEL1 == label, 'ZT'] = u[:, 2]
            tracks.loc[tracks.LABEL1 == label, 'ZT0'] = u0[:, 2]
            tracks.loc[tracks.LABEL1 == label, 'T'] = v[:, 1]
            tracks.loc[tracks.LABEL1 == label, 'T0'] = v0[:, 1]
            tracks.loc[tracks.LABEL1 == label, 'P'] = v[:, 2]
            tracks.loc[tracks.LABEL1 == label, 'P0'] = v0[:, 2]

        return tracks
