"""Provides an interface to run Zgoubi from Python; supports multiprocessing.

.. seealso::

    The full `Zgoubi User Guide`_ can also be consulted for reference.

    .. _Zgoubi User Guide: https://sourceforge.net/projects/zgoubi/


"""
from typing import List, Mapping, Iterable, Optional, Tuple
from functools import partial as _partial
import logging
import shutil
import tempfile
import os
import sys
import re
import multiprocessing
from multiprocessing.pool import ThreadPool as _ThreadPool
import subprocess as sub
import pandas as _pd
from .input import Input
from .output import read_plt_file, read_matrix_file

_logger = logging.getLogger(__name__)


class ZgoubiException(Exception):
    """Exception raised for errors when running Zgoubi."""

    def __init__(self, m):
        self.message = m


class ZgoubiResults:
    """Results from a Zgoubi executable run.

    Examples:
        >>> 1 + 1 # TODO

    """
    def __init__(self, results: List[Mapping]):
        """

        Args:
            results: a list of dictionnaries structure with the Zgoubi run information and errors.
        """
        self._results: List[Mapping] = results
        self._tracks: Optional[_pd.DataFrame] = None
        self._matrix: Optional[_pd.DataFrame] = None

    def __len__(self):
        return len(self._results)

    def __getitem__(self, item):
        return self._results[item]

    def get_tracks(self, parameters: Optional[List[Mapping[Tuple[str], float]]] = None):
        """
        Collects all tracks from the different Zgoubi instances matching the given parameters list
        in the results and concatenate them.

        Returns:
            A concatenated DataFrame with all the tracks in the result matching the parameters list.

        Raises:
            FileNotFoundError in case the file is not present.
        """
        if self._tracks is not None and parameters is None:
            return self._tracks
        tracks = list()
        for r in self.results:
            if parameters is None or r['mapping'] in parameters:
                try:
                    tracks.append(read_plt_file(path=r['path']))
                except FileNotFoundError:
                    _logger.warning(
                        f"Unable to read and load the Zgoubi .plt files required to collect the tracks for path "
                        "{r['path']}."
                    )
                    return None
        tracks = _pd.concat(tracks)
        if parameters is None:
            self._tracks = tracks
        return tracks

    @property
    def tracks(self) -> Optional[_pd.DataFrame]:
        """
        Collects all tracks from the different Zgoubi instances in the results and concatenate them.

        Returns:
            A concatenated DataFrame with all the tracks in the result.

        Raises:
            FileNotFoundError in case the file is not present.
        """
        return self.get_tracks()

    @property
    def matrix(self) -> Optional[_pd.DataFrame]:
        """
        Collects all matrix data from the different Zgoubi instances in the results and concatenate them.

        Returns:
            A concatenated DataFrame with all the matrix information from the previous run.

        Raises:
            FileNotFoundError in case the file is not present.

        """
        if self._matrix is None:
            try:
                m = list()
                for r in self._results:
                    m.append(read_matrix_file(path=r['path']))
                self._matrix = _pd.concat(m)
            except FileNotFoundError:
                _logger.warning(
                    "Unable to read and load the Zgoubi MATRIX files required to collect the matrix data."
                )
                return None
        return self._matrix

    @property
    def results(self) -> List[Mapping]:
        """Raw information from the Zgoubi run.

        Provides the raw data structures from the Zgoubi runs.

        Returns:
            a list of mappings.
        """
        return self._results

    @property
    def paths(self) -> List[tempfile.TemporaryDirectory]:
        """Path of all the directories for the runs present in the results.

        Returns:
            a list of directories.
        """
        return [r['path'] for r in self.results]

    @property
    def mappings(self) -> List[Mapping[Tuple[str], float]]:
        """Parametric mappings of all the runs present in the results.

        Returns:
            a list of parametric mappings.
        """
        return [r['mapping'] for r in self.results]

    def print(self, what: str = 'result'):
        """Helper function to print the raw results from a Zgoubi run."""
        for r in self.results:
            print('\n'.join(r[what]))


