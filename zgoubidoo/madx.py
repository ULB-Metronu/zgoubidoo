"""Provides an interface to run MAD-X from Python; supports multiprocessing and concurrent programming.

.. seealso::

    The full `Zgoubi User Guide`_ can also be consulted for reference.

    .. _Zgoubi User Guide: https://sourceforge.net/projects/zgoubi/

"""
from __future__ import annotations
from typing import List, Mapping, Optional, Tuple, Union
import logging
import tempfile
import pandas as _pd
from .executable import Executable
from .input import MappedParametersType as _MappedParametersType
from .input import MappedParametersListType as _MappedParametersListType
from .output.madx import load_madx_twiss_table, load_madx_twiss_headers

__all__ = ['MadException', 'MadResults', 'Mad']
_logger = logging.getLogger(__name__)


class MadException(Exception):
    """Exception raised for errors when running Zgoubi."""

    def __init__(self, m):
        self.message = m


class MadResults:
    """Results from a MAD-X executable run."""
    def __init__(self, results: List[Mapping]):
        """
        `MadResults` is used to store results and outputs from a single or multiple MAD-X runs. It is instanciated from
        a list of dictionnaries containing the results (each one being a mapping between `MappedParameters` (to identify
        from which run the results are from) and the results themselves (also a dictionnary)).

        Methods and properties of `MadResults` are used to access and process individual or multiple results. In
        particular it is possible to extract a set of tracks from the results.

        Examples:
            >>> 1 + 1 # TODO

        Args:
            results: a list of dictionnaries structure with the Zgoubi run information and errors.
        """
        self._results: List[Mapping] = results
        self._twiss: Optional[_pd.DataFrame] = None
        self._twiss_header: Optional[_pd.Series] = None
        self._matrix: Optional[_pd.DataFrame] = None
        self._srloss: Optional[_pd.DataFrame] = None

    @classmethod
    def merge(cls, *results: MadResults):
        """Merge multiple MadResults into one.

        Args:
            results: list of `MadResults` to copy

        Returns:
            a new `MadResults` instance containing the concatenated results.
        """
        return cls([rr for r in results for rr in r._results])

    def __len__(self) -> int:
        """Length of the results list."""
        return len(self._results)

    def __copy__(self) -> MadResults:
        """Shallow copy operation."""
        return MadResults(self._results)

    def __getitem__(self, item: int):
        """Retrieve results from the list using a numeric index."""
        return self._results[item]

    def get_twiss(self,
                  parameters: Optional[_MappedParametersListType] = None,
                  force_reload: bool = False
                  ) -> _pd.DataFrame:
        """
        Collects all Twiss data from the different MAD-X instances matching the given parameters list
        in the results and concatenate them.

        Args:
            parameters:
            force_reload:

        Returns:
            A concatenated DataFrame with all the Twiss data in the result matching the parameters list.
        """
        if self._twiss is not None and parameters is None and force_reload is False:
            return self._twiss
        twiss = list()
        for k, r in self.results:
            if parameters is None or k in parameters:
                try:
                    try:
                        p = r['path'].name
                    except AttributeError:
                        p = r['path']
                    twiss.append(load_madx_twiss_table(path=p))
                    for kk, vv in k.items():
                        twiss[-1][f"{kk}"] = vv
                except FileNotFoundError:
                    _logger.warning(
                        f"Unable to read and load the Twiss files required to collect the Twiss data for path "
                        "{r['path']}."
                    )
                    continue
        if len(twiss) > 0:
            twiss = _pd.concat(twiss)
        else:
            twiss = _pd.DataFrame()
        if parameters is None:
            self._twiss = twiss
        return twiss

    @property
    def twiss(self) -> _pd.DataFrame:
        """
        Collects all tracks from the different Zgoubi instances in the results and concatenate them.

        Returns:
            A concatenated DataFrame with all the tracks in the result.
        """
        return self.get_twiss()

    @property
    def results(self) -> List[Tuple[_MappedParametersType, Mapping]]:
        """Raw information from the MAD-X run.

        Provides the raw data structures from the Zgoubi runs.

        Returns:
            a list of mappings.
        """
        return [(r['mapping'], r) for r in self._results]

    @property
    def paths(self) -> List[Tuple[_MappedParametersType, Union[str, tempfile.TemporaryDirectory]]]:
        """Path of all the directories for the runs present in the results.

        Returns:
            a list of directories.
        """
        return [(m, r['path']) for m, r in self.results]

    @property
    def mappings(self) -> List[_MappedParametersType]:
        """Parametric mappings of all the runs present in the results.

        Returns:
            a list of parametric mappings.
        """
        return [m for m, r in self.results]

    def print(self, what: str = 'stdout'):
        """Helper function to print the raw results from a MAD-X run."""
        for m, r in self.results:
            print(f"Results for mapping {m}")
            print('\n'.join(r[what]))
            print("========================")


class Mad(Executable):
    """High level interface to run MAD-X from Python."""

    EXECUTABLE_NAME: str = 'madx'
    """Default name of the MAD-X executable."""

    INPUT_FILENAME: str = 'input.mad'
    """Name of the input file for the executable."""

    COMMAND_ARGUMENT: bool = True
    """A flag to indicate if the input file name must be used as an argument to the command."""

    def __init__(self, executable: str = EXECUTABLE_NAME, path: str = None, n_procs: Optional[int] = None):
        """
        `Mad` is responsible for running the MAD-X executable within Zgoubidoo. It will run MAD-X as a subprocess
        and offers a variety of concurency and parallelisation features.

        The `Mad` object is an interface to the MAD-X executable. The executable can be found automatically or its
        name and path can be specified.

        The MAD-X executable is called on an instance of `Input` specifying a list of paths containing MAD-X input
        files. Multiple instances can thus be run in parallel.

        TODO details on concurrency

        Args:
            - executable: name of the MAD-X executable
            - path: path to the MAD-X executable
            - n_procs: maximum number of MAD-X simulations to be started in parallel

        """
        super().__init__(executable=executable, results_type=MadResults, path=path, n_procs=n_procs)
