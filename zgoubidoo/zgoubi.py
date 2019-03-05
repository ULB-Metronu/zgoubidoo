"""Provides an interface to run Zgoubi from Python; supports multiprocessing and concurrent programming.

.. seealso::

    The full `Zgoubi User Guide`_ can also be consulted for reference.

    .. _Zgoubi User Guide: https://sourceforge.net/projects/zgoubi/

"""
from __future__ import annotations
from typing import List, Mapping, Iterable, Optional, Tuple, Dict, Callable, Union
import logging
import shutil
import tempfile
import os
import sys
import re
import multiprocessing
from concurrent.futures import ThreadPoolExecutor as _ThreadPoolExecutor
from concurrent.futures import Future as _Future
import subprocess as sub
import pandas as _pd
from .input import Input
from .input import MappedParametersType as _MappedParametersType
from .input import MappedParametersListType as _MappedParametersListType
from .input import PathsDictType as _PathDict
from .input import ZGOUBI_INPUT_FILENAME as _ZGOUBI_INPUT_FILENAME
from .output import read_plt_file, read_matrix_file, read_srloss_file

__all__ = ['ZgoubiException', 'ZgoubiResults', 'Zgoubi']
_logger = logging.getLogger(__name__)


class ZgoubiException(Exception):
    """Exception raised for errors when running Zgoubi."""

    def __init__(self, m):
        self.message = m


class ZgoubiResults:
    """Results from a Zgoubi executable run."""
    def __init__(self, results: List[Mapping]):
        """
        `ZgoubiResults` is used to store results and outputs from a single or multiple Zgoubi runs. It is instanciated from
        a list of dictionnaries containing the results (each one being a mapping between `MappedParameters` (to identify
        from which run the results are from) and the results themselves (also a dictionnary)).

        Methods and properties of `ZgoubiResults` are used to access and process individual or multiple results. In
        particular it is possible to extract a set of tracks from the results.

        Examples:
            >>> 1 + 1 # TODO

        Args:
            results: a list of dictionnaries structure with the Zgoubi run information and errors.
        """
        self._results: List[Mapping] = results
        self._tracks: Optional[_pd.DataFrame] = None
        self._matrix: Optional[_pd.DataFrame] = None
        self._srloss: Optional[_pd.DataFrame] = None

    @classmethod
    def merge(cls, *results: ZgoubiResults):
        """Merge multiple ZgoubiResults into one.

        Args:
            results: list of `ZgoubiResults` to copy

        Returns:
            a new `ZgoubiResults` instance containing the concatenated results.
        """
        return cls([rr for r in results for rr in r._results])

    def __len__(self) -> int:
        """Length of the results list."""
        return len(self._results)

    def __copy__(self) -> ZgoubiResults:
        """Shallow copy operation."""
        return ZgoubiResults(self._results)

    def __getitem__(self, item: int):
        """Retrieve results from the list using a numeric index."""
        return self._results[item]

    def get_tracks(self, parameters: Optional[List[_MappedParameters]] = None) -> _pd.DataFrame:
        """
        Collects all tracks from the different Zgoubi instances matching the given parameters list
        in the results and concatenate them.

        Returns:
            A concatenated DataFrame with all the tracks in the result matching the parameters list.
        """
        if self._tracks is not None and parameters is None:
            return self._tracks
        tracks = list()
        for k, r in self.results.items():
            if parameters is None or k in parameters:
                try:
                    try:
                        p = r['path'].name
                    except AttributeError:
                        p = r['path']
                    tracks.append(read_plt_file(path=p))
                    for kk, vv in k.items():
                        tracks[-1][f"{kk[0]}.{kk[1]}"] = vv
                except FileNotFoundError:
                    _logger.warning(
                        f"Unable to read and load the Zgoubi .plt files required to collect the tracks for path "
                        "{r['path']}."
                    )
                    continue
        if len(tracks) > 0:
            tracks = _pd.concat(tracks)
        else:
            tracks = _pd.DataFrame()
        if parameters is None:
            self._tracks = tracks
        return tracks

    @property
    def tracks(self) -> _pd.DataFrame:
        """
        Collects all tracks from the different Zgoubi instances in the results and concatenate them.

        Returns:
            A concatenated DataFrame with all the tracks in the result.
        """
        return self.get_tracks()

    def get_srloss(self, parameters: Optional[List[_MappedParameters]] = None) -> _pd.DataFrame:
        """

        Args:
            parameters:

        Returns:

        """
        if self._srloss is not None and parameters is None:
            return self._srloss
        srloss = list()
        for k, r in self.results.items():
            if parameters is None or k in parameters:
                try:
                    try:
                        p = r['path'].name
                    except AttributeError:
                        p = r['path']
                    srloss.append(read_srloss_file(path=p))
                    for kk, vv in k.items():
                        srloss[-1][f"{kk[0]}.{kk[1]}"] = vv
                except FileNotFoundError:
                    _logger.warning(
                        "Unable to read and load the Zgoubi SRLOSS files required to collect the SRLOSS data."
                    )
                    continue
        if len(srloss) > 0:
            srloss = _pd.concat(srloss)
        else:
            srloss = _pd.DataFrame()
        if parameters is None:
            self._srloss = srloss
        return srloss

    @property
    def srloss(self) -> _pd.DataFrame:
        """

        Returns:

        """
        return self.get_srloss()

    @property
    def matrix(self) -> Optional[_pd.DataFrame]:
        """
        Collects all matrix data from the different Zgoubi instances in the results and concatenate them.

        Returns:
            A concatenated DataFrame with all the matrix information from the previous run.
        """
        if self._matrix is None:
            try:
                m = list()
                for r in self._results:
                    try:
                        p = r['path'].name
                    except AttributeError:
                        p = r['path']
                    m.append(read_matrix_file(path=p))
                self._matrix = _pd.concat(m)
            except FileNotFoundError:
                _logger.warning(
                    "Unable to read and load the Zgoubi MATRIX files required to collect the matrix data."
                )
                return None
        return self._matrix

    @property
    def results(self) -> Dict[_MappedParameters, Mapping]:
        """Raw information from the Zgoubi run.

        Provides the raw data structures from the Zgoubi runs.

        Returns:
            a list of mappings.
        """
        return {r['mapping']: r for r in self._results}

    @property
    def paths(self) -> Dict[_MappedParameters, Union[str, tempfile.TemporaryDirectory]]:
        """Path of all the directories for the runs present in the results.

        Returns:
            a list of directories.
        """
        return {k: v['path'] for k, v in self.results.items()}

    @property
    def mappings(self) -> List[_MappedParameters]:
        """Parametric mappings of all the runs present in the results.

        Returns:
            a list of parametric mappings.
        """
        return [m for m in self.results]

    def print(self, what: str = 'result'):
        """Helper function to print the raw results from a Zgoubi run."""
        for r in self.results.values():
            print('\n'.join(r[what]))


