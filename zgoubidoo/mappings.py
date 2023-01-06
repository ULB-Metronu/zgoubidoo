"""
TODO
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import List, Mapping, Sequence, Tuple, Union

from . import Q_ as _Q

ParametersMappingType = Mapping[str, Sequence[Union[_Q, float]]]
"""Type alias for a parametric mapping of string keys and values."""

ParametersMappingListType = List[ParametersMappingType]
"""Type alias for a list of parametric mappings."""

MappedParametersType = Mapping[str, Union[_Q, float, str]]
"""Type alias for a dictionnary of parametric keys and values."""

MappedParametersListType = List[MappedParametersType]
"""Type alias for a list of mapped parameters."""

flatten = itertools.chain.from_iterable
"""Helper function to flatten an iterable."""


@dataclass
class ParametricMapping:
    """Abstraction for multi-dimensional parametric mappings.

    Main feature is to compute the complete "cross product" of the different parameters to support multi-dimensional
    mapping. It also accounts for "coupled" variables.

    Note:
        TODO FIX Using the special value "LABEL" for the first element of the mapping's label deactivate the sequence
        adjustment mechanism.

    See also:
        for implementation details, see also https://codereview.stackexchange.com/q/211121/52027 .

    Examples:
        >>> pm = ParametricMapping([{('B3G', 'B1'): [1.0, 2.0], ('B1G', 'B1'): [11.0, 12.0]}, {('B2G', 'B1'): [1.5, 2.5, 3.5]}])
        >>> pm.combinations
        [{('B3G', 'B1'): 1.0, ('B1G', 'B1'): 11.0, ('B2G', 'B1'): 1.5},
         {('B3G', 'B1'): 1.0, ('B1G', 'B1'): 11.0, ('B2G', 'B1'): 2.5},
         {('B3G', 'B1'): 1.0, ('B1G', 'B1'): 11.0, ('B2G', 'B1'): 3.5},
         {('B3G', 'B1'): 2.0, ('B1G', 'B1'): 12.0, ('B2G', 'B1'): 1.5},
         {('B3G', 'B1'): 2.0, ('B1G', 'B1'): 12.0, ('B2G', 'B1'): 2.5},
         {('B3G', 'B1'): 2.0, ('B1G', 'B1'): 12.0, ('B2G', 'B1'): 3.5}]
    """

    mappings: ParametersMappingListType = field(default_factory=lambda: [{}])

    @property
    def labels(self) -> Tuple[str]:
        """List of labels of the parametric mapping."""
        return tuple(flatten(self.mappings))

    @property
    def pools(self) -> List[List[Sequence[Union[_Q, float]]]]:
        """All combinations of values for the parametric mapping."""
        return [list(map(tuple, zip(*arg.values()))) for arg in self.mappings]

    @property
    def combinations(self) -> MappedParametersListType:
        """Cartesian product adapted to work with dictionaries, roughly similar to `itertools.product`.

        Returns:
            a list of the cartesian product of the mappings.

        See also:
            - https://docs.python.org/3/library/itertools.html#itertools.product
            - https://codereview.stackexchange.com/q/211121/52027
        """
        pool_values = [flatten(term) for term in itertools.product(*self.pools)]
        return [dict(zip(self.labels, v)) for v in pool_values] or [{}]

    def __add__(self, other):
        """TODO might need to be adapted or with iadd also ?"""
        if len(self.labels) == 0:
            self.mappings = other.mappings
        elif len(other.labels) == 0:
            return self
        else:
            self.mappings += other.mappings
        return self
