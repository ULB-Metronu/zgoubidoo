"""Provides an interface to run Zgoubi from Python; supports multiprocessing.

.. seealso::

    The full `Zgoubi User Guide`_ can also be consulted for reference.

    .. _Zgoubi User Guide: https://sourceforge.net/projects/zgoubi/


"""
from typing import List, Mapping, Iterable, Optional
from functools import partial as _partial
import logging
import shutil
import os
import sys
import re
import multiprocessing
from multiprocessing.pool import ThreadPool as _ThreadPool
import subprocess as sub
import pandas as _pd
from .commands import Matrix as _Matrix
from .input import Input
from .output import read_plt_file, read_matrix_file


class ZgoubiException(Exception):
    """Exception raised for errors when running Zgoubi."""

    def __init__(self, m):
        self.message = m


class ZgoubiRun:
    """

    """
    def __init__(self, results: List[Mapping], with_matrix: bool = False):
        """

        Args:
            results: a list of dictionnaries structure with the Zgoubi run information and errors.
            with_matrix: if True, the Zgoubi MATRIX file output is read as well.
        """
        self._with_matrix: bool = with_matrix
        self._results: List[Mapping] = results
        self._tracks: Optional[_pd.DataFrame] = None
        self._matrix: Optional[_pd.DataFrame] = None

    @property
    def tracks(self) -> Optional[_pd.DataFrame]:
        """
        Collects all tracks from the different Zgoubi instances in the results and concatenate them.

        Returns:
            A concatenated DataFrame with all the tracks in the result.

        Raises:
            FileNotFoundError in case the file is not present.
        """
        if self._tracks is None:
            try:
                tracks = list()
                for r in self._results:
                    tracks.append(read_plt_file(path=r['path']))
                self._tracks = _pd.concat(tracks)
            except FileNotFoundError:
                logging.getLogger(__name__).warning(
                    "Unable to read and load the Zgoubi .plt files required to collect the tracks."
                )
                return None
        return self._tracks

    @property
    def matrix(self) -> Optional[_pd.DataFrame]:
        """
        Collects all matrix data from the different Zgoubi instances in the results and concatenate them.

        Returns:
            A concatenated DataFrame with all the matrix information from the previous run.

        Raises:
            FileNotFoundError in case the file is not present.

        """
        if self._matrix is None and self._with_matrix:
            try:
                m = list()
                for r in self._results:
                    m.append(read_matrix_file(path=r['path']))
                self._matrix = _pd.concat(m)
            except FileNotFoundError:
                logging.getLogger(__name__).warning(
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

    def print(self, what='result'):
        """Print."""
        for r in self.results:
            print('\n'.join(r[what]))


class Zgoubi:
    """High level interface to run Zgoubi from Python."""

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

    def __call__(self, zgoubi_input: Input, debug: bool = False, n_procs: Optional[int] = None) -> ZgoubiRun:
        """
        Starts up to `n_procs` Zgoubi runs.

        Args:
            zgoubi_input: `Input` object specifying the Zgoubi inputs and input paths.
            debug: verbose output
            n_procs: maximum number of Zgoubi simulations to be started in parallel
            (default to `multiprocessing.cpu_count`)

        Returns:
            a ZgoubiRun object holding the simulation results.

        Raises:
            a ZgoubiException in case the input paths list is empty.
        """
        n = n_procs or multiprocessing.cpu_count()
        self._results = list()
        pool = _ThreadPool(n)
        if len(zgoubi_input.paths) == 0:
            raise ZgoubiException("The input must be written before calling Zgoubi.")
        for p in zgoubi_input.paths:
            try:
                path = p.name  # Path from a TemporaryDirectory
            except AttributeError:
                path = p  # Path as a string
            self._results.append(pool.apply_async(self._execute_zgoubi, (zgoubi_input, path)))
        pool.close()
        pool.join()
        return ZgoubiRun(results=list(map(lambda _: getattr(_, 'get', None)(), self._results)),
                         with_matrix=bool(_Matrix in zgoubi_input)
                         )

    def _execute_zgoubi(self, zgoubi_input: Input, path: str = '.', debug=False) -> dict:
        """Run Zgoubi as a subprocess.

        Zgoubi is run as a subprocess; the standard IOs are piped to the Python process and retrieved.

        Args:
            zgoubi_input: Zgoubi input sequence (used after the run to process the output of each element).
            path: path to the input file.
            debug: verbose output.

        Returns:
            a dictionary holding the results of the run.

        Raises:
            FileNotFoundError if the result file is not present at the end of the execution.
        """
        stderr = None
        p = sub.Popen([self._get_exec()],
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
        return {
            'stdout': output[0].decode().split('\n'),
            'stderr': stderr,
            'cputime': cputime,
            'result': result,
            'input': zgoubi_input,
            'path': path,
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
    def find_labeled_output(out: Iterable[str], label: str) -> list:
        """
        Process the Zgoubi output and retrieves output data for a particular labeled element.

        Args:
            - out: the Zgoubi output
            - label: the label of the element to be retrieved

        Returns:
            the output of the given label
        """
        data = []
        for l in out:
            if label in l and 'Keyword' in l:
                data.append(l)
                continue
            if len(data) > 0:
                if '****' in l:
                    break
                data.append(l)
        return list(filter(lambda _: len(_), data))