class Zgoubi:
    """High level interface to run Zgoubi from Python.

    `Zgoubi` is responsible for running the Zgoubi executable within Zgoubidoo. It will run Zgoubi as a subprocess and
    offers a variety of concurency and parallelisation features.
    """

    ZGOUBI_EXECUTABLE_NAME: str = 'zgoubi'
    """Default name of the Zgoubi executable."""

    ZGOUBI_RES_FILE: str = 'zgoubi.res'
    """Default name of the Zgoubi result '.res' file."""

    def __init__(self, executable: str = ZGOUBI_EXECUTABLE_NAME, path: str = None):
        """
        The created `Zgoubi` object is an interface to the Zgoubi executable. The executable can be found
        automatically or its name and path can be specified.

        The Zgoubi executable is called on an instance of `Input` specifying a list of paths containing Zgoubi input
        files. Multiple instances can thus be run in parallel.

        Args:
            - executable: name of the Zgoubi executable
            - path: path to the Zgoubi executable
        """
        self._executable: str = executable
        self._path: str = path
        self._results: List[multiprocessing.pool.ApplyResult] = list()

    @property
    def executable(self) -> str:
        """Provides the full path to the Zgoubi executable.

        Returns:
            full path to the Zgoubi executable.
        """
        return self._get_exec()

    def __call__(self, zgoubi_input: Input, debug: bool = False, n_procs: Optional[int] = None) -> ZgoubiResults:
        """
        Execute up to `n_procs` Zgoubi runs.

        Args:
            zgoubi_input: `Input` object specifying the Zgoubi inputs and input paths.
            debug: verbose output
            n_procs: maximum number of Zgoubi simulations to be started in parallel
            (default to `multiprocessing.cpu_count`)

        Returns:
            a ZgoubiResults object holding the simulation results.

        Raises:
            a ZgoubiException in case the input paths list is empty.
        """

        def execute_in_thread():
            """Closure to execute Zgoubi within a Threadpool"""
            if len(zgoubi_input.paths) == 0:
                raise ZgoubiException("The input must be written before calling Zgoubi.")
            for p, m in zgoubi_input.paths.items():
                try:
                    path = p.name  # Path from a TemporaryDirectory
                except AttributeError:
                    path = p  # Path as a string
                _logger.info(f"Starting Zgoubi in {path}.")
                self._results.append(pool.apply_async(self._execute_zgoubi, (zgoubi_input, path, m)))

        n = n_procs or multiprocessing.cpu_count()
        self._results = list()
        pool: _ThreadPool = _ThreadPool(n)
        execute_in_thread()
        pool.close()
        pool.join()
        return ZgoubiResults(results=list(map(lambda _: _.get(), self._results)))

    def _execute_zgoubi(self,
                        zgoubi_input: Input,
                        path: str = '.',
                        mapping: Mapping[Tuple[str], float] = None,
                        debug=False
                        ) -> dict:
        """Run Zgoubi as a subprocess.

        Zgoubi is run as a subprocess; the standard IOs are piped to the Python process and retrieved.

        Args:
            zgoubi_input: Zgoubi input sequence (used after the run to process the output of each element).
            path: path to the input file.
            mapping: TODO
            debug: verbose output.

        Returns:
            a dictionary holding the results of the run.

        Raises:
            FileNotFoundError if the result file is not present at the end of the execution.
        """
        stderr = None
        p = sub.Popen([self.executable],
                      stdin=sub.PIPE,
                      stdout=sub.PIPE,
                      stderr=sub.STDOUT,
                      cwd=path,
                      )

        # Run
        output = p.communicate()

        # Collect STDERR
        if output[1] is not None:
            stderr = output[1].decode()

        # Extract element by element output
        try:
            result = open(os.path.join(path, Zgoubi.ZGOUBI_RES_FILE)).read().split('\n')
        except FileNotFoundError:
            raise ZgoubiException("Zgoubi execution ended but result '.res' file not found.")
        for e in zgoubi_input.line:
            list(
                map(_partial(e.attach_output, zgoubi_input=zgoubi_input), Zgoubi.find_labeled_output(result, e.LABEL1))
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

    def _get_exec(self, optional_path: str = '/usr/local/bin') -> str:
        """Retrive the path to the Zgoubi executable.

        Args:
            optional_path: additional path provided to the `which` command.

        Returns:
            a string representing the full path to the executable.
        """
        if self._path is not None:
            return os.path.join(self._path, self._executable)
        elif sys.platform in ('win32', 'win64'):
            return shutil.which(self._executable)
        else:
            if os.path.isfile(f"{sys.prefix}/bin/{self._executable}"):
                return f"{sys.prefix}/bin/{self._executable}"
            else:
                return shutil.which(self._executable, path=os.path.join(os.environ['PATH'], optional_path))

    @staticmethod
    def find_labeled_output(out: Iterable[str], label: str) -> Iterable[str]:
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