class Zgoubi:
    """High level interface to run Zgoubi from Python."""

    ZGOUBI_EXECUTABLE_NAME: str = 'zgoubi'
    """Default name of the Zgoubi executable."""

    ZGOUBI_RES_FILE: str = 'zgoubi.res'
    """Default name of the Zgoubi result '.res' file."""

    def __init__(self, executable: str = ZGOUBI_EXECUTABLE_NAME, path: str = None, n_procs: Optional[int] = None):
        """
        `Zgoubi` is responsible for running the Zgoubi executable within Zgoubidoo. It will run Zgoubi as a subprocess
        and offers a variety of concurency and parallelisation features.

        The `Zgoubi` object is an interface to the Zgoubi executable. The executable can be found automatically or its
        name and path can be specified.

        The Zgoubi executable is called on an instance of `Input` specifying a list of paths containing Zgoubi input
        files. Multiple instances can thus be run in parallel.

        TODO details on concurrency

        Args:
            - executable: name of the Zgoubi executable
            - path: path to the Zgoubi executable
            - n_procs: maximum number of Zgoubi simulations to be started in parallel

        """
        self._executable: str = executable
        self._n_procs: int = n_procs or multiprocessing.cpu_count()
        self._path: Optional[str] = path
        self._futures: List[Tuple[_PathDict, _Future]] = list()
        self._pool: _ThreadPoolExecutor = _ThreadPoolExecutor(max_workers=self._n_procs)

    def cleanup(self):
        """

        Returns:

        """
        self.wait()
        self._futures = list()

    @property
    def executable(self) -> str:
        """Provides the full path to the Zgoubi executable.

        Returns:
            full path to the Zgoubi executable.
        """
        return self._get_exec()

    def __call__(self,
                 zgoubi_input: Input,
                 mapping: _MappedParametersListType = None,
                 debug: bool = False,
                 cb: Callable = None,
                 filename: str = _ZGOUBI_INPUT_FILENAME,
                 path: Optional[str] = None,
                 ) -> Zgoubi:
        """
        Execute up to `n_procs` Zgoubi runs.

        Args:
            zgoubi_input: `Input` object specifying the Zgoubi inputs and input paths.
            mapping: TODO
            debug: verbose output
            (default to `multiprocessing.cpu_count`)

        Returns:
            a ZgoubiResults object holding the simulation results.

        Raises:
            a ZgoubiException in case the input paths list is empty.
        """
        if len(zgoubi_input.paths) == 0:
            paths = zgoubi_input(mappings=mapping, filename=filename, path=path)
        else:
            paths = zgoubi_input.paths

        for m, path in paths.items():
            _logger.info(f"Starting Zgoubi in {path}.")
            future = self._pool.submit(
                self._execute_zgoubi,
                {**mapping, **m},
                zgoubi_input,
                path,
            )
            if cb is not None:
                future.add_done_callback(cb)
            self._futures.append((paths, future))
        return self

    def wait(self):
        """
        TODO

        """
        self._pool.shutdown()
        self._pool = _ThreadPoolExecutor(max_workers=self._n_procs)

    def collect(self) -> ZgoubiResults:
        """
        TODO
        Returns:

        """
        self.wait()
        return ZgoubiResults(results=list(map(lambda _: _[1].result(), self._futures)))

    def _execute_zgoubi(self,
                        mapping: _MappedParametersType,
                        zgoubi_input: Input,
                        path: Union[str, tempfile.TemporaryDirectory] = '.',
                        debug=False
                        ) -> dict:
        """Run Zgoubi as a subprocess.

        Zgoubi is run as a subprocess; the standard IOs are piped to the Python process and retrieved.

        Args:
            zgoubi_input: Zgoubi input physics (used after the run to process the output of each element).
            path: path to the input file.
            mapping: TODO
            debug: verbose output.

        Returns:
            a dictionary holding the results of the run.

        Raises:
            FileNotFoundError if the result file is not present at the end of the execution.
        """
        stderr = None
        try:
            p = path.name  # Path from a TemporaryDirectory
        except AttributeError:
            p = path  # p is a string
        proc = sub.Popen([self.executable],
                         stdin=sub.PIPE,
                         stdout=sub.PIPE,
                         stderr=sub.STDOUT,
                         cwd=p,
                         )

        # Run
        _logger.info(f"Zgoubi process in {path} has started.")
        output = proc.communicate()

        # Collect STDERR
        if output[1] is not None:
            stderr = output[1].decode()

        # Extract element by element output
        try:
            result = open(os.path.join(p, Zgoubi.ZGOUBI_RES_FILE)).read().split('\n')
        except FileNotFoundError:
            raise ZgoubiException("Zgoubi execution ended but result '.res' file not found.")

        for e in zgoubi_input.line:
            e.attach_output(outputs=Zgoubi.find_labeled_output(result, e.LABEL1),
                            zgoubi_input=zgoubi_input,
                            parameters=mapping,
                            )

        # Extract CPU time
        cputime = -1.0
        if stderr is None:
            lines = [line.strip() for line in output[0].decode().split('\n') if
                     re.search('CPU time', line)]
            if len(lines):
                cputime = float(re.search(r"\d+\.\d+[E|e]?[+|-]?\d+", lines[0]).group())
        if debug:
            print(output[0].decode())
        _logger.info(f"Zgoubi process in {path} finished in {cputime} s.")
        return {
            'stdout': output[0].decode().split('\n'),
            'stderr': stderr,
            'cputime': cputime,
            'result': result,
            'input': zgoubi_input,
            'path': path,
            'mapping': mapping,
        }

    def _get_exec(self, optional_path: Optional[str] = '/usr/local/bin') -> str:
        """Retrive the path to the Zgoubi executable.

        Args:
            optional_path: additional path provided to the `which` command.

        Returns:
            a string representing the full path to the executable.
        """
        executable = None
        if self._path is not None:
            executable = os.path.join(self._path, self._executable)
        elif sys.platform in ('win32', 'win64'):
            executable = shutil.which(self._executable)
        else:
            if os.path.isfile(f"{sys.prefix}/bin/{self._executable}"):
                executable = f"{sys.prefix}/bin/{self._executable}"
            else:
                executable = shutil.which(self._executable, path=os.path.join(os.environ['PATH'], optional_path))
        if executable is None:
            raise ZgoubiException("Unable to locate the Zgoubi executable.")
        return executable

    @staticmethod
    def find_labeled_output(out: Iterable[str], label: str) -> List[str]:
        """
        Process the Zgoubi output and retrieves output data for a particular labeled element.

        Args:
            - out: the Zgoubi output
            - label: the label of the element to be retrieved

        Returns:
            the output of the given label
        """
        data: List[str] = []
        for l in out:
            if label in l and 'Keyword' in l:
                data.append(l)
                continue
            if len(data) > 0:
                if '****' in l:  # This might be a bit fragile
                    break
                data.append(l)
        return list(filter(lambda _: len(_), data))
