"""High-level interface for Zgoubi using sequences and beams.

"""
from __future__ import annotations
from typing import Optional, List, Tuple, Mapping, Union
from dataclasses import dataclass
import pandas as _pd
from ..commands import particules
from ..commands.particules import ParticuleType as _ParticuleType
from ..commands.particules import Proton as _Proton
from ..kinematics import Kinematics as _Kinematics
from .elements import Element as _Element
from .. import ureg as _ureg

__all__ = ['ZgoubidooSequenceException',
           'SequenceMetadata',
           'Sequence',
           ]


class ZgoubidooSequenceException(Exception):
    """Exception raised for errors when using zgoubidoo.Sequence"""

    def __init__(self, m):
        self.message = m


@dataclass
class SequenceMetadata:
    """TODO"""
    data: _pd.Series = None
    kinematics: _Kinematics = None
    particle: _ParticuleType = None

    def __post_init__(self):
        # Try to infer the particle type from the metadata
        try:
            self.particle = self.particle or getattr(particules, str(self.data['PARTICLE'].capitalize()))
        except KeyError:
            self.particle = _Proton

        # Try to infer the kinematics from the metadata
        try:
            self.kinematics = self.kinematics or _Kinematics(float(self.data['PC']) * _ureg.GeV_c,
                                                             particle=self.particle)
        except KeyError:
            pass
        try:
            self.kinematics = self.kinematics or _Kinematics(float(self.data['ENERGY']) * _ureg.GeV,
                                                             particle=self.particle)
        except KeyError:
            pass
        try:
            self.kinematics = self.kinematics or _Kinematics(float(self.data['GAMMA']),
                                                             particle=self.particle)
        except KeyError:
            pass


class Sequence:
    """Sequence.

    """
    def __init__(self,
                 name: str = '',
                 data: Optional[List[Tuple[_Element,
                                           _ureg.Quantity,
                                           _ureg.Quantity,
                                           _ureg.Quantity]]] = None,
                 metadata: Optional[SequenceMetadata] = None,
                 reference_placement: str = 'ENTRY',
                 element_keys: Optional[Mapping[str, str]] = None,
                 ):
        """

        Args:
            name: the name of the physics
            data: the list of commands composing the physics
            metadata:
            reference_placement:
            element_keys:
        """
        self._name: str = name
        self._data: List[Tuple[_Element, _ureg.Quantity, _ureg.Quantity, _ureg.Quantity]] = data or []
        self._metadata = metadata
        self._reference_placement = reference_placement
        self._element_keys = element_keys or {
            k: k for k in [
                'L',
            ]
        }

    def __repr__(self):
        return repr(self._data)

    @property
    def name(self) -> str:
        """Provides the name of the physics."""
        return self._name

    @property
    def metadata(self) -> SequenceMetadata:
        """Provides the metadata associated with the sequence."""
        return self._metadata

    @property
    def kinematics(self) -> _Kinematics:
        """Provides the kinematics data associated with the sequence metadata."""
        return self.metadata.kinematics

    @property
    def particle(self) -> _ParticuleType:
        """Provides the particle type associated with the sequence metadata."""
        return self.metadata.particle

    def to_df(self) -> _pd.DataFrame:
        """TODO"""
        df = _pd.DataFrame([{**e[0].data, **{
            'AT_ENTRY': e[1],
            'AT_CENTER': e[2],
            'AT_EXIT': e[3]
        }} for e in self._data])
        df.name = self.name
        return df

    def place(self,
              element_or_sequence: Union[_Element, Sequence],
              at: Optional[_ureg.Quantity] = None,
              at_entry: Optional[_ureg.Quantity] = None,
              at_center: Optional[_ureg.Quantity] = None,
              at_exit: Optional[_ureg.Quantity] = None,
              ):
        """

        Args:
            element_or_sequence:
            at:
            at_center:
            at_entry:
            at_exit:

        Returns:

        """
        ats = locals()
        if at is not None:
            ats[f"at_{self._reference_placement.lower()}"] = at
        self._data.append((element_or_sequence, ats['at_entry'], ats['at_center'], ats['at_exit']))

    @classmethod
    def from_madx_twiss(cls,
                        filename: str = 'twiss.outx',
                        path: str = '.',
                        columns: List = None,
                        options: Optional[dict] = None,
                        converters: Optional[dict] = None,
                        elements_database: Optional[dict] = None,
                        from_element: str = None,
                        to_element: str = None,) -> Sequence:
        """
        TODO
        Args:
            filename: name of the Twiss table file
            path: path to the Twiss table file
            columns: the list of columns in the Twiss file
            options:
            converters:
            elements_database:
            from_element:
            to_element:

        Returns:

        Examples:
            >>> lhec = zgoubidoo.from_madx_twiss(filename='lhec.outx', path='.')
        """
        madx_converters = {k.split('_')[2].upper(): getattr(sys.modules[__name__], k)
                           for k in globals().keys() if k.startswith('create_madx')}
        conversion_functions = {**madx_converters, **(converters or {})}
        elements_database = elements_database or {}
        options = options or {}
        twiss_headers = load_madx_twiss_headers(filename, path)
        twiss_table = load_madx_twiss_table(filename, path, columns).loc[from_element:to_element]
        particle_name = twiss_headers['PARTICLE'].capitalize()
        p = getattr(particules, particle_name if particle_name != 'Default' else 'Proton')
        k = Kinematics(float(twiss_headers['PC']) * _ureg.GeV_c, particle=p)
        converted_table: list = list(
            twiss_table.apply(
                lambda _: elements_database.get(_.name,
                                                conversion_functions.get(_['KEYWORD'], lambda _, __, ___: None)
                                                (_, k, options.get(_['KEYWORD'], {}))
                                                ),
                axis=1
            ).values
        )
        return cls(name=twiss_headers['NAME'],
                         sequence=list(itertools.chain.from_iterable(converted_table)),
                         metadata=twiss_headers,
                         particle=p,
                         table=twiss_table,
                         initial_twiss=get_twiss_values(twiss_table),
                         )
